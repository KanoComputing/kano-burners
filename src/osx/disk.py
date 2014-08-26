
# disk.py
#
# Copyright (C) 2014 Kano Computing Ltd.
# License: http://www.gnu.org/licenses/gpl-2.0.txt GNU General Public License v2
#
# [File description]


from src.common.utils import run_cmd, debugger, BYTES_IN_GIGABYTE


def get_disks_list():
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
        if disk['size'] < 4 or disk['size'] > 64:  # GB
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
    report_ui('unmounting disk')
    unmount_disk(disk_id)

    report_ui('formating disk')
    format_disk(disk_id)

    report_ui('unmounting disk')
    unmount_disk(disk_id)


def unmount_disk(disk_id):
    cmd = 'diskutil unmountDisk {}'.format(disk_id)
    _, error, return_code = run_cmd(cmd)

    if not return_code:
        debugger('{} successfully unmounted'.format(disk_id))
    else:
        debugger('[ERROR] ' + error.strip('\n'))


def format_disk(disk_id):
    cmd = 'diskutil eraseDisk fat32 UNTITLED {}'.format(disk_id)
    _, error, return_code = run_cmd(cmd)

    if not return_code:
        debugger('{} successfully erased and formatted'.format(disk_id))
    else:
        debugger('[ERROR] ' + error.strip('\n'))


def eject_disk(disk_id):
    cmd = 'diskutil eject {}'.format(disk_id)
    _, error, return_code = run_cmd(cmd)

    if not return_code:
        debugger('{} successfully ejected'.format(disk_id))
    else:
        debugger('[ERROR] ' + error.strip('\n'))
