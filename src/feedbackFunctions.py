import os
import pandas as pd
import numpy as np
from nilearn.maskers import NiftiSpheresMasker

def test_function():
    print("Hello World!")

def get_paths(run_type, tr, subject_label, fmriprep_dir, data_dir):
    task_label = f'task-{run_type}_acq-{round(tr*1000):04}_run-1'
    active_cond_name = 'Ambiguous' if run_type=='AA' else 'Unambiguous'
    fmri_img = os.path.join(fmriprep_dir, subject_label, 'func', f'{subject_label}_{task_label}_space-MNI152NLin2009cAsym_res-2_desc-preproc_bold.nii.gz')
    confounds_file = os.path.join(fmriprep_dir, subject_label, 'func', f'{subject_label}_{task_label}_desc-confounds_timeseries.tsv')
    events_file = os.path.join(data_dir, subject_label, 'func', f'{subject_label}_{task_label}_events.tsv')
    return task_label, fmri_img, confounds_file, events_file, active_cond_name

def extract_timeseries(cluster_coords, fmri_img, confounds, tr, subject_label):

    print(f'Extracting timeseries for {subject_label} with highpass, zscore sample standardization, and smoothing')
    
    masker_ss = NiftiSpheresMasker(
        seeds = cluster_coords,
        radius = 6,
        allow_overlap = True,
        smoothing_fwhm = 6,
        standardize = "zscore_sample",
        detrend = False, # this might remove important stuff since the block is long ?
        low_pass = None, # usual for RS but not for task ?
        high_pass = 0.003,
        t_r = tr,
        verbose = 5
        )

    return masker_ss.fit_transform(fmri_img, confounds=confounds)
    
def execute(subject, tr, run, cluster_coords, fmriprep_dir, data_dir):

    print(f'{subject}_{tr}_{run}')

    # Get paths
    _, fmri_img, confounds_file, _, _ = get_paths(run, tr, subject, fmriprep_dir, data_dir)
 
    # Fetch confounds
    confounds = pd.read_csv(confounds_file, sep='\t')
    confounds = confounds.filter(regex='^(csf|trans|rot).*')
    confounds.fillna(0, inplace=True)

    # Extract timeseries
    time_series = extract_timeseries(cluster_coords, fmri_img, confounds, tr, subject)

    # Save timeseries
    np.save(os.path.join(data_dir, 'derivatives', 'timecourses', f'{subject}_{tr}_{run}_hp_std-zscoresample_ss.npy'), time_series)
    

def read_events(events_file,hrf_delay,tr,active_cond_name):
    events = pd.read_csv(events_file, sep='\t')

    # Fetch the points of 'Static' events (to normalize the time_series)
    static_events = events[events['trial_type']=='Static']

    # Get the time points of the static events - these start at the onset and last for duration
    static_events_onsets = static_events['onset'].values
    static_events_durations = static_events['duration'].values

    # create vector with all the time points of the static events
    static_events_indexes = np.array([])
    for i in range(len(static_events_onsets)):
        static_events_indexes = np.append(static_events_indexes, np.arange(static_events_onsets[i]/tr, static_events_onsets[i]/tr+static_events_durations[i]/tr))

    static_events_indexes = ( static_events_indexes + (hrf_delay/tr) ).astype(int)

    # get the time points of the ambiguous/unambiguous blocks
    active_events = events[events['trial_type']==active_cond_name]
    active_events_onsets = active_events['onset'].values
    active_events_durations = active_events['duration'].values

    # create matrix with all the time points of the ambiguous blocks, one per column
    active_events_indexes = np.array([])

    # convert times to indexes and add hemodynamic delay
    for i in range(len(active_events_onsets)):
        active_events_indexes = np.append(active_events_indexes,
                                            np.arange(active_events_onsets[i]/tr, active_events_onsets[i]/tr+active_events_durations[i]/tr))

    active_events_indexes = ( active_events_indexes + (hrf_delay/tr) ).astype(int)

    return static_events_indexes, active_events_indexes