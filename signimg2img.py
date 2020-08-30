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
#   Thanks to anestisb (simg2img), no copyright asserted by them.

from subprocess import *
import struct
import sys
import glob
import time
import shutil
import os

__version__ = '1.4'

SRC_HEADERS = [
	1178748482,\
    1397969747
]

BFBF_SIZE = 16448

if sys.platform.startswith("darwin") or sys.platform.startswith("win") or sys.platform.startswith("linux"):
    pass
else:
    raise Exception("Unsupported platform")

if sys.version_info[0] != 3:
    raise Exception("Python 3.x is required")

def display(s):
    text = "[signimg2img-log] {}".format(s)
    print(text)

def shCommand(sh_command, output):
    if output is 0:
       call(sh_command, shell=True, stdin=PIPE, stdout=PIPE, stderr=STDOUT, close_fds=True)
    else:
       call(sh_command, shell=True)

def get_offset(image):
    image = open(image, 'rb')
    image.read(60)
    offset = struct.unpack('<I', image.read(4))[0]
    return offset

def delete_header(image, outimage, hdr_type, offset):
    display("Deleting the header...")
    if hdr_type == "BFBF":
       with open(image, 'rb') as in_file:
          with open(outimage, 'wb') as out_file:
            out_file.write(in_file.read()[BFBF_SIZE:])
    elif hdr_type == "SSSS":
       if sys.platform.startswith("win"):
          raise RuntimeError("Windows cannot unpack images with SSSS header!")
       shCommand("dd if=system-sign.img of=system.img iflag=count_bytes,skip_bytes bs=8192 skip=64 count={}".format(offset), 0)
       display("Header remove complete!")
    else:
       raise Exception("Must be SSSS or BFBF not {}".format(hdr_type))

def regen_folder(folder):
    try:
        os.rmdir(folder)
    except OSError:
        display("Warning: {} isn't empty...".format(folder))
        shutil.rmtree(folder)
    os.mkdir(folder)

def check_header(image):
    try:
      with open(image, "rb") as image:
         image_header = struct.unpack('<I', image.read(4))[0]
         image.seek(0x000010) 
         try:
             img_string = (image.read(8)).decode("utf-8")
         except UnicodeDecodeError:
             display("Warning: Cannot parse the string inside the image..")
             global header
      if image_header == SRC_HEADERS[0]:
         display("Header is BFBF: {}".format(image_header))
         display("Found {} at 0x000010".format(img_string))
         header = "BFBF"
      elif image_header == SRC_HEADERS[1]:
         display("Header is SSSS: {}".format(image_header))
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
          display("Got {} as offset!".format(offset))
          delete_header("system-sign.img", "system.img", header, offset)
      display("Converting to ext4 image...")
      p = Popen("simg2img system.img system.ext4", shell=True, stdin=PIPE, stdout=PIPE, stderr=PIPE, close_fds=True)
      if(len(p.stderr.read()) != 0):
        raise RuntimeError("Something went wrong while converting to ext4 image. Is simg2img installed? Bailing out...")
      display("Unpacking system image...")
      if os.path.exists("system_out"):
          shCommand("sudo umount system_out", 0)
          regen_folder("system_out")
      else:
          os.mkdir("system_out")
      shCommand("mount -r -t ext4 -o loop system.ext4 system_out", 0)
      display("system-sign.img extracted at system_out\n")
      exit()

def remove_old_files(image):
    display("Removing old files if they're present...")
    if os.path.isfile("signimg2img.py"):
       for file in glob.glob('*.*'):
           if image is "full":
               if file.startswith("signimg2img") or file.startswith("LICENSE") or file.startswith("README"):
                   pass
               else:
                   os.remove(file)
           elif file.endswith(".unpack") or file.endswith(".ext4"):
               os.remove(file)
           elif file.startswith("signimg2img") or file.endswith("-sign.img") or file.startswith("LICENSE") or file.startswith("README"):
               pass
           else:
               os.remove(file)

def help():
    display("USAGE: signimg2img.py -option:\n")
    print("   -u image-sign.img: Unsigns the given image. (If is system will unpack it)")
    print("   -o: Get image info (-o image_name).")
    print("   -c: Full cleanup (removes all!)")
    print("")
    exit()

def main():
    print('signimg2img binary - version: {}\n'.format(__version__))
    if len(sys.argv) == 1:
         display("Expected more arguments.\n")
         help()
    elif sys.argv[1] == "-h":
         help()
    elif sys.argv[1] == "-u" and len(sys.argv) != 1:
      display("Selected: Unpack {}".format(sys.argv[2]))
      check_header(sys.argv[2])
      remove_old_files(sys.argv[2])
      if "system" in sys.argv[2]:
          unpack_system(header)
      else:
          delete_header(sys.argv[2], "{}.unpack".format(sys.argv[2]), header, 0)
          display("Done, image extracted as {}.unpack\n".format(sys.argv[2]))
    elif sys.argv[1] == "-o":
      check_header(sys.argv[2])
      if header is "SSSS":
          offset = get_offset(sys.argv[2])
          display("Offset: {}".format(offset))
      display("Size: {} bytes".format(os.path.getsize(sys.argv[2])))
      if header is "BFBF" or "SSSS":
          display("Image can be unpacked: yes\n")
      else:
          display("Image can be unpacked: no (invalid header)\n")
    elif sys.argv[1] == "-c":
       remove_old_files("full")
       if os.path.exists("system_out"):
          p = Popen("umount system_out", shell=True, stdin=PIPE, stdout=PIPE, stderr=PIPE, close_fds=True)
          if(len(p.stderr.read()) != 0):
              raise RuntimeError("Cannot unmount the system_out folder!")
          shutil.rmtree("system_out")
       display("Cleaned up!\n")    
    else:
      display("Invalid option: {}\n".format(sys.argv[1]))
      help()

if __name__ == "__main__":
   if os.getuid() != 0:
       raise RuntimeError("Script must be ran as root")
   main()
