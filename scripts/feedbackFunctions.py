import os
import pandas as pd
import numpy as np
from nilearn.maskers import NiftiSpheresMasker

def iteration(ss,subject, tr_list, run_list, n_volumes_list, roi_ss_coords, hrf_delay, fmriprep_dir, data_dir, TC):

    for tt,tr in enumerate(tr_list):

        for rr,run in enumerate(run_list):

            print(f'{subject}_{tr}_{run}')

            # Get paths
            task_label, fmri_img, confounds_file, events_file, active_cond_name = get_paths(run, tr, subject, fmriprep_dir, data_dir)

            # Read events
            static_events_indexes, active_events_indexes = read_events(events_file,hrf_delay,tr,active_cond_name)

            # Fetch confounds
            confounds = pd.read_csv(confounds_file, sep='\t')
            confounds = confounds.filter(regex='^(csf|white_matter|trans|rot).*')
            confounds.fillna(0, inplace=True)

            # Extract timeseries
            time_series = extract_timeseries(roi_ss_coords, fmri_img, confounds, tr, subject)

            # create time vector based on the number of time points and the tr
            time_vector = np.arange(0, time_series.shape[0]*tr, tr)

            # calculate mean of rois
            time_series_mean = time_series.mean(axis=1)

            TC[ss,tt,rr,:n_volumes_list[tt]] = time_series_mean
    
    return TC

def test_function():
    print("Hello World!")

def get_paths(run_type, tr, subject_label, fmriprep_dir, data_dir):
    task_label = f'task-{run_type}_acq-{round(tr*1000):04}_run-1'
    active_cond_name = 'Ambiguous' if run_type=='AA' else 'Unambiguous'
    fmri_img = os.path.join(fmriprep_dir, subject_label, 'func', f'{subject_label}_{task_label}_space-MNI152NLin2009cAsym_res-2_desc-preproc_bold.nii.gz')
    confounds_file = os.path.join(fmriprep_dir, subject_label, 'func', f'{subject_label}_{task_label}_desc-confounds_timeseries.tsv')
    events_file = os.path.join(data_dir, subject_label, 'func', f'{subject_label}_{task_label}_events.tsv')
    return task_label, fmri_img, confounds_file, events_file, active_cond_name

def extract_timeseries(roi_ss_coords, fmri_img, confounds, tr, subject_label):
    # extract x,y,z coordinates of this subject's hMT+ roi
    cluster_coords = [[0, 0, 0], [0, 0, 0]]
    cluster_coords[0] = roi_ss_coords[roi_ss_coords['subject']==subject_label].iloc[:,0:3].values[0].tolist()
    cluster_coords[1] = roi_ss_coords[roi_ss_coords['subject']==subject_label].iloc[:,3:6].values[0].tolist()

    masker_ss = NiftiSpheresMasker(
        cluster_coords,
        radius=8,
        detrend=True,
        standardize=False,
        high_pass=0.003,
        t_r=tr
        )

    return masker_ss.fit_transform(fmri_img, confounds=confounds)

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

    static_events_indexes = ( static_events_indexes - 1 + (hrf_delay/tr) ).astype(int)

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

    active_events_indexes = ( active_events_indexes - 1 + (hrf_delay/tr) ).astype(int)

    return static_events_indexes, active_events_indexes
    


#def estimate_feedback():