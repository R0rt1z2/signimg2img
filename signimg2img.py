#!/usr/bin/env python3

         #====================================================#
         #              FILE: signimg2img.py                  #
         #              AUTHOR: R0rt1z2                       #
         #====================================================#

#   Android signed images extractor. To use the script:
#   "python3 signimg2img -b/-r/-s" or -i image_name to unpack any other image.
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

from subprocess import *
from sys import version_info as __pyver__
import struct
import sys
import glob
import time
import shutil
import os

# Defines section
__version__ = '1.3'
__pyver__ = str(__pyver__[0])

# Defines
BFBF_HDR = 1178748482
SSSS_HDR = 1397969747
str_start_addr = 0x000010 # 16 bytes after the BFBF header

# Check for platform
if sys.platform.startswith("linux"):
    print("")
else:
    print("Unsopported platform!")
    exit()

# Check for python ver
if __pyver__[0] == "3":
    time.sleep(0.1)
else:
    print(f'Invalid Python Version.. You need python 3.X to use this script. Your Version is: {__pyver__}\n')
    exit()

def display(s):
    text = f"[signimg2img-log] {s}"
    print(text)

def shCommand(sh_command, stderr):
    if stderr == "out":
       call(sh_command, shell=True, stdin=PIPE, stdout=PIPE, stderr=STDOUT, close_fds=True)
    else:
       call(sh_command, shell=True)

# display and shCommand should be the first functions. If not, will cause errors.

def get_offset(image):
    # Thanks to carlitos900 for the shell method.
    # This is the "pythonic" method.
    # This is for little endian arch.
    image = open(image, 'rb')
    image.read(60) # Header
    offset, = struct.unpack('<I', image.read(4)) # SSSS 4 bytes ---> <I
    return offset
    
def grep_filetype(type):
    typefiles = str(glob.glob(type))
    typefiles = typefiles.replace("[", "").replace("'", "").replace("]", "").replace(",", "")
    return typefiles

def delete_header(image, outimage, hdr_type, offset): # If there's no need of offset (i.e: "BFBF" use "0")
    display("Deleting the header...")
    if hdr_type == "BFBF":
       time.sleep(0.5)
       shCommand(f'dd if={image} of={outimage} bs=$((0x4040)) skip=1', "out") # dd command to delete "BFBF" header.
    elif hdr_type == "SSSS":
       shCommand(f'dd if=system-sign.img of=system.img iflag=count_bytes,skip_bytes bs=8192 skip=64 count={offset}', "out") # dd command to delete "SSSS" header. Needs defined offset.
       display("Header remove complete!")
    else:
       raise Exception("Must be SSSS or BFBF not {}".format(hdr_type))

def check_header(image, ext):
    if ext == "img":
        images = str(grep_filetype("*.img"))
    elif ext == "bin":
        images = str(grep_filetype("*.bin"))
    if image in images:
      with open(image, "rb") as binary_file:
         data = binary_file.read(4) # First 4 bytes show header string.
         img_hdr, = struct.unpack('<I', data) # 4 bytes ---> <I
         binary_file.seek(str_start_addr) # Go to the string offset.
         img_string = (binary_file.read(8)).decode("utf-8") # Read the string offset
         global header # Define here the header variable, otherwise will fail.
      if img_hdr == BFBF_HDR:
         display(f"Header is BFBF: {img_hdr}")
         display(f"Found {img_string} at {str_start_addr}")
         header = "BFBF"
         return
      elif img_hdr == SSSS_HDR:
         display(f"Header is SSSS: {img_hdr}")
         header = "SSSS"
      else:
         display("This is not a signed image!!\n")
         exit()
    else:
      display(f"Cannot find {image}!\n")
      exit()    

def unpack_system(header):
      oldfiles()
      if header == "BFBF":
          delete_header("system-sign.img", "system.img", header, 0)
      elif header == "SSSS":
          display("Getting the offset...")
          offset = get_offset("system-sign.img")
          display(f'Got {offset} as offset!')
          delete_header("system-sign.img", "system.img", header, offset)
      display("Converting to ext4 image...")
      p = Popen("simg2img system.img system.ext4", shell=True, stdin=PIPE, stdout=PIPE, stderr=PIPE, close_fds=True)
      if(len(p.stderr.read()) != 0):
        sys.exit("simg2img is not installed!")
      display("Unpacking system image...")
      os.mkdir("system_out")
      shCommand("sudo mount -r -t ext4 -o loop system.ext4 /mnt", "noout")
      shCommand("sudo cp -r /mnt/* system_out", "noout")
      shCommand("sudo umount /mnt", "noout")
      shCommand("sudo chown -R $USER:$USER system_out", "noout")
      display("system-sign.img extracted at >>system_out<<\n")
      exit()

def oldfiles():
       display("Removing old files if they're present...")
       shCommand("rm boot.img && rm recovery.img && system.img && rm system.ext4 && rm -rf system_out && rm *.unpack && rm *.tmp", "out")
       if os.path.exists("system_out"):
           shCommand("mv system_out system_out_old", "out")

def help():
         display("USAGE: signimg2img.py -option:\n")
         print("     -b: Convert Android Signed Boot Image.")
         print("     -r: Convert Android Signed Recovery Image.")
         print("     -s: Convert & extract Android Signed System Image.")
         print("     -i: Convert any other image (i.e: cache-sign, lk-sign, etc).")
         print("     -o: Get image info (-o image_name).")
         print("     -c: Full cleanup (removes all!)")
         print("")
         exit()

def main():
    print('signimg2img binary - version: {}\n'.format(__version__))
    if len(sys.argv) == 1:
         display("Expected more arguments.\n")
         help()
         exit()
    elif sys.argv[1] == "-h":
         help()      
    elif sys.argv[1] == "-s":
      display("Selected: Unpack system-sign.img")
      check_header("system-sign.img", "img")
      unpack_system(header)
    elif sys.argv[1] == "-b":
      display("Selected Image to unpack: boot-sign.img")
      check_header("boot-sign.img", "img")
      oldfiles()
      delete_header("boot-sign.img", "boot.img", header, 0)
      display("Done, image extracted as boot.img\n")
    elif sys.argv[1] == "-r":
      display("Selected: Unpack recovery-sign.img")
      check_header("recovery-sign.img", "img")
      oldfiles()
      delete_header("recovery-sign.img", "recovery.img", header, 0)
      display("Done, image extracted as recovery.img\n")
    elif sys.argv[1] == "-o":
      image = sys.argv[2]
      if "bin" in sys.argv[2]:
         imgis = "bin"
      elif "img" in sys.argv[2]:
         imgis = "img"
      check_header(image, imgis)
      if header is "SSSS":
          offset = get_offset(image)
          display(f'Offset: {offset}')
      with open(image, "rb") as fin:
        data = len(fin.read())
      display(f'Size: {data} bytes')
      if header is "BFBF" or "SSSS":
         unpack = "yes"
      else:
         unpack = "no"
      display(f'Image can be unpacked: {unpack}\n')
      exit()
    elif sys.argv[1] == "-i":
      image = sys.argv[2]
      display(f"Selected: Unpack {image}")
      if "bin" in sys.argv[2]:
         imgis = "bin"
      elif "img" in sys.argv[2]:
         imgis = "img"
      check_header(sys.argv[2], imgis)
      oldfiles()
      delete_header(f"{image}", f"{image}.unpack", header, 0)
      display(f"Done, image extracted as {image}.unpack\n")
    elif sys.argv[1] == "-c":
       # TODO: Implement a cleaner way to remove all files (i.e: Using glob.glob).
       shCommand("rm *.img && rm *.ext4 && rm *.unpack && rm system.tmp", "out")
       shCommand("rm system.tmp", "out")
       if os.path.exists("system_out"):
           shutil.rmtree("system_out")
       if os.path.exists("system_out_old"):
           shutil.rmtree("system_out_old")
       display("Cleaned up!\n")    
    else:
      display(f"Invalid option: {sys.argv[1]}\n")
      help()
      exit()

if __name__ == "__main__":
   main()
