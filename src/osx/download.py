
# download.py
# 
# Copyright (C) 2014 Kano Computing Ltd.
# License: http://www.gnu.org/licenses/gpl-2.0.txt GNU General Public License v2
#
# [File description]


import sys
import platform
import subprocess
from time import sleep
from src.common.utils import run_cmd


URL_GZIP = 'http://dev.kano.me/public/squeak.tar.gz'
#URL_GZIP = 'http://dev.kano.me/public/kanux-latest.gz'
URL_ZIP = 'http://dev.kano.me/public/kanux-latest.zip'


def debugger(text):
    if True:
        print '[DEBUG]', text


def reportProgress(progress, speed):
	sys.stdout.write('{} completed at {}\r'.format(progress, speed))
	sys.stdout.flush()


def downloadKanoOS():
	cmd = 'wget -P temp/ {}'.format(URL_GZIP)
	debugger('   with command ' + cmd)
	
	process = subprocess.Popen(cmd, shell=True, stderr=subprocess.PIPE)
	
	for line in iter(process.stderr.readline, ''):
		parts = line.split()
		if len(parts) >= 8 and '%' in parts[6]:
			reportProgress(parts[6], parts[7])

	if not process.returncode:
		debugger('Downloading successfully finished')
	else:
		debugger('[ERROR] downloading Kano image failed')


def gzipDecompress(file):
	cmd = 'gzip -d {}'.format(file)
	debugger('   with command ' + cmd)
	run_cmd(cmd)


def getAvailableSpaceMB():
	cmd = "df -m | grep -v 'Available' | awk '{print $4}' | head -n1"
	debugger('   with command ' + cmd)
	output, _, _ = run_cmd(cmd)
	return int(output)
