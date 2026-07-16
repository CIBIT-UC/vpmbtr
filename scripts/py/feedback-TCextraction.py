# %%
"""Batch extraction of ROI BOLD time courses for the feedback simulator.

For every (subject, TR, run) combination this script pulls the subject-specific
hMT+ and V1 seed coordinates, then extracts the percent-signal-change time
courses via ``feedbackFunctions.execute`` (which cleans, masks and saves them).
The combinations are processed in parallel over a multiprocessing pool.

Run from the repository root (so that ``import src...`` resolves), on the machine
that holds the BIDS dataset (paths below are absolute to that server).
"""

import os
import pandas as pd
import numpy as np
import src.feedbackFunctions as ff

# %%
# Settings -- absolute paths on the acquisition/analysis server.
data_dir = '/DATAPOOL/VPMB/BIDS-VPMB-SPE'
fmriprep_dir = os.path.join(data_dir,'derivatives','fmriprep23','fmriprep')
nilearn_dir = os.path.join(data_dir,'derivatives','nilearn_glm')

subject_list = [x for x in os.listdir(data_dir) if 'sub-' in x]
subject_list.sort()

tr_list = [0.5, 0.75, 1, 2.5]
run_list = ['AA','UA']

# %%
# Load subject-specific ROI coordinates.
# roi_ss_matrix.txt has one row per subject and 12 columns: the x,y,z MNI
# coordinates of L hMT+, R hMT+, L V1, R V1 (in that order), produced by
# step-03_roiDefinition.
roi_ss_coords = pd.read_csv(os.path.join(nilearn_dir,'group','roi_ss_matrix.txt'), sep='\t', header=None,
                            names=['left_mt_x','left_mt_y','left_mt_z','right_mt_x','right_mt_y','right_mt_z',
                                   'left_v1_x','left_v1_y','left_v1_z','right_v1_x','right_v1_y','right_v1_z'])

# Attach subject labels by position. NOTE: this assumes the rows of
# roi_ss_matrix.txt are in the same order as the sorted subject_list; if a
# subject is missing from the dataset the alignment silently breaks.
roi_ss_coords['subject'] = subject_list

# %%
# Build the list of (subject, tr, run) jobs, embedding each subject's 4 ROI
# coordinates so the worker function is self-contained.
C = []
for ss,subject in enumerate(subject_list):
    # extract x,y,z coordinates of this subject's hMT+ and V1 roi
    cluster_coords = [[0, 0, 0], [0, 0, 0], [0, 0, 0], [0, 0, 0]]
    cluster_coords[0] = roi_ss_coords[roi_ss_coords['subject']==subject].iloc[:,0:3].values[0].tolist()
    cluster_coords[1] = roi_ss_coords[roi_ss_coords['subject']==subject].iloc[:,3:6].values[0].tolist()
    cluster_coords[2] = roi_ss_coords[roi_ss_coords['subject']==subject].iloc[:,6:9].values[0].tolist()
    cluster_coords[3] = roi_ss_coords[roi_ss_coords['subject']==subject].iloc[:,9:12].values[0].tolist()

    for tt,tr in enumerate(tr_list):
        for rr,run in enumerate(run_list):
            C.append([subject, tr, run, cluster_coords, fmriprep_dir, data_dir])


# %%
# Open a parallel pool and run ff.execute on every job.
# NOTE: Pool(20) hard-codes 20 workers; each worker also loads a 4D image, so
# peak memory can be large -- reduce if the machine is memory-constrained.
from multiprocessing import Pool
pool = Pool(20)

pool.starmap(ff.execute,C)
pool.close()

print('DONE!')
