#!/usr/bin/env python

# dependency.py
#
# Copyright (C) 2014 Kano Computing Ltd.
# License: http://www.gnu.org/licenses/gpl-2.0.txt GNU General Public License v2
#
#
# Windows - Dependency checking
#
# The application needs to meet a few dependencies before
# it can have the green light to start.
#
# Firstly, we check that the necessary tools are installed, e.g. dd, gzip
# Secondly, we check that there is an internet connection.
# And finally, we make sure there is enough space to download the OS.


import os
import sys
import win32con
import win32com.shell.shell as shell

from src.common.utils import run_cmd_no_pipe, is_internet, debugger, BYTES_IN_MEGABYTE
from src.common.errors import INTERNET_ERROR, TOOLS_ERROR, FREE_SPACE_ERROR
from src.common.paths import _7zip_path, _dd_path, _nircmd_path, temp_path


# TODO: grab this value with pySmartDL
REQUIRED_MB = 3100  # MB necessary free space


def request_admin_privileges():
    ASADMIN = 'asadmin'

    if sys.argv[-1] != ASADMIN:
        script = os.path.abspath(sys.argv[0])
        params = ' '.join([script] + sys.argv[1:] + [ASADMIN])
        shell.ShellExecuteEx(lpVerb='runas', lpFile=sys.executable,
                             lpParameters=params, nShow=win32con.SW_SHOW)
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
        debugger('No internet connection detected')
        return INTERNET_ERROR

    # making sure the tools folder is there
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
    # the tools necessary are included in win\ folder
    found_7zip = os.path.exists(os.path.join(_7zip_path, "7za.exe"))
    found_dd = os.path.exists(os.path.join(_dd_path, "dd.exe"))
    found_nircmd = os.path.exists(os.path.join(_nircmd_path, "nircmd.exe"))

    tools = """
        diskpart
        wmic
    """

    # return whether we have found all tools
    return found_7zip and found_dd and found_nircmd and is_installed(tools.split())


def is_installed(programs_list):
    cmd = 'where.exe {}'.format(' '.join(programs_list))
    output, error, return_code = run_cmd_no_pipe(cmd)

    if return_code:
        debugger('[ERROR] ' + error.strip('\n'))
        return True  # if something goes wrong here, it shouldn't be catastrophic

    programs_found = 0
    for line in output.splitlines():
        if line and 'not find' not in line:
            programs_found += 1

    return programs_found == len(programs_list)


def is_sufficient_space():
    cmd = "dir {}".format(temp_path)
    output, _, _ = run_cmd_no_pipe(cmd)

    try:
        # grab the last line from the output
        free_space_line = output.splitlines()[-1]

        # grab the number in bytes, remove comma delimiters, and convert to MB
        free_space_mb = float(free_space_line.split()[2].replace(',', '')) / BYTES_IN_MEGABYTE
    except:
        debugger('[ERROR] Failed parsing the line ' + output)
        return True

    debugger('Free space {0:.2f} MB in {1}'.format(free_space_mb, temp_path))
    return free_space_mb > REQUIRED_MB
