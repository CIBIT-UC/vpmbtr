clear, clc;

addpath(fullfile('..','tools','edf-converter'))

%% Configs

% --- Configuration data
load('Configs_VP_INHIBITION.mat')

% --- Retrieve participants with eyetracker data
subjectsList = datasetConfigs.subjects(logical(datasetConfigs.eyetracker));
nSubjects = length(subjectsList);
nRuns = 6;

% --- I/O Folders
inputFolder = fullfile('..','data','expC-raw-eyetracker');
outputFolder = fullfile('..','data','expC-eyetracker');

% --- Initialise matrix for fixation percentage
Fixation = zeros(nSubjects,1);
FixationRun = nan(nSubjects,nRuns);
FixationRun_ROI = nan(nSubjects,nRuns);

% --- Screen center and area of interest
centerX = 1920/2;
centerY = 1080/2;
devX = angle2pix(156,70,centerX*2,2.5); % dist, width, width in px, v angle
devY = angle2pix(156,70,centerY*2,2.5); % dist, width, width in px, v angle
fs = 1000; % sampling frequency of the eyetracker system in Hz

% --- Counter for excluded runs
excluded = 0;

%% Iterate on subjects and fill matrix

for s = 1:nSubjects
    
    auxDir = dir(fullfile(inputFolder,subjectsList{s},'*.edf'));
            
    auxArray = zeros(length(auxDir),1);

    % Iterate on the edf files
    for i = 1:length(auxDir)
        
        fname = fullfile(auxDir(i).folder,auxDir(i).name);
        myDataInfo = Edf2Mat(fname); % Convert edf to mat
        
        auxDur = myDataInfo.Events.Efix.duration; % fixation durations

        % run duration
        runDur = (myDataInfo.Events.End.time-myDataInfo.Events.Start.time);
        runDur_expected = 374*fs;
        extra_timepoints = runDur - runDur_expected;

        % exclude fixation events before the start of the MRI acquisition
        if any(myDataInfo.Events.Efix.start < extra_timepoints)
            auxDur(myDataInfo.Events.Efix.start < extra_timepoints) = 0;
            warning('excluding some events before the start')
        end

        FixationRun(s,i) = sum(auxDur) / runDur_expected;
        
        if FixationRun(s,i) < 0.75 % exclude runs with less than 75% of fixation
            auxArray(i) = NaN;
            excluded = excluded + 1;
        else           
            posX = myDataInfo.Events.Efix.posX; % fixation X position
            posY = myDataInfo.Events.Efix.posY; % fixation Y position
            
%             posX(posX<0) = NaN; % just to be sure :)
%             posY(posY<0) = NaN; % just to be sure :)

            % find which fixation events are inside the region of interest
            fixInt = (posX < centerX + devX) & (posX > centerX - devX) & (posY < centerY + devY) & (posY > centerY - devY) ;

            % calculate fixation duration / total duration and save
            auxArray(i) = sum(auxDur(fixInt)) / runDur_expected;
            FixationRun_ROI(s,i) = auxArray(i);
        end
        
    end % end iteration on edf files
    
    % calculate mean of subject
    Fixation(s) = nanmean(auxArray);
    
    fprintf('End of subject %i\n',s);
    
end

%% Exclude bad data
% cut at 0.5
inc = Fixation>0.5;

%% Print results
% Fixation percentage: M = 0.83 , SD = 0.11 
fprintf('Fixation percentage: M = %.2f , SD = %.2f \n',nanmean(Fixation(inc)),nanstd(Fixation(inc)));

%% Export data
clear auxArray i s myDataInfo fname auxDir auxDur runDur fixInt
save(fullfile(outputFolder,['FixationData_N' num2str(nSubjects)]))
