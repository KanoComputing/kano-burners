#!/usr/bin/env python

# disk.py
#
# Copyright (C) 2014,2015 Kano Computing Ltd.
# License: http://www.gnu.org/licenses/gpl-2.0.txt GNU General Public License v2
#
#
# OSX - Disk related operations
#
# There are two main operations here.
#
# 1. Providing a list of disks Kano OS can be burned to. We will exclude
#    any potential hard drives from this list or disks which are too small.
#
# 2. Preparing the given disk for the burning process (unmounting, formatting).
#
# Tools used: diskutil


from src.common.utils import run_cmd, debugger, BYTES_IN_GIGABYTE
from src.common.errors import UNMOUNT_ERROR, FORMAT_ERROR, EJECT_ERROR


class disk_error(Exception):
    pass


def get_disks_list():
    '''
    This method is used by the BurnerGUI when the user clicks the ComboBox.

    It grabs all disk ids and then for every disk we get the name and size.
    Sizes will be converted to GB (not GiB).

    NOTE: We do no return all disks that are found!

    Example:
        disk id: /dev/rdisk2
        disk name: APPLE SD Card Reader USB
        disk size: 16.03
    '''

    disks = list()

    for disk_id in get_disk_ids():

        # change disk to raw to increase performance
        disk_id = disk_id[:5] + 'r' + disk_id[5:]

        # get the disk manufacturer and size in GB
        disk_name, disk_size = get_disk_name_size(disk_id)

        disk = {
            'id': disk_id,
            'name': disk_name,
            'size': disk_size
        }

        # make sure we do not list any potential hard drive or too small SD card
        if disk['size'] < 3.5 or disk['size'] > 16.5:  # GB
            debugger('Ignoring {}'.format(disk))
        else:
            debugger('Listing {}'.format(disk))
            disks.append(disk)

    return disks


def get_disk_ids():
    cmd = "diskutil list | grep '/dev/'"
    output, error, return_code = run_cmd(cmd)

    if not return_code:
        return output.split()
    else:
        debugger('[ERROR] ' + error.strip('\n'))


def get_disk_name_size(disk_id):
    cmd = "diskutil info {}".format(disk_id)
    output, error, return_code = run_cmd(cmd)

    disk_name = ''
    disk_size = 0

    if return_code:
        debugger('[ERROR] ' + error.strip('\n'))

    for line in output.splitlines():
        if 'Device / Media Name:' in line:
            disk_name = ' '.join(line.split()[4:])
        if 'Total Size:' in line:
            disk_size = float(line.split()[4][1:]) / BYTES_IN_GIGABYTE

    if not disk_name or not disk_size:
        debugger('[ERROR] Parsing disk name and size failed')

    return disk_name, disk_size


def prepare_disk(disk_id, report_ui):
    '''
    This method is used by the backendThread to unmount
    and format the disk before the burning process starts.
    '''

    try:
        report_ui('unmounting disk')
        unmount_disk(disk_id)

        report_ui('formating disk')
        format_disk(disk_id)

        # OSX mounts the disk back after formatting
        report_ui('unmounting disk')
        unmount_disk(disk_id)
    except disk_error as e:
        return e.args[0]


def unmount_disk(disk_id):
    cmd = 'diskutil unmountDisk {}'.format(disk_id)
    _, error, return_code = run_cmd(cmd)

    if not return_code:
        debugger('{} successfully unmounted'.format(disk_id))
    else:
        debugger('[ERROR: {}] {}'.format(cmd,  error.strip('\n')))
        raise disk_error(UNMOUNT_ERROR)


def format_disk(disk_id):
    cmd = 'diskutil eraseDisk fat32 UNTITLED {}'.format(disk_id)
    _, error, return_code = run_cmd(cmd)

    if not return_code:
        debugger('{} successfully erased and formatted'.format(disk_id))
    else:
        debugger('[ERROR: {}] {}'.format(cmd, error.strip('\n')))
        raise disk_error(FORMAT_ERROR)


def eject_disk(disk_id):
    '''
    This method is used by the backendThread to ensure safe removal
    after burning finished successfully.
    '''

    cmd = 'diskutil eject {}'.format(disk_id)
    _, error, return_code = run_cmd(cmd)

    if not return_code:
        debugger('{} successfully ejected'.format(disk_id))
        return None
    else:
        debugger('[ERROR: {}] {}'.format(cmd, error.strip('\n')))
        return EJECT_ERROR
