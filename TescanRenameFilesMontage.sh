#!/bin/sh

# $1 = directory
# $2 = overlap of tiles (in percent, e.g. 10)
# $3 = output tile size in mosaic (in pixels, e.g. 500)

cd $1

TILETEXT=$(ls [0-9]*.jpg | tail -1 | cut -f 1 -d '.' | tr _ x)

find -regex '\./[0-9_]+' -type d -exec mv -n -- {}/Snap_1.jpg {}.jpg 2>/dev/null \;
find -regex '\./[0-9_]+' -type d -exec mv -n -- {}/Snap_1-jpg.hdr {}-jpg.hdr 2>/dev/null \; -empty -delete

montage -rotate -90 -border -$2% -geometry $3x -tile $TILETEXT *jpg panorama.jpg
convert panorama.jpg -rotate +90 panorama.jpg


