#!/bin/sh
# Export the deck to PDF and to 200 dpi page images, so the layout can be judged from pixels
# rather than from source. There is no LibreOffice on this machine, so the export is driven
# through the installed PowerPoint via AppleScript; it opens and closes the file and quits.
#
# Usage: sh render.sh          (from talk/pptx, or anywhere -- paths are resolved here)
set -e
DIR=$(CDPATH= cd -- "$(dirname -- "$0")" && pwd)
PPTX="$DIR/orbit_evidence_talk.pptx"
PDF="$DIR/orbit_evidence_talk.pdf"

[ -f "$PPTX" ] || { echo "render: $PPTX missing -- run build_deck.py first" >&2; exit 1; }

rm -f "$PDF" "$DIR"/pg-*.png

osascript >/dev/null <<AS
tell application "Microsoft PowerPoint"
  activate
  open POSIX file "$PPTX"
  delay 2
  save active presentation in POSIX file "$PDF" as save as PDF
  delay 1
  close active presentation saving no
  quit
end tell
AS

[ -f "$PDF" ] || { echo "render: PowerPoint produced no PDF" >&2; exit 1; }
pdftoppm -r 200 -png "$PDF" "$DIR/pg"
echo "render: $(ls -1 "$DIR"/pg-*.png | wc -l | tr -d ' ') page image(s) at 200 dpi"
