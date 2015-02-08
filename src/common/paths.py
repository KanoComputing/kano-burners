#!/usr/bin/env python

# paths.py
#
# Copyright (C) 2014 Kano Computing Ltd.
# License: http://www.gnu.org/licenses/gpl-2.0.txt GNU General Public License v2
#
#
# Paths used throughout the project
#
# We create path constants for resources and windows tools, as well as
# detecting whether we are running from source or a PyInstaller bundle.
# This is important when setting the base path of the project.


import os
import sys


# the current working directory differs when a
# we are running from a PyInstaller bundle
if getattr(sys, 'frozen', False):
    # debugger('Running from PyInstaller bundle')
    base_path = os.path.abspath(sys._MEIPASS)
else:
    # debugger('Running from source')
    base_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '../..'))


# setting a Temp directory path
temp_path = os.path.join(base_path, 'temp')
if not os.path.exists(temp_path):
        os.makedirs(temp_path)

# setting Resources paths - css and images
res_path = os.path.join(base_path, 'res')
images_path = os.path.join(res_path, 'images')
css_path = os.path.join(res_path, 'CSS')

# setting Windows Tools paths
win_tools_path = os.path.join(base_path, 'win')
_7zip_path = os.path.join(win_tools_path, '7zip')
_dd_path = os.path.join(win_tools_path, 'dd')
_nircmd_path = os.path.join(win_tools_path, 'nircmd')
