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

    disk_ids = get_disk_ids()
    disk_names = get_disk_names()
    disk_sizes = get_disk_sizes()

    # check for parsing errors
    if len(disk_ids) != len(disk_names) or len(disk_names) != len(disk_sizes):
        return disks

    for index in range(0, len(disk_ids)):

        # append all data here, this would need changing if logic changes
        disk = {
            'id': disk_ids[index],
            'name': disk_names[index],
            'size': disk_sizes[index]
        }

        # make sure we do not list any potential hard drive or too small SD card
        if disk['size'] < 3.5 or disk['size'] > 64:  # GB
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


def get_disk_names():
    cmd = "parted --list | grep 'Model:'"
    output, error, return_code = run_cmd(cmd)

    disk_names = []
    for name in output.splitlines():
        disk_names.append(' '.join(name.split()[1:-1]))

    if return_code:
        debugger('[ERROR] ' + error.strip('\n'))

    # grab the first line of the output and the name is from the 4th word onwards
    return disk_names


def get_disk_sizes():
    cmd = "fdisk -l | grep 'Disk /dev/'"
    output, error, return_code = run_cmd(cmd)

    disk_sizes = []
    for line in sorted(output.splitlines()):
        size = line.split()[4]
        disk_sizes.append(float(size) / BYTES_IN_GIGABYTE)

    if return_code:
        debugger('[ERROR] ' + error.strip('\n'))

    return disk_sizes


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
