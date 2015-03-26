#!/usr/bin/env python

# burn.py
#
# Copyright (C) 2014 Kano Computing Ltd.
# License: http://www.gnu.org/licenses/gpl-2.0.txt GNU General Public License v2
#
#
# OSX - Burning Kano OS module
#
# The burning process consists of two tasks: one for writing
# and one for progress polling.
#
# The writing (burning) thread uses a gzip to dd pipe to eliminate the
#    need for uncompressing the image and extra space needed.
#
# The polling thread sends a signal to dd which triggers it to output
#    its progress to stderr in the form of 'X bytes written'.
#
# We will also notify the UI of any errors that might have occured.


import os
import time
import Queue
import threading
import subprocess

from src.common.utils import run_cmd, calculate_eta, debugger, BYTES_IN_MEGABYTE
from src.common.errors import BURN_ERROR
from src.common.paths import temp_path


def start_burn_process(os_info, disk, report_progress_ui):
    '''
    This method is used by the backendThread to burn Kano OS.

    It starts the burning process on a separate thread and then
    sits in the polling loop. It uses a Queue to get results from
    the burning thread and returns an error if necessary.
    '''

    # Set the progress to 0% on the UI progressbar, and write what we're up to
    report_progress_ui(0, 'preparing to burn OS image..')

    # since a thread cannot return, use this queue to add the return boolean
    thread_output = Queue.Queue()

    # start the burning process on a separate thread and such that this one polls for progress
    burn_thread = threading.Thread(target=burn_kano_os,
                                   args=(os.path.join(temp_path, os_info['filename']),
                                         disk,
                                         os_info['uncompressed_size'],
                                         thread_output,
                                         report_progress_ui))
    burn_thread.start()

    # start the polling loop and pass the reference of the burning thread
    poll_burning_thread(burn_thread)

    # make sure we clean up threading resources
    burn_thread.join()

    successful = thread_output.get()
    if not successful:
        return BURN_ERROR
    else:
        return None


def burn_kano_os(path, disk, size, return_queue, report_progress_ui):
    cmd = 'gzip -dc {} | dd of={} bs=4m'.format(path, disk)
    process = subprocess.Popen(cmd, shell=True, stderr=subprocess.PIPE)

    failed = False
    unparsed_line = ''

    # as long as Popen is running, read it's stderr line by line
    # each time an INFO signal is sent to dd, it outputs 3 lines
    # and we are only interested in the last one i.e. 'x bytes written in y seconds'
    for line in iter(process.stderr.readline, ''):
        if 'bytes' in line:
            try:
                parts = line.split()

                written_bytes = float(parts[0])
                progress = int(written_bytes / size * 100)

                speed = float(parts[6][1:]) / BYTES_IN_MEGABYTE

                eta = calculate_eta(written_bytes, size, int(parts[6][1:]))

                report_progress_ui(progress, 'speed {0:.2f} MB/s  eta {1:s}  completed {2:d}%'
                                   .format(speed, eta, progress))
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
        return_queue.put(False)
    else:
        debugger('Burning successfully finished')
        return_queue.put(True)


def poll_burning_thread(thread):
    time.sleep(1)  # wait for dd to start
    debugger('Polling burner for progress..')
    cmd = 'kill -INFO `pgrep ^dd`'

    # as long as the burning thread is running, send SIGINFO
    # to dd to trigger progress output
    while thread.is_alive():
        _, error, return_code = run_cmd(cmd)
        if return_code:
            debugger('[ERROR] Sending signal to burning thread failed')
            return False
        time.sleep(0.3)
    return True
