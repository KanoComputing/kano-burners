#!/bin/bash

# build.sh
#
# Copyright (C) 2014 Kano Computing Ltd.
# License: http://www.gnu.org/licenses/gpl-2.0.txt GNU General Public License v2
#
#
# Linux build script
#
# This script calls PyInstaller to build Kano Burner
# from the generated .spec file obtained by running
# make-spec.sh
#
# NOTE: Before running this, make sure the spec file has
#       been correctly generated and customised as needed.
#
# WARNING: Do not run this script with sudo!
#
# For more info:
# http://pythonhosted.org/PyInstaller/#using-spec-files


pyinstaller \
    --distpath=~/Desktop/Kano\ Burner/ \
    --specpath=~/Desktop/Kano\ Burner/build/ \
    --workpath=~/Desktop/Kano\ Burner/build/ \
    --clean \
    --noconfirm \
    Kano\ Burner.spec
