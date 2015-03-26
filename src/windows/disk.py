#!/usr/bin/env python

# disk.py
#
# Copyright (C) 2014 Kano Computing Ltd.
# License: http://www.gnu.org/licenses/gpl-2.0.txt GNU General Public License v2
#
#
# Windows - Disk related operations
#
# There are two main operations here.
#
# 1. Providing a list of disks Kano OS can be burned to. We will exclude
#    any potential hard drives from this list or disks which are too small.
#
# 2. Preparing the given disk for the burning process (unmounting, formatting, etc).
#    On Windows this is particularly tricky, as the disk may deny access quite often.
#
# Tools used: wmic, diskpart, mountvol, dd.exe, nircmd.exe


import os
import time

from src.common.utils import run_cmd_no_pipe, write_file_contents, debugger, BYTES_IN_GIGABYTE
from src.common.paths import _nircmd_path, temp_path


def get_disks_list():
    '''
    This method is used by the BurnerGUI when the user clicks the ComboBox.

    It grabs all disk physical ids, names, and sizes with one command and
    then parses the output. Sizes will be converted to GB (not GiB).

    NOTE: We do no return all disks that are found!

    Example:
        disk id: \\?\Device\Harddisk2\Partition0
        disk name: Sandisk Media USB
        disk size: 16.03

        disk volume: \\?\Volume{5fd765ff-068e-11e4-bc8d-806e6f6e6963}\
        physical disk: \\.\PHYSICALDRIVE2

        NOTE: physical drive id and device id match!
    '''

    disks = list()

    cmd = "wmic diskdrive get deviceid, model, size /format:list"
    output, error, return_code = run_cmd_no_pipe(cmd)

    if return_code:
        debugger('[ERROR] ' + error.strip('\n'))

    # remove random empty lines in the output
    output_lines = [line for line in output.splitlines() if line]

    for index in range(0, len(output_lines)):
        if output_lines[index].startswith("DeviceID="):

            # grab the disk id from e.g. \\.\PHYSICALDRIVE[0] and use Partition0
            # which for dd is the entire disk, not some partition on the disk
            drive_loc = output_lines[index].lower().find('physicaldrive') + len('physicaldrive')
            id_num = output_lines[index][drive_loc:]
            disk_id = "\\\\?\\Device\\Harddisk{}\\Partition0".format(id_num)

            # for the disk model, remove the last word which is always 'device'
            model = output_lines[index + 1].split('=')[1]
            disk_name = ' '.join(model.split()[:-1])

            # the size may not be listed (i.e. ''), in which case we assume
            # the device is not plugged in e.g. an empty USB SD card reader
            disk_size = -1
            try:
                size_bytes = float(output_lines[index + 2].split('=')[1])
                disk_size = size_bytes / BYTES_IN_GIGABYTE
            except:
                pass

            # append all data here, this would need changing if logic changes
            disk = {
                'id': disk_id,
                'name': disk_name,
                'size': disk_size
            }

            # make sure we do not list any potential hard drive or too small SD card
            if disk['size'] < 3.5 or disk['size'] > 64.5 or disk['size'] == -1:
                debugger('Ignoring {}'.format(disk))
            else:
                debugger('Listing {}'.format(disk))
                disks.append(disk)

    return disks


def prepare_disk(disk_id, report_ui):
    '''
    Windows magic

    This method is used by the backendThread to enable the disk
    for writing with dd and getting passed denial of access.
    '''

    report_ui('closing all Explorer windows')
    close_all_explorer_windows()

    report_ui('formatting the disk')
    format_disk(disk_id)

    # hopefully, the disk should be 'enabled' at this point and
    # dd should have no trouble to write the OS to Partition0


def close_all_explorer_windows():
    cmd = '{}\\nircmd.exe win close class "CabinetWClass"'.format(_nircmd_path)
    _, error, return_code = run_cmd_no_pipe(cmd)

    if not return_code:
        debugger('Closed all Explorer windows')
    else:
        debugger('[ERROR]: ' + error.strip('\n'))


def format_disk(disk_id):
    # TODO: look into cmd = 'format {}: /Q /X'.format(disk_mount)

    # extract the id of the physical disk, required by diskpart
    # e.g. \\?\Device\Harddisk[id]\Partition0
    id = int(disk_id.split("Harddisk")[1][0])  # access by string index alone is dangerous!

    # create a diskpart script to format the given disk
    diskpart_format_script = 'select disk {} \nclean'.format(id)
    diskpart_script_path = os.path.join(temp_path, "format_disk.txt")
    write_file_contents(diskpart_format_script, diskpart_script_path)

    # run the created diskpart script
    cmd = 'diskpart /s {}'.format(diskpart_script_path)
    _, error, return_code = run_cmd_no_pipe(cmd)
    time.sleep(15)  # diskpart requires a timeout between calls

    if not return_code:
        debugger('Formatted disk {} with diskpart'.format(id))
    else:
        debugger('[ERROR] ' + error.strip('\n'))


def eject_disk(disk_id):
    '''
    This method is used by the backendThread to ensure safe removal
    after burning finished successfully.
    '''

    # TODO? Windows does not really require this
    pass
