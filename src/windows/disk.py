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


from src.common.utils import run_cmd_no_pipe, write_file_contents, debugger, BYTES_IN_GIGABYTE
from src.common.paths import _dd_path, _nircmd_path


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
            id = output_lines[index].split('=')[1][-1]
            disk_id = "\\\\?\\Device\\Harddisk{}\\Partition0".format(id)

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
            if disk['size'] < 4 or disk['size'] > 64 or disk['size'] == -1:
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

    report_ui('retrieving mount point and disk volume..')
    disk_mount = get_disk_mount(disk_id)
    # disk_volume = get_disk_volume(disk_id, disk_mount)

    report_ui('closing all Explorer windows')
    close_all_explorer_windows()

    report_ui('formatting the disk')
    format_disk(disk_id)

    # Make SURE this is needed BEFORE uncommenting! READ warning!
    # report_ui('unmounting disk')
    # unmount_disk(disk_mount)

    report_ui('testing writing to disk')
    test_write(disk_mount)

    # hopefully, the disk should be 'enabled' at this point and
    # dd should have no trouble to write the OS to Partition0


def get_disk_mount(disk_id):
    TEMP_DIR = 'C:\\temp\\kano-burner\\'
    disk_mount = ''   # mount point e.g. C:\ or D:\

    # extract the id of the physical disk, required by diskpart
    # e.g. \\?\Device\Harddisk[id]\Partition0
    id = int(disk_id.split("Harddisk")[1][0])  # access by string index alone is dangerous!

    # create a diskpart script to find the mount point for the given disk
    diskpart_detail_script = 'select disk {} \ndetail disk'.format(id)
    write_file_contents(TEMP_DIR + "detail_disk.txt", diskpart_detail_script)

    # run the created diskpart script
    cmd = 'diskpart /s {}'.format(TEMP_DIR + "detail_disk.txt")
    output, error, return_code = run_cmd_no_pipe(cmd)

    if not return_code:
        debugger('Ran diskpart detail script')
    else:
        debugger('[ERROR] ' + error.strip('\n'))
        return

    # now the mount point is the third word on the last line of the output
    disk_mount = output.splitlines()[-1].split()[2]

    return disk_mount


# This function is not currently being used
def get_disk_volume(disk_id, disk_mount):
    disk_volume = ''  # a unique ID e.g. \\?\Volume{5fd765ff-068e-11e4-bc8d-806e6f6e6963}\

    # we now need to link the mount point to the volume id that is actually used
    cmd = '{}\\dd.exe --list'.format(_dd_path)
    _, output, return_code = run_cmd_no_pipe(cmd)

    # we will process the output line by line to find the line containing the mount point
    # the line at [index - 3] from the respective one contains the volume id
    output_lines = output.splitlines()
    disk_mount_dd = '\\\\.\\{}:'.format(disk_mount.lower())

    for index in range(0, len(output_lines)):
        if disk_mount_dd in output_lines[index]:
            disk_volume = output_lines[index - 3].strip()
            break

    return disk_volume


def close_all_explorer_windows():
    cmd = '{}\\nircmd.exe win close class "CabinetWClass"'.format(_nircmd_path)
    _, error, return_code = run_cmd_no_pipe(cmd)

    if not return_code:
        debugger('Closed all Explorer windows')
    else:
        debugger('[ERROR]: ' + error.strip('\n'))


def test_write(disk_mount):
    cmd = '{}\\dd.exe if=/dev/random of=\\\\.\\{}: bs=4M count=10'.format(_dd_path, disk_mount)
    _, output, return_code = run_cmd_no_pipe(cmd)

    if not return_code:
        debugger('Written 40M random data to {}:\\'.format(disk_mount))
    else:
        debugger('[ERROR]: ' + output.strip('\n'))


# This function is not currently being used
# WARNING: If this function is called make sure mount_disk() is executed!
#          Otherwise, the mount point will remain removed from the volume directory!
#          This is a persistent change and CANNOT be fixed by a reboot!
def unmount_disk(disk_mount):
    cmd = "mountvol {}:\\ /D".format(disk_mount)
    error, _, return_code = run_cmd_no_pipe(cmd)

    if not return_code:
        debugger('{}:\\ successfully unmounted'.format(disk_mount))
    else:
        debugger('[ERROR]: ' + error.strip('\n'))


# This function is not currently being used - WORK IN PROGRESS
# WARNING: If unmount_disk() was called, make sure this function is executed!
#          Otherwise, the mount point will remain removed from the volume directory!
#          This is a persistent change and CANNOT be fixed by a reboot!
def mount_disk(disk_id):
    # the following may not work if the disk has been unmounted, consider caching
    disk_mount = get_disk_mount(disk_id)
    disk_volume = get_disk_volume(disk_id, disk_mount)

    cmd = "mountvol {}:\\ {}".format(disk_mount, disk_volume)
    _, error, return_code = run_cmd_no_pipe(cmd)

    if not return_code:
        debugger('{} successfully mounted'.format(disk_mount))
    else:
        debugger('[ERROR]: ' + error.strip('\n'))


def format_disk(disk_id):
    # TODO: look into cmd = 'format {}: /Q /X'.format(disk_mount)
    TEMP_DIR = 'C:\\temp\\kano-burner\\'

    # extract the id of the physical disk, required by diskpart
    # e.g. \\?\Device\Harddisk[id]\Partition0
    id = int(disk_id.split("Harddisk")[1][0])  # access by string index alone is dangerous!

    # create a diskpart script to format the given disk
    diskpart_format_script = 'select disk {} \nclean'.format(id)
    write_file_contents(TEMP_DIR + "format_disk.txt", diskpart_format_script)

    # run the created diskpart script
    cmd = 'diskpart /s {}'.format(TEMP_DIR + "format_disk.txt")
    _, error, return_code = run_cmd_no_pipe(cmd)

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
