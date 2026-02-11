# Dotfiles

My personal configuration files for my arch setup.

## What's included

- **[niri](https://github.com/YaLTeR/niri)** - Scrollable-tiling Wayland compositor
- **[waybar](https://github.com/Alexays/Waybar)** - Wayland status bar (no longer used)
- **[foot](https://codeberg.org/dnkl/foot)** - Fast, lightweight and minimalistic Wayland terminal emulator
- **[fastfetch](https://github.com/fastfetch-cli/fastfetch)** - System information tool
- **[swaylock](https://github.com/swaywm/swaylock)** - Screen locker for Wayland
- **[MPD](https://github.com/MusicPlayerDaemon/MPD)** - Music Player Daemon
- **[thunar](https://docs.xfce.org/xfce/thunar/start)** - Modern file manager
- **[fuzzel](https://codeberg.org/dnkl/fuzzel)** - App launcher and fuzzy finder for Wayland

## Screenshot
<img width="1920" height="1200" alt="Screenshot" src="https://raw.githubusercontent.com/idefasoft/dotfiles/main/screenshot.jpeg" />

## Custom scripts

### dashboard.sh:
`~/.config/scripts/dashboard.sh` - A shell script that:
- Replaces waybar by displaying useful information using `fastfetch`.
- Allows launching `btop` or `nmtui` directly.
- Provides options to shutdown or suspend the PC.

### tracker.py:
`~/.config/scripts/tracker.py` - A python script that:
- Records applications used in real time.
- Lets me later visualize usage statistics with `~/.config/scripts/viewer.py`.

### Old wallpaper changer:
`~/.config/scripts/wallpaper_old.py` - A python script that:
- Sets a random wallpaper from a specified directory
- Automatically adapts niri and waybar themes based on the wallpaper colors
- Inspired by [pywal](https://github.com/dylanaraps/pywal)

## Installation

Clone this repository and copy the `.config` folder to your home directory.

## Changelog

### Between August 21, 2025 and February 11, 2026

I realized that I was barely using waybar, except to check the time or battery level. So I removed it to save space and added a special shortcut that launches a floating terminal displaying all the information I need. I also added another python program that runs permanently in the background and tracks my application usage (in terms of time). I like stats :).

### August 21, 2025

My first config. At that time, I was using niri as the compositor, waybar as the status bar, foot as the terminal, fuzzel as the launcher, and thunar as the file explorer. A python program changed the wallpaper every 10 minutes using swww and automatically adapted certain colors using the `fast_colorthief` module.

## ⚠️ Warning

The keyboard shortcuts in the configuration are set up for an AZERTY keyboard layout. Some shortcuts won't work correctly on QWERTY keyboards.
