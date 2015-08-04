#!/usr/bin/env python

# utils.py
#
# Copyright (C) 2014,2015 Kano Computing Ltd.
# License: http://www.gnu.org/licenses/gpl-2.0.txt GNU General Public License v2
#
#
# Utility functions
#
# This is a mixed collection of functions which can be
# used on all three platforms. Anything else, must be
# placed in the appropriate platform folder.


import os
import sys
import shutil
import signal
import subprocess
from urllib import urlencode
from urllib2 import urlopen
from PyQt4 import QtCore
import platform
import threading

from src.common.paths import temp_path


# Conversion constants
# technically, gigabyte=1000^3 and gibibyte=1024^3 - here, the difference matters
BYTES_IN_MEGABYTE = 1000000
BYTES_IN_GIGABYTE = 1000000000

BURNER_VERSION = 2

# Path for submitting feedback
FEEDBACK_URL = "http://api.kano.me/feedback"

cmd_env = os.environ.copy().update(LC_ALL='C')

# The URL used to download information about the lastest OS release
LATEST_OS_INFO_URL=None
if os.environ.has_key('KANO_BURNER_TEST_URL'):
    LATEST_OS_INFO_URL= os.environ['KANO_BURNER_TEST_URL']
else:
    LATEST_OS_INFO_URL = 'http://downloads.kano.me/public/latest.json'

deb_path = None
logfile = False
# if we are running from a PyInstaller bundle, print debug to file
if getattr(sys, 'frozen', False) or os.environ.has_key("KANO_BURNER_TEST_LOG"):
    deb_path = os.path.join(temp_path, 'debug.txt')
    logfile = True
else:
    if deb_path is None:
        if platform.system() == 'Darwin':
            deb_path='/dev/tty'

def debugger(text):
    global deb_path
    if deb_path is not None:
        with open(deb_path, "a") as debug_file:
            debug_file.write(text + '\n')
            debug_file.flush()
    else:
        print text
        sys.stdout.flush()


def get_log():
    global logfile, deb_path
    if not logfile:
        # No log file, can't submit errors
        return None
    try:        
        return read_file_contents(deb_path)
    except:
        return None


def submit_log(log, email):

    payload = {
        "text": log,
        "email": email,
        "username": "NotApplicable",
        "category": "Burner",
        "subject": "Burner failure in version {} on {}".format(BURNER_VERSION, platform.version())
    }
    data = urlencode(payload)
    debugger("URL: "+FEEDBACK_URL+data)
    #content = urlopen(url=FEEDBACK_URL, data=data).read()
    debugger(content)


        
def run_cmd(cmd):
    process = subprocess.Popen(cmd, shell=True, env=cmd_env,
                               stdout=subprocess.PIPE, stderr=subprocess.PIPE,
                               preexec_fn=restore_signals)

    stdout, stderr = process.communicate()
    return_code = process.returncode
    debugger('ran: [{}] {}'.format(cmd, return_code))
    return stdout, stderr, return_code


def restore_signals():
        signals = ('SIGPIPE', 'SIGXFZ', 'SIGXFSZ')
        for sig in signals:
            if hasattr(signal, sig):
                signal.signal(getattr(signal, sig), signal.SIG_DFL)


def run_cmd_no_pipe(cmd):
    # used on Windows as there is no support for 'preexec_fn'
    # all handles (in, out, err) need to be set due to PyInstaller bundling
    process = subprocess.Popen(cmd, shell=True, stdin=subprocess.PIPE,
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


def read_file_contents(path):
    if os.path.exists(path):
        with open(path) as infile:
            content = infile.readlines()
            lines = [line.strip() for line in content]
            return '\n'.join(lines)


def write_file_contents(data, path):
    with open(path, 'w') as outfile:
        outfile.write(data)


def is_internet():
    url_list = ['http://google.com',
                'http://twitter.com',
                'http://facebook.com',
                'http://youtube.com']
    for url in url_list:
        try:
            urlopen(url, timeout=1)
            return True
        except Exception as e:
            debugger('internet {}'.format(e))
    return False


def load_css_for_widget(widget, css_path, res_path=''):
    '''
    This method is used to set CSS styling for a given
    widget from a given CSS file.

    If a resource path is given, it will attempt to replace
    {res_path} in the CSS with that path.

    NOTE: It assumes only one {res_path} string will be on a single line.
    '''

    css = QtCore.QFile(css_path)
    css.open(QtCore.QIODevice.ReadOnly)
    if css.isOpen():
        style_sheet = str(QtCore.QVariant(css.readAll()).toString())

        if res_path:
            style_sheet_to_format = style_sheet
            style_sheet = ''

            for line in style_sheet_to_format.splitlines():
                try:
                    line = line.format(res_path=os.path.join(res_path, '').replace('\\', '/'))
                except ValueError:
                    pass
                except Exception:
                    debugger('[ERROR] Formatting CSS file {} failed on line "{}"'
                             .format(css_path, line))

                style_sheet += line + '\n'

        widget.setStyleSheet(style_sheet)
    css.close()


def calculate_eta(progress, total, speed):
    '''
    This function is used by the burning process to calculate when
    it is expected to finish based on current progress, the total
    needed, and the speed - e.g. 450 MB of 1000 MB at 50 MB/s.

    NOTE: Units must match.
    '''

    eta_seconds = float(total - progress) / (speed + 1)

    hours = int(eta_seconds / 3600)
    minutes = int(eta_seconds / 60 - hours * 60)
    seconds = int(eta_seconds % 60)

    if hours:
        return '{} hours, {} minutes, {} seconds'.format(hours, minutes, seconds)
    elif minutes:
        return '{} minutes, {} seconds'.format(minutes, seconds)
    else:
        return '{} seconds'.format(seconds)


def dump_pipe(filehandle):
    def dump_read(dump_file):
        for line in dump_file:
            pass

    dump_thread = threading.Thread(target=dump_read,
                                   args=(filehandle))
    dump_thread.start()


