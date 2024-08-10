#!/bin/zsh

# install zfs in archiso
curl -s https://raw.githubusercontent.com/eoli3n/archiso-zfs/master/init | bash

# umount boot
umount /mnt/boot
umount -R /mnt

# destroy zpool (if available)
ZPOOL=$(zpool list | awk '/ONLINE/ {print $1}')
if [[ $ZPOOL ]] ; then ; zfs umount -a ; zpool destroy $ZPOOL ; fi

# make partitions /dev/sd{a..c}
for p in {a..c} ; do sfdisk --force /dev/sd${p} < installarch_partitions.sfdisk ; sleep 1 ; done

# make zfs pool command
MKZFS="zpool create -f -o ashift=12 -O acltype=posixacl -O relatime=on -O xattr=sa -O dnodesize=legacy -O normalization=formD -O mountpoint=none -O canmount=off -O devices=off -R /mnt zroot raidz1 "

# generate command wirh partuuids
for id in $(ls -l /dev/disk/by-partuuid | awk '/2$/ {print $9}') ; do MKZFS="$MKZFS /dev/disk/by-partuuid/$id" ; done

echo $MKZFS
ls -l /dev/disk/by-partuuid | grep 2$
eval ${MKZFS}
sleep 1
zfs list
zpool status

# create zfs datasets
zfs create -o mountpoint=none zroot/data
zfs create -o mountpoint=none zroot/ROOT
zfs create -o mountpoint=/ -o canmount=noauto zroot/ROOT/default
zfs create -o mountpoint=/home zroot/data/home
zfs create -o mountpoint=/root zroot/data/home/root

# create zfs system datasets
zfs create -o mountpoint=/var -o canmount=off     zroot/var
zfs create                                        zroot/var/log
zfs create -o mountpoint=/var/lib -o canmount=off zroot/var/lib
zfs create                                        zroot/var/lib/libvirt
zfs create                                        zroot/var/lib/docker

# export/import zfs pool (seems necessary?)
zpool export zroot
sleep 1
zpool import -d /dev/disk/by-partuuid -R /mnt zroot -N
sleep 1

zfs list

zfs mount zroot/ROOT/default
zfs mount -a

zpool set bootfs=zroot/ROOT/default zroot
zpool set cachefile=/etc/zfs/zpool.cache zroot
sleep 1
mkdir -p /mnt/etc/zfs
cp /etc/zfs/zpool.cache /mnt/etc/zfs/zpool.cache
sleep -1

# mount boot
mkdir /mnt/boot
mount /dev/sda1 /mnt/boot
sleep 1

# genfstab
genfstab -U /mnt >> /mnt/etc/fstab.tmp
grep "boot" /mnt/etc/fstab.tmp > /mnt/etc/fstab

# candy
sed -i -e 's/#ParallelDownloads/ParallelDownloads/' -e 's/#ILoveCandy/ILoveCandy/' /etc/pacman.conf

# install base system
pacstrap -K /mnt base linux-lts linux-lts-headers base-devel curl wget cmake tmux zsh mc zfs-dkms zfs-utils dhclient openssh man-db man-pages texinfo nano qemu-guest-agent git

cp -r /root/overlay/* /mnt/
chown -R root:root /mnt/etc
chown -R root:root /mnt/boot

chmod 750 /mnt/etc/sudoers.d

cp installarch_chroot.zsh /mnt/root/
arch-chroot /mnt zsh /root/installarch_chroot.zsh

sleep 1
umount -R /mnt

echo "fertig"