
# disk.py
#
# Copyright (C) 2014 Kano Computing Ltd.
# License: http://www.gnu.org/licenses/gpl-2.0.txt GNU General Public License v2
#
# [File description]


from src.common.utils import run_cmd, debugger, BYTES_IN_GIGABYTE


def get_disks_list():
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

        # make sure we do not list any potential hard drive
        if disk['size'][len(disk['size'])-2:] != 'GB' or float(disk['size'][:-2]) > 64:
            debugger('Ignoring {}'.format(disk))
        else:
            disks.append(disk)
            debugger('Listing {}'.format(disk))

    return disks


def get_disk_ids():
    #cmd = "fdisk -l | grep 'Disk /dev/.*:' | awk '{print $2}'"
    cmd = "parted --list | grep 'Disk /dev/.*:' | awk '{print $2}'"
    output, error, return_code = run_cmd(cmd)

    disk_ids = []
    for id in output.splitlines():
        disk_ids.append(id[:-1])

    if return_code:
        debugger('[ERROR] ' + error.strip('\n'))
    
    return disk_ids


def get_disk_names():
    #cmd = "lshw -short | grep {}".format(disk_id)
    cmd = "parted --list | grep 'Model:'"
    output, error, return_code = run_cmd(cmd)

    disk_names = []
    for name in output.splitlines():
        disk_names.append(' '.join(name.split()[1:-1]))

    if return_code:
        debugger('[ERROR] ' + error.strip('\n'))
    
    # grab the first line of the output and the name is from the 4th word onwards
    #return ' '.join(output.split('\n')[0].split()[4:])
    return disk_names


def get_disk_sizes():
    #cmd = "fdisk -l | grep 'Disk %s:' | awk '{print $5}'" % disk_id
    cmd = "parted --list | grep 'Disk /dev/.*:' | awk '{print $3}'"
    output, error, return_code = run_cmd(cmd)

    disk_sizes = []
    for size in output.splitlines():
        disk_sizes.append(size)

    if return_code:
        debugger('[ERROR] ' + error.strip('\n'))

    #return '{0:.2f} GB'.format(float(int(output)) / BYTES_IN_GIGABYTE)
    return disk_sizes


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


def unmount_volumes(disk_id):
    # all volumes on a disk have an index attached (e.g. /dev/sdb1, /dev/sdb2)
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
    cmd = 'eject {}'.format(disk_id)
    _, error, return_code = run_cmd(cmd)

    if not return_code:
        debugger('{} successfully ejected'.format(disk_id))
    else:
        debugger('[ERROR] ' + error.strip('\n'))
