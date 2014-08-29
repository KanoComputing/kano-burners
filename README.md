kano-burners
============

Kano OS Burner is a cross-platform application for Mac, Linux, and Windows with which users can quickly burn the latest version of Kano OS on an SD card. It is written in Python 2.7 and PyQt 4, integrating with the system tools for specific functionality. For Mac and Windows, the project also includes PyInstaller build scripts to make distribution as easy as possible.


### How it works

The application checks for dependencies when it is launched and will prompt you if something is missing. If everything is alright after this point, you will see a drop down menu saying `Select device` and a disabled button. When you click the menu, the application scans all disks connected to the machine and will list those that can be used to burn Kano OS. By default, disks smaller than 4GB and larger than 64GB will **not** be listed to avoid hard drive wipes. You then select the disk you want to burn Kano OS to, click `BURN!` and the process starts. The application then downloads the OS, formats the disk, and finally burns the OS on the disk.


### More info

Please visit the [wiki pages](https://github.com/KanoComputing/kano-burners/wiki)!
