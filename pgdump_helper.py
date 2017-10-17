#!/usr/bin/env python3

import sys, argparse, os, datetime, glob, getpass
from os.path import isfile

def main(argv):
    filename = 'drec_stud_site_backup_{0}'.format(datetime.datetime.now().strftime('%Y_%m_%d_%H_%M_%S'))

    parser = argparse.ArgumentParser(description='Restore PostgreSQL database. Database must exist and should be empty.')

    parser.add_argument('-r', '--restore', action='store_true', help='restore database from backup file; creates backup by default')
    parser.add_argument('-f', '--file', type=str, default=filename, required=False, help='set backup file (no extention)')

    args = parser.parse_args()

    if args.file[-4:] != '.sql':
        args.file += '.sql'
    filename += '.sql'
    command_str = ''
    
    # See https://www.postgresql.org/docs/9.5/static/backup-dump.html
    if args.restore:
        if isfile(args.file) == False and args.file != filename:
            sys.exit('File "{0}" does not exist!'.format(args.file))
        elif args.file == filename:
            l = glob.glob('drec_stud_site_backup_*')
            if len(l) > 1:
                sys.exit('Too many files with default filenames found! Conflict: {0}'.format(str(l)))
            elif not l:
                sys.exit('File "{0}" does not exist!'.format(args.file))
            else:
                args.file = l[0]
        pswd = getpass.getpass(prompt = 'Enter \'postgres\' password: ')
        if pswd:
            pswd = '-p {0}'.format(pswd)
        try:
            os.system('dropdb -U postgres {0} drec_stud_site'.format(pswd))
        except:
            pass
        command_str = 'createdb -U postgres {0} -T template0 drec_stud_site\n'.format(pswd)
        command_str += 'psql -U postgres {0} -d drec_stud_site < {1}\n'.format(pswd, args.file)
        command_str += 'psql -U postgres {0} -d drec_stud_site -c "GRANT ALL PRIVILEGES ON DATABASE drec_stud_site TO drec_stud_site_admin"'.format(pswd)
    else:
        command_str = 'pg_dump -U drec_stud_site_admin drec_stud_site > {0}'.format(args.file)
        
    print (args)

    print ('Trying to process:\n$ ', command_str.replace('\n', '\n$ '))
    os.system(command_str)

if __name__ == '__main__':
    main(sys.argv[1:])
