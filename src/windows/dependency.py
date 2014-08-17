
# dependency.py
#
# Copyright (C) 2014 Kano Computing Ltd.
# License: http://www.gnu.org/licenses/gpl-2.0.txt GNU General Public License v2
#
# [File description]

import os
import sys
import win32com.shell.shell as shell

from src.common.errors import INTERNET_ERROR, ARCHIVER_ERROR, FREE_SPACE_ERROR
from src.common.utils import run_cmd_no_pipe, is_internet, debugger, \
    _7zip_path, _dd_path, _nircmd_path, BYTES_IN_MEGABYTE


# TODO: grab this value with pySmartDL
REQUIRED_MB = 600  # MB necessary free space


def request_admin_privileges():
    ASADMIN = 'asadmin'

    if sys.argv[-1] != ASADMIN:
        script = os.path.abspath(sys.argv[0])
        params = ' '.join([script] + sys.argv[1:] + [ASADMIN])
        shell.ShellExecuteEx(lpVerb='runas', lpFile=sys.executable, lpParameters=params, nShow=5)
        sys.exit(0)


def check_dependencies(tmp_dir):
    # looking for an internet connection
    if is_internet():
        debugger('Internet connection detected')
    else:
        debugger('No internet connection detected')
        return INTERNET_ERROR

    # making sure the tools folder is there
    if is_tools_preset():
        debugger('All necessary tools have been found')
    else:
        debugger('[ERROR] Not all tools are present!')
        return ARCHIVER_ERROR

    # making sure we have enough space to download OS
    if is_sufficient_space(tmp_dir, REQUIRED_MB):
        debugger('Sufficient available space')
    else:
        debugger('Insufficient available space (min {} MB)'.format(REQUIRED_MB))
        return FREE_SPACE_ERROR

    # everything is ok, return successful and no error
    debugger('All dependencies were met')
    return None


def is_tools_preset():
    # the tools necessary are included in win\ folder
    found_7zip = is_file_present(_7zip_path, "7za.exe")
    found_dd = is_file_present(_dd_path, "dd.exe")
    found_nircmd = is_file_present(_nircmd_path, "nircmd.exe")

    # return whether we have found both
    return found_7zip and found_dd and found_nircmd


def is_file_present(path, filename):
    cmd = "dir {}".format(path)
    output, error, return_code = run_cmd_no_pipe(cmd)

    found = False
    if not return_code:
        for line in output.splitlines():
            if filename in line:
                found = True
                break

    if found:
        debugger("Found {} in {}".format(filename, path))
    else:
        debugger("[ERROR] Could not find {} in {}".format(filename, path))
    return found


def is_sufficient_space(path, requred_mb):
    cmd = "dir {}".format(path)
    output, _, _ = run_cmd_no_pipe(cmd)

    # grab the last line from the output
    free_space_line = output.splitlines()[-1]

    # grab the number in bytes, remove comma delimiters, and convert to MB
    free_space_mb = float(free_space_line.split()[2].replace(',', '')) / BYTES_IN_MEGABYTE

    debugger('Free space {} MB in {}'.format(free_space_mb, path))
    return free_space_mb > requred_mb
