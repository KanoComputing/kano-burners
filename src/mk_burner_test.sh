#!/bin/sh

# mk_burner_test.sh
#
# Copyright (C) 2015 Kano Computing Ltd.
# License: http://www.gnu.org/licenses/gpl-2.0.txt GNU General Public License v2

# make short a burner file suitable for testing, 

N=burner_test
F=${N}.img


dd if=/dev/urandom bs=1M count=10 of=$(F)

gzip ${F}
zcat ${F}.gz >${F}
rm ${F}.zip
zip ${F}.zip ${F}
echo >${F}.json {
echo >>${F}.json ' "uncompressed_md5":"'$(md5sum ${F} |cut -d ' ' -f 1)'"',
echo >>${F}.json ' "compressed_md5":"'$(md5sum ${F}.gz | cut -d ' ' -f 1)'"',
echo >>${F}.json ' "zip_md5":"'$(md5sum ${F}.zip | cut -d ' ' -f 1)'"',
echo >>${F}.json ' "uncompressed_size":'$(stat -c "%s" ${F}),
echo >>${F}.json ' "compressed_size":'$(stat -c "%s" ${F}.gz),
echo >>${F}.json ' "zip_size":'$(stat -c "%s" ${F}.zip)

echo >>${F}.json }

cat >${N}.json <<EOF
{
  "name": "Kano OS",
  "version": "Beta 1.3.4",
  "base_url": "http://dev.kano.me/temp/",
  "filename": "burner_test.img",
  "url": "http://dev.kano.me/temp/burner_test.img.gz",
  "url_zip": "http://dev.kano.me/temp/burner_test.img.zip"
}
EOF
