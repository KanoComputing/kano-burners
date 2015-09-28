#!/usr/bin/env python

# burn.py
#
# Copyright (C) 2014,2015 Kano Computing Ltd.
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

from src.common.utils import run_cmd, calculate_eta, debugger
from src.common.utils import BYTES_IN_MEGABYTE, cmd_env
from src.common.errors import BURN_ERROR
from src.common.paths import temp_path

final_message = "PLEASE EJECT THE SD CARD!"

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
    failed = False
    unparsed_line = ''
    try:
        gzip_cmd = "gzip -dc '{}'".format(path)
        dd_cmd = "dd 'of={}' bs=4m".format(disk)
        gzip_process = subprocess.Popen(gzip_cmd,
                                        env=cmd_env,
                                        stderr=subprocess.PIPE,
                                        stdout=subprocess.PIPE,
                                        shell=True)
        dd_process = subprocess.Popen(dd_cmd,
                                      env=cmd_env,
                                      stderr=subprocess.PIPE,
                                      stdin=gzip_process.stdout,
                                      stdout=subprocess.PIPE,
                                      shell=True)
        gzip_process.stdout.close()

        gzip_err_output = Queue.Queue()

        def gzip_read(gzip_file, return_queue):
            lines = gzip_file.readlines()
            return_queue.put(lines)

        gzip_thread = threading.Thread(target=gzip_read,
                                       args=(gzip_process.stderr, gzip_err_output))
        gzip_thread.start()


        # as long as Popen is running, read it's stderr line by line
        # each time an INFO signal is sent to dd, it outputs 3 lines
        # and we are only interested in the last one i.e. 'x bytes written in y seconds'
        for line in iter(dd_process.stderr.readline, ''):
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

        # dd has closed its stdout, so everything should have finished.
        # But check anyway.

        dd_process.poll()
        if dd_process.returncode is None:
            dd_process.kill()
            dd_process.wait()

        gzip_process.poll()
        if gzip_process.returncode is None:
            gzip_process.kill()
            gzip_process.wait()

        if dd_process.returncode != 0:
            debugger('[ERROR] dd returned error code {}'
                     .format(dd_process.returncode))
            failed = True

        if gzip_process.returncode != 0:
            debugger('[ERROR] gzip returned error code {}'
                     .format(gzip_process.returncode))
            failed = True

        gzip_thread.join(100)
        gzip_stderr = gzip_err_output.get()

        debugger("gzip output: " + str(gzip_stderr))

        # make sure the progress bar is filled and show an appropriate message
        # if we failed, the UI will immediately show the error screen
        report_progress_ui(100, 'burning finished successfully')
    except Exception as e:
        debugger(str(e))
        failed = True

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
