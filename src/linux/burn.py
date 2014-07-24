
# burn.py
#
# Copyright (C) 2014 Kano Computing Ltd.
# License: http://www.gnu.org/licenses/gpl-2.0.txt GNU General Public License v2
#
# [File description]


import subprocess
import threading
import Queue

from time import sleep
from src.common.utils import run_cmd, debugger, BYTES_IN_MEGABYTE
from src.common.errors import BURN_ERROR


uncompressed_size = 0  # gets set the first time the uncompressed image is calculated
                       # avoids recalculating when trying again


def start_burn_process(path, disk, report_progress_ui):
    global uncompressed_size

    # check if the file is found and get it's size
    report_progress_ui(0, 'calculating uncompressed image size..')
    if not uncompressed_size:
        uncompressed_size = get_gzip_uncompressed_size(path + 'Kanux-Beta-v1.1.0.img.gz')

    # since a thread cannot return, use this queue to add the return boolean
    thread_output = Queue.Queue()
    burn_thread = threading.Thread(target=burn_kano_os, args=(path, disk, uncompressed_size,
                                   thread_output, report_progress_ui))
    burn_thread.start()

    # delegate the polling loop job and pass the reference of the burning thread
    poll_burning_thread(burn_thread)

    # make sure we clean up threading resources
    burn_thread.join()

    successful = thread_output.get()
    if not successful:
        return False, BURN_ERROR
    else:
        return True, None


def burn_kano_os(path, disk, size, return_queue, report_progress_ui):
    cmd = 'gzip -dc {}Kanux-Beta-v1.1.0.img.gz | dd of={} bs=4M'.format(path, disk)
    process = subprocess.Popen(cmd, shell=True, stderr=subprocess.PIPE)
    failed = False

    # as long as Popen is running, read it's stderr line by line
    # each time an INFO signal is sent to dd, it outputs 3 lines
    # and we are only interested in the last one i.e. 'x bytes written in y seconds'
    for line in iter(process.stderr.readline, ''):
        if 'bytes' in line:
            parts = line.split()

            written_bytes = float(parts[0])
            progress = int(written_bytes / size * 100)

            speed = float(parts[7])

            eta = calculate_eta(written_bytes, size, speed * BYTES_IN_MEGABYTE)

            report_progress_ui(progress, 'speed {0:.2f} MB/s  eta {1:s}  completed {2:d}%'
                               .format(speed, eta, progress))

        # watch out for an error output from dd
        if 'Input/output error' in line:
            failed = True

    if failed:
        debugger('[ERROR] burning Kano image failed')
        return_queue.put(False)
        return False
    else:
        debugger('Burning successfully finished')
        return_queue.put(True)
        return True


def poll_burning_thread(thread):
    sleep(1)
    debugger('Polling burner for progress..')
    cmd = 'kill -USR1 `pgrep ^dd`'

    # as long as the burning thread is running, send SIGINFO
    # to dd to trigger progress output
    while thread.is_alive():
        _, error, return_code = run_cmd(cmd)
        if return_code:
            debugger('[ERROR] sending signal to burning thread failed')
            return False
        sleep(0.3)
    return True


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


def get_gzip_uncompressed_size(path):
    debugger('Calculating uncompressed image size..')
    cmd = 'gzip -dc {} | wc -c'.format(path)
    process = subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE)

    for line in iter(process.stdout.readline, ''):
        output = line

    debugger('Uncompressed gzip file is {} bytes'.format(int(output)))
    return int(output)
