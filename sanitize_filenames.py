#!/usr/bin/env python
import os
from glob import glob

from unidecode import unidecode


if __name__ == '__main__':
    for f in glob('*pdf'):
        clean_name = unidecode(f.decode('utf-8'))
        if f != clean_name:
            os.rename(f, clean_name)
            print('renamed "{0}" to "{1}"'.format(f, clean_name))
