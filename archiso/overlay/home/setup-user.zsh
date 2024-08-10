#!/bin/zsh

git clone https://aur.archlinux.org/yay.git
cd yay
makepkg -si
cd ..

yay -S oh-my-zsh fzf
git clone https://github.com/hsaunders1904/pyautoenv.git ~/.oh-my-zsh/custom/plugins/pyautoenv/

