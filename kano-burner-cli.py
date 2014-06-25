
# kano-burner-cli.py
# 
# Copyright (C) 2014 Kano Computing Ltd.
# License: http://www.gnu.org/licenses/gpl-2.0.txt GNU General Public License v2
#
# [File description]


import sys
import platform
import threading
from time import sleep
from src.common.utils import run_cmd, delete_dir, ensure_dir, is_installed


def debugger(text):
    if True:
        print '[DEBUG]', text



# Step 1: Detect platform to import appropriate modules
if platform.system() == 'Darwin':
    debugger('Mac OS detected')
    from src.osx.download import *
    from src.osx.burn import *

elif platform.system() == 'Linux':
    debugger('Linux OS detected')
    from src.linux.download import *
    from src.linux.burn import *

elif platform.system() == 'Windows':
	debugger('Windows OS detected')
	from src.windows.download import *
	from src.windows.burn import *


# Step 2: intro screen > press any button to continue
#raw_input('Welcome to Kano Burner client.\nPress [ENTER] to start the process.')


# Step 3: check for internet
cmd = 'is_internet'
_, _, returnCode = run_cmd(cmd)
if not returnCode:
	debugger('You must be connected to the internet to use this utility')
	sys.exit(1)
else:
	debugger('Internet connection detected')


# Step 4: look for archiver tools
if is_installed('gzip'):
	debugger('Gzip tool is installed')
	decompress = gzipDecompress

elif is_installed('winrar'):
	debugger('WinRAR tool is installed')
	decompress = winrarDecompress

elif is_installed('winzip'):
	debugger('WinZip tool is installed')
	decompress = winzipDecompress

elif is_installed('7-Zip'):
	debugger('7-Zip tool is installed')
	decompress = zipDecompress
else:
	debugger('No appropriate archiver tool found to decompress image')
	sys.exit(1)


# Step 5: check for available space
debugger('Checking for available space')
freeSpaceMB = getAvailableSpaceMB()
debugger('Free space {} GB'.format(freeSpaceMB / 1024))

if freeSpaceMB < 3270:
	debugger('Please ensure you have at least 3.2GB available space locally')
	sys.exit(1)


# Step 6: list drives
debugger('Scanning drives..')
disks = getDisks()
if not disks:
	print 'No available disks were found. Did you insert the SD card?'
	sys.exit(1)


# Step 7: ask user to select a disk
print 'Select a drive to burn Kano OS'
for index in xrange(0, len(disks)):
	print('{}) {} {} {}'.format(index + 1, disks[index].get('disk_id'), disks[index].get('name'), disks[index].get('size')))
selected = int(raw_input('Option: ')[0]) - 1
selectedDisk = disks[selected].get('disk_id')


# Step 8: make 'temp' folder for image and archive
debugger('Making temp directory')
ensure_dir('temp')


# Step 9: download the latest Kano OS image
print 'Downloading latest Kano OS image'
downloadThread = threading.Thread(target = downloadKanoOS)
downloadThread.start()
downloadThread.join()


# Step 10: do checksum to verify integrity



# Step 11: unzip image
debugger('Decompressing image')
decompress('temp/squeak.tar.gz')
#decompress('temp/kanux-latest.gz')


# Step 12: clean SD card
# necessary? appropriate format? MS-DOS (FAT)?
debugger('Erasing SD card')
eraseDisk(selectedDisk)


# Step 13: unmount SD card
debugger('Unmounting disk ' + selectedDisk)
unmountDisk(selectedDisk)


# Step 14: burn image
print 'Burning image to SD card on ' + selectedDisk
burnThread = threading.Thread(target = burnImage, args = (selectedDisk,))
burnThread.start()

debugger('Polling burner for progress')
cmd = 'kill -INFO `pgrep ^dd`'
debugger('   with command ' + cmd)

while burnThread.isAlive():
	sleep(1)
	run_cmd(cmd)
	

# Step 15: delete temp files
debugger('Removing temp files')
#delete_dir('temp')


# Step 16: eject disk
debugger('Waiting for things to settle..')
sleep(5) # wait for dd to mount the disk back
debugger('Ejecting SD card')
ejectDisk(selectedDisk)


# Step 16: success messsage
#raw_input('Kano OS has successfully been installed.\nPress [ENTER] to quit.')
