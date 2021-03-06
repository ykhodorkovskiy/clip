#!/usr/bin/python
import os
import sys

import shutil
import parted
import subprocess
import optparse
import tempfile
import re


def main():


    def usage():
        usage = 'usage: mkbiarch.py <x86 Live ISO File> <x64 Live ISO File> <Target Multi Arch Image File>'
        print >> sys.stdout, usage


    def mount(src, dst, options=None):
        if os.path.exists(src):
            if not os.path.exists(dst):
                os.makedir(dst)
            if options is None:
                args = ("/bin/mount", src, dst)
            else:
                args = ("/bin/mount", options, src, dst)
            rc = subprocess.call(args)
            return rc
        return


    def umount(src):
        if os.path.exists(src):
                args = ("/bin/umount", src)
                rc = subprocess.call(args)
                return rc
        return


    def copy(src, dst):
        if os.path.exists(src):
            if not os.path.exists(dst):
                if not os.path.isfile(src):
                    mkdir(dst)
            shutil.copy(src, dst)


    def move(src, dst):
        if os.path.exists(src):
            shutil.move(src, dst)

    def mkdir(dir=None):
        if dir is None:
            tmp = tempfile.mkdtemp()
            return tmp
        else:
            args = ("/bin/mkdir", "-p", dir)
            rc = subprocess.call(args)


    def losetup(src, dst, offset=None):
        if os.path.exists(src):
            if os.path.exists(dst):
                if offset is None:
                    args = ("/sbin/losetup", src, dst)
                else:
                    args = ("/sbin/losetup", "-o", str(offset), src, dst)
                rc = subprocess.call(args)
        return rc

    def lounset(device):
        args = ("/sbin/losetup", "-d", device)
        rc = subprocess.call(args) 

    def null():
        fd = open(os.devnull, 'w')
        return fd

    def dd(file, target):
        args = ("/bin/dd", "if=%s"%file, "of=%s"%target)
        rc = subprocess.call(args)

    def lo():
        args = ("/sbin/losetup", "--find")
        rc = subprocess.Popen(args, stdout=subprocess.PIPE).communicate()[0].rstrip()
        return rc

    def lodev(file):
        args = ("/sbin/losetup", "-j", file)
        rc = subprocess.Popen(args, stdout=subprocess.PIPE).communicate()[0].split(":")
        return rc[0]


    def mkimage(bs, count):
        tmp = tempfile.mkstemp()
        image = tmp[1]
        args = ("/bin/dd", "if=/dev/zero",
                 "of=%s"%image, "bs=%s"%bs,
                 "count=%s"%count)
        rc = subprocess.call(args)
        return image


    def size(ent):
        if os.path.exists(ent):
            return os.stat(ent).st_size

    def bs(size):
        return size / 2048

    def partition(device):
        dev = parted.Device(path=device)
        disk = parted.freshDisk(dev, 'msdos')
        constraint = parted.Constraint(device=dev)

        new_geom = parted.Geometry(device=dev,
                                   start=1,
                                   end=(constraint.maxSize - 1))
        filesystem = parted.FileSystem(type="ext2",
                                       geometry=new_geom)
        partition = parted.Partition(disk=disk,
                                     fs=filesystem,
                                     type=parted.PARTITION_NORMAL,
                                     geometry=new_geom)
        constraint = parted.Constraint(exactGeom=new_geom)
        partition.setFlag(parted.PARTITION_BOOT)
        disk.addPartition(partition=partition,
                          constraint=constraint)
        
        disk.commit()

    def format(partition):
        args = ("/sbin/mke2fs", "-j", partition)
        rc = subprocess.call(args)

    def mbr(target):
        mbr = "/usr/share/syslinux/mbr.bin"
        dd(mbr, target)

    def getuuid(device):
        args = ("/sbin/blkid", "-s", "UUID", "-o", "value", device)
        rc = subprocess.Popen(args, stdout=subprocess.PIPE).communicate()[0].rstrip()
        return rc

    def syslinux(multitmp, config, **args):
        arg = ("/sbin/extlinux", "--install", multitmp + "/extlinux/")
        rc = subprocess.call(arg)

        content = """
        default vesamenu.c32
        timeout 100

        menu background splash.jpg
        menu title Welcome to Fedora 13
        menu color border 0 #ffffffff #00000000
        menu color sel 7 #ffffffff #ff000000
        menu color title 0 #ffffffff #00000000
        menu color tabmsg 0 #ffffffff #00000000
        menu color unsel 0 #ffffffff #00000000
        menu color hotsel 0 #ff000000 #ffffffff
        menu color hotkey 7 #ffffffff #ff000000
        menu color timeout_msg 0 #ffffffff #00000000
        menu color timeout 0 #ffffffff #00000000
        menu color cmdline 0 #ffffffff #00000000
        menu hidden
        menu hiddenrow 5

        label Fedora-13-x86
        menu label Fedora-13-x86
        kernel vmlinuz0
        append initrd=initrd0.img root=UUID=%(uuid)s rootfstype=auto ro live_dir=/x86/LiveOS liveimg
        
        label Fedora-13-x64
        menu label Fedora-13-x64
        kernel vmlinuz1
        append initrd=initrd1.img root=UUID=%(uuid)s rootfstype=auto ro live_dir=/x64/LiveOS liveimg
        """ % args
        fd = open(config, 'w')
        fd.write(content)
        fd.close()

    def verify():
        # use md5 module to verify image files
        pass

    def setup(x86, x64, multi):

        sz = size(x86) + size(x64)
        count = bs(sz)
        blsz = str(2048)

        count = count + 102400

        multi = mkimage(blsz, count)    
        losetup(lo(), multi)
 
        mbr(lodev(multi))
        partition(lodev(multi))
 
        lounset(lodev(multi))
     
        losetup(lo(), multi, offset=512)
        format(lodev(multi))

        multitmp = mkdir()
        mount(lodev(multi), multitmp)

        losetup(lo(), x86)
        losetup(lo(), x64)
 
        x86tmp = mkdir()
        x64tmp = mkdir()

        mount(lodev(x86), x86tmp)
        mount(lodev(x64), x64tmp)


        dirs = ("/extlinux/", "/x86/", "/x64/")
        for dir in dirs:
            mkdir(multitmp + dir)
        dirs = ("/x86/", "/x64/")
        for dir in dirs:
            mkdir(multitmp + dir + "/LiveOS/")

        intermediate = tempfile.mkdtemp() # loopdev performance is slow
                                          # copy to here first then back
                                          # to multitmp + dir which is looback also

        imgs = ("squashfs.img", "osmin.img")
        for img in imgs:
            copy(x86tmp + "/LiveOS/" + img, intermediate)
            copy(intermediate + "/" + img, multitmp + "/x86/LiveOS/")
        for img in imgs:
            copy(x64tmp + "/LiveOS/" + img, intermediate)
            copy(intermediate + "/" + img, multitmp + "/x64/LiveOS/")

        for file in os.listdir(x86tmp + "/isolinux/"):
            copy(x86tmp + "/isolinux/" + file, multitmp + "/extlinux/")

        copy(x64tmp + "/isolinux/vmlinuz0", multitmp + "/extlinux/vmlinuz1")
        copy(x64tmp + "/isolinux/initrd0.img", multitmp + "/extlinux/initrd1.img")
            

       
        uuid = getuuid(lodev(multi))

  
        config = (multitmp + "/extlinux/extlinux.conf")
        syslinux(multitmp,
                 config,
                 uuid=uuid)



        umount(x86tmp)
        umount(x64tmp)
        umount(multitmp)

        lounset(lodev(x86))
        lounset(lodev(x64))
        lounset(lodev(multi))

        shutil.rmtree(x86tmp)
        shutil.rmtree(x64tmp)
        shutil.rmtree(multitmp)
        shutil.rmtree(intermediate)   
        


        if os.path.exists(sys.argv[3]):
            os.unlink(sys.argv[3])
        move(multi, sys.argv[3])
 

    def parse(x86, x64, multi):
        for file in x86, x64:
            if os.path.exists(file):
                pass
            else:
                usage()
        if not multi:
            usage()
        setup(x86, x64, multi)





    try: 
        parse(sys.argv[1], sys.argv[2], sys.argv[3])
    except:
        usage()



        
        


if __name__ == "__main__":
    sys.exit(main())
