#!/usr/bin/env python

# build.py
#
# Copyright (C) 2014 Kano Computing Ltd.
# License: http://www.gnu.org/licenses/gpl-2.0.txt GNU General Public License v2
#
#
# Automatic bundling with PyInstaller
#
# There are 3 main steps here:
#
# 1. Generate .spec file for the OS distribution we are currently running.
#    This involves running make-spec.[sh/bat] in /build/[OS]/
#
# 2. Modify the generated .spec file to point to the right folder
#    (e.g. pathex=['C:\...\kano-burners'])
#    and to add all resource files to the distribution.
#
# 3. Run the build.[sh/bat] script in /build/[OS]/
#    The script uses the .spec file to bundle the application.
#
# One ring to rule them all, one script to build them all.


import os
import sys
import glob
import platform


def extra_datas(path):
    '''
    This method takes a given path and returns all files (including subfolders)
    in the appropriate format required by PyInstaller's Analysis object.

    Simply append the returned results to the Analyser .datas field.
    '''
    def recursive_glob(path, files):
        for file_path in glob.glob(path):
            if os.path.isfile(file_path):
                files.append(os.path.join(os.getcwd(), file_path))
            recursive_glob('{}/*'.format(file_path), files)

    files = []
    extra_datas = []

    if os.path.isfile(path):
        files.append(os.path.join(os.getcwd(), path))
    else:
        recursive_glob('{}/*'.format(path), files)

    for f in files:
        extra_datas.append((f.split('kano-burners')[1][1:], f, 'DATA'))
    return extra_datas


def compile_resources():
    '''
    Compile a list of all resources and tools of the project for the App bundle.

    If the project requires additional resources, include them below.
    '''
    resources = list()

    resources += extra_datas(os.path.join(os.getcwd(), '..', '..', 'res'))
    resources += extra_datas(os.path.join(os.getcwd(), '..', '..', 'win'))
    resources += extra_datas(os.path.join(os.getcwd(), '..', '..', 'DISCLAIMER'))

    return resources


def read_file_lines(path):
    if os.path.exists(path):
        with open(path) as infile:
            content = infile.readlines()
            lines = [line for line in content]
            return lines


def write_file_contents(data, path):
    with open(path, 'w') as outfile:
        outfile.write(data)


# Detect OS platform and set the approriate script paths, i.e. build/[patform]
if platform.system() == 'Darwin':
    print 'Mac OS detected'
    os.chdir('osx')
    build_script_path = os.path.abspath(os.path.join(os.getcwd(), 'build.sh'))
    make_spec_path = os.path.abspath(os.path.join(os.getcwd(), 'make-spec.sh'))

elif platform.system() == 'Linux':
    print 'Linux OS detected'
    os.chdir('linux')
    build_script_path = os.path.abspath(os.path.join(os.getcwd(), 'build.sh'))
    make_spec_path = os.path.abspath(os.path.join(os.getcwd(), 'make-spec.sh'))

elif platform.system() == 'Windows':
    print 'Windows OS detected'
    os.chdir('windows')
    build_script_path = os.path.abspath(os.path.join(os.getcwd(), 'build.bat'))
    make_spec_path = os.path.abspath(os.path.join(os.getcwd(), 'make-spec.bat'))


# make sure Mac/Linux user is not root
if (platform.system() == 'Darwin' or platform.system() == 'Linux') and os.getuid() == 0:
    print 'This script does not require sudo!'
    print "To avoid changing PyQt permissions, simply run with 'python build.py'"
    sys.exit()


# Step 1: Generate a .spec file
os.system(make_spec_path)


# Step 2: Adapt .spec file to include project resources
resources = compile_resources()
spec_lines = read_file_lines('Kano Burner.spec')
passed_analysis = False

for index in range(0, len(spec_lines)):

    # modify the path to the project - because we generated the file in build/[platform]
    if 'pathex' in spec_lines[index]:
        # go up two levels to fix the path
        correct_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))
        line_parts = spec_lines[index].split("'")
        line_parts[1] = correct_path
        spec_lines[index] = "'".join(line_parts)

    # after the Analysis object has been defined, append all resources to its datas field
    if ')' in spec_lines[index] and not passed_analysis:
        resource_line = 'a.datas += {}\n'.format(resources)
        spec_lines.insert(index + 1, resource_line)
        passed_analysis = True

# save the new .spec file
write_file_contents(''.join(spec_lines), 'Kano Burner.spec')


# Step 3: Run PyInstaller build script with the .spec file
os.system(build_script_path)
