# system-sign unpacker
# By R0rt1z2
# simg2img is made by anestisb.
import argparse, subprocess, os

# Define current path
PATH = os.getcwd() + "/system_out/"

def main():
    subprocess.call("echo '1'>>firstrun",shell=True)
    parser = argparse.ArgumentParser()
    parser.add_argument("system", help="Signed System Image for unpack")
    args = parser.parse_args()
    system = args.system
# Check for old files.
    print("Checking old files...")
    subprocess.call("ls | grep firstrun > old",shell=True)
    with open('old') as myfile:
       old = myfile.read()
    if "firstrun" in old:
       print("Detected old files. Cleaning up...")
       subprocess.call("sudo rm system.img && rm simg2img.info && rm firstrun && rm system.ext4",shell=True)
       # This folder needs one line xD
       subprocess.call("sudo rm -rf system_out",shell=True)
       check()
    else:
       ("Old files not detected. Continue.")
       check()

# Check if simg2img is installed
def check():
    print("Detecting if simg2img is installed...")
    subprocess.call("apt list --installed | grep simg2img > simg2img.info",shell=True)
    with open('simg2img.info') as myfile:
       simg2img = myfile.read(8)
    if "simg2img" in simg2img:
       unpack()
    else:
       # Other way for print in color? ¯\_(ツ)_/¯
       subprocess.call("echo '\e[31msimg2img not detected! Install it first for use this tool. Bye'",shell=True)
       print("")
       exit()

# Unpack section.
def unpack():
    print("This will unpack your system-sign.img. Press any key for continue\nPress ctrl+c for finish the script")
    input()
    print("Deleting magic header from system-sign.img...")
    subprocess.call("dd if=system-sign.img of=system.img bs=$((0x4040)) skip=1",shell=True)
    unpack = input("Do you want to unpack sparse system.img? y/n >> ")
    if "y" in unpack:
       print("Converting to ext4 image...")
       subprocess.call("simg2img system.img system.ext4",shell=True)
       print("Unpacking system image...")
       subprocess.call("sudo mkdir system_out",shell=True)
       subprocess.call("sudo mount -r -t ext4 -o loop system.ext4 /mnt",shell=True)
       subprocess.call("sudo cp -r /mnt/* system_out",shell=True)
       subprocess.call("sudo umount /mnt",shell=True)
       subprocess.call("sudo chown -R $USER:$USER system_out",shell=True)
       # Other way for print in color? ¯\_(ツ)_/¯
       subprocess.call("echo '\e[32mSystem.img unpacked succsefully at >>system_out<<'",shell=True)
    if "n" in unpack:
       subprocess.call("echo '\e[32mYour unpacked img is >>system.img<<'",shell=True)
       exit()

if __name__ == "__main__":
   main()
