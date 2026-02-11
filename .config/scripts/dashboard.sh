#!/bin/bash

BTOP_WIDTH=1400
BTOP_HEIGHT=900

NMTUI_WIDTH=800
NMTUI_HEIGHT=600

tput civis

resize_window() {
    local width=$1
    local height=$2
    niri msg action set-window-width "$width" > /dev/null 2>&1
    niri msg action set-window-height "$height" > /dev/null 2>&1
    niri msg action center-window > /dev/null 2>&1
}

print_bottom() {
    tput cup $(($(tput lines) - 1)) 0
    echo -ne "$1"
    tput el
}

while true; do
    clear
    fastfetch -c dashboard

    print_bottom "\033[1;30m[b]top  [n]mtui  [i]dle  [s]hutdown  [q]uit\033[0m"

    read -n 1 -s key

    case "$key" in
        w|W|q|Q)
            break
            ;;

        s|S)
            print_bottom "\033[1;31mPress 's' again to confirm shutdown...\033[0m"
            read -n 1 -s confirm
            if [[ "$confirm" == "s" || "$confirm" == "S" ]]; then
                systemctl poweroff
                break
            fi
            ;;

        i|I)
            print_bottom "\033[1;33mPress 'i' again to sleep...\033[0m"
            read -n 1 -s confirm
            if [[ "$confirm" == "i" || "$confirm" == "I" ]]; then
                systemctl suspend
                break
            fi
            ;;

        b|B)
            resize_window $BTOP_WIDTH $BTOP_HEIGHT
            exec btop
            ;;

        n|N)
            resize_window $NMTUI_WIDTH $NMTUI_HEIGHT
            exec nmtui
            ;;
    esac
done
