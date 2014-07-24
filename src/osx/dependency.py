
# dependency.py
#
# Copyright (C) 2014 Kano Computing Ltd.
# License: http://www.gnu.org/licenses/gpl-2.0.txt GNU General Public License v2
#
# [File description]


from src.common.utils import run_cmd, debugger


def is_gzip_installed():
    _, _, return_code = run_cmd('which gzip')
    return return_code == 0


def is_sufficient_space(path, requred_mb):
    cmd = "df -m %s | grep -v 'Available' | awk '{print $4}'" % path
    free_space, _, _ = run_cmd(cmd)

    debugger('Free space {} MB in {}'.format(free_space.strip(), path))
    return int(free_space.strip()) > requred_mb
