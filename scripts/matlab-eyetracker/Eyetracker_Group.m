clear, clc;

addpath(genpath('edf-converter'));

%% Configs

% --- Configuration data

% --- Retrieve participants with eyetracker data
subjectsList = {'01','02','03','05','06','07','08','10',...
                '11','15','16',...
                '21','22','23'};
nSubjects = length(subjectsList);
nRuns = 9;
run_seconds = 390;

% --- I/O Folders
inputFolder = fullfile('..','..','data','eyetracker-raw');
outputFolder = fullfile('..','..','data','eyetracker');

% --- Initialise matrix for fixation percentage
FixationRun_ROI = nan(nSubjects,nRuns);

% --- Area of interest
aoi_radius_va = 2; %in visual angle

%% Iterate on subjects and fill matrix

for s = 1:nSubjects
    
    auxDir = dir(fullfile(inputFolder,subjectsList{s},'*.edf'));

    % Iterate on the edf files
    for i = 1:length(auxDir)
        
        fname = fullfile(auxDir(i).folder,auxDir(i).name);
        
        [fixation_percent, total_duration] = compute_fixation_percent(fname, aoi_radius_va, run_seconds);

        FixationRun_ROI(s,i) = fixation_percent;
        
    end % end iteration on edf files
    
    fprintf('End of subject %i\n',s);
    
end

%% Some data cleaning for inplausible values
FixationRun_ROI(FixationRun_ROI < 25) = nan;

%% Mean across subject runs
Fixation = nanmean(FixationRun_ROI, 2);

%% Print results
% Fixation percentage: 
fprintf('Fixation percentage: M = %.2f , SD = %.2f \n',nanmean(Fixation),nanstd(Fixation));

%% Export data
clear i s fname auxDir
save(fullfile(outputFolder,['FixationData_N' num2str(nSubjects)]))
