#!/bin/bash

# build.sh
#
# Copyright (C) 2014 Kano Computing Ltd.
# License: http://www.gnu.org/licenses/gpl-2.0.txt GNU General Public License v2
#
# [File description]


pyinstaller \
    --distpath=~/Desktop/Kano\ Burner/ \
    --specpath=~/Desktop/Kano\ Burner/build/ \
    --workpath=~/Desktop/Kano\ Burner/build/ \
    --clean \
    --noconfirm \
    Kano\ Burner.spec
