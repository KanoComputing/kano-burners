#!/usr/bin/env python

# disk.py
#
# Copyright (C) 2014 Kano Computing Ltd.
# License: http://www.gnu.org/licenses/gpl-2.0.txt GNU General Public License v2
#
#
# Linux - Disk related operations
#
# There are two main operations here.
#
# 1. Providing a list of disks Kano OS can be burned to. We will exclude
#    any potential hard drives from this list or disks which are too small.
#
# 2. Preparing the given disk for the burning process (unmounting, formatting).
#
# Tools used: parted, fdisk, mkdosfs, umount, eject


from src.common.utils import run_cmd, debugger, BYTES_IN_GIGABYTE
from src.common.errors import UNMOUNT_ERROR


class unmount_error(Exception):
    pass


def get_disks_list():
    '''
    This method is used by the BurnerGUI when the user clicks the ComboBox.

    It grabs all disk ids, disk names, and disk sizes separately and then
    matches them by index. Sizes will be converted to GB (not GiB).

    NOTE: We do no return all disks that are found!

    Example:
        disk id: /dev/sda
        disk name: Sandisk Ultra USB
        disk size: 16.03
    '''

    disks = list()

    for disk_id in get_disk_ids():

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
    cmd = "parted --list | grep 'Disk /dev/.*:' | awk '{print $2}'"
    output, error, return_code = run_cmd(cmd)

    disk_ids = []
    for id in output.splitlines():
        disk_ids.append(id[:-1])

    if return_code:
        debugger('[ERROR] ' + error.strip('\n'))

    return disk_ids


def get_disk_name_size(disk_id):
    cmd = "parted {} unit B print".format(disk_id)
    output, error, return_code = run_cmd(cmd)

    disk_name = ''
    disk_size = 0

    if return_code:
        debugger('[ERROR] ' + error.strip('\n'))

    for line in output.splitlines():
        if 'Model:' in line:
            disk_name = ' '.join(line.split()[1:])
        if 'Disk {}:'.format(disk_id) in line:
            disk_size = float(line[:-1].split()[2]) / BYTES_IN_GIGABYTE

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
    except unmount_error:
        return UNMOUNT_ERROR


def unmount_disk(disk_id):
    # to unmount an entire disk, we first need to unmount all it's volumes
    unmount_volumes(disk_id)

    # now we can safely unmount the disk
    cmd = 'umount {}'.format(disk_id)
    _, error, return_code = run_cmd(cmd)
    if not return_code:
        debugger('disk {} successfully unmounted'.format(disk_id))
    else:
        debugger('[ERROR] ' + error.strip('\n'))
        raise unmount_error


def unmount_volumes(disk_id):
    # all volumes on a disk have an index attached e.g. /dev/sdb1, /dev/sdb2
    cmd = "fdisk -l | grep '%s[0-9][0-9]*' | awk '{print $1}'" % disk_id
    output, _, _ = run_cmd(cmd)

    # it may also happen that the disk does not have volumes
    # in which case the loop below won't do anything
    for volume in output.splitlines():
        cmd = 'umount {}'.format(volume)
        _, error, return_code = run_cmd(cmd)
        if not return_code:
            debugger('volume {} successfully unmounted'.format(volume))
        else:
            debugger('[ERROR] ' + error.strip('\n'))


def format_disk(disk_id):
    cmd = 'mkdosfs -I -F 32 -v {}'.format(disk_id)
    _, error, return_code = run_cmd(cmd)

    if not return_code:
        debugger('{} successfully erased and formatted'.format(disk_id))
    else:
        debugger('[ERROR] ' + error.strip('\n'))


def eject_disk(disk_id):
    '''
    This method is used by the backendThread to ensure safe removal
    after burning finished successfully.
    '''

    cmd = 'eject {}'.format(disk_id)
    _, error, return_code = run_cmd(cmd)

    if not return_code:
        debugger('{} successfully ejected'.format(disk_id))
    else:
        debugger('[ERROR] ' + error.strip('\n'))
