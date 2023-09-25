# %%
import os
import glob
import numpy as np
import pandas as pd
from nilearn.maskers import NiftiSpheresMasker

# %%
# Settings
data_dir = '/DATAPOOL/VPMB/BIDS-VPMB-SPE'
#fmriprep_dir = os.path.join(data_dir,'derivatives','fmriprep23','fmriprep')
nilearn_dir = os.path.join(data_dir,'derivatives','nilearn_glm')
#output_dir = os.path.join(data_dir,'derivatives','feedbackSimulator')
out_dir = '/DATAPOOL/home/alexandresayal/GitRepos/vpmb-tr/data'
subject_list = [x for x in os.listdir(data_dir) if 'sub-' in x]
subject_list.sort()

tr_list = [0.5, 0.75, 1, 2.5]
tr_label_list = ['0500','0750','1000','2500']
#n_volumes_list = [780, 520, 390, 156]
run_list = ['AA','UA']
#hrf_delay = 3 # in seconds

# %%
# Load subject-specific roi coordinates
roi_ss_coords = pd.read_csv(os.path.join(nilearn_dir,'group','roi_ss_matrix.txt'), sep='\t', header=None,
                            names=['left_mt_x','left_mt_y','left_mt_z','right_mt_x','right_mt_y','right_mt_z',
                                   'left_v1_x','left_v1_y','left_v1_z','right_v1_x','right_v1_y','right_v1_z'])

# add new column with the subject names
roi_ss_coords['subject'] = subject_list
roi_labels = ['hMT+ L', 'hMT+ R', 'V1 L', 'V1 R']

# %%
# Initialize matrix to store the beta values of all subjects per tr
BETAS = np.zeros((len(subject_list), len(tr_list), len(run_list), len(roi_labels)))
TVALS = np.zeros((len(subject_list), len(tr_list), len(run_list), len(roi_labels)))
ZVALS = np.zeros((len(subject_list), len(tr_list), len(run_list), len(roi_labels)))

# %%
# Create combinations of subject, tr and run
C = []
for ss,subject in enumerate(subject_list):
    # extract x,y,z coordinates of this subject's hMT+ roi
    cluster_coords = [[0, 0, 0], [0, 0, 0], [0, 0, 0], [0, 0, 0]]
    cluster_coords[0] = roi_ss_coords[roi_ss_coords['subject']==subject].iloc[:,0:3].values[0].tolist()
    cluster_coords[1] = roi_ss_coords[roi_ss_coords['subject']==subject].iloc[:,3:6].values[0].tolist()
    cluster_coords[2] = roi_ss_coords[roi_ss_coords['subject']==subject].iloc[:,6:9].values[0].tolist()
    cluster_coords[3] = roi_ss_coords[roi_ss_coords['subject']==subject].iloc[:,9:12].values[0].tolist()

    C.append([ss, subject, cluster_coords])

C

# %%
for ss in range(len(subject_list)):
    print(f"Subject: {subject_list[ss]}")

    masker = NiftiSpheresMasker(
        seeds=C[ss][2],
        radius=6,
        detrend=False,
        standardize=False,
        low_pass=None,
        high_pass=None,
        resampling_target=None
        )
    
    masker.fit()

    for tr in range(len(tr_list)):
        for rr in range(len(run_list)):

            # contrast naming
            if run_list[rr] == "AA":
                contrast_name_valid = "AmbiguousMinusStatic"
            elif run_list[rr] == "UA":
                contrast_name_valid = "UnambiguousMinusStatic"

            beta_img = os.path.join(nilearn_dir,
                            f"{subject_list[ss]}_task-{run_list[rr]}_acq-{tr_label_list[tr]}_stat-beta_con-{contrast_name_valid}.nii.gz"
                            )
                        
            t_img = os.path.join(nilearn_dir,
                            f"{subject_list[ss]}_task-{run_list[rr]}_acq-{tr_label_list[tr]}_stat-t_con-{contrast_name_valid}.nii.gz"
                            )
            
            z_img = os.path.join(nilearn_dir,
                            f"{subject_list[ss]}_task-{run_list[rr]}_acq-{tr_label_list[tr]}_stat-z_con-{contrast_name_valid}.nii.gz"
                            )

            BETAS[ss,tr,rr,:] = masker.fit_transform(beta_img)[0]
            TVALS[ss,tr,rr,:] = masker.fit_transform(t_img)[0]
            ZVALS[ss,tr,rr,:] = masker.fit_transform(z_img)[0]

# %%
# save 4D matrices as npy files as safe measure
np.save(os.path.join(out_dir,'BETAS.npy'), BETAS)
np.save(os.path.join(out_dir,'TVALS.npy'), TVALS)
np.save(os.path.join(out_dir,'ZVALS.npy'), ZVALS)

# %%
# convert BETAS to a dataframe with the following columns: subject, tr, task, roi, beta
DF = pd.DataFrame(columns=['subject', 'tr', 'task', 'roi', 'beta', 'tval', 'zval'])
idx = 0
for ss,subject in enumerate(subject_list):
    for tt,tr in enumerate(tr_label_list):
        for ta,task in enumerate(run_list):
            for rr,roi in enumerate(roi_labels):
                beta = BETAS[ss,tt,ta,rr]
                tval = TVALS[ss,tt,ta,rr]
                zval = ZVALS[ss,tt,ta,rr]
                DF.loc[idx] = [subject, tr, task, roi, beta, tval, zval]
                idx += 1

# %%
#DF

# %%
# save dataframe
DF.to_csv(os.path.join(out_dir,'nilearn-roianalysis-AAUA.tsv'), sep='\t', index=False)


