
# disk.py
#
# Copyright (C) 2014 Kano Computing Ltd.
# License: http://www.gnu.org/licenses/gpl-2.0.txt GNU General Public License v2
#
# [File description]


from src.common.utils import run_cmd_no_pipe, write_file_contents, debugger, \
    _dd_path, _nircmd_path, BYTES_IN_GIBIBYTE


def get_disks_list():
    disks = list()

    cmd = "wmic diskdrive get deviceid, model, size /format:list"
    output, error, return_code = run_cmd_no_pipe(cmd)

    if return_code:
        debugger('[ERROR] ' + error.strip('\n'))

    # remove random empty lines in the output
    output_lines = [line for line in output.splitlines() if line]

    for index in range(0, len(output_lines)):
        if output_lines[index].startswith("DeviceID="):

            # grab the disk id from e.g. \\.\PHYSICALDRIVE0 and use Partition0
            # which for dd is the entire disk
            id = output_lines[index].split('=')[1][-1]
            disk_id = "\\\\?\\Device\\Harddisk{}\\Partition0".format(id)

            # for the disk model, remove the last word which is always 'device'
            model = output_lines[index + 1].split('=')[1]
            disk_name = ' '.join(model.split()[1:-1])

            # the size may not be listed (i.e. ''), in which case we assume
            # the device is not plugged in e.g. an empty USB SD card reader
            disk_size = -1
            try:
                size_bytes = float(output_lines[index + 2].split('=')[1])
                disk_size = int(size_bytes / BYTES_IN_GIBIBYTE)
            except:
                pass

            # append all data here, this would need changing if logic changes
            disk = {
                'id': disk_id,
                'name': disk_name,
                'size': disk_size
            }

            # make sure we do not list any potential hard drive
            if disk['size'] > 64 or disk['size'] == -1:
                debugger('Ignoring {}'.format(disk))
            else:
                disk['size'] = str(disk['size']) + " GB"
                disks.append(disk)
                debugger('Listing {}'.format(disk))

    return disks


def prepare_disk(disk_id, report_ui):
    # Windows magic

    report_ui('retrieving mount point and disk volume..')
    disk_mount, disk_volume = get_disk_volume_and_mount(disk_id)

    report_ui('closing all Explorer windows')
    close_all_explorer_windows()

    report_ui('formatting the disk')
    format_disk(disk_id)

    # report_ui('unmounting disk')
    # unmount_disk(disk_mount)

    report_ui('testing writing to disk')
    test_write(disk_mount)

    # hopefully, the disk should be 'enabled' at this point and
    # dd should have no trouble to write the OS to Partition0


def get_disk_volume_and_mount(disk_id):
    TEMP_DIR = 'C:\\temp\\kano-burner\\'
    disk_mount = ''   # mount point e.g. C:\ or D:\
    disk_volume = ''  # a unique ID e.g. \\?\Volume{5fd765ff-068e-11e4-bc8d-806e6f6e6963}\

    # create a diskpart script to find the mount point for the given disk
    # below we also extract the id of the physical disk, required by diskpart
    # e.g. \\?\Device\Harddisk[id]\Partition0
    id = int(disk_id.split("Harddisk")[1][0])  # access by string index alone is dangerous!
    diskpart_detail_script = 'select disk {}\n'.format(id) + 'detail disk'
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

    # we now need to link the mount point to the volume id that is actually used
    cmd = '{}dd.exe --list'.format(_dd_path)
    _, output, return_code = run_cmd_no_pipe(cmd)

    if not return_code:
        debugger('Retrieved dd --list output')
    else:
        debugger('[ERROR] ' + error.strip('\n'))
        return

    # we will process the output line by line to find the line containing the mount point
    # the line at [index - 3] from the respective one contains the volume id
    output_lines = output.splitlines()
    disk_mount_dd = '\\\\.\\{}:'.format(disk_mount.lower())

    for index in range(0, len(output_lines)):
        if disk_mount_dd in output_lines[index]:
            disk_volume = output_lines[index - 3].strip()
            break

    return disk_mount, disk_volume


def close_all_explorer_windows():
    cmd = '{}nircmd.exe win close class "CabinetWClass"'.format(_nircmd_path)
    _, error, return_code = run_cmd_no_pipe(cmd)

    if not return_code:
        debugger('Closed all Explorer windows')
    else:
        debugger('[ERROR] close_all_explorer_windows(): ' + error.strip('\n'))


def test_write(disk_mount):
    cmd = '{}dd.exe if=/dev/random of=\\\\.\\{}: bs=4M count=10'.format(_dd_path, disk_mount)
    _, output, return_code = run_cmd_no_pipe(cmd)

    if not return_code:
        debugger('Written 40M random data to {}:\\'.format(disk_mount))
    else:
        debugger('[ERROR] test_write(): ' + output.strip('\n'))


# WARNING: If this function is called make sure mount_disk() is executed!
#          Otherwise, the mount point will remain removed from the volume directory!
#          This is a persistent change and CANNOT be fixed by a reboot!
def unmount_disk(disk_mount):
    cmd = "mountvol {}:\\ /D".format(disk_mount)
    error, _, return_code = run_cmd_no_pipe(cmd)

    if not return_code:
        debugger('{}:\\ successfully unmounted'.format(disk_mount))
    else:
        debugger('[ERROR] unmount_disk(): ' + error.strip('\n'))


# WARNING: If unmount_disk() was called, make sure this function is executed!
#          Otherwise, the mount point will remain removed from the volume directory!
#          This is a persistent change and CANNOT be fixed by a reboot!
def mount_disk(disk_id):
    disk_mount, disk_volume = get_disk_volume_and_mount(disk_id)

    cmd = "mountvol {}:\\ {}".format(disk_mount, disk_volume)
    _, error, return_code = run_cmd_no_pipe(cmd)

    if not return_code:
        debugger('{} successfully mounted'.format(disk_mount))
    else:
        debugger('[ERROR] mount_disk(): ' + error.strip('\n'))


def format_disk(disk_id):
    TEMP_DIR = 'C:\\temp\\kano-burner\\'

    id = int(disk_id.split("Harddisk")[1][0])  # access by string index alone is dangerous!
    diskpart_format_script = 'select disk {}\n'.format(id) + 'clean'
    write_file_contents(TEMP_DIR + "format_disk.txt", diskpart_format_script)

    # run the created diskpart script
    cmd = 'diskpart /s {}'.format(TEMP_DIR + "format_disk.txt")
    _, error, return_code = run_cmd_no_pipe(cmd)

    if not return_code:
        debugger('Formatted disk {} with diskpart'.format(id))
    else:
        debugger('[ERROR] ' + error.strip('\n'))


def eject_disk(disk_id):
    # TODO?
    pass
