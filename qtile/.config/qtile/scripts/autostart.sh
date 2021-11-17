#!/bin/sh

polkit-dumb-agent &
./setWallpaper.sh &
picom --experimental-backends &
dunst &
numlockx on &
emacs --daemon
xmodmap ~/.Xmodmap
