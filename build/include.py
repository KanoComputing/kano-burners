
# include.py
#
# Copyright (C) 2014 Kano Computing Ltd.
# License: http://www.gnu.org/licenses/gpl-2.0.txt GNU General Public License v2
#
# [File description]


import os
import glob

def extra_datas(path):
    def recursive_glob(path, files):
        for file_path in glob.glob(path):
            if os.path.isfile(file_path):
                files.append(os.path.join(os.getcwd(), file_path))
            recursive_glob('{}/*'.format(file_path), files)

    files = []
    extra_datas = []

    if os.path.isfile(path):
        files.append(os.path.join(os.getcwd(), path))
    else:
        recursive_glob('{}/*'.format(path), files)

    for f in files:
        extra_datas.append((f.split('kano-burners')[1][1:], f, 'DATA'))
    return extra_datas

a.datas += extra_datas(os.path.join(os.getcwd(), '..', '..', 'res'))
a.datas += extra_datas(os.path.join(os.getcwd(), '..', '..', 'win'))
a.datas += extra_datas(os.path.join(os.getcwd(), '..', '..', 'DISCLAIMER'))
