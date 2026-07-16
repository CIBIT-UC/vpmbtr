"""Reusable helpers for the neurofeedback time-course pipeline (VPMB-TR).

This module supports the "feedback simulator" analysis, which asks whether the
temporal resolution (TR) of fMRI changes the quality of a real-time feedback
signal derived from the BOLD response of visual ROIs (bilateral hMT+ and V1).

The typical flow is:
    1. ``get_paths``          -> build BIDS/fMRIPrep file paths for one run.
    2. ``extract_timeseries`` -> pull the ROI BOLD time courses from the
                                 preprocessed image (percent-signal-change units).
    3. ``execute``            -> orchestrate 1-2 for a single (subject, TR, run)
                                 combination and save the result to disk. This is
                                 the function fanned out over a multiprocessing
                                 Pool in ``scripts/py/feedback-TCextraction.py``.
    4. ``read_events``        -> convert the BIDS events file into volume indices
                                 for the baseline ("static") and active blocks,
                                 shifted by the assumed hemodynamic delay.

Design conventions
------------------
* ``run_type`` / ``run`` is either ``'AA'`` (ambiguous) or ``'UA'`` (unambiguous).
* ``tr`` is given in seconds (0.5, 0.75, 1.0, 2.5); the BIDS ``acq`` label is the
  TR in milliseconds zero-padded to four digits (e.g. 0.75 s -> ``acq-0750``).
"""

import os
import pandas as pd
import numpy as np
from nilearn.maskers import NiftiSpheresMasker


def test_function():
    """Smoke-test helper used to confirm the package imports correctly."""
    print("Hello World!")


def get_paths(run_type, tr, subject_label, fmriprep_dir, data_dir):
    """Build the BIDS/fMRIPrep file paths for a single run.

    Parameters
    ----------
    run_type : str
        Task run, ``'AA'`` (ambiguous) or ``'UA'`` (unambiguous).
    tr : float
        Repetition time in seconds (e.g. 0.5). Converted to the 4-digit,
        millisecond ``acq`` label used in the filenames.
    subject_label : str
        BIDS subject id including the prefix, e.g. ``'sub-01'``.
    fmriprep_dir, data_dir : str
        Root of the fMRIPrep derivatives and of the raw BIDS dataset.

    Returns
    -------
    tuple
        ``(task_label, fmri_img, confounds_file, events_file, active_cond_name)``.

    Notes
    -----
    ``active_cond_name`` here still uses the legacy 'Ambiguous'/'Unambiguous'
    labels. The current events files (see ``data/bids_events``) label blocks as
    ``motion``/``coherent``/``incoherent``/``static``, so this value is stale and
    must NOT be fed into ``read_events`` as-is. Downstream callers currently
    discard it (``feedback-TCextraction.py``) or override it explicitly
    (``step-05_feedback_new.ipynb`` passes ``active_cond_name='motion'``).
    """
    # ``acq`` label = TR in milliseconds, zero-padded to 4 digits (0.75 s -> 0750).
    task_label = f'task-{run_type}_acq-{round(tr*1000):04}_run-1'
    # NOTE: legacy naming, kept for backwards compatibility only (see docstring).
    active_cond_name = 'Ambiguous' if run_type=='AA' else 'Unambiguous'
    fmri_img = os.path.join(fmriprep_dir, subject_label, 'func', f'{subject_label}_{task_label}_space-MNI152NLin2009cAsym_res-2_desc-preproc_bold.nii.gz')
    confounds_file = os.path.join(fmriprep_dir, subject_label, 'func', f'{subject_label}_{task_label}_desc-confounds_timeseries.tsv')
    events_file = os.path.join(data_dir, subject_label, 'func', f'{subject_label}_{task_label}_events.tsv')
    return task_label, fmri_img, confounds_file, events_file, active_cond_name


def extract_timeseries(cluster_coords, fmri_img, confounds, tr, subject_label):
    """Extract ROI BOLD time courses as percent signal change.

    A spherical masker (6 mm radius) is placed at each seed coordinate and the
    mean signal within each sphere is returned after cleaning (high-pass filter,
    detrending, PSC standardization, confound regression).

    Parameters
    ----------
    cluster_coords : list of [x, y, z]
        Subject-specific MNI seed coordinates (typically L/R hMT+ and L/R V1).
    fmri_img : str
        Path to the preprocessed 4D BOLD image.
    confounds : pandas.DataFrame
        Confound regressors already trimmed to the desired columns.
    tr : float
        Repetition time in seconds (needed for the temporal filters).
    subject_label : str
        Subject id, used only for the progress message.

    Returns
    -------
    numpy.ndarray
        Array of shape ``(n_volumes, n_seeds)`` with one PSC time course per ROI.
    """
    print(f'Extracting timeseries for {subject_label} with highpass, psc standardization and detrend.')

    masker_ss = NiftiSpheresMasker(
        seeds = cluster_coords,
        radius = 6,                 # sphere radius in mm
        allow_overlap = True,       # L/R spheres of the same ROI may touch
        smoothing_fwhm = None,      # no extra smoothing here
        standardize = "psc",        # express signal as percent signal change
        detrend = True,             # NOTE: blocks are long, detrending may remove real signal
        low_pass = None,            # no low-pass (task, not resting state)
        # NOTE: 0.003 Hz == ~333 s cutoff period, i.e. almost no high-pass at all.
        # This is 10x lower than the 0.03 Hz used in the localizer GLM; verify it
        # is intentional and not an order-of-magnitude typo (see ANALYSIS.md).
        high_pass = 0.003,
        t_r = tr,
        verbose = 5
        )

    return masker_ss.fit_transform(fmri_img, confounds=confounds)


def execute(subject, tr, run, cluster_coords, fmriprep_dir, data_dir):
    """Extract and save the ROI time courses for one (subject, TR, run) combo.

    This is the unit of work fanned out over a multiprocessing pool. It resolves
    the paths, loads and trims the fMRIPrep confounds (CSF + 6 motion parameters
    and their derivatives/powers via the regex), extracts the PSC time courses,
    and writes them to ``<data_dir>/derivatives/timecourses``.
    """
    print(f'{subject}_{tr}_{run}')

    # Get paths (active_cond_name intentionally discarded; see get_paths notes)
    _, fmri_img, confounds_file, _, _ = get_paths(run, tr, subject, fmriprep_dir, data_dir)

    # Fetch confounds and keep only CSF / translation / rotation columns
    confounds = pd.read_csv(confounds_file, sep='\t')
    confounds = confounds.filter(regex='^(csf|trans|rot).*')
    confounds.fillna(0, inplace=True)  # fMRIPrep leaves NaNs in the first derivative rows

    # Extract timeseries
    time_series = extract_timeseries(cluster_coords, fmri_img, confounds, tr, subject)

    # Save timeseries as .npy (shape: n_volumes x n_seeds)
    np.save(os.path.join(data_dir, 'derivatives', 'timecourses', f'{subject}_{tr}_{run}_hp_std-psc_detrend.npy'), time_series)


def read_events(events_file, hrf_delay, tr, active_cond_name):
    """Convert a BIDS events file into baseline and active-block volume indices.

    Onsets/durations (in seconds) are converted to volume indices by dividing by
    the TR, and shifted forward by ``hrf_delay`` (also in seconds) to
    approximately align stimulus timing with the delayed BOLD response.

    Parameters
    ----------
    events_file : str
        Path to the ``*_events.tsv`` file (columns: onset, duration, trial_type).
    hrf_delay : float
        Assumed hemodynamic delay in seconds (0 disables the shift).
    tr : float
        Repetition time in seconds.
    active_cond_name : str
        Label of the active block to extract. With the current events files this
        should be ``'motion'`` (or ``'coherent'``/``'incoherent'``), NOT the
        legacy ``'Ambiguous'``/``'Unambiguous'``; passing a label absent from the
        file yields an empty ``active_events_indexes`` array.

    Returns
    -------
    tuple of numpy.ndarray
        ``(static_events_indexes, active_events_indexes)`` as integer volume
        indices.

    Notes
    -----
    Indices are not clipped to the length of the run, so after adding the HRF
    delay the last few values may exceed the number of acquired volumes; callers
    that index a time series with them should guard against out-of-range values.
    """
    events = pd.read_csv(events_file, sep='\t')

    # Baseline: 'static' blocks are used to normalize the time series.
    static_events = events[events['trial_type']=='static']

    # Static block onsets/durations, in seconds.
    static_events_onsets = static_events['onset'].values
    static_events_durations = static_events['duration'].values

    # Expand each static block into its constituent volume indices.
    static_events_indexes = np.array([])
    for i in range(len(static_events_onsets)):
        static_events_indexes = np.append(static_events_indexes, np.arange(static_events_onsets[i]/tr, (static_events_onsets[i]/tr) + (static_events_durations[i]/tr) ))

    # Shift by the hemodynamic delay and cast to integer volume indices.
    static_events_indexes = ( static_events_indexes + (hrf_delay/tr) ).astype(int)

    # Active blocks (label given by active_cond_name, e.g. 'motion').
    active_events = events[events['trial_type']==active_cond_name]
    active_events_onsets = active_events['onset'].values
    active_events_durations = active_events['duration'].values

    # Expand each active block into its constituent volume indices.
    active_events_indexes = np.array([])

    # convert times to indexes and add hemodynamic delay
    for i in range(len(active_events_onsets)):
        active_events_indexes = np.append(active_events_indexes,
                                            np.arange(active_events_onsets[i]/tr, active_events_onsets[i]/tr+active_events_durations[i]/tr))

    active_events_indexes = ( active_events_indexes + (hrf_delay/tr) ).astype(int)

    return static_events_indexes, active_events_indexes
