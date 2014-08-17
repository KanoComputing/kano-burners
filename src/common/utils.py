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
from PyQt4 import QtCore


# Paths used throughout the project
res_path = "res/"
images_path = res_path + "images/"
css_path = res_path + "CSS/"
win_tools_path = "win\\"
_7zip_path = win_tools_path + "7zip\\"
_dd_path = win_tools_path + "dd\\"
_nircmd_path = win_tools_path + "nircmd\\"


# Conversion constants
BYTES_IN_MEGABYTE = 1048576
BYTES_IN_GIGABYTE = 1073741824
BYTES_IN_GIBIBYTE = 1000000000


# The URL used to download information about the lastest OS release
LATEST_OS_INFO_URL = 'http://downloads.kano.me/public/latest.json'


# This should be FALSE when building for distribution
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


# used on Windows as there is no support for 'preexec_fn'
def run_cmd_no_pipe(cmd):
    process = subprocess.Popen(cmd, shell=True,
                               stdout=subprocess.PIPE, stderr=subprocess.PIPE)

    stdout, stderr = process.communicate()
    return_code = process.returncode
    return stdout, stderr, return_code


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


def write_file_contents(path, data):
    with open(path, 'w') as outfile:
        outfile.write(data)


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


# This method is used to set CSS styling
# for a given widget from a given CSS file
def load_css_for_widget(widget, css_path):
    css = QtCore.QFile(css_path)
    css.open(QtCore.QIODevice.ReadOnly)
    if css.isOpen():
        widget.setStyleSheet(QtCore.QVariant(css.readAll()).toString())
    css.close()
