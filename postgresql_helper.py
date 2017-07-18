#!/usr/bin/env python2

import sys, argparse, os
from os.path import isfile

def main(argv):
    filename = 'drec_stud_site_backup'

    arg_file = [
            '-f', 
            '--file', 
            'filename', 
            'set PostgreSQL backup file to restore', 
            'filename'
            ]
    parser = argparse.ArgumentParser(description='Restore PostgreSQL database. Database must exist and should be empty.')

    parser.add_argument('-r', '--restore', action='store_true', help='restore database from backup file; creates backup by default')
    parser.add_argument('-f', '--file', type=str, default=filename, required=False, help='set backup file (no extention)')

    args = parser.parse_args()

    args.file += '.sql'
    
    if args.restore:
        if isfile(args.file) == False:
            sys.exit('File "{0}" does not exist!'.format(args.file))
        command_str = 'pgsql drec_stud_site < {0}'.format(args.file)
    else:
        command_str = 'pg_dump drec_stud_site > {0}'.format(args.file)
        
    print (args)

    print ('Trying to process:\n$ ', command_str)
    os.system(command_str)

if __name__ == '__main__':
main(sys.argv[1:])
