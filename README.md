# Tescan-Image-Surface-Acquisition
Software to efficiently acquire electron images from a Tescan scanning electron microscope

Instruments and Software:
This software was developed on a Tescan MIRA3 FEG-SEM using Tescan Control Software Version 4.2.27.0 build 1382 (64bit). The add-on package “Image Snapper” is required. Matlab (2018b), Python (3.6), and ImageMagick are also required.

Description of Problem:
We wish to acquire BSE or SE images on a sample that has some slight tilt. The magnitude of height differences from one end of an inch-wide sample to the other is much greater than the depth of focus of the electron image (typically ~10 microns). So this makes it impossible to acquire thousands of high-resolution images (FOV of 50 microns, 1536x1536 pixels) across an inch-sized sample without using autofocus. Autofocus greatly slows down the image acquisition, and does not find the focus about ~10% of the time (more or less) on the Tescan. 

Solution:
The solution we’ve developed is to acquire a set of low-resolution images with AutoFocus turned on, which will give us a “focus map” of the sample, in terms of the working distance. Then we fit a 2-D surface to these values, write out an Image Snapper XML file at the required locations for the high-res imaging, and collect the images quickly with autofocus turned off.

Challenges:
1) To change the working-distance for each image, ImageSnapper requires that each image be acquired as a separate “Sample”. This makes for a large number of directories and does not allow for stitching within the Tescan software. Solution: We move and rename all acquired image with a simply bash script, and stitch the images manually (without correlation matching) using “montage” (ImageMagick).

2) The Z stage value written out in the hdr file does not contain enough digits. Image Snapper will interpret this less-precise Z stage value as a different Z, move the stage a little bit, which ruins the focus height for all the images. Solution: Acquire the true Z stage value via a Shark SEM python script.

Work Flow:
1) Mount sample and tune SEM.
2) Acquire a set of focus map images via ImageSnapper at the appropriate WD & Z values
3) Save this focus map ImageSnapper XML file and enter its filename into "TescanImageSnapper.m"
4) Run TescanImageSnapper.m (Matlab script) on the .hdr files obtained in (1) using the Z stage value obtained in (2). This script will write ImageSnapper.xml
5) Load ImageSnapper.xml into Image Snapper, change relevant Image Snapper parameters (Auto Brightness / Contrast, Image Size, etc)
6) Run ImageSnapper
7) Run TescanRenameFilesMontage.sh on the folder acquired in (6) to rename/move files and create the montage
