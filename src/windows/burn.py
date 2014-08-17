
# burn.py
#
# Copyright (C) 2014 Kano Computing Ltd.
# License: http://www.gnu.org/licenses/gpl-2.0.txt GNU General Public License v2
#
# [File description]


import time
import subprocess
from src.common.errors import BURN_ERROR
from src.common.utils import debugger, _7zip_path, _dd_path, BYTES_IN_MEGABYTE


# used to calculate burning speed
last_written_mb = 0


def start_burn_process(path, os_info, disk, report_progress_ui):
    # the Windows version of dd can easily output writing progress, unlike OSX and Linux
    # so we do not need multithreading and progress polling
    successful = burn_kano_os(path + os_info['filename'], disk,
                              os_info['uncompressed_size'], report_progress_ui)

    if not successful:
        return BURN_ERROR
    else:
        return None


def burn_kano_os(os_path, disk, size, report_progress_ui):
    cmd = '"{}7za.exe" e -so "{}" | "{}dd.exe" of="{}" bs=4M --progress'.format(_7zip_path, os_path, _dd_path, disk)
    process = subprocess.Popen(cmd, shell=True, stderr=subprocess.PIPE, universal_newlines=True)
    failed = False

    # initialise UI timed reporting
    previous_timestamp = time.time()

    # as long as Popen is running, read it's stderr line by line
    # dd uses a carriage return when printing it's progress, but using
    # universal_newlines converts all line endings into \n
    for line in iter(process.stderr.readline, ''):
        line = line.strip()

        # looking for dd's progress in the output e.g. '1,234M   \n'
        # and making sure we report to UI at fixed time intervals, not like dd
        elapsed_seconds = time.time() - previous_timestamp

        if line and line[-1] == 'M' and elapsed_seconds > 0.3:
            total_written_mb = float(line.strip('M').replace(',', ''))

            # calculate stats to be reported to UI
            progress = int(total_written_mb / (size / BYTES_IN_MEGABYTE) * 100)
            speed = calculate_speed(total_written_mb, elapsed_seconds)
            eta = calculate_eta(total_written_mb, size / BYTES_IN_MEGABYTE, speed)

            report_progress_ui(progress, 'speed {0:.2f} MB/s  eta {1:s}  completed {2:d}%'
                               .format(speed, eta, progress))

            # update the time at which we last reported with the current time
            previous_timestamp = time.time()

        # watch out for an error output from dd
        if 'error' in line.lower() or 'invalid' in line.lower():
            debugger('[ERROR] ' + line)
            failed = True

    # make sure the progress bar is filled and show an appropriate message
    report_progress_ui(100, 'burning finished successfully')

    if failed:
        debugger('[ERROR] burning Kano image failed')
        return False
    else:
        debugger('Burning successfully finished')
        return True


def calculate_speed(total_written_mb, elapsed_seconds):
    global last_written_mb

    # calculate how much we've written since previous_timestep
    newly_written_mb = total_written_mb - last_written_mb
    last_written_mb = total_written_mb

    # return the speed as MB/s
    return float(newly_written_mb) / elapsed_seconds


def calculate_eta(progress, total, speed):
    eta_seconds = float(total - progress) / (speed + 1)

    hours = int(eta_seconds / 3600)
    minutes = int(eta_seconds / 60 - hours * 60)
    seconds = int(eta_seconds % 60)

    if hours:
        return '{} hours, {} minutes, {} seconds'.format(hours, minutes, seconds)
    elif minutes:
        return '{} minutes, {} seconds'.format(minutes, seconds)
    else:
        return '{} seconds'.format(seconds)
