function pix = angle2pix(viewDistCm, screenWidthCm, screenResX, visualAngleDeg)
% ANGLE2PIX Converts visual angle (deg) to pixels
%
% pix = angle2pix(viewDistCm, screenWidthCm, screenResX, visualAngleDeg)
%
% INPUTS:
%   viewDistCm       - Distance from viewer to screen (in cm)
%   screenWidthCm    - Physical screen width (in cm)
%   screenResX       - Horizontal screen resolution (in pixels)
%   visualAngleDeg   - Visual angle (in degrees)
%
% OUTPUT:
%   pix              - Size in pixels corresponding to visual angle
%
% Assumes square pixels and viewer perpendicular to screen.

    % Size on screen in cm that corresponds to the visual angle
    sizeCm = 2 * viewDistCm * tan(deg2rad(visualAngleDeg / 2));

    % Convert physical size to pixels
    cmPerPixel = screenWidthCm / screenResX;
    pix = round(sizeCm / cmPerPixel);
end