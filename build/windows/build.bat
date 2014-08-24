
:: build.bat
::
:: Copyright (C) 2014 Kano Computing Ltd.
:: License: http://www.gnu.org/licenses/gpl-2.0.txt GNU General Public License v2
::
:: [File description]


pyinstaller ^
    --distpath=%HomePath%"\Desktop\Kano Burner" ^
    --specpath=%HomePath%"\Desktop\Kano Burner\build" ^
    --workpath=%HomePath%"\Desktop\Kano Burner\build" ^
    --clean ^
    "Kano Burner.spec"
