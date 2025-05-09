function [fixation_percent, total_recording_duration, total_fixation_duration, fixations] = compute_fixation_percent(edf_file, aoi_radius_va, run_durations_secs)
% COMPUTE_FIXATION_PERCENT Detects fixations within a central AOI and computes the percentage of time spent there.
%
%   [fixation_percent, total_recording_duration, total_fixation_duration, fixations] = ...
%       compute_fixation_percent(edf_file, aoi_radius_va, run_durations_secs)
%
% This function loads raw gaze data from an EyeLink EDF file (converted via Edf2Mat),
% identifies custom-defined fixations based on spatial and temporal criteria,
% and calculates the proportion of time spent fixating within a circular Area of Interest (AOI)
% centered on the screen.
%
% --- INPUTS ---
%   edf_file (string)
%       Path to the EyeLink .edf file (requires Edf2Mat from https://github.com/uzh/edf-converter).
%
%   aoi_radius_va (double)
%       Radius of the AOI in degrees of visual angle.
%
%   run_durations_secs (double)
%       Expected duration of the run (in seconds), used to trim padding from the recording.
%
% --- OUTPUTS ---
%   fixation_percent (double)
%       Percentage of the recording duration spent fixating inside the AOI.
%
%   total_recording_duration (double)
%       Total usable recording time in milliseconds (after trimming).
%
%   total_fixation_duration (double)
%       Total duration of all fixations in the AOI (in milliseconds).
%
%   fixations (table)
%       Table with one row per detected fixation, containing:
%           - start: start time (ms)
%           - end: end time (ms)
%           - duration: fixation duration (ms)
%           - x: mean x gaze coordinate
%           - y: mean y gaze coordinate
%
% --- NOTES ---
%   - Fixations are defined as consecutive gaze samples inside the AOI lasting at least 80 ms.
%   - AOI is defined as a circle centered on the screen, with radius converted from visual angle.
%   - If the recording is shorter than the expected run duration, the function returns NaNs.


% === PARAMETERS ===
sampling_rate_hz = 500;
min_duration_ms = 80;
min_samples = round((min_duration_ms / 1000) * sampling_rate_hz);

screen_width = 1920;
screen_height = 1080;
aoi_radius_px = angle2pix(156, 70, screen_width, aoi_radius_va);
center_x = screen_width / 2;
center_y = screen_height / 2;

% === READ FILE ===
edf = Edf2Mat(edf_file);
x_coords = edf.Samples.posX;
y_coords = edf.Samples.posY;
timestamps = edf.Samples.time;

% === CUT SAMPLES BASED ON END OF FILE ===
rec_samples = (timestamps(end)-timestamps(1)) / 1000 * sampling_rate_hz; % actual recording number of samples
run_samples = run_durations_secs * sampling_rate_hz; % expected recording number of samples
extra_samples = rec_samples - run_samples;
extra_samples = round(extra_samples); % safety measure

if extra_samples < 0 % exclude localizer (shorter) run
    fixation_percent = nan;
    total_recording_duration = nan;
    total_fixation_duration = nan;
    fixations = nan;
    return
end

x_coords = x_coords(extra_samples:end);
y_coords = y_coords(extra_samples:end);
timestamps = timestamps(extra_samples:end);

% === DETECT FIXATIONS IN AOI ===
distances = sqrt((x_coords - center_x).^2 + (y_coords - center_y).^2);
in_aoi = distances <= aoi_radius_px;
fixations = [];
run_start = NaN;

for i = 1:length(in_aoi)

    if in_aoi(i) % If the current gaze sample is inside the AOI...

        if isnan(run_start) % ...and this is the first sample in a new run, mark the start.
            run_start = i;
        end
        % If we're already in a run, do nothing and continue accumulating.

    else % If the current sample is outside the AOI...

        if ~isnan(run_start) % ...and we were previously inside the AOI, it's the end of a run.

            run_end = i - 1;                         % Mark the last in-AOI index
            run_len = run_end - run_start + 1;       % Calculate how many samples were in the run

            if run_len >= min_samples % If the run lasted long enough (temporal criterion met)...

                segment_idx = run_start:run_end;      % Indices of the fixation
                fixation.start = timestamps(run_start);     % Start time of fixation
                fixation.end = timestamps(run_end);         % End time of fixation
                fixation.duration = fixation.end - fixation.start;  % Duration in ms
                fixation.x = mean(x_coords(segment_idx));   % Mean x position
                fixation.y = mean(y_coords(segment_idx));   % Mean y position

                % Add this fixation to the list
                fixations = [fixations; struct2table(fixation)];
            end

            % Reset for the next potential fixation
            run_start = NaN;
        end
    end
end

% Check for fixation at the end -  if the gaze is still inside the AOI when the data ends
if ~isnan(run_start)
    run_end = length(in_aoi);
    run_len = run_end - run_start + 1;
    if run_len >= min_samples
        segment_idx = run_start:run_end;
        fixation.start = timestamps(run_start);
        fixation.end = timestamps(run_end);
        fixation.duration = fixation.end - fixation.start;
        fixation.x = mean(x_coords(segment_idx));
        fixation.y = mean(y_coords(segment_idx));
        fixations = [fixations; struct2table(fixation)];
    end
end

% === CALCULATE DURATION STATS ===
if isempty(fixations)
    fixation_percent = 0;
    total_fixation_duration = 0;
else
    total_fixation_duration = sum(fixations.duration);
end

total_recording_duration = timestamps(end) - timestamps(1);
fixation_percent = (total_fixation_duration / total_recording_duration) * 100;
end