#!/bin/sh
# Logout current user
USERNAME=${SUDO_USER:-$(id -u -n)}
HOMEDIR="/home/$USERNAME"

if [[ $DESKTOP_SESSION =~ ^.*openbox$ ]]; then
  openbox --exit
elif [[ $DESKTOP_SESSION =~ ^.*i3$ ]]; then
  i3-msg exit
elif [[ $DESKTOP_SESSION =~ ^.*qtile$ ]]; then
  /usr/bin/python "qtile-logoff"
elif [[ $DESKTOP_SESSION =~ ^.*fluxbox$ ]]; then
  killall fluxbox
elif [[ $DESKTOP_SESSION =~ ^.*bspwm$ ]]; then
  bspc quit 1
else
  /usr/bin/loginctl terminate-user $USERNAME
fi
