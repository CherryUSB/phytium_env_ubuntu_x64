#!/usr/bin/env python3
# '''
#  : Copyright (c) 2021 Phytium Information Technology, Inc. 
 
# SPDX-License-Identifier: Apache-2.0.

# Date: 2021-10-29 15:59:56
# LastEditTime: 2021-10-29 16:00:42
# Description:  This files is for setup pythium dev environment, which inlcude
#          - Define PHYTIUM_DEV_PATH as global variable
#          - Unpack GNU Cross tools
# Modify History: 
#  Ver   Who        Date         Changes
# ----- ------     --------    --------------------------------------
# '''
import sys
import os
import pwd
import stat
import platform
import getpass
import tarfile
import re
import shutil
import zipfile

### platform constant
platform_tags = ["Linux_X86_64" "Linux_AARCH64" "Msys2" "WSL"]
linux_x86 = 0
linux_aarch64 = 1
windows_msys2 = 2
linux_x86_wsl = 3

### environment constant
old_dev_profile_path = "/etc/profile.d/phytium_standalone_sdk.sh"
dev_profile_path = "/etc/profile.d/phytium_dev.sh"

def rm_line(str, file_path):
    with open(file_path,'r+') as f:
        lines = [line for line in f.readlines() if str not in line]
        f.seek(0)
        f.truncate(0)
        f.writelines(lines)

def ap_line(str, file_path):
    with open(file_path, 'a') as f:
        f.write(str + '\n')

#################################################################
# STEP 1: Check environment

# get absoulte path current pwd to install sdk
phytium_dev_path, install_script = os.path.split(os.path.abspath(__file__))
curr_path = os.getcwd()
standalone_sdk_path = ''

# in case user call this script not from current path
if (curr_path != phytium_dev_path):
    print("[1]: Please cd to install script path first !!!")
    exit()

# check install environment
if ("microsoft-standard-WSL" in platform.uname().release) or ("microsoft-standard-WSL2" in platform.uname().release):
    install_platform = linux_x86_wsl
elif (platform.system() == 'Linux' ) and (platform.processor() == 'x86_64'):
    install_platform = linux_x86
elif (platform.system() == 'Linux' ) and (platform.processor() == 'aarch64'):
    install_platform = linux_aarch64
elif (re.search('MSYS_NT', platform.system()).span() == (0, len('MSYS_NT'))):
    install_platform = windows_msys2
else:
    print("[1]: Platform not support !!! ")
    exit()

# get current user to install, profile depends on user
usr = getpass.getuser()
if (install_platform == windows_msys2):
    # arch is not able to get for msys2
    print("[1]: Usr: {}, OS: {}, Type: {}".format(usr, platform.system(), install_platform))
else:
    print("[1]: Usr: {}, OS: {}, Arch: {}, Type: {}".format(usr, platform.system(), platform.processor(), install_platform))

print("[1]: Enviroment variables will set at {}".format(dev_profile_path))

# delete old dev profile
if os.path.exists(old_dev_profile_path):
    print("[1]: Remove old dev profile {}...".format(old_dev_profile_path))
    if windows_msys2 == install_platform:
        os.system("rm {}".format(old_dev_profile_path))
    else:
        os.system("sudo rm {}".format(old_dev_profile_path))

# create dev profile if not exist, assign read & write rights for all users
if not os.path.exists(dev_profile_path):
    print("[1]: Create dev profile {}...".format(dev_profile_path))
    if windows_msys2 == install_platform:
        os.system("touch {}".format(dev_profile_path))
        os.system("chmod 666 {}".format(dev_profile_path))
    else:
        os.system("sudo touch {}".format(dev_profile_path))
        os.system("sudo chmod 666 {}".format(dev_profile_path))

# check if dev profile create success
if not os.path.exists(dev_profile_path):
    print("[1] Create dev profile {} failed !!!".format(dev_profile_path))
    exit()

# remove old PHYTIUM_DEV_PATH definition
rm_line('PHYTIUM_DEV_PATH', dev_profile_path)

## STEP 2: reset environment
# remove environment from old profile for compatible
old_profile_path = os.environ.get('HOME') + '/.profile'
os.system("sed -i '/### PHYTIUM DEV SETTING START/d' "+ old_profile_path)
os.system("sed -i '/export AARCH32_CROSS_PATH=/d' " + old_profile_path)
os.system("sed -i '/export PATH=\$PATH:\$AARCH32_CROSS_PATH/d' " + old_profile_path)
os.system("sed -i '/export AARCH64_CROSS_PATH=/d' " + old_profile_path)
os.system("sed -i '/export PATH=\$PATH:\$AARCH64_CROSS_PATH/d' " + old_profile_path)
os.system("sed -i '/export PHYTIUM_OPENOCD_PATH=/d' " + old_profile_path)
os.system("sed -i '/export PATH=\$PATH:\$PHYTIUM_OPENOCD_PATH/d' " + old_profile_path)
os.system("sed -i '/### PHYTIUM DEV SETTING END/d' "+ old_profile_path)

# remove environment variables
rm_line('PHYTIUM DEV SETTING', dev_profile_path)
rm_line('export AARCH32_CROSS_PATH=', dev_profile_path)
rm_line('export PATH=$PATH:$AARCH32_CROSS_PATH', dev_profile_path)
rm_line('export AARCH64_CROSS_PATH=', dev_profile_path)
rm_line('export PATH=$PATH:$AARCH64_CROSS_PATH', dev_profile_path)
rm_line('export PHYTIUM_OPENOCD_PATH=', dev_profile_path)
rm_line('export PATH=$PATH:$PHYTIUM_OPENOCD_PATH', dev_profile_path)

print("[2]: Reset dev environment")

## STEP 3: get cross-platform compiler
cc_install_path = curr_path + '/'
# set cc package name, download url and install dst dir
if (install_platform == linux_x86_wsl):
    aarch32_cc = 'xpack-arm-none-eabi-gcc-12.2.1-1.2-linux-x64'
    aarch64_cc = 'xpack-aarch64-none-elf-gcc-12.2.1-1.2-linux-x64'
    openocd_bin = 'openocd'

    # cc package name
    aarch32_cc_pack = aarch32_cc + '.tar.xz'
    aarch64_cc_pack = aarch64_cc + '.tar.xz' 

    # openocd package name
    openocd_pack = 'openocd' + '.tar.xz'
elif (install_platform == linux_x86):

    aarch32_cc = 'xpack-arm-none-eabi-gcc-12.2.1-1.2-linux-x64'
    aarch64_cc = 'xpack-aarch64-none-elf-gcc-12.2.1-1.2-linux-x64'
    openocd_bin = 'openocd'

    # cc package name
    aarch32_cc_pack = aarch32_cc + '.tar.gz'
    aarch64_cc_pack = aarch64_cc + '.tar.gz' 

    # openocd package name
    openocd_pack = 'openocd' + '.tar.gz'
elif (install_platform == linux_aarch64):

    aarch32_cc = 'gcc-arm-10.3-2021.07-aarch64-arm-none-eabi'
    aarch64_cc = 'gcc-arm-10.3-2021.07-aarch64-aarch64-none-elf'
    openocd_bin = 'openocd'

    # cc package name
    aarch32_cc_pack = aarch32_cc + '.tar.xz'
    aarch64_cc_pack = aarch64_cc + '.tar.xz' 

    # openocd package name
    openocd_pack = 'openocd' + '.tar.xz'
elif (install_platform == windows_msys2):

    aarch32_cc = 'xpack-arm-none-eabi-gcc-12.2.1-1.2-win32-x64'
    aarch64_cc = 'xpack-aarch64-none-elf-gcc-12.2.1-1.2-win32-x64'
    openocd_bin = 'openocd'

    # cc package name
    aarch32_cc_pack = aarch32_cc + '.zip'
    aarch64_cc_pack = aarch64_cc + '.zip' 

    # openocd package name
    openocd_pack = 'openocd' + '.tar.xz'
      
aarch32_cc_pack_path = phytium_dev_path + '/' + aarch32_cc_pack
aarch64_cc_pack_path = phytium_dev_path + '/' + aarch64_cc_pack

aarch32_cc_install_path = cc_install_path + aarch32_cc
aarch64_cc_install_path = cc_install_path + aarch64_cc  

# check aarch32 cc install path
if os.path.exists(aarch32_cc_install_path):
    print("[4]: AARCH32 CC install success at {}".format(aarch32_cc_install_path))
else:
    print("[4]: AARCH32 CC install failed !!!")
    exit()

# check aarch32 cc install path
if os.path.exists(aarch64_cc_install_path):
    print("[4]: AARCH64 CC install success at {}".format(aarch64_cc_install_path))
else:
    print("[4]: AARCH64 CC install failed !!!")
    exit()

# install openocd
openocd_pack_path = phytium_dev_path + '/' + openocd_pack
openocd_install_path = cc_install_path + openocd_bin

# check aarch32 cc install path
if os.path.exists(openocd_install_path):
    print("[4]: OpenOCD install success at {}".format(openocd_install_path))
else:
    print("[4]: OpenOCD install failed !!!")
    exit()

print("[4]: GNU CC version: 10.3.1-2021.07")
print("[4]: OpenOCD version: 0.12.0")

os.environ['AARCH32_CROSS_PATH'] = aarch32_cc_install_path
os.environ['AARCH64_CROSS_PATH'] = aarch64_cc_install_path
os.environ['PHYTIUM_OPENOCD_PATH'] = openocd_install_path

ap_line('### PHYTIUM DEV SETTING START', dev_profile_path)
ap_line('export AARCH32_CROSS_PATH={}'.format(aarch32_cc_install_path), dev_profile_path)
ap_line('export PATH=$PATH:$AARCH32_CROSS_PATH/bin', dev_profile_path)
ap_line('export AARCH64_CROSS_PATH={}'.format(aarch64_cc_install_path), dev_profile_path)
ap_line('export PATH=$PATH:$AARCH64_CROSS_PATH/bin', dev_profile_path)
ap_line('export PHYTIUM_OPENOCD_PATH={}'.format(openocd_install_path), dev_profile_path)
ap_line('export PATH=$PATH:$PHYTIUM_OPENOCD_PATH/bin', dev_profile_path)

ap_line('### PHYTIUM DEV SETTING END', dev_profile_path)

print("[5]: Success!!! Dev Setup Done for {}".format(usr))
print("[5]: Input 'source {}' or Reboot System to Active it".format(dev_profile_path))
