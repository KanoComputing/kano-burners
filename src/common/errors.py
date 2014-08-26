
# errors.py
#
# Copyright (C) 2014 Kano Computing Ltd.
# License: http://www.gnu.org/licenses/gpl-2.0.txt GNU General Public License v2
#
# [File description]


INTERNET_ERROR = {
    'title': 'No internet connection..',
    'description': 'You need to be connected to the internet to download Kano OS'
}
FREE_SPACE_ERROR = {
    'title': 'Insufficient available space..',
    'description': 'Please ensure you have at least 600 MB available space locally'
}
TOOLS_ERROR = {
    'title': 'Missing some tools..',
    'description': 'Please visit the dependency page for more information'
}
NO_DISKS_ERROR = {
    'title': 'SD Card not found..',
    'description': 'Make sure you have inserted the SD card correctly'
}
DOWNLOAD_ERROR = {
    'title': 'There was an error downloading Kano OS..',
    'description': 'Please check your internet connection or try again later'
}
MD5_ERROR = {
    'title': 'Could not verify download integrity..',
    'description': 'Kano OS download may have been corrupted - please try again'
}
BURN_ERROR = {
    'title': 'Burning Kano OS failed..',
    'description': 'Make sure the SD card is still correctly inserted and try again'
}
