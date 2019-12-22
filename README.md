IMG-SIGN Extractor (signimg2img) v1.2
=====================================
This script, allows you to unpack a Signed Android img. It currently supports 3 types (see above for details). This tool is basically used to extract the "BFBF" header from the image.

Requisites:
=====================================
* simg2img
* python3

Supported OS:
=====================================
* Linux based systems.
* Windows (coming soon...).

How to unpack?
=====================================
* Copy the img to extract into the tool folder.
* Open a terminal or cmd in the tool folder.
* ```python3 signimg2img.py -s/-b/-r``` or -i image_name (Replace image_name with your image name) to unpack other image types.

Example of output:
```$ python3 signimg2img.py -i lk-sign.bin

signimg2img binary - version: 1.2

{signimg2img-log} Selected: Unpack lk-sign.bin
{signimg2img-log} Detected BFBF header: b'BFBF\x02\x00\x00\x00'
{signimg2img-log} Removing old files if they're present...
{signimg2img-log} Deleting the header...
{signimg2img-log} Done, image extracted as lk-sign.bin.unpack

$```

Supported images:
=====================================
* Boot.img-sign (Use -b)
* System-sign.img (Use -r)
* Recovery-sign.img (Use -s)
* Any other image (i.e: cache-sign.img) (Use for example -i cache-sign.img)

NOTE: If you try to unpack images that are not signed, the script will obviously fail..

LICENSE:
=====================================
This program is licensed under the GNU General Public License. See LICENSE.md for details.

Thanks to:
=====================================
* anestisb for his simg2img
