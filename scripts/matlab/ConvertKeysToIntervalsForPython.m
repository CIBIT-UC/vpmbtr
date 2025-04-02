
clear,clc

%% data input

subjectList = {'VPMBAUS01';'VPMBAUS02';'VPMBAUS03';'VPMBAUS05';'VPMBAUS06';'VPMBAUS07';'VPMBAUS08';'VPMBAUS10';'VPMBAUS11';'VPMBAUS12';'VPMBAUS15';'VPMBAUS16';'VPMBAUS21';'VPMBAUS22';'VPMBAUS23'};
subjectNumberList = {'01';'02';'03';'05';'06';'07';'08';'10';'11';'12';'15';'16';'21';'22';'23'};

runList = {'AA','UA'};
trList = {'0500','0750','1000','2500'};
trValues = [0.5, 0.75, 1, 2.5];

nSubjects = length(subjectList);
[combSub,combTR,combRun] = meshgrid(1:nSubjects,1:4,1:2);
nCombs = length(subjectList)*4*2;

%% Iterate

for cc = 1:nCombs
    
    
    %% load keypress

    matFile =  dir(['/home/alexandresayal/GitRepos/vpmb-tr/data/keypress-raw/S' subjectNumberList{combSub(cc)} '_OUT_*.mat']);
    
    load(fullfile(matFile.folder,matFile.name),'Output')

    keys = Output.(sprintf('Run%s_TR%s',runList{combRun(cc)},trList{combTR(cc)})).Keys;
    keycodes = Output.(sprintf('Run%s_TR%s',runList{combRun(cc)},trList{combTR(cc)})).KeyCodes;
    
    %% load template protocol for this TR
    [ ~ , ~ , intervals ] = readProtocol('prt',['Run' runList{combRun(cc)} '_TR' trList{combTR(cc)} '.prt'], trValues(combTR(cc)));
    
    %% convert to continuous report
    KeysContinuous = zeros(size(keys(:,1)));
    saved = 0;
    for ii = 1:length(KeysContinuous)

        if (keys(ii,1) ~= 0) && (keys(ii,1) ~= saved)
            saved = keys(ii,1);
        end

        KeysContinuous(ii) = saved;

    end

    framesDots = KeysContinuous;
    framesDots(framesDots == keycodes(1)) = 22; % coherent
    framesDots(framesDots == keycodes(2)) = 33; % incoherent
    
    %% adjust static periods and create intervalsDots
    TR = trValues(combTR(cc));
    fps = 60;

    nVols = length(intervals);
    nFrames = nVols*fps*TR;

    intervalsDots = zeros(nVols,1);

    for t = 0:nVols-1

        if intervals(t+1) == 4 % discard
            framesDots(t*fps*TR+1:(t+1)*fps*TR) = 55;
        elseif intervals(t+1) == 3 % mae
            framesDots(t*fps*TR+1:(t+1)*fps*TR) = 44;
        elseif intervals(t+1) == 1 % static
            framesDots(t*fps*TR+1:(t+1)*fps*TR) = 11;
        end

        intervalsDots(t+1,1) = mode(framesDots(t*fps*TR+1:(t+1)*fps*TR));

    end
    
    %% fill zeros with static
    intervalsDots(intervalsDots == 0) = 11;
    
    %% Find the sequence of events
    changes = find(diff(intervalsDots)~=0);
    SEQ = [55 ; intervalsDots(changes + 1)]; % +1 to capture what the change is to
    DUR = diff([0 ; changes ; nVols]);
    
    %% convert to single vectors of ones and zeros and limit reports to motion block
    motion = (intervals == 2)';
    motion_changes = find(diff(motion)~=0);
    motion_DUR = [motion_changes(2)-motion_changes(1) ; motion_changes(4) - motion_changes(3)];
    motion_changes = motion_changes([1,3]);
    
    %% build matrices
    
    nSEQ = length(SEQ);
    
    trial_type = cell(nSEQ+2,1);
    
    trial_type(SEQ==11) = {'static'};
    trial_type(SEQ==22) = {'coherent'};
    trial_type(SEQ==33) = {'incoherent'};
    trial_type(SEQ==44) = {'mae'};
    trial_type(SEQ==55) = {'discard'};
    trial_type(end-1:end) = {'motion'};
    
    duration = [DUR ; motion_DUR];
        
    %% build onsets
    onset = zeros(nSEQ+2,1);
    startValue = 0;
    
    for jj = 1:nSEQ
        
        onset(jj) = startValue;
        startValue = onset(jj) + duration(jj);
        
    end
    
    onset(end-1:end) = motion_changes;
    
    %% convert to seconds
    onset = onset * TR;
    duration = duration * TR;
   
    %% re-sort
    [onset,idx] = sort(onset);
    trial_type = trial_type(idx);
    duration = duration(idx);
    
    %% export

    T = table(onset,duration,trial_type);
    
    export_file_name = fullfile('/home/alexandresayal/GitRepos/vpmb-tr/data/keypress-events-tsv',...
            sprintf('sub-%s_task-%s_acq-%s_run-%i_events.txt',subjectNumberList{combSub(cc)},runList{combRun(cc)},trList{combTR(cc)},1) );

    writetable(T,export_file_name,'Delimiter','\t');
    movefile(export_file_name,[export_file_name(1:end-4) '.tsv']);

    %%
    clear Output

    
end

%% Copy to BIDS

BIDS_path = '/home/alexandresayal/mnt/DATAPOOL/VPMB/BIDS-VPMB-SPE';

for cc = 1:nCombs
    
    input_file_name = fullfile('/home/alexandresayal/GitRepos/vpmb-tr/data/keypress-events-tsv',...
        sprintf('sub-%s_task-%s_acq-%s_run-%i_events.tsv',subjectNumberList{combSub(cc)},runList{combRun(cc)},trList{combTR(cc)},1) );

    export_file_name = fullfile(BIDS_path,...
        sprintf('sub-%s',subjectNumberList{combSub(cc)}),...
        'func', ...
        sprintf('sub-%s_task-%s_acq-%s_run-%i_events.tsv',subjectNumberList{combSub(cc)},runList{combRun(cc)},trList{combTR(cc)},1));
    
    copyfile(input_file_name, export_file_name); 
    
end


