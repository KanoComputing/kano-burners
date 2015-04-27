#!/usr/bin/env python

# download.py
#
# Copyright (C) 2014 Kano Computing Ltd.
# License: http://www.gnu.org/licenses/gpl-2.0.txt GNU General Public License v2
#
#
# Downloading Kano OS module

from src.common.utils import debugger
import os.path
import os
import subprocess
import xmlrpclib
import sys
import atexit
import time


class HashFailedException(Exception):
    pass

_aria2_path=None
def set_aria2_path(path):
    global _aria2_path
    _aria2_path = path

class Downloader:
    def __init__(self, url, dest, progress_bar=False):
        self.url = url
        self.dest = dest
        self.hash_type = None
        self.hash_value = None
        self.process = None
        self.secret = ''.join(format(ord(x), 'x') for x in os.urandom(10))
        self.gid = 'DEADC0D9BEEFFACE'

        self.status = None
        self.failed = False
        self.failure = None

        self.ariaStatus = {}
        self.gid = None

    def add_hash_verification(self, hash_type, hash_value):
        self.hash_type = hash_type
        self.hash_value = hash_value

    def start(self, blocking=False):
        checksum_opts = []

        if self.hash_type:
            checksum_opts = ['-V']
            checksum_opt = '{}={}'.format(self.hash_type, self.hash_value)
        port = 5900
        l1 = [
            _aria2_path,
            '-d', self.dest,
            '-x', '5',
            '-j', '5',
            '-s', '5',
            '--rpc-listen-port={}'.format(port),
            '--enable-rpc=true',
            '--rpc-listen-all',
            '--rpc-secret={}'.format(self.secret)
            ]
        cmd_args = l1 + checksum_opts
        cmd = ' '.join(cmd_args)
        self.process = subprocess.Popen(cmd, shell=True, universal_newlines=True,
                                        stdout=sys.stdout,
                                        stderr=subprocess.STDOUT)
        atexit.register(self.close)
        
        debugger('ran [{}] pid {}'.format(cmd, self.process.pid))
        try:
            self.server = xmlrpclib.ServerProxy('http://localhost:{}/rpc'.format(port))
        except Exception as e:
            self.failed = True
            self.failure = e
            debugger(' failed to start server {}'.format(e))

        if not self.failed:
            try:
                self.process.poll()
                debugger('rc {}'.format(self.process.returncode))
                time.sleep(1)
                self.gid = self.server.aria2.addUri('token:'+self.secret, [self.url], {'checksum':checksum_opt})
                debugger('added download gid:{}'.format(self.gid))
            except Exception as e:
                debugger('addUri failed {}'.format(e))
                self.failed = True
                self.failure = e

    def getAriaStatus(self):
        self.process.poll()
        if not self.process.returncode:
            try:
                self.ariaStatus = self.server.aria2.tellStatus('token:'+self.secret, self.gid)
                if not isinstance(self.ariaStatus, dict):
                    self.ariaStatus = {}
            except Exception as e:
                self.failed = True
                self.failure = e
                debugger('status call error {}'.format(e))

    def isFinished(self):
        self.process.poll()
        if self.process.returncode:
            debugger('aria returned {}'.format(self.status.returncode))
            return True  # aria finished; since it's not supposed to until we tell it, it probably died
        if self.failed:
            debugger('aria failed {}'.format(self.failure))
            return True

        self.getAriaStatus()
        result = self.ariaStatus['status']
        finished = result != 'active' and result != 'waiting'
        return finished

    def get_progress(self):
        self.getAriaStatus()

        if all(x in self.ariaStatus for x in
               ['totalLength', 'completedLength']):
            try:
                proportion = (float(self.ariaStatus['completedLength'])*1.0 /
                              float(self.ariaStatus['totalLength']))
            except ZeroDivisionError:
                proportion = 0.0
            return proportion
        else:
            return 0.0

        return proportion

    def get_speed(self, human=True):
        self.getAriaStatus()
        if 'downloadSpeed' in self.ariaStatus:
            speed = float(self.ariaStatus['downloadSpeed'])/1024.0/1024.0
        else:
            speed = 0
        if human:
            return '{0:.1f} MB/s'.format(speed)
        else:
            return speed

    def get_eta(self, human=True):
        self.getAriaStatus()

        if all(x in self.ariaStatus for x in
               ['totalLength', 'completedLength', 'downloadSpeed']):
            try:
                     eta = int((float(self.ariaStatus['totalLength']) -
                            float(self.ariaStatus['completedLength'])
                        )*1.0/float(self.ariaStatus['downloadSpeed']))
            except ZeroDivisionError:
                     eta = '???'
                     
        else:
            eta = '???'

        if human:
            if eta == '???':
                return '??? secs'
            else:
                return '{} secs'.format(int(eta))
        else:
            if eta == '???':
                return 365*24*60*60
            else:
                return eta

    def close(self):
        self.process.poll()
        if not self.process.returncode:
            self.process.kill()
            time.sleep(1)
            self.process.poll()
            if not self.process.returncode:
                self.process.terminate()
                pass

    def isSuccessful(self):
        if self.failed:
            return False
        self.getAriaStatus()
        debugger('Final aria status {}'.format(self.ariaStatus))

        # Fixme: check codes present in dict
        # Fixme: check for hash failed code

        if self.ariaStatus['status'] != 'complete' or int(self.ariaStatus['errorCode']) != 0:
            debugger('Download status {}'.format(self.ariaStatus['status']))
            debugger('Downloader returned error code {}'.format(self.ariaStatus['errorCode']))
            return False

        return True

    def get_errors(self):
        # fixme more here
        return [self.failure]
