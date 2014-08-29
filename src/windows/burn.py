#!/usr/bin/env python

# burn.py
#
# Copyright (C) 2014 Kano Computing Ltd.
# License: http://www.gnu.org/licenses/gpl-2.0.txt GNU General Public License v2
#
#
# Windows - Burning Kano OS module
#
# The writing (burning) process uses a 7zip to dd pipe to eliminate the
# need for uncompressing the image and extra space needed.
#
# As opposed to OSX and Linux versions of dd, here do not need a polling loop.
# However, dd does not report its writing speed, so we time it ourselves.
#
# We will also notify the UI of any errors that might have occured.


import time
import subprocess

from src.common.errors import BURN_ERROR
from src.common.utils import calculate_eta, debugger, BYTES_IN_MEGABYTE
from src.common.paths import _7zip_path, _dd_path


# used to calculate burning speed
last_written_mb = 0


def start_burn_process(path, os_info, disk, report_progress_ui):
    '''
    This method is used by the backendThread to burn Kano OS.

    It starts the burning process and returns any errors if necessary.
    '''

    # Set the progress to 0% on the UI progressbar, and write what we're up to
    report_progress_ui(0, 'preparing to burn OS image..')

    # the Windows version of dd can easily output writing progress, unlike OSX and Linux
    # so we do not need multithreading and progress polling
    successful = burn_kano_os(path + os_info['filename'], disk,
                              os_info['uncompressed_size'], report_progress_ui)

    if not successful:
        return BURN_ERROR
    else:
        return None


def burn_kano_os(os_path, disk, size, report_progress_ui):
    cmd = '"{}\\7za.exe" e -so "{}" | "{}\\dd.exe" of="{}" bs=4M --progress'.format(_7zip_path, os_path, _dd_path, disk)
    # all handles (in, out, err) need to be set due to PyInstaller bundling
    process = subprocess.Popen(cmd, shell=True, universal_newlines=True,
                               stdin=subprocess.PIPE, stdout=subprocess.PIPE,
                               stderr=subprocess.PIPE)
    failed = False
    unparsed_line = ''

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

        try:
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

        except:
            unparsed_line = line

        # watch out for an error output from dd
        if 'error' in line.lower() or 'invalid' in line.lower():
            debugger('[ERROR] ' + line)
            failed = True

    # make sure the progress bar is filled and show an appropriate message
    # if we failed, the UI will immediately show the error screen
    report_progress_ui(100, 'burning finished successfully')

    # making sure we log anything nasty that has happened
    if unparsed_line:
        debugger('[ERROR] Failed parsing the line: ' + unparsed_line)

    if failed:
        debugger('[ERROR] Burning Kano image failed')
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
