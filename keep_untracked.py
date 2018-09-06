#!/usr/bin/env python3

import sys, os

def main(argv):
    file_list = [
        'setting_additions.py',
    ]
    for f in file_list:
        print('Stop stacking: {0}'.format(f))
        os.system('git update-index --assume-unchanged {0}'.format(f))

if __name__ == '__main__':
    main(sys.argv[1:])
