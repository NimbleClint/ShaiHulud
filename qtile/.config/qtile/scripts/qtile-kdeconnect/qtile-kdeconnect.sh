#!/usr/bin/env bash

# Icons shown in qtile
PHONE=''

show_devices (){
    devices=""
    for device in $(qdbus --literal org.kde.kdeconnect /modules/kdeconnect org.kde.kdeconnect.daemon.devices); do
        deviceid=$(echo "$device" | awk -F'["|"]' '{print $2}')
        isreach="$(qdbus org.kde.kdeconnect "/modules/kdeconnect/devices/$deviceid" org.kde.kdeconnect.device.isReachable)"
        istrust="$(qdbus org.kde.kdeconnect "/modules/kdeconnect/devices/$deviceid" org.kde.kdeconnect.device.isTrusted)"
        bar=""
        if [ "$isreach" = "true" ] && [ "$istrust" = "true" ]
        then
            bar="$(get_icon 1)"
        elif [ "$isreach" = "false" ] && [ "$istrust" = "true" ]
        then
            bar="$(get_icon 2)"
        else
            bar="$(get_icon 3)"
        fi
    done
    echo "$bar"
}

get_icon () {
    case $1 in
    "1")     ICON="$PHONE" ;;
    "2")     ICON="$PHONE" ;;
    "3")     ICON="$PHONE" ;;
    esac
    echo $ICON
}
show_devices
