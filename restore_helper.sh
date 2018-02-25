set -e
# Remember! Only double quotes accept inserting variables
# For getopt see www.bahmanm.com/blogs/command-line-options-how-to-parse-in-bash-using-getopt
# Features:
# - help
# - directory path
# - destination file
# - user existing pg_dump
# Default values:
DIRECTORY=''
RESTORE_FLAG=0
NOCLEAR_FLAG=0
PGDUMP_FILE=''
FILE=''
# getopt will parse our arguments
TEMP=`getopt -o d:f:F:h --long directory:,file:,pgdump_file:,help,restore,noclear -n 'restore_helper.sh' -- "$@"`
# Execute command
eval set -- "$TEMP"

# Extract result into variables
# Infinite loop is required because we don`t know the number of arguments
while true ; do
    case "$1" in
        -d|--directory)
            case "$2" in
                "") shift 2 ;;
                *) DIRECTORY=$2 ; shift 2 ;;
            esac ;;
        -f|--file)
            case "$2" in
                "") shift 2 ;;
                *) FILE=$2 ; shift 2 ;;
            esac ;;
        -F|--pgdump_file)
            case "$2" in
                "") shift 2 ;;
                *) PGDUMP_FILE=$2 ; shift 2 ;;
            esac ;;
        --noclear) NOCLEAR_FLAG=1 ; shift ;;
        --restore) RESTORE_FLAG=1 ; shift ;;
        -h|--help) printf "\
restore_helper.sh - restore and backup database and static files.
Arguments:
  -h,--help        - show this help
  -d,--directory   - select directory to restore to/from
  -f,--file        - select file to restore to/from
  -F,--pgdump_file - specify file for pgdump_helper.py
  --restore        - restore, otherwize; Note: database must exits
  -F,--pgdump_file - specify file for pgdump_helper.py\n" ; exit 0 ;;
        --) shift ; break ;;
        *) printf "Error! %s\n" "$1" ; exit 1 ;;
    esac
done

printf "Input: RESTORE=%d, DIRECTORY=%s, FILE=%s, PGDUMP_FILE=%s, NOCLEAR=%d\n" "$RESTORE_FLAG" "$DIRECTORY" "$FILE" "$PGDUMP_FILE"

# Restore
if [ $RESTORE_FLAG -eq 1 ]; then
    if [ -n "$FILE" ] && [ !-f $FILE ]; then
        echo "File \"$FILE\" not found!" ; exit 1 ;
    elif [ -z "$FILE" ]; then
        m=(drec_stud_site_*.zip)
        if [ ${#m[@]} -eq 0 ]; then
            echo "No 'drec_stud_site_*.zip' file found. Please set archive via (-f)/(--file) option" ; exit 0 ;
        elif [ ${#m[@]} -gt 1 ]; then
            echo "Too many files were detected. Please one it via (-f)/(--file) option" ; exit 0 ;
        fi
        #echo $m
        #echo ${#m[@]}
        FILE=${m[0]}
    fi
    # Check DIRECTORY
    if [ -n "$DIRECTORY" ] && [ ! -d "$DIRECTORY" ]; then
        echo "Directory \"$DIRECTORY\" does not exists"; exit 1;
    else
        if [ ${DIRECTORY: -1} != '/' ]; then
            DIRECTORY="${DIRECTORY}/"
        fi
    fi
    if [ -n "$DIRECTORY" ]; then
        DIRECTORY_COM="-d ${DIRECTORY}"
    fi
    # Make .sql filename from FILE
    PGDUMP_FILE="${DIRECTORY}$(basename $FILE '.zip').sql"
    printf "Final: RESTORE=%d, DIRECTORY=%s, FILE=%s, PGDUMP_FILE=%s, NOCLEAR=%d\n" "$RESTORE_FLAG" "$DIRECTORY" "$FILE" "$PGDUMP_FILE"
    # Unzip
    COM="unzip -o \"$DIRECTORY_COM\" \"$FILE\""
    echo $COM
    unzip -o $DIRECTORY_COM $FILE
    # Restore database
    ./pgdump_helper.py --restore -f $PGDUMP_FILE
    # Clear mess if not canceled
    if [ $NOCLEAR_FLAG -eq 0 ]; then
        rm $PGDUMP_FILE
    fi
# Backup, default
else
    # Check DIRECTORY
    if [ -z "$DIRECTORY" ]; then
        if [ ! -d 'collected_static' ] || [ ! -d 'media' ] || [ ! -d 'logs' ] || [ ! -d 'src' ]; then
            echo `Some of "collected_static", "media", "logs" or "src" not found at "$PWD"`; exit 1;
        fi
    else
        if [ ${DIRECTORY: -1} != '/' ]; then
            DIRECTORY="${DIRECTORY}/"
        fi
        if [ ! -d "${DIRECTORY}collected_static" ] || [ ! -d "${DIRECTORY}media"] || [ ! -d "${DIRECTORY}logs" ] || [ ! -d "${DIRECTORY}src" ]; then
            echo "Some of \"collected_static\", \"media\", \"logs\" or \"src\" not found at \"$DIRECTORY\""; exit 1;
        fi
    fi
    # Check FILE extention
    if [ -z "$FILE" ]; then
        FILE="drec_stud_site_backup_$(date +'%Y_%m_%d_%H_%M_%S')"
    fi
    # Check PGDUMP_FILE
    if [ -z "$PGDUMP_FILE" ]; then
        ./pgdump_helper.py -f ${DIRECTORY}${FILE}
        PGDUMP_FILE=${FILE}.sql
    else
        if [ ! -f ${DIRECTORY}$PGDUMP_FILE ]; then
            echo `File "$PGDUMP_FILE" not found in ${PWD}${DIRECTORY}`; exit 1;
        fi
    fi
    if [ ${FILE: -4} != '.zip' ]; then
        FILE="${FILE}.zip"
    fi
    printf "Final: RESTORE=%d, DIRECTORY=%s, FILE=%s, PGDUMP_FILE=%s, NOCLEAR=%d\n" "$RESTORE_FLAG" "$DIRECTORY" "$FILE" "$PGDUMP_FILE"
    # Zip result, cd before (otherwise it will be mess)
    # push/pop path
    if [ -z "$DIRECTORY" ]; then
        DIRECTORY='.'
    fi
    pushd $DIRECTORY
    zip -r ${FILE} media collected_static logs $PGDUMP_FILE
    popd
    # Clear mess if not canceled
    if [ $NOCLEAR_FLAG -eq 0 ]; then
        rm $PGDUMP_FILE
    fi
fi

echo 'Done!'
