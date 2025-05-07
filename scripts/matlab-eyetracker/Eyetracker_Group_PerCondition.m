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

% --- Screen center and area of interest
centerX = 1920/2;
centerY = 1080/2;
devX = angle2pix(156,70,centerX*2,2.5); % dist, width, width in px, v angle
devY = angle2pix(156,70,centerY*2,2.5); % dist, width, width in px, v angle

%%
f_percond_duration = struct();  
conditionNames = {'Coh_aCoh','Coh_aInCoh','Coh_aNA','InCoh_aCoh','InCoh_aInCoh','InCoh_aNA','Coherent','Incoherent','NonAdapt'};
nConditions = length(conditionNames);

fs = 1000; % sampling frequency of the eyetracker signal in Hz
duration_expected = 374 * fs; % the runs have 374 seconds

%% Iterate
for ss = 1:nSubjects
    
    auxDir = dir(fullfile(inputFolder,subjectsList{ss},'*.edf'));
            
    auxArray = zeros(length(auxDir),1);

    % Iterate on the edf files
    for rr = 1:length(auxDir) % six runs
        
        fname = fullfile(auxDir(rr).folder,auxDir(rr).name);
        myDataInfo = Edf2Mat(fname); % Convert edf to mat

        %% syncronization eyetracker <-> MRI
        % since the start of the eyetracker was not syncronized with the start of
        % the MRI, we must cut according to the end of the recording (which was
        % syncronized with the end of the MRI acquisition)
        duration_actual = myDataInfo.timeline(end) - myDataInfo.timeline(1);
        
        extra_timepoints = duration_actual-duration_expected;
        
        % sanity check for incorrect values
        if extra_timepoints < 0
            fprintf('\n!! extra_timepoints is incorrect for subject %i run %i \n',ss,rr)
        end
        
        %% Import run protocol
        protocolFolder = fullfile('..','data','input-stimulus');
        protocolFile = load(fullfile(protocolFolder,sprintf('Protocols_RunMRI_D12_R%i.mat',rr)),'intervalsPRT');
               
        % Convert to eyetracer timepoints
        for jj = 1:nConditions % conditions
           
            protocolFile.timepoints.(conditionNames{jj}) = (protocolFile.intervalsPRT.(conditionNames{jj}) - 1) * fs;
            
            if jj<7
                protocolFile.condDuration.(conditionNames{jj}) = 6*2*fs;
            else
                protocolFile.condDuration.(conditionNames{jj}) = 12*2*fs;
            end

        end
        
        %% Select fixations inside the region of interest
        posX = myDataInfo.Events.Efix.posX; % fixation X position
        posY = myDataInfo.Events.Efix.posY; % fixation Y position

        % find which fixation events are inside the region of interest
        fixInt = (posX < centerX + devX) & (posX > centerX - devX) & (posY < centerY + devY) & (posY > centerY - devY) ;

        %% Read data from valid fixation events      
        f_start = myDataInfo.Events.Efix.start(fixInt) - myDataInfo.timeline(1) + extra_timepoints;
        f_end = myDataInfo.Events.Efix.end(fixInt) - myDataInfo.timeline(1) + extra_timepoints;
        f_duration = myDataInfo.Events.Efix.duration(fixInt);

        %%
        for jj = 1:nConditions % conditions
        
           cond_range = [ protocolFile.timepoints.(conditionNames{jj})(1,1):protocolFile.timepoints.(conditionNames{jj})(1,2) protocolFile.timepoints.(conditionNames{jj})(2,1):protocolFile.timepoints.(conditionNames{jj})(2,2) ];
           
           %% find fixation events that started during this condition
           inter = ismember(f_start, cond_range); 
            
           % find events that end after the end of the condition to trim its
           % duration
           inter_end = f_end(inter);
        
           over_ind_1 = (inter_end > protocolFile.timepoints.(conditionNames{jj})(1,2)) & (inter_end < protocolFile.timepoints.(conditionNames{jj})(2,1)); % bigger than the end of this block and smaller than the start of the following
           over_ind_2 = inter_end > protocolFile.timepoints.(conditionNames{jj})(2,2);
        
           inter_end(over_ind_1) = protocolFile.timepoints.(conditionNames{jj})(1,2);
           inter_end(over_ind_2) = protocolFile.timepoints.(conditionNames{jj})(2,2);
        
           % recalculate durations
           inter_durations = inter_end - f_start(inter);

           %% find fixation events that started before the condition but end during the condition
           inter2 = ismember(f_end, cond_range);
           inter2 = (inter2 - inter)>0;
          
           if sum(inter2) > 0
               disp('found some more')

               inter2_end = f_end(inter2);
               inter2_durations = f_duration(inter2);
    
               % trim the durations
               idxs1 = inter2_end < protocolFile.timepoints.(conditionNames{jj})(1,2);
               inter2_durations(idxs1) = inter2_end(idxs1) - protocolFile.timepoints.(conditionNames{jj})(1,1);
    
               idxs2 = inter2_end < protocolFile.timepoints.(conditionNames{jj})(2,2) & inter2_end > protocolFile.timepoints.(conditionNames{jj})(2,1);
               inter2_durations(idxs2) = inter2_end(idxs2) - protocolFile.timepoints.(conditionNames{jj})(2,1);
           else
               inter2_durations = 0;
           end

           %% Calculate percentage of fixation over the duration of the condition block
           f_percond_duration.(conditionNames{jj})(ss,rr) = (sum(inter_durations)+sum(inter2_durations)) / protocolFile.condDuration.(conditionNames{jj}) * 100; % condition lasts 6 seconds, 2 trials
        
        end
    end
end

%% Stat analysis
% ttest Coh_aCoh vs. InCoh_aCoh - p=0.3056
% ttest Coh_aInCoh vs. InCoh_aInCoh - p=0.0993
% ttest Coherent vs. Incoherent - p=0.0714

[h1,p1] = ttest(sum(f_percond_duration.Coh_aCoh,2),sum(f_percond_duration.InCoh_aCoh,2))

[h2,p2] = ttest(sum(f_percond_duration.Coh_aInCoh,2),sum(f_percond_duration.InCoh_aInCoh,2))

[h3,p3] = ttest(sum(f_percond_duration.Coherent,2),sum(f_percond_duration.Incoherent,2))

%% Simple boxplot
figure

subplot(1,3,1)
boxplot([mean(f_percond_duration.Coh_aCoh,2),mean(f_percond_duration.InCoh_aCoh,2),mean(f_percond_duration.Coh_aNA,2)])
xticklabels({'Coh_aCoh','InCoh_aCoh','Coh_aNA'})
ylabel('Fixation percentage')
ylim([0 100])

subplot(1,3,2)
boxplot([mean(f_percond_duration.Coh_aInCoh,2),mean(f_percond_duration.InCoh_aInCoh,2),mean(f_percond_duration.InCoh_aNA,2)])
xticklabels({'Coh_aInCoh','InCoh_aInCoh','InCoh_aNA'})
ylabel('Fixation percentage')
ylim([0 100])

subplot(1,3,3)
boxplot([mean(f_percond_duration.Coherent,2),mean(f_percond_duration.Incoherent,2), mean(f_percond_duration.NonAdapt,2)])
xticklabels({'Coherent','Incoherent','NonAdapt'})
ylabel('Fixation percentage')
ylim([0 100])
