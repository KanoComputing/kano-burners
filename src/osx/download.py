
# download.py
#
# Copyright (C) 2014 Kano Computing Ltd.
# License: http://www.gnu.org/licenses/gpl-2.0.txt GNU General Public License v2
#
# [File description]


from time import sleep
from pySmartDL import SmartDL, HashFailedException

from src.common.utils import debugger, read_file_contents_as_lines
from src.common.errors import DOWNLOAD_ERROR, MD5_ERROR


TEST_URL = 'http://repo.kano.me/archive/pool/main/r/raspberrypi-firmware/libraspberrypi-doc_1.20140326-1.20140413_armhf.deb'
TEST2_URL = 'http://dev.kano.me/public/squeak.tar.gz'
#GZIP_OS_URL = 'http://dev.kano.me/public/kanux-latest.img.gz'
#GZIP_MD5_URL = 'http://dev.kano.me/public/kanux-latest.img.gz.md5'
#ZIP_OS_URL = 'http://dev.kano.me/public/Kanux-Beta-v1.1.0.img.gz'
#ZIP_MD5_URL = 'http://dev.kano.me/public/Kanux-Beta-v1.1.0.img.gz.md5'
GZIP_OS_URL = 'http://dev.kano.me/public/Kanux-Beta-v1.1.0.img.gz'
GZIP_MD5_URL = 'http://dev.kano.me/public/Kanux-Beta-v1.1.0.img.gz.md5'


class Downloader(SmartDL):

    def __init__(self, *args, **kwargs):
        SmartDL.__init__(self, *args, **kwargs)

        # we register the stop() method of SmartDL to be called when the program exits
        # it makes sure any downloading threads are safely terminated
        import atexit
        atexit.register(self.stop)


def download_kano_os(path, report_progress_ui):
    # simply make sure the file was not corrupted - not for cryptographic security
    downloaded_md5 = download_md5(GZIP_MD5_URL, path)

    #downloader = SmartDL(TEST2_URL, dest=path, progress_bar=False)
    downloader = Downloader(GZIP_OS_URL, dest=path, progress_bar=False)
    downloader.add_hash_verification('md5', downloaded_md5)

    # the documentation is misleading - if non blocking mode is used,
    # exceptions can still be thrown
    try:
        downloader.start(blocking=False)
    except:
        pass

    # the downloader is running separate threads so here we wait for the
    # process to finish and call the UI function which reports the process
    # when the application is closed, we need to specifically kill it and check that status
    while not downloader.isFinished() and not downloader._killed:
        report_progress_ui(downloader.get_progress() * 100, 'speed {}  eta {}  completed {}%'
                           .format(downloader.get_speed(human=True),
                                   downloader.get_eta(human=True),
                                   int(downloader.get_progress() * 100)))
        sleep(0.3)

    # check if the download finished successfully
    if downloader.isSuccessful():
        debugger('Downloading successfully finished and md5 check passed')
        report_progress_ui(100, 'download completed')
        return True, None
    else:
        # look through the errors that occured and report an MD5 error
        for error in downloader.get_errors():
            if isinstance(error, HashFailedException):
                debugger('[ERROR] md5 verification failed')
                return False, MD5_ERROR

        # for any other errors, report a general message
        debugger('[ERROR] downloading Kano image failed')
        return False, DOWNLOAD_ERROR


def download_md5(url, path):
    downloader = Downloader(url, dest=path, progress_bar=False)

    # again, making sure we catch any exceptions pySmartDL may throw
    try:
        downloader.start(blocking=True)
    except:
        debugger('[ERROR] could not start md5 download')
        return False, DOWNLOAD_ERROR

    # check if the MD5 download finished successfully
    if downloader.isSuccessful():
        debugger('md5 download was successful')

        # add the md5 file name to the temp dir's path and read it
        path += url.rsplit('/', 1)[1]
        lines = read_file_contents_as_lines(path)

        # the md5 checksum is the first 'word' in the first (and only) line
        downloaded_md5 = lines[0].split()[0]
        return downloaded_md5
    else:
        debugger('[ERROR] md5 download was not successful')
        return ''
