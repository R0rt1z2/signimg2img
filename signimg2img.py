#!/usr/bin/env python3

         #====================================================#
         #              FILE: signimg2img.py                  #
         #              AUTHOR: R0rt1z2                       #
         #====================================================#

#   Android signed images extractor. To use the script:
#   "python3 signimg2img -b/-r/-s" (-flag depends on the image to unpack).
#
#   This program is free software: you can redistribute it and/or modify
#   it under the terms of the GNU General Public License as published by
#   the Free Software Foundation, either version 3 of the License, or
#   (at your option) any later version.
#
#   This program is distributed in the hope that it will be useful,
#   but WITHOUT ANY WARRANTY; without even the implied warranty of
#   MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#   GNU General Public License for more details.
#
#   You should have received a copy of the GNU General Public License
#   along with this program.  If not, see <https://www.gnu.org/licenses/>.
#
#   All copyrights of simg2img goes for anestisb.

from argparse import ArgumentParser
from subprocess import Popen, PIPE, DEVNULL, STDOUT, check_call, call
from sys import version_info as __pyver__
import sys
import glob
import time
import os

# Defines section
__version__ = '1.1'
__pyver__ = str(__pyver__[0])

# Check for platform
if sys.platform.startswith("linux"):
    print("")
else:
    print("Unsopported platform!")
    exit()

# Check for python version
if __pyver__[0] == "3":
    time.sleep(0.1)
else:
    print(f'Invalid Python Version.. You need python 3.X to use this script. Your Version is: {__pyver__}\n')
    exit()

def display(s):
    text = f"[sign2img-log] {s}"
    print(text)

def shCommand(sh_command):
    call(sh_command, shell=True)

def check_header(image):
    images = str(glob.glob("*.img"))
    images = images.replace("[", "").replace("'", "").replace("]", "").replace(",", "")
    if image in images:
      with open(image, "rb") as binary_file:
         header = binary_file.read(8)
         header = str(header)
      if "BFBF" in header:
         display(f"Detected BFBF header: {header}")
      else:
         display("This is not a signed image!!\n")
         exit()
    else:
      display(f"Cannot find {image}!\n")
      exit()

def package():
    display("Detecting if simg2img is installed...")
    simg2img = Popen('apt list --installed | grep simg2img', shell=True, bufsize=64, stdin=PIPE, stdout=PIPE, stderr=STDOUT, close_fds=True).stdout.read().strip().decode('utf-8')
    if "simg2img" in simg2img:
       display("simg2img is installed... Continue")
    else:
       display("simg2img is not installed, install it for unpack the system!\n")
       exit()

def system():
      oldfiles()
      display("Deleting magic header from system-sign.img...")
      shCommand("dd if=system-sign.img of=system.img bs=$((0x4040)) skip=1")
      display("Converting to ext4 image...")
      shCommand("simg2img system.img system.ext4")
      display("Unpacking system image...")
      os.mkdir("system_out")
      shCommand("sudo mount -r -t ext4 -o loop system.ext4 /mnt")
      shCommand("sudo cp -r /mnt/* system_out")
      shCommand("sudo umount /mnt")
      shCommand("sudo chown -R $USER:$USER system_out")
      display("system-sign.img extracted at >>system_out<<\n")
      exit()

def oldfiles():
    display("Checking for old files...")
    files = str(glob.glob("*.img"))
    files = files.replace("[", "").replace("'", "").replace("]", "").replace(",", "")
    if "boot.img" in files or "recovery.img" in files or "system.img" in files:
       display("Detected old files. Deleting them...")
       call("rm boot.img && rm recovery.img && system.img && rm -rf system_out", shell=True, stdin=PIPE, stdout=PIPE, stderr=STDOUT, close_fds=True)
    else:
       display("There's no old files, continue...")

def main():
    print('signimg2img binary - version: {}\n'.format(__version__))
    parser = ArgumentParser()
    parser.add_argument("-s", "--system", action='store_true', dest='systemsign', default=False,
                        help="Extract system-sign.img")
    parser.add_argument("-b", "--boot", action='store_true', dest='bootsign', default=False,
                        help="Extract boot-sign.img")
    parser.add_argument("-r", "--recovery", action='store_true', dest='recoverysign', default=False,
                        help="Extract recovery-sign.img")
    args = parser.parse_args()
    if args.systemsign:
      display("Selected: Unpack recovery-sign.img")
      check_header("system-sign.img")
      system()
    elif args.bootsign:
      display("Selected Image to unpack: boot-sign.img")
      check_header("boot-sign.img")
      oldfiles()
      shCommand("dd if=boot-sign.img of=boot.img bs=$((0x4040)) skip=1")
      display("Done, image extracted as boot.img\n")
    elif args.recoverysign:
      display("Selected: Unpack recovery-sign.img")
      check_header("recovery-sign.img")
      oldfiles()
      shCommand("dd if=recovery-sign.img of=recovery.img bs=$((0x4040)) skip=1")
      display("Done, image extracted as recovery.img\n")
    else:
      display("No option selected\n")
      exit()

if __name__ == "__main__":
   main()
