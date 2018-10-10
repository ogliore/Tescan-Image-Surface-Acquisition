#!/bin/sh

# $1 = directory
# $2 = overlap of tiles (in percent, e.g. 10)
# $3 = output tile size in mosaic (in pixels, e.g. 100)
# $4 = extension (e.g. jpg)
# $5 = output file (e.g. ~/Documents/panorama.jpg)

STARTTIME=`date +%s`

MONTAGEOVERLAP=$(echo "scale=2 ; $3*($2 / 2)/100" | bc)


cd $1

# TILETEXT=$(ls [0-9]*.jpg | tail -1 | cut -f 1 -d '.' | tr _ x)
# TILETEXT=$(ls 001_[0-9]*.jpg | tail -1 | cut -f 1 -d '.' | tr _ x)
NX=$(ls -l *_001.$4 | wc -l)
#echo $TITLETEXT
find -regex '\./[0-9_]+' -type d -exec mv -n -- {}/Snap_1.$4 {}.$4 2>/dev/null \;
find -regex '\./[0-9_]+' -type d -exec mv -n -- {}/Snap_1-$4.hdr {}-$4.hdr 2>/dev/null \; -empty -delete
#rm -f panorama.jpg
#montage *.jpg -limit area 0 -limit memory 0 -limit map 0 -rotate -90 -border -$2% -geometry $3x -tile $TILETEXT  panorama.jpg
mkdir -p $MAGICK_TEMPORARY_PATH/stripimages_
for i in $( seq 1 $NX )
do
echo $(printf "%03d" $i)
montage -rotate -90 -geometry $3x-$MONTAGEOVERLAP -tile x1 $(printf "%03d" $i)_*.$4 $MAGICK_TEMPORARY_PATH/stripimages_/strip$(printf "%03d" $i).$4
done
montage -geometry 1x1+0-$MONTAGEOVERLAP'<' -tile 1x $MAGICK_TEMPORARY_PATH/stripimages_/strip*.$4 $5
rm -rf $MAGICK_TEMPORARY_PATH/stripimages_

ENDTIME=`date +%s`

echo Run time = $((ENDTIME-STARTTIME)) seconds

