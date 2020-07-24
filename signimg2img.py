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
SRC_HEADERS = [
	1178748482,\
    1397969747
]

BFBF_SIZE = 16448

str_start_addr = 0x000010

# Check for platform
if sys.platform.startswith("linux") or ("win"):
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
    text = "[signimg2img-log] {}".format(s)
    print(text)

def shCommand(sh_command, stderr):
    if stderr == "out":
       call(sh_command, shell=True, stdin=PIPE, stdout=PIPE, stderr=STDOUT, close_fds=True)
    else:
       call(sh_command, shell=True)


def get_offset(image):
    # Thanks to carlitos900 for the shell method.
    # This is the "pythonic" method.
    # This is for little endian arch.
    image = open(image, 'rb')
    image.read(60) # Header
    offset, = struct.unpack('<I', image.read(4))
    return offset
    
def grep_filetype(type):
    typefiles = str(glob.glob("*.{}".format(type)))
    typefiles = typefiles.replace("[", "").replace("'", "").replace("]", "").replace(",", "")
    return typefiles

def remove_files(files):
    cmd = files.replace(" ", " & rm ")
    cmd = " ".join(("rm", cmd))
    shCommand(cmd, "out")

def delete_header(image, outimage, hdr_type, offset):
    display("Deleting the header...")
    if hdr_type == "BFBF":
       time.sleep(0.5)
       with open(image, 'rb') as in_file:
          with open(outimage, 'wb') as out_file:
            out_file.write(in_file.read()[BFBF_SIZE:])
    elif hdr_type == "SSSS":
       if sys.platform.startswith("win"):
          raise RuntimeError("Windows cannot unpack SSSS header!")
       shCommand(f'dd if=system-sign.img of=system.img iflag=count_bytes,skip_bytes bs=8192 skip=64 count={offset}', "out")
       display("Header remove complete!")
    else:
       raise Exception("Must be SSSS or BFBF not {}".format(hdr_type))

def check_header(image):
    try:
      with open(image, "rb") as binary_file:
         data = binary_file.read(4)
         img_hdr, = struct.unpack('<I', data)
         binary_file.seek(str_start_addr) 
         try:
             img_string = (binary_file.read(8)).decode("utf-8")
         except UnicodeDecodeError:
             display("Warning: Cannot parse the string inside the image..")
         global header
      if img_hdr == SRC_HEADERS[0]:
         display(f"Header is BFBF: {img_hdr}")
         display(f"Found {img_string} at {str_start_addr}")
         header = "BFBF"
         return
      elif img_hdr == SRC_HEADERS[1]:
         display(f"Header is SSSS: {img_hdr}")
         header = "SSSS"
      else:
         display("This is not a signed image!!\n")
         exit()
    except FileNotFoundError:
      raise RuntimeError("Cannot find {}. Is it in the correct path?".format(image))
      exit()    

def unpack_system(header):
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
        raise RuntimeError("simg2img is not installed!")
      display("Unpacking system image...")
      if os.path.exists("system_out"):
          shCommand("sudo umount system_out", "noout")
          os.rmdir("system_out")
          os.mkdir("system_out")
      shCommand("sudo mount -r -t ext4 -o loop system.ext4 system_out", "noout")
      shCommand("sudo chown -R $USER:$USER system_out", "noout")
      display("system-sign.img extracted at system_out\n")
      exit()

def rm_old_files(image):
       display("Removing old files if they're present...")
       if os.path.isfile("signimg2img.py"):
           for file in glob.glob('*.*'):
               if file.endswith(".unpack") or file.endswith(".ext4"):
                   os.remove(file)
               elif file.startswith("signimg2img") or file.endswith("-sign.img") or file.startswith("LICENSE") or file.startswith("README"):
                   pass
               else:
                   os.remove(file)

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
    elif sys.argv[1] == "-h":
         help()      
    elif sys.argv[1] == "-s":
      display("Selected: Unpack system-sign.img")
      check_header("system-sign.img")
      unpack_system(header)
    elif sys.argv[1] == "-b":
      display("Selected Image to unpack: boot-sign.img")
      check_header("boot-sign.img")
      rm_old_files("boot-sign.img")
      delete_header("boot-sign.img", "boot.img", header, 0)
      display("Done, image extracted as boot.img\n")
    elif sys.argv[1] == "-r":
      display("Selected: Unpack recovery-sign.img")
      check_header("recovery-sign.img")
      rm_old_files("recovery-sign.img")
      delete_header("recovery-sign.img", "recovery.img", header, 0)
      display("Done, image extracted as recovery.img\n")
    elif sys.argv[1] == "-o":
      check_header(sys.argv[2])
      if header is "SSSS":
          offset = get_offset(sys.argv[2])
          display(f'Offset: {offset}')
      with open(sys.argv[2], "rb") as fin:
        data = len(fin.read())
      display(f'Size: {data} bytes')
      if header is "BFBF" or "SSSS":
          display(f'Image can be unpacked: yes\n')
      else:
          display(f'Image can be unpacked: no (invalid header)\n')
    elif sys.argv[1] == "-i":
      display(f"Selected: Unpack {sys.argv[1]}")
      check_header(sys.argv[2])
      rm_old_files(sys.argv[2])
      delete_header(f"{sys.argv[2]}", f"{sys.argv[2]}.unpack", header, 0)
      display(f"Done, image extracted as {sys.argv[2]}.unpack\n")
    elif sys.argv[1] == "-c":
       unpack_files = grep_filetype("unpack")
       ext4_files = grep_filetype("ext4")
       img_files = grep_filetype("img")
       remove_files(img_files)
       remove_files(ext4_files)
       remove_files(unpack_files)
       if os.path.exists("system_out"):
           shutil.rmtree("system_out")
       if os.path.exists("system_out_old"):
           shutil.rmtree("system_out_old")
       display("Cleaned up!\n")    
    else:
      display("Invalid option: {}\n".format(sys.argv[1]))
      help()

if __name__ == "__main__":
   main()
