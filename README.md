IMG-SIGN Extractor (signimg2img)
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
* ```python3 signimg2img.py -s/-b/-r``` (Use -h to see help)

Supported images:
=====================================
* Boot.img-sign
* System-sign.img
* Recovery-sign.img

NOTE: If you try to unpack images that are not signed, the script will obviously fail..

LICENSE:
=====================================
This program is licensed under the GNU General Public License. See LICENSE.md for details.

Thanks to:
=====================================
* anestisb for his simg2img
