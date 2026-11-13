#!/usr/bin/env bash
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
DEST="$ROOT/piano/assets"
ARCHIVE="$DEST/upright-piano-kw.7z"
mkdir -p "$DEST"
URL="https://freepats.zenvoid.org/Piano/UprightPianoKW/UprightPianoKW-SF2-20220221.7z"
if [[ ! -f "$DEST/upright_piano_kw.sf2" ]]; then
  command -v 7z >/dev/null || { echo "7z/p7zip is required" >&2; exit 1; }
  curl -fL "$URL" -o "$ARCHIVE"
  7z x -y -o"$DEST/extracted" "$ARCHIVE" >/dev/null
  SF2="$(find "$DEST/extracted" -type f -iname '*.sf2' -print -quit)"
  [[ -n "$SF2" ]] || { echo "No SF2 file found in the downloaded archive" >&2; exit 1; }
  cp "$SF2" "$DEST/upright_piano_kw.sf2"
  rm -rf "$DEST/extracted" "$ARCHIVE"
fi
echo "SoundFont ready: $DEST/upright_piano_kw.sf2"
