#!/bin/bash

# make-spec.sh
#
# Copyright (C) 2014 Kano Computing Ltd.
# License: http://www.gnu.org/licenses/gpl-2.0.txt GNU General Public License v2
#
#
# Linux PyInstaller .spec file generator
#
# This is the first script to run as part of the build process.
#
# It generates a standard .spec file for PyInstaller which you
# will need to customise afterwards as described in the README
#
# For more info:
# http://pythonhosted.org/PyInstaller/#general-options
# http://pythonhosted.org/PyInstaller/#building-mac-os-x-app-bundles


pyi-makespec \
    --onefile \
    --noconsole \
    --name="Kano Burner" \
    --icon=../../res/icon/burner_icon.png \
    ../../bin/kano-burner
