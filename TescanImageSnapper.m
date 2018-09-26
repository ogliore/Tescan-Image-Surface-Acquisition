clear;
close all;

% If Zstage is not *exactly* as the SEM thinks it is, it will move the
% stage and compromise the focus of the sample. We need to give the xml
% file the exact same Z value so that the stage will not move. The value
% recorded in the .hdr files, or shown in Stage Control, does not contain
% enough digits! The value given by Shark SEM is enough:
Zstage='4.02625'; % From GetStageZ.py, save as string with same digits as Python gives

docuts=1;% Switch to cut by WD (before outlier removal)

dooutliers=1; % Switch to remove outliers

doremovepoints=0; % Switch to particular points (after the two prior cuts)

surfaceshape='poly22'; % poly11=plane, poly22=surface quadratic

fov=50; % in microns

overlap_fraction=0.05; % 10% = 0.1

focusimagedir='G:\Ryan\Genesis_50684.10\Sample2\';

imagepath='G:\Ryan\Genesis_50684.10\HighRes'; % Output directory for high-res images

if (~exist(imagepath, 'dir'))
    mkdir(imagepath); 
end



imageformat='jpeg';

% Upload the .hdr files from autofocus map into the hdrfiles directory
% Script will write an xml file which can be loaded into imagesnapper



imagedir=dir([focusimagedir '*hdr']);
nfiles=numel(imagedir);

WD=zeros(nfiles,1);
YStage=zeros(nfiles,1);
XStage=zeros(nfiles,1);


for ii=1:nfiles
    
    fid = fopen([imagedir(ii).folder '/' imagedir(ii).name]);
    dd = textscan(fid,'%s');
    dd=dd{1};
    fclose(fid);

    wdstr='WD=';
    ss=strfind(dd,wdstr);
    index = false(1, numel(ss));
    for k = 1:numel(ss)
      if numel(ss{k} == 1)==0
         index(k) = 0;
      else
         index(k) = 1;
      end     
    end
    ll=dd{index};
    WD(ii)=str2double(ll((numel(wdstr)+1):end));
   
 
    ystr='StageY=';
    ss=strfind(dd,ystr);
    index = false(1, numel(ss));
    for k = 1:numel(ss)
      if numel(ss{k} == 1)==0
         index(k) = 0;
      else
         index(k) = 1;
      end     
    end
    ll=dd{index};
    YStage(ii)=str2double(ll((numel(ystr)+1):end));
    
    xstr='StageX=';
    ss=strfind(dd,xstr);
    index = false(1, numel(ss));
    for k = 1:numel(ss)
      if numel(ss{k} == 1)==0
         index(k) = 0;
      else
         index(k) = 1;
      end     
    end
    ll=dd{index};
    XStage(ii)=str2double(ll((numel(xstr)+1):end));
    
end

if docuts
       
cut_index=WD<0.02;
   
WD=WD(cut_index);
XStage=XStage(cut_index);
YStage=YStage(cut_index);
        
end

if dooutliers

[~,hampel_index] = hampel(WD); % outler detection and removal (out of focus image removal)

WD=WD(~hampel_index);
XStage=XStage(~hampel_index);
YStage=YStage(~hampel_index);

end

if doremovepoints
    
    badpointindices=[1,170];
    
    WD(badpointindices)=[];
    XStage(badpointindices)=[];
    YStage(badpointindices)=[];

end

fprintf('%d files, %d outliers\n\n',nfiles,nfiles-numel(WD));
    

sf=fit([XStage,YStage],-WD,surfaceshape); 

plot(sf,[XStage,YStage],-WD)

n_vec=[sf.p10;sf.p01;-1];
n_vec=-n_vec./norm(n_vec);
qfac=5*std(-WD);
if strcmp(surfaceshape,'poly11') % plot surface normal only for plane
hold on
quiver3(mean(XStage),mean(YStage),sf.p00+sf.p10*mean(XStage) + sf.p01*mean(YStage),qfac*n_vec(1),qfac*n_vec(2),qfac*n_vec(3),'Color','red','LineWidth',4)
hold off
end
daspect([1 1 0.2])
%axis equal

xv=min(XStage):1e-6*fov*(1-overlap_fraction):max(XStage);
yv=min(YStage):1e-6*fov*(1-overlap_fraction):max(YStage);

nxv=numel(xv);
nyv=numel(yv);

ptsxyz=zeros(nxv*nyv,3);
coordn=zeros(nxv*nyv,2);

for jj=1:nyv
    % This will flip the direction every other line to minimize stage
    % movement:
    if mod(jj,2)==1
        iiloopvec=1:nxv;
    else
        iiloopvec=nxv:-1:1;
    end
    % 
    for ii=1:nxv
        ptsxyz(ii+(jj-1)*nxv,:)=[xv(iiloopvec(ii)),yv(jj),-sf(xv(iiloopvec(ii)),yv(jj))];
        coordn(ii+(jj-1)*nxv,:)=[iiloopvec(ii),jj];
    end
end


res=writeImageSnapper(ptsxyz,Zstage,fov,coordn,imagepath,imageformat);

fclose('all');

sprintf('%d images',size(coordn,1))