
# dependency.py
#
# Copyright (C) 2014 Kano Computing Ltd.
# License: http://www.gnu.org/licenses/gpl-2.0.txt GNU General Public License v2
#
# [File description]


from src.common.utils import run_cmd, is_internet, debugger
from src.common.errors import INTERNET_ERROR, ARCHIVER_ERROR, FREE_SPACE_ERROR


# TODO: grab this value with pySmartDL
REQUIRED_MB = 600  # MB necessary free space


def request_admin_privileges():
    # TODO
    pass


def check_dependencies(tmp_dir):
    # looking for an internet connection
    if is_internet():
        debugger('Internet connection detected')
    else:
        debugger('No internet connection found')
        return INTERNET_ERROR

    # looking for a suitable archiver tool
    if is_gzip_installed():
        debugger('Gzip is installed')
    else:
        debugger('Gzip is not installed')
        return ARCHIVER_ERROR

    # making sure we have enough space to download OS
    if is_sufficient_space(tmp_dir, REQUIRED_MB):
        debugger('Sufficient available space')
    else:
        debugger('Insufficient available space (min {} MB)'.format(REQUIRED_MB))
        return FREE_SPACE_ERROR

    # everything is ok, return successful and no error
    return None


def is_gzip_installed():
    _, _, return_code = run_cmd('which gzip')
    return return_code == 0


def is_sufficient_space(path, requred_mb):
    cmd = "df -m %s | grep -v 'Available' | awk '{print $4}'" % path
    free_space, _, _ = run_cmd(cmd)

    debugger('Free space {} MB in {}'.format(free_space.strip(), path))
    return int(free_space.strip()) > requred_mb
