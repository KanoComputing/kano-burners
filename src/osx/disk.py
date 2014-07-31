
# disk.py
#
# Copyright (C) 2014 Kano Computing Ltd.
# License: http://www.gnu.org/licenses/gpl-2.0.txt GNU General Public License v2
#
# [File description]


from src.common.utils import run_cmd, debugger


def get_disks_list():
    disks = list()

    for disk_id in get_disk_ids():

        # change disk to raw to increase performance
        disk_id = disk_id[:5] + 'r' + disk_id[5:]

        disk = {
            'id': disk_id,
            'name': get_disk_name(disk_id),
            'size': get_disk_size(disk_id)
        }

        # make sure we do not list the primary HDD
        if 'disk0' in disk['id']:
            debugger('Considering {} as primary HDD'.format(disk))
        else:
            disks.append(disk)
            debugger('Detected disk {}'.format(disk))

    return disks


def get_disk_ids():
    cmd = "diskutil list | grep '/dev/'"
    output, error, return_code = run_cmd(cmd)

    if not return_code:
        return output.split()
    else:
        debugger('[ERROR] ' + error.strip('\n'))
        return list()


def get_disk_name(disk_id):
    cmd = "diskutil info {} | grep 'Device / Media Name'".format(disk_id)
    output, error, return_code = run_cmd(cmd)

    if not return_code:
        return ' '.join(output.split()[4:])
    else:
        debugger('[ERROR] ' + error.strip('\n'))
        return ''


def get_disk_size(disk_id):
    cmd = "diskutil info {} | grep 'Total Size'".format(disk_id)
    _, error, return_code = run_cmd(cmd)
    output, error, return_code = run_cmd(cmd)

    if not return_code:
        return ' '.join(output.split()[2:4])
    else:
        debugger('[ERROR] ' + error.strip('\n'))
        return ''


def unmount_disk(disk_id):
    cmd = 'diskutil unmountDisk {}'.format(disk_id)
    _, error, return_code = run_cmd(cmd)

    if not return_code:
        debugger('{} successfully unmounted'.format(disk_id))
    else:
        debugger('[ERROR] ' + error.strip('\n'))


# Not used - can be included in kano-burner > BurnerBackendThread > run
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
