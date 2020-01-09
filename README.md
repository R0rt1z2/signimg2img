IMG-SIGN Extractor (signimg2img) v1.3
=====================================
This script, allows you to unpack/delete the header of Android Signed Images.

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
* ```python3 signimg2img.py -option```

Example of system-sign (SSSS) unpack output:
```
sudo python3 signimg2img.py -s

signimg2img binary - version: 1.3

[signimg2img-log] Selected: Unpack system-sign.img
[signimg2img-log] Header is SSSS: 1397969747
[signimg2img-log] Checking if simg2img is installed...
[signimg2img-log] simg2img is installed... Continue
[signimg2img-log] Removing old files if they're present...
[signimg2img-log] Getting the offset...
[signimg2img-log] Got 1885696592 as offset!
[signimg2img-log] Deleting the header...
[signimg2img-log] Start the 1st Stage...
[signimg2img-log] Start the 2nd Stage...
[signimg2img-log] Header remove complete!
[signimg2img-log] Converting to ext4 image...
[signimg2img-log] Unpacking system image...
[signimg2img-log] system-sign.img extracted at >>system_out<<
```

Supported headers:
=====================================
* BFBF
* SSSS

Available options (Use -h to see them in the tool):
=====================================
* -b: Convert Android Signed Boot Image.
* -r: Convert Android Signed Recovery Image.
* -s: Convert & extract Android Signed System Image.
* -i: Convert any other image (i.e: cache-sign, lk-sign, etc).
* -o: Get image info (-o image_name).
* -c: Full cleanup (removes all!)

Supported images:
=====================================
* All signed images except vendor-sign.img (Working on it..)

NOTE: If you try to unpack images that are not signed, the script will obviously fail..

LICENSE:
=====================================
This program is licensed under the GNU General Public License. See LICENSE.md for details.

Thanks to:
=====================================
* anestisb for his simg2img.
* carlitos900 and kjones for the help with the SSSS header.
