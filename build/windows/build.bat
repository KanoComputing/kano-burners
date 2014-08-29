
:: build.bat
::
:: Copyright (C) 2014 Kano Computing Ltd.
:: License: http://www.gnu.org/licenses/gpl-2.0.txt GNU General Public License v2
::
::
:: Windows build script
::
:: This script calls PyInstaller to build Kano Burner
:: from the generated .spec file obtained by running
:: make-spec.bat
::
:: NOTE: Before running this, make sure the spec file has
::       been correctly generated and customised as needed.
::
:: For more info:
:: http://pythonhosted.org/PyInstaller/#using-spec-files


pyinstaller ^
    --distpath=%HomePath%"\Desktop\Kano Burner" ^
    --specpath=%HomePath%"\Desktop\Kano Burner\build" ^
    --workpath=%HomePath%"\Desktop\Kano Burner\build" ^
    --clean ^
    --noconfirm ^
    "Kano Burner.spec"
