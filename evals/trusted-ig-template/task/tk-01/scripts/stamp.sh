#!/bin/sh
# stamp.sh VERSION FILE: writes the footer stamp
printf '<span class="stamp">Version %s</span>\n' "$1" > "$2"
