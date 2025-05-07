function pix = angle2pix(dist,width,resolutionX,ang)
%pix = angle2pix(display,ang)
%
%converts visual angles in degrees to pixels.
%
%Inputs:
%display.dist (distance from screen (cm))
%display.width (width of screen (cm))
%display.resolution (number of pixels of display in horizontal direction)
%
%ang (visual angle)
%
%Warning: assumes isotropic (square) pixels

%Written 11/1/07 gmb zre

%Calculate pixel size
pixSize = width/resolutionX;   %cm/pix

sz = 2*dist*tan(pi*ang/(2*180));  %cm

pix = round(sz/pixSize);   %pix 

end



