System-sign.img Unpacker
=====================================

This script, allows you to unpack a Signed Android system.img.
It simply removes the magic header from it, convers it into an ext4 and if you want it extracts it.

Requisites:
=====================================
* simg2img
* python3

How to unpack?
=====================================
* Copy the system-sign.img into the tool folder.
* Open a terminal or cmd in the tool folder.
* ```python3 system-sign-extractor.py system-sign.img```

Thanks to:
=====================================
* anestisb for his simg2img
