#!/usr/bin/env python

# utils.py
#
# Copyright (C) 2014 Kano Computing Ltd.
# License: http://www.gnu.org/licenses/gpl-2.0.txt GNU General Public License v2
#


import os
import subprocess
import signal
import shutil
from urllib2 import urlopen


BYTES_IN_MEGABYTE = 1048576     # conversion constants
BYTES_IN_GIGABYTE = 1073741824


def debugger(text):
    if True:
        print text


def run_cmd(cmd):
    process = subprocess.Popen(cmd, shell=True,
                               stdout=subprocess.PIPE, stderr=subprocess.PIPE,
                               preexec_fn=restore_signals)

    stdout, stderr = process.communicate()
    return_code = process.returncode
    return stdout, stderr, return_code


def restore_signals():
        signals = ('SIGPIPE', 'SIGXFZ', 'SIGXFSZ')
        for sig in signals:
            if hasattr(signal, sig):
                signal.signal(getattr(signal, sig), signal.SIG_DFL)


def delete_dir(directory):
    if os.path.exists(directory):
        shutil.rmtree(directory)


def make_dir(directory):
    if not os.path.exists(directory):
        os.makedirs(directory)


def read_file_contents_as_lines(path):
    if os.path.exists(path):
        with open(path) as infile:
            content = infile.readlines()
            lines = [line.strip() for line in content]
            return lines


def is_internet():
    url_list = ['http://173.194.34.84',  # google
                'http://199.16.156.38',  # twitter
                'http://31.13.80.65',    # facebook
                'http://173.194.34.78',  # youtube
                'http://178.236.7.220']  # amazon
    for url in url_list:
        try:
            urlopen(url, timeout=1)
            return True
        except:
            pass
    return False
