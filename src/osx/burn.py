
# burn.py
# 
# Copyright (C) 2014 Kano Computing Ltd.
# License: http://www.gnu.org/licenses/gpl-2.0.txt GNU General Public License v2
#
# [File description]


import os
import sys
import platform
import subprocess
import signal

from time import sleep
from src.common.utils import run_cmd


def debugger(text):
    if True:
        print '[DEBUG]', text


def getDisks():
	cmd = 'diskutil list'
	output, error, returnCode = run_cmd(cmd)

	disks = list()
	disk = None

	for line in output.splitlines():
		line = line.strip()

		if line.startswith('/'):
			disk = line[:5] + 'r' + line[5:]
		else:
			if not disk:
				debugger('Parsing error - could not get disks.')

			if line.startswith('0:'):
				parts = line.split()
				size = float(parts[2][1:])

			elif line.startswith('1:'):
				parts = line.split()
				name = ' '.join(parts[2:-3])

				# append all data here, as this will always be the last
				# this would need changing if logic changes
				
				data = {
					'disk_id': disk,
					'name': name,
					'size': size
				}

				# make sure we do not list any potential hard drive
				if size >= 64 or 'disk0' in disk:
					debugger('Considering {} as HDD'.format(data))
				else:
					disks.append(data)
					debugger('Detected disk {}'.format(data))
	return disks


def unmountDisk(disk):
	cmd = 'diskutil unmountDisk {}'.format(disk)
	debugger('   with command ' + cmd)
	_, error, returnCode = run_cmd(cmd)

	if not returnCode:
		debugger('{} successfully unmounted'.format(disk))
	else:
		debugger('[ERROR] ' + error.strip('\n'))


def eraseDisk(disk):
	cmd = 'diskutil eraseDisk MS-DOS UNTITLED {}'.format(disk)
	debugger('   with command ' + cmd)
	_, error, returnCode = run_cmd(cmd)

	if not returnCode:
		debugger('{} successfully erased and formatted'.format(disk))
	else:
		debugger('[ERROR] ' + error.strip('\n'))


def ejectDisk(disk):
	cmd = 'diskutil eject {}'.format(disk)
	debugger('   with command ' + cmd)
	_, error, returnCode = run_cmd(cmd)

	if not returnCode:
		debugger('{} successfully ejected'.format(disk))
	else:
		debugger('[ERROR] ' + error.strip('\n'))


kanoImgSize = os.path.getsize('temp/kanux-latest.img')

def reportProgress(progress):
	sys.stdout.write('{}% completed\r'.format(progress / kanoImgSize * 100))
	sys.stdout.flush()


def burnImage(disk):
	cmd = 'dd if=temp/kanux-latest.img of={} bs=1m'.format(disk)
	debugger('   with command ' + cmd)
	
	process = subprocess.Popen(cmd, shell=True, stderr=subprocess.PIPE)
	
	# as long as Popen is running, read it's stderr line by line
	# each time an INFO signal is sent to dd, it outputs 3 lines
	# and we are only interested in the last one i.e. 'x bytes written in y seconds'
	for line in iter(process.stderr.readline, ''):
		if 'bytes' in line:
			reportProgress(float(line.split()[0]))

	if not process.returncode:
		debugger('Burning successfully finished')
	else:		
		debugger('[ERROR] burning Kano image failed')
	
