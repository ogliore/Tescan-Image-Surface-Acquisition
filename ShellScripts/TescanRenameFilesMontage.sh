#!/bin/sh

# $1 = directory
# $2 = horizontal overlap of tiles (in percent, e.g. 10)
# $3 = vertical overlap of tiles (in percent, e.g. 10)
# $4 = output tile size in mosaic (in pixels, e.g. 100)
# $5 = extension (e.g. jpg)
# $6 = output file (e.g. ~/Documents/panorama.jpg)
# montage memory issues: https://github.com/ImageMagick/ImageMagick/issues/396
# First test this script on four images from the middle of the panorama. Must rename the images to 001_001.jpg, 001_002.jpg, 002_001.jpg, 002_002.jpg. Adjust $2 and $3 until blend is good.
# Max supported dimension for imagemagick is 65500 pixels
# nm/pixel for panorama will be: (original image nm/pixel) * (original-image-size/$4)
# For example if original image 1536x1536 pixel image is 100 nm/pixel (in hdr file) and tile size is 150:
# Panorama will be 100 * 1536/250 = 614.4 nm/pixel
# ./TescanRenameFilesMontage.sh ~/Data/Tescan/Ryan/Kapoeta-67331/Mosaic02 9.1 7.6 250 jpg ~/Documents/KapoetaPano.jpg

STARTTIME=`date +%s`

#INCREASEOVERLAPFAC=1.21
#INCREASEOVERLAPFACSTRIP=1
#0.18

MONTAGEOVERLAP=$(echo "scale=2 ; $4*($2 / 2)/100" | bc)
MONTAGEOVERLAPSTRIP=$(echo "scale=2 ; $4*($3 / 2)/100" | bc)

cd $1

FIRSTROW=$(ls *.$5 | head -1 | awk -v FS="(_|\.)" '{print $2}')
MONTAGEFORMATCODE=%0${#FIRSTROW}d

find -regex '\./[0-9_]+' -type d -exec mv -n -- {}/Snap_1.$5 {}.$5 2>/dev/null \;
find -regex '\./[0-9_]+' -type d -exec mv -n -- {}/Snap_1-$5.hdr {}-$5.hdr 2>/dev/null \; -empty -delete

NX=$(ls -1 ${FIRSTROW}_*.$5 | wc -l)

#echo $FIRSTROW first row
echo $NX columns

mkdir -p $MAGICK_TEMPORARY_PATH/stripimages_

for i in $( seq 1 $NX )
do
echo $(printf "%03d" $i)
montage -tile x1 -geometry $4x-$MONTAGEOVERLAP  $(ls -1 *_$(printf $MONTAGEFORMATCODE $i).$5 | sort -r) $MAGICK_TEMPORARY_PATH/stripimages_/strip$(printf $MONTAGEFORMATCODE $i).$5
done

montage -tile 1x -geometry 1x1+0-$MONTAGEOVERLAPSTRIP'<' $MAGICK_TEMPORARY_PATH/stripimages_/strip*.$5 -quality 100 $6

rm -rf $MAGICK_TEMPORARY_PATH/stripimages_

ENDTIME=`date +%s`

# To create DeepZoom files for use with OpenSeaDragon:
# vips dzsave Renazzo_Panorama.jpg RenazzoN1126 --suffix .jpg[Q=100]

echo Run time = $((ENDTIME-STARTTIME)) seconds

