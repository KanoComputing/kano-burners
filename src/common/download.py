#!/usr/bin/env python

# download.py
#
# Copyright (C) 2014 Kano Computing Ltd.
# License: http://www.gnu.org/licenses/gpl-2.0.txt GNU General Public License v2
#
#
# Downloading Kano OS module
#
# The module uses PySmartDL to download the OS image file and
# urllib2 to get the information about the latest OS release.
#
# The downloading process is also required to report it's progress
# back to the UI, therefore we run PySmartDL as a child process
# and sit in a polling loop while it is running.
#
# We will also notify the UI of any errors that might have occured.


import time
import json
import urllib2
import traceback

from src.common.pySmartDL.pySmartDL import SmartDL, HashFailedException
from src.common.utils import debugger, LATEST_OS_INFO_URL
from src.common.errors import DOWNLOAD_ERROR, MD5_ERROR
from src.common.paths import temp_path


class Downloader(SmartDL):
    '''
    This class acts as a PySmartDL wrapper which fixes a process killing bug.

    When the application is closed via the [X] button, we want all downloading
    threads to be killed immediately and cleaned up.
    '''

    def __init__(self, *args, **kwargs):
        SmartDL.__init__(self, *args, **kwargs)

        # we register the stop() method of SmartDL to be called when the program exits
        # it makes sure any downloading threads are safely terminated
        import atexit
        atexit.register(self.stop)

    # @Override
    def isFinished(self):
        # the default method now needs to also report whether it was killed or not
        return not self._killed and SmartDL.isFinished(self)


def download_kano_os(report_progress_ui):
    '''
    This method is used by the backendThread to download Kano OS.

    We start PySmartDL as a child process and then sit in a polling loop
    to report progress to the UI. We will also return the OS info dict
    along with any error that might have occured.
    '''

    # set the progress to 0% on the UI progressbar, and write what we're up to
    report_progress_ui(0, 'preparing to download OS image..')

    # get information about the latest OS version e.g. url, filename, md5 checksum
    os_info = get_latest_os_info()
    if not os_info:
        return None, DOWNLOAD_ERROR

    # the documentation is misleading - if non blocking mode is used,
    # pySmartDL may still throw exceptions
    try:
        downloader = Downloader(os_info['url'], dest=temp_path, progress_bar=False)
        # simply make sure the file was not corrupted - not for cryptographic security
        downloader.add_hash_verification('md5', os_info['compressed_md5'])
        downloader.start(blocking=False)

    except KeyError:
        debugger('[ERROR] Server returned an unsupported json key')
        debugger(traceback.format_exc())
        return None, DOWNLOAD_ERROR
    except:
        debugger('[ERROR] pySmartDL has crashed')
        debugger(traceback.format_exc())
        return None, DOWNLOAD_ERROR

    # the downloader is running separate threads so here we wait for the
    # process to finish and call the UI function which reports the process
    while not downloader.isFinished():
        report_progress_ui(downloader.get_progress() * 100, 'speed {}  eta {}  completed {}%'
                           .format(downloader.get_speed(human=True),
                                   downloader.get_eta(human=True),
                                   int(downloader.get_progress() * 100)))
        time.sleep(0.3)

    # check if the download finished successfully
    if downloader.isSuccessful():
        debugger('Downloading successfully finished and md5 check passed')
        report_progress_ui(100, 'download completed')
        return os_info, None

    else:
        # look through the errors that occured and report an MD5 error
        for error in downloader.get_errors():
            if isinstance(error, HashFailedException):
                debugger('[ERROR] MD5 verification failed')
                return None, MD5_ERROR

        # for any other errors, report a general message
        debugger('[ERROR] Downloading Kano image failed')
        return None, DOWNLOAD_ERROR


def get_latest_os_info():
    debugger("Downloading latest OS information")

    # we put everything in a try block as urlopen raises URLError
    try:
        # get latest.json from download.kano.me
        response = urllib2.urlopen(LATEST_OS_INFO_URL)
        latest_json = json.load(response)
        latest_json['filename'] += '.gz'  # the .gz will be used on all OSs

        # give the server some time to breathe between requests
        debugger('Latest Kano OS image is {}'.format(latest_json['filename']))
        time.sleep(1)

        # use the url for the latest os version to get info about the image
        latest_image_json = '{base_url}{filename}.json'.format(
            base_url=latest_json['base_url'],
            filename=latest_json['filename'])

        debugger('Latest Kano OS image json is {}'.format(latest_image_json))
        response = urllib2.urlopen(latest_image_json)
        os_json = json.load(response)

        # give the server some time to breathe between requests
        time.sleep(1)

    except:
        debugger('[ERROR] Downloading OS info failed')
        return None

    # merge the two jsons, add derived values and return a single info dict
    os_info = dict(latest_json.items() + os_json.items())
    return os_info
