#!/usr/bin/env python

# dependency.py
#
# Copyright (C) 2014 Kano Computing Ltd.
# License: http://www.gnu.org/licenses/gpl-2.0.txt GNU General Public License v2
#
#
# OSX - Dependency checking
#
# The application needs to meet a few dependencies before
# it can have the green light to start.
#
# Firstly, we check that the necessary tools are installed, e.g. dd, gzip
# Secondly, we check that there is an internet connection.
# And finally, we make sure there is enough space to download the OS.


import os
import sys

from src.common.utils import run_cmd, is_internet, debugger, BYTES_IN_MEGABYTE
from src.common.errors import INTERNET_ERROR, TOOLS_ERROR, FREE_SPACE_ERROR
from src.common.paths import temp_path


# TODO: grab this value with pySmartDL
REQUIRED_MB = 700  # MB necessary free space


def request_admin_privileges():
    ask_sudo_osascript = """' \
        do shell script "{}" \
            with administrator privileges \
    '""".format(os.path.abspath(sys.argv[0]).replace(' ', '\\\\ '))

    if os.getuid() != 0:
        os.system("""osascript -e {}""".format(ask_sudo_osascript))
        sys.exit(0)


def check_dependencies():
    '''
    This method is used by the BurnerGUI at the start
    of the application and on a retry.
    '''

    # looking for an internet connection
    if is_internet():
        debugger('Internet connection detected')
    else:
        debugger('No internet connection found')
        return INTERNET_ERROR

    # checking all necessary tools are installed
    if verify_tools():
        debugger('All necessary tools have been found')
    else:
        debugger('[ERROR] Not all tools are present')
        return TOOLS_ERROR

    # making sure we have enough space to download OS
    if is_sufficient_space():
        debugger('Sufficient available space')
    else:
        debugger('Insufficient available space (min {} MB)'.format(REQUIRED_MB))
        return FREE_SPACE_ERROR

    # everything is ok, return successful and no error
    debugger('All dependencies were met')
    return None


def verify_tools():
    tools = """
        awk
        dd
        df
        diskutil
        grep
        gzip
        kill
        osascript
        pgrep
    """

    # return whether we have found all tools
    return is_installed(tools.split())


def is_installed(programs_list):
    cmd = 'which {}'.format(' '.join(programs_list))
    output, error, return_code = run_cmd(cmd)

    if return_code:
        debugger('[ERROR] ' + error.strip('\n'))
        return True  # if something goes wrong here, it shouldn't be catastrophic

    return len(output.split()) == len(programs_list)


def is_sufficient_space():
    cmd = "df %s | grep -v 'Available' | awk '{print $4}'" % temp_path
    output, _, _ = run_cmd(cmd)

    try:
        free_space_mb = float(output.strip()) * 512 / BYTES_IN_MEGABYTE
    except:
        debugger('[ERROR] Failed parsing the line ' + output)
        return True

    debugger('Free space {0:.2f} MB in {1}'.format(free_space_mb, temp_path))
    return free_space_mb > REQUIRED_MB
