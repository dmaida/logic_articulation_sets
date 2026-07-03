#!/usr/bin/env bash
# Copy generated articulation sets into Logic Pro's user library.
# Restart Logic afterwards, then assign a set from a track's Articulation Set menu.
set -euo pipefail

SRC="$(cd "$(dirname "$0")" && pwd)/sets"
DST="$HOME/Music/Audio Music Apps/Articulation Settings"

if [ ! -d "$SRC" ] || ! ls "$SRC"/*.plist >/dev/null 2>&1; then
  echo "No .plist files in $SRC — run: python3 gen_artic.py" >&2
  exit 1
fi

mkdir -p "$DST"
count=0
for f in "$SRC"/*.plist; do
  cp "$f" "$DST/"
  count=$((count + 1))
done
echo "Installed $count articulation set(s) to:"
echo "  $DST"
echo "Restart Logic Pro to pick them up."
