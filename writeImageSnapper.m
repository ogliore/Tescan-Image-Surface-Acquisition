function res=writeImageSnapper(ptsxyz,Zstage,viewfield,coordn,imagepath,imageformat)

autofocus=0;
autogain=0;
stitching=0;
snapshotsize=4; 
panoramasize=100;
panoramamaxw=1e4;
%Z=21.484375; % in mm (read off "Z" in Stage Control);
% WD=14.9333;  % in mm (read off "WD & Z" in Stage Control);
%viewfield=250;  % in *microns* (read off info panel, convert to microns)
imagebasename='Snap';

npts=size(ptsxyz,1);

fid=fopen('ImageSnapper.xml','w');

fprintf(fid,'<?xml version="1.0" encoding="utf-8" standalone="yes"?>\n');
fprintf(fid,'<ImageSnapperProject>\n');
fprintf(fid,'<Settings AutoFocus="%d" AutoGainBlack="%d" Stitching="%d" ShadingCorrection="0" AddInfobar="0" Path="%s" ImageFormat="%s" SnapshotSize="%d" PanoramaSize="%d" PanoramaMaxW="%d"/>\n',autofocus,autogain,stitching,imagepath,imageformat,snapshotsize,panoramasize,panoramamaxw);
fprintf(fid,'<Samples Count="%d">\n',npts);

formatcodex=sprintf('%%0%dd',ceil(log10(max(coordn(:,1)))));
formatcodey=sprintf('%%0%dd',ceil(log10(max(coordn(:,2)))));


for ii=1:npts
        samplenamei=[sprintf(formatcodex,coordn(ii,1)) '_' sprintf(formatcodey,coordn(ii,2))];
        fprintf(fid,['<PointSample Name="%s" Z="%s" WD="%.9f" ViewField="%.6f" Overlapping="0" ImageBaseName="%s" Pos="%.4f,%.4f"/>\n'],samplenamei,Zstage,ptsxyz(ii,3),viewfield*1e-6,imagebasename,ptsxyz(ii,1)*1e3,ptsxyz(ii,2)*1e3);
end


fprintf(fid,'</Samples>\n');
fprintf(fid,'</ImageSnapperProject>\n');

res=fclose(fid);
