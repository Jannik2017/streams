#!/bin/zsh

ln -sf /usr/share/zoneinfo/Europe/Berlin /etc/localtime
sed -i 's/#de_DE.UTF-8/de_DE.UTF-8/' /etc/locale.gen
sed -i 's/#en_US.UTF-8/en_US.UTF-8/' /etc/locale.gen

locale-gen

echo "LAN=de_DE.UTF-8" > /etc/locale.conf
echo "LC_ALL=C" >> /etc/locale.conf

echo "KEYMAP=de-latin1" > /etc/vconsole.conf

echo "total-recall" > /etc/hostname

sed -i 's/^MODULES=()/MODULES=(zfs)/' /etc/mkinitcpio.conf
sed -i 's/filesystems fsck/zfs filesystems/' /etc/mkinitcpio.conf

sleep 1

for user in /home/*
do 
    useradd -m $(basename ${user})
    chown -R $(basename ${user}) ${user}
    # soll der user selber ausführen bis sudo passt
    #sudo -iu $(basename ${user}) zsh /home/setup-user.zsh
done

chmod -R g-rwx o-rwx /home/*
usermod -aG wheel aibix

systemctl enable dhclient@enp6s18
systemctl enable sshd
systemctl enable zfs.target
systemctl enable zfs-import-cache
systemctl enable zfs-mount
systemctl enable zfs-import.target
systemctl enable qemu-guest-agent

zgenhostid $(hostid)

bootctl install

mkinitcpio -P

zpool set cachefile=/etc/zfs/zpool.cache zroot

