#!/bin/sh

# $1 = directory
# $2 = overlap of tiles (in percent, e.g. 10)
# $3 = output tile size in mosaic (in pixels, e.g. 100)
# $4 = extension (e.g. jpg)
# $5 = output file (e.g. ~/Documents/panorama.jpg)
# montage memory issues: https://github.com/ImageMagick/ImageMagick/issues/396

STARTTIME=`date +%s`

INCREASEOVERLAPFAC=1.21
INCREASEOVERLAPFACSTRIP=1
#0.18

MONTAGEOVERLAP=$(echo "scale=2 ; $INCREASEOVERLAPFAC*$3*($2 / 2)/100" | bc)
MONTAGEOVERLAPSTRIP=$(echo "scale=2 ; $INCREASEOVERLAPFACSTRIP*$3*($2 / 2)/100" | bc)

cd $1

FIRSTROW=$(ls *.$4 | head -1 | awk -v FS="(_|\.)" '{print $2}')
MONTAGEFORMATCODE=%0${#FIRSTROW}d

find -regex '\./[0-9_]+' -type d -exec mv -n -- {}/Snap_1.$4 {}.$4 2>/dev/null \;
find -regex '\./[0-9_]+' -type d -exec mv -n -- {}/Snap_1-$4.hdr {}-$4.hdr 2>/dev/null \; -empty -delete

NX=$(ls -l *_$FIRSTROW.$4 | wc -l)

mkdir -p $MAGICK_TEMPORARY_PATH/stripimages_

for i in $( seq 1 $NX )
do
echo $(printf "%03d" $i)
montage -tile x1 -geometry $3x-$MONTAGEOVERLAP  $(ls -1 *_$(printf $MONTAGEFORMATCODE $i).$4 | sort -r) $MAGICK_TEMPORARY_PATH/stripimages_/strip$(printf $MONTAGEFORMATCODE $i).$4
done

montage -tile 1x -geometry 1x1+0-$MONTAGEOVERLAPSTRIP'<' $MAGICK_TEMPORARY_PATH/stripimages_/strip*.$4 $5

rm -rf $MAGICK_TEMPORARY_PATH/stripimages_

ENDTIME=`date +%s`

# To create DeepZoom files for use with OpenSeaDragon:
# vips dzsave Renazzo_Panorama.jpg RenazzoN1126 --suffix .jpg[Q=100]

echo Run time = $((ENDTIME-STARTTIME)) seconds

