# Copyright (c) 2010 Aldo Cortesi
# Copyright (c) 2010, 2014 dequis
# Copyright (c) 2012 Randall Ma
# Copyright (c) 2012-2014 Tycho Andersen
# Copyright (c) 2012 Craig Barnes
# Copyright (c) 2013 horsik
# Copyright (c) 2013 Tao Sauvage
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in
# all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.

import os
import subprocess
import socket
import owm
import re
from typing import List  # noqa: F401

from libqtile import bar, layout, widget, hook
from libqtile.config import Click, Drag, Group, Key, Match, Screen
from libqtile.lazy import lazy

mod = "mod4"
terminal = "kitty"

home = os.path.expanduser("~")

# Load script to read colors from pywal
import colors
color = colors.colors

def window_to_prev_group(qtile):
    if qtile.currentWindow is not None:
        i = qtile.groups.index(qtile.currentGroup)
        qtile.currentWindow.togroup(qtile.groups[i - 1].name)

def window_to_next_group(qtile):
    if qtile.currentWindow is not None:
        i = qtile.groups.index(qtile.currentGroup)
        qtile.currentWindow.togroup(qtile.groups[i + 1].name)

def window_to_previous_screen(qtile):
    i = qtile.screens.index(qtile.current_screen)
    if i != 0:
        i = i - 1
    else:
        i = len(qtile.screens) - 1
    group = qtile.screens[i].group.name
    qtile.current_window.togroup(group)
    qtile.focus_screen(i)

def window_to_next_screen(qtile):
    i = qtile.screens.index(qtile.current_screen)
    if i + 1 != len(qtile.screens):
        i = i + 1
    else:
        i = 0
    group = qtile.screens[i].group.name
    qtile.current_window.togroup(group)
    qtile.focus_screen(i)

keys = [
    # Switch between windows in current stack pane
    Key([mod], "j", lazy.layout.down()),
    Key([mod], "k", lazy.layout.up()),
    Key([mod], "h", lazy.layout.left()),
    Key([mod], "l", lazy.layout.right()),

    Key([mod], "Down", lazy.layout.down()),
    Key([mod], "Up", lazy.layout.up()),
    Key([mod], "Left", lazy.layout.left()),
    Key([mod], "Right", lazy.layout.right()),

    # Move windows up or down in current stack
    Key([mod, "control"], "j",
        lazy.layout.shuffle_down(),
        lazy.layout.rotate()),
    Key([mod, "control"], "k",
        lazy.layout.shuffle_up(),
        lazy.layout.rotate()),

    # Resize Windows
    Key([mod, "control"], "i", lazy.layout.shrink()),
    Key([mod, "control"], "o", lazy.layout.grow()),

    # Move focus to different monitor
    Key([mod], "period", lazy.prev_screen()),
    Key([mod], "comma", lazy.next_screen()),

    # Move windows to different screens
    Key([mod, "control"], "period", lazy.function(window_to_previous_screen)),
    Key([mod, "control"], "comma", lazy.function(window_to_next_screen)),

    # Switch window focus to other pane(s) of stack
    Key([mod], "n", lazy.layout.next()),

    # Toggle Floating
    Key([mod], "t", lazy.window.toggle_floating()),

    # Swap panes of split stack
    Key([mod], "r", lazy.layout.rotate()),

    # Toggle between different layouts as defined below
    Key([mod], "Tab", lazy.next_layout()),

    # Restart Qtile
    Key([mod, "shift"], "r", lazy.restart()),

    # Shutdown Qtile
    Key([mod, "control"], "q", lazy.shutdown()),

    # Power Menu
    Key([mod, "shift"], "q", lazy.spawn([home + '/.config/rofi/applets/menu/powermenu.sh'])),

    # Volume Keys
    Key([], "XF86AudioMute", lazy.spawn("pactl set-sink-mute @DEFAULT_SINK@ toggle")),
    Key([], "XF86AudioLowerVolume", lazy.spawn("pactl set-sink-volume @DEFAULT_SINK@ -5%")),
    Key([], "XF86AudioRaiseVolume", lazy.spawn("pactl set-sink-volume @DEFAULT_SINK@ +5%")),

    # Media Keys
    Key([], "XF86AudioPlay", lazy.spawn("playerctl play-pause")),
    Key([], "XF86AudioPause", lazy.spawn("playerctl play-pause")),
    Key([], "XF86AudioNext", lazy.spawn("playerctl next")),
    Key([], "XF86AudioPrev", lazy.spawn("playerctl previous")),

    # Print Screen
    Key([], "Print", lazy.spawn("gnome-screenshot -i")),
    Key([mod,], "Print", lazy.spawn("gnome-screenshot -a")),

    # Kill Window
    Key([mod,], "q", lazy.window.kill()),

    # Launch Terminal
    Key([mod], "Return", lazy.spawn(terminal)),

    # Launch File Manager
    Key([mod], "e", lazy.spawn("nautilus")),

    # Launch Internet Browser
    Key([mod], 'b', lazy.spawn("firefox")),

    # Launch Rofi App Launcher
    Key([mod], "space", lazy.spawn([home + '/.config/qtile/scripts/rofi-dmenu.sh'])),
    #Key([mod, "control"], "space", lazy.spawn([home + '/.config/qtile/scripts/rofi-center.sh'])),

    # Rofi Notification Center
    # Key([mod], 'd', lazy.spawn([home + '/.config/dunst/scripts/rofi_notif_center.sh'])),
]

# Define Groups
group_names=[
        (" 1 ", {}),
        (" 2 ", {}),
        (" 3 ", { }),
        (" 4 ", { }),
        (" 5 ", { }),
        (" 6 ", { }),
        (" 7 ", { }),
        (" 8 ", {}),
        (" 9 ", {}),
    ]

groups = [Group(name, **kwargs) for name, kwargs in group_names]
for i, (name, kwargs) in enumerate(group_names, 1):
        keys.append(Key([mod], str(i), lazy.group[name].toscreen())),
        keys.append(Key([mod, "shift"], str(i), lazy.window.togroup(name))),

layout_theme = {
        "border_width": 2,
        "border_focus": color[6],
        "border_normal": color[1],
        }

layouts = [
    layout.MonadTall(
        **layout_theme,
         margin = 10,
        name = "Tall",
        ),
    layout.MonadWide(
        **layout_theme,
         margin = 10,
        name = "Wide"),
    layout.Max(
        **layout_theme,
        margin = 10,
        name = "Max",
        ),
    layout.Stack(
        **layout_theme,
        margin = 10,
        num_stacks=2),
    # Try more layouts by unleashing below layouts.
    # layout.Bsp(
    #     name = "BSP",
    #     ),
    # layout.Columns(
    #     name = "Columns",
    #     ),
    # layout.Matrix(
    #     name = "Matrix",
    #     ),
    #     layout.RatioTile(),
    # layout.Tile(
    #     name = "Tile",
    #     ),
    # layout.TreeTab(
    #     name = "Tree",
    #     ),
    # layout.VerticalTile(
    #     name = "VTile",
    #     ),
    layout.Zoomy(
        name = "Zoomy",
        ),
]

widget_defaults = dict(
    font='Fira Sans',
    fontsize=14,
    background = color[0],
    foreground = color[15],
    opacity = 1,
    padding = 5
)
extension_defaults = widget_defaults.copy()

screens = [
    Screen(
        bottom=bar.Bar(
            [
               widget.Sep(
                   linewidth = 0,
                   ),
               widget.GroupBox(
                   rounded = False,
                   linewidth = 0,
                   active = color[15],
                   inactive = color[8],
                   highlight_method = 'line',
                   highlight_color = color[6],
                   this_current_screen_border = color[6],
                   this_screen_border = color[1],
                   other_current_screen_border = color[8],
                   other_screen_border = color[8],
                   urgent_border = color[5],

                   ),
               widget.Sep(
                   linewidth = 0,
                   ),
               widget.WindowName(),
               widget.Spacer(),
               widget.Systray(
               ),
               widget.Sep(
                   linewidth = 0,
               ),
               # owm.OpenWeatherMap(
               #     api_key="",
               #     latitude=0,
               #     longitude=0,
               # ),
               widget.Clock(
                   format='%a, %b %d | %I:%M %p',
                   ),
               widget.Volume(
                   ),
               widget.CurrentLayout(
                   )
                ],
            28,
        ),
    ),
    Screen(
        bottom=bar.Bar(
            [
               widget.Sep(
                   linewidth = 0,
                   ),
               widget.GroupBox(
                   rounded = False,
                   linewidth = 0,
                   active = color[15],
                   inactive = color[8],
                   highlight_method = 'line',
                   highlight_color = color[6],
                   this_current_screen_border = color[6],
                   this_screen_border = color[1],
                   other_current_screen_border = color[8],
                   other_screen_border = color[8],
                   urgent_border = color[5],
                   ),
               widget.Sep(
                   linewidth = 0,
                   ),
               widget.WindowName(),
               widget.Spacer(),
               widget.Clock(
                   format='%I:%M %p',
                   foreground = color[15],
                   ),
               widget.CurrentLayout(
                   foreground = color[15],
                   ),

            ],
            28,
        ),
    ),
    Screen(
        bottom=bar.Bar(
            [
               widget.Sep(
                   linewidth = 0,
                   ),
               widget.GroupBox(
                   rounded = False,
                   linewidth = 0,
                   active = color[15],
                   inactive = color[8],
                   highlight_method = 'line',
                   highlight_color = color[6],
                   this_current_screen_border = color[6],
                   this_screen_border = color[1],
                   other_current_screen_border = color[8],
                   other_screen_border = color[8],
                   urgent_border = color[5],
                   ),
               widget.Sep(
                   linewidth = 0,
                   ),
               widget.WindowName(),
               widget.Spacer(),
               widget.Clock(
                   format='%I:%M %p',
                   padding = 10,
                   foreground = color[15],
                   ),
               widget.CurrentLayout(
                   foreground = color[15],
                   ),

            ],
            28,
        ),

    )
]

# Drag floating layouts.
mouse = [
    Drag([mod], "Button1", lazy.window.set_position_floating(),
         start=lazy.window.get_position()),
    Drag([mod], "Button3", lazy.window.set_size_floating(),
         start=lazy.window.get_size()),
    Click([mod], "Button2", lazy.window.bring_to_front())
]


dgroups_key_binder = None
dgroups_app_rules = []  # type: List
main = None  # WARNING: this is deprecated and will be removed soon
follow_mouse_focus = True
bring_front_click = False
cursor_warp = False
floating_layout = layout.Floating(float_rules=[
    # Run the utility of `xprop` to see the wm class and name of an X client.
    Match(wm_class='confirm'),
    Match(wm_class='dialog'),
    Match(wm_class='download'),
    Match(wm_class='error'),
    Match(wm_class='file_progress'),
    Match(wm_class='notification'),
    Match(wm_class='splash'),
    Match(wm_class='toolbar'),
    Match(wm_class='confirmreset'),
    Match(wm_class='makebranch'),
    Match(wm_class='maketag'),
    Match(wm_class='ssh-askpass'),
    Match(wm_class='Gnome-screenshot'),
    Match(wm_class='Godot_Engine'),
    Match(wm_class='matplotlib'),
    Match(wm_class='reaper'),
    Match(title='branchdialog'),
    Match(title='pinentry'),
])
auto_fullscreen = True
focus_on_window_activation = "smart"
reconfigure_screens = True


# Autostart
@hook.subscribe.startup
def autostart():
    subprocess.call([home + '/.config/qtile/scripts/autostart.sh']),
    subprocess.call([home + '/.config/qtile/scripts/setWallpaper.sh']),

# XXX: Gasp! We're lying here. In fact, nobody really uses or cares about this
# string besides java UI toolkits; you can see several discussions on the
# mailing lists, GitHub issues, and other WM documentation that suggest setting
# this string if your java app doesn't work correctly. We may as well just lie
# and say that we're a working one by default.
#
# We choose LG3D to maximize irony: it is a 3D non-reparenting WM written in
# java that happens to be on java's whitelist.
wmname = "LG3D"

# floating_layout = layout.Floating(float_rules=[
#     # Run the utility of `xprop` to see the wm class and name of an X client.
#     *layout.Floating.default_float_rules,
#     Match(wm_class='confirmreset'),  # gitk
#     Match(wm_class='makebranch'),  # gitk
#     Match(wm_class='maketag'),  # gitk
#     Match(wm_class='ssh-askpass'),  # ssh-askpass
#     Match(title='branchdialog'),  # gitk
#     Match(title='pinentry'),  # GPG key password entry
# ])
# reconfigure_screens = True
