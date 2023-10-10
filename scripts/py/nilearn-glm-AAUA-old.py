# %% [markdown]
# # GLM analysis on the main task data
# It uses nilearn and performs the following steps:
# 1. Load the data from fmriPrep in BIDS format
# 2. Iterate on the subjects to:
#    1. Select the predictors and confounds for the design matrix
#    2. Generate 1st level model
#    3. Estimate contrast maps
# 3. Generate group level maps
# 4. Extract values for the group ROI from the localizer

# %%
# Imports
import os
import glob
from nilearn.glm.first_level import first_level_from_bids
from nilearn.interfaces.bids import save_glm_to_bids
from nilearn.glm import threshold_stats_img
from nilearn import plotting
from nilearn.plotting.cm import _cmap_d as nilearn_cmaps
import matplotlib.pyplot as plt
import pandas as pd
import numpy as np
from nilearn.glm.second_level import SecondLevelModel
from nilearn.reporting import get_clusters_table
from nilearn.image import math_img, load_img
from nilearn.masking import apply_mask

# %%
# Settings
data_dir = '/DATAPOOL/VPMB/BIDS-VPMB-SPE'
space_label = "MNI152NLin2009cAsym"
derivatives_folder = "derivatives/fmriprep23/fmriprep"
task_label = "UA" # "AA_acq-0500", "AA_acq-0750", "AA_acq-1000", "AA_acq-2500", "UA_acq-0500", "UA_acq-0750", "UA_acq-1000", "UA_acq-2500"
acq_label = '2500'
smoothing_fwhm = 6.0
high_pass_hz = 0.003

# %%
# contrast naming
if task_label == "AA":
    contrast_name = "Ambiguous - Static"
    contrast_name_valid = "AmbiguousMinusStatic"
elif task_label == "UA":
    contrast_name = "Unambiguous - Static"
    contrast_name_valid = "UnambiguousMinusStatic"

# %% [markdown]
# ## 1. Load the data from fmriPrep in BIDS format

# %%
# import first level data automatically from fmriPrep derivatives
(
    models,
    models_run_imgs,
    models_events,
    models_confounds,
) = first_level_from_bids(
    data_dir,
    task_label,
    space_label,
    img_filters=[('acq', acq_label)],
    hrf_model="spm",
    noise_model="ar2",
    smoothing_fwhm=smoothing_fwhm,
    high_pass=high_pass_hz,
    slice_time_ref=None,
    n_jobs=15,
    derivatives_folder=derivatives_folder,
)

# %% [markdown]
# ## 2. Iterate on the subjects in parallel

# %%
from joblib import Parallel, delayed

# Define function for first level analysis
def f(idx):

    # fetch model
    model, imgs, events, confounds = (
        models[idx],
        models_run_imgs[idx],
        models_events[idx],
        models_confounds[idx],
    )

    subject = f"sub-{model.subject_label}"

    print(f"Executing for subject {subject}...")

    # trim confounds
    confounds = confounds[0][['csf','csf_derivative1','csf_power2','csf_derivative1_power2',
                                          'trans_x', 'trans_x_derivative1', 'trans_x_power2', 'trans_x_derivative1_power2',
                                          'trans_y', 'trans_y_derivative1', 'trans_y_power2', 'trans_y_derivative1_power2',
                                          'trans_z', 'trans_z_derivative1', 'trans_z_power2', 'trans_z_derivative1_power2',
                                          'rot_x', 'rot_x_derivative1', 'rot_x_power2', 'rot_x_derivative1_power2',
                                          'rot_y', 'rot_y_derivative1', 'rot_y_power2', 'rot_y_derivative1_power2',
                                          'rot_z', 'rot_z_derivative1', 'rot_z_power2', 'rot_z_derivative1_power2',
                                          ]]

    # replace NaNs with 0s in confounds
    confounds = confounds.fillna(0)
    
    # Fit and contrasts
    model.fit(imgs, events, confounds)

    z_map = model.compute_contrast(contrast_name, output_type="z_score")
    t_map = model.compute_contrast(contrast_name, output_type="stat")
    beta_map = model.compute_contrast(contrast_name, output_type="effect_size")

    # save maps to disk
    z_map.to_filename(os.path.join(data_dir,"derivatives","nilearn_glm",
                                      f"{subject}_task-{task_label}_acq-{acq_label}_stat-z_con-{contrast_name_valid}.nii.gz"))
    t_map.to_filename(os.path.join(data_dir,"derivatives","nilearn_glm",
                                        f"{subject}_task-{task_label}_acq-{acq_label}_stat-t_con-{contrast_name_valid}.nii.gz"))
    beta_map.to_filename(os.path.join(data_dir,"derivatives","nilearn_glm",
                                            f"{subject}_task-{task_label}_acq-{acq_label}_stat-beta_con-{contrast_name_valid}.nii.gz")) 
    
    # create figure with thresholded map for fun
    clean_map, threshold = threshold_stats_img(
        z_map, alpha=0.05, height_control="bonferroni", cluster_threshold=50
    )

    plotting.plot_glass_brain(
        clean_map,
        colorbar=True,
        threshold=threshold,
        plot_abs=False,
        display_mode="ortho",
        figure=plt.figure(figsize=(10, 4)),
    )

    plt.savefig(os.path.join(
        data_dir,'derivatives','nilearn_glm',
        f"{subject}_task-{task_label}_acq-{acq_label}_plot-z_con-{contrast_name_valid}_c-bonferroni_p-0.05_clusterk-50.png"
        )
    )

    # Export cluster table
    table = get_clusters_table(z_map, threshold, 50)
    table.to_csv(os.path.join(data_dir,"derivatives","nilearn_glm",
                              f"{subject}_task-{task_label}_acq-{acq_label}_table-clusters_con-{contrast_name_valid}_c-bonferroni_p-0.05_clusterk-50.tsv"),sep='\t')
    
    del model, events, confounds, imgs

# Run in parallel
Parallel(n_jobs=15)(delayed(f)(idx) for idx in range(len(models)))


# %% [markdown]
# ## 3. Group level analysis

# %%
# List all tmap nii.gz files
tmap_files = glob.glob(
    os.path.join(data_dir,'derivatives','nilearn_glm',
        f"sub-*_task-{task_label}_acq-{acq_label}_stat-t_con-{contrast_name_valid}.nii.gz"
    )
)
tmap_files.sort()

# List all zmap nii.gz files
zmap_files = glob.glob(
    os.path.join(data_dir,'derivatives','nilearn_glm',
        f"sub-*_task-{task_label}_acq-{acq_label}_stat-z_con-{contrast_name_valid}.nii.gz"
    )
)
zmap_files.sort()

subject_list = [os.path.basename(f).split('_')[0] for f in tmap_files]
subject_list

# %%
# Plot all subjects
fig, axes = plt.subplots(nrows=5, ncols=3, figsize=(10, 10))
for cidx, tmap in enumerate(tmap_files):
    P = plotting.plot_glass_brain(
        tmap,
        colorbar=True,
        threshold=6.0,
        vmax=25,
        axes=axes[cidx % 5, int(cidx / 5)],
        plot_abs=False,
        display_mode="x",
    )
    P.title(subject_list[cidx], size=8)
fig.suptitle("subjects t_map")
plt.show()

# %%
# create design matrix for 2nd level
second_level_input = zmap_files
design_matrix_g = pd.DataFrame(
    [1] * len(second_level_input),
    columns=["intercept"],
)

# define 2nd level model
second_level_model = SecondLevelModel(smoothing_fwhm=6.0, n_jobs=20)

second_level_model = second_level_model.fit(
    second_level_input,
    design_matrix=design_matrix_g,
)

# compute contrast (z score map)
z_map_g = second_level_model.compute_contrast(
    second_level_contrast="intercept",
    output_type="z_score",
)

# compute contrast (t score map)
t_map_g = second_level_model.compute_contrast(
    second_level_contrast="intercept",
    output_type="stat",
)

# compute contrast (beta map)
beta_map_g = second_level_model.compute_contrast(
    second_level_contrast="intercept",
    output_type='effect_size',
)

# %%
# Threshold zmap and plot it
clean_map_g, threshold_g = threshold_stats_img(
    z_map_g, alpha=0.05, height_control="bonferroni", cluster_threshold=50
)

plotting.plot_glass_brain(
    clean_map_g,
    colorbar=True,
    threshold=threshold_g,
    plot_abs=False,
    display_mode="ortho",
    vmax=8,
    figure=plt.figure(figsize=(10, 4)),
    symmetric_cbar=False,
    cmap=nilearn_cmaps["cold_hot"],
)

plt.savefig(os.path.join(data_dir,"derivatives","nilearn_glm","group",
                         f"group_task-{task_label}_acq-{acq_label}_plot-z_con-{contrast_name_valid}_c-bonferroni_p-0.05_clusterk-50.png"))

# %%
# Export cluster table
table,cluster_map_g = get_clusters_table(z_map_g, threshold_g, 50,
                                return_label_maps=True)

table.to_csv(os.path.join(data_dir,"derivatives","nilearn_glm","group",
                          f"group_task-{task_label}_acq-{acq_label}_table-clusters_con-{contrast_name_valid}_c-bonferroni_p-0.05_clusterk-50.tsv"),sep='\t')
#print(table)
#print(table.to_latex())
table


# %%
# Save z_map_g, t_map_g, beta_map_g
z_map_g.to_filename(os.path.join(data_dir,"derivatives","nilearn_glm","group",
                                 f"group_task-{task_label}_stat-z_con-{contrast_name_valid}_c-bonferroni_p-0.05_clusterk-50.nii.gz"))

t_map_g.to_filename(os.path.join(data_dir,"derivatives","nilearn_glm","group",
                                    f"group_task-{task_label}_stat-t_con-{contrast_name_valid}_c-bonferroni_p-0.05_clusterk-50.nii.gz"))

beta_map_g.to_filename(os.path.join(data_dir,"derivatives","nilearn_glm","group",
                                    f"group_task-{task_label}_stat-beta_con-{contrast_name_valid}_c-bonferroni_p-0.05_clusterk-50.nii.gz"))

# %%
# View map interactively
plotting.view_img(clean_map_g,
         threshold=threshold_g
        )

# %% [markdown]
# # ROI analysis

# %%
# Load mask from group GLM
mask_hMT = load_img(os.path.join(data_dir,"derivatives","nilearn_glm","group",'mask_hMT.nii.gz'))

plotting.plot_roi(mask_hMT)

# %%
# List all tmap nii.gz files
tmap_files = glob.glob(
    os.path.join(data_dir,'derivatives','nilearn_glm',
        f"sub-*_task-{task_label}_acq-{acq_label}_stat-t_con-{contrast_name_valid}.nii.gz"
    )
)
tmap_files.sort()

# List all zmap nii.gz files
zmap_files = glob.glob(
    os.path.join(data_dir,'derivatives','nilearn_glm',
        f"sub-*_task-{task_label}_acq-{acq_label}_stat-z_con-{contrast_name_valid}.nii.gz"
    )
)
zmap_files.sort()

# List all beta nii.gz files
beta_files = glob.glob(
    os.path.join(data_dir,'derivatives','nilearn_glm',
        f"sub-*_task-{task_label}_acq-{acq_label}_stat-beta_con-{contrast_name_valid}.nii.gz"
    )
)
beta_files.sort()

# %%
# apply mask to all t maps
T = apply_mask(tmap_files, mask_hMT)
# apply mask to all z maps
Z = apply_mask(zmap_files, mask_hMT)
# apply mask to all beta maps
B = apply_mask(beta_files, mask_hMT)

# %%
#mean per subject
MT = np.mean(T,axis=1)
MZ = np.mean(Z,axis=1)
MB = np.mean(B,axis=1)

# export MT as tsv
np.savetxt(os.path.join(data_dir,"derivatives","nilearn_glm","group",
                        f"group_task-{task_label}_acq-{acq_label}_table-meanTvaluePerSub_con-{contrast_name_valid}_c-bonferroni_p-0.05_clusterk-50.tsv"),
            MT,delimiter='\t',fmt='%.4f')

# export MZ as tsv
np.savetxt(os.path.join(data_dir,"derivatives","nilearn_glm","group",
                        f"group_task-{task_label}_acq-{acq_label}_table-meanTvaluePerSub_con-{contrast_name_valid}_c-bonferroni_p-0.05_clusterk-50.tsv"),
            MZ,delimiter='\t',fmt='%.4f')

# export MB as tsv
np.savetxt(os.path.join(data_dir,"derivatives","nilearn_glm","group",
                        f"group_task-{task_label}_acq-{acq_label}_table-meanTvaluePerSub_con-{contrast_name_valid}_c-bonferroni_p-0.05_clusterk-50.tsv"),
            MB,delimiter='\t',fmt='%.4f')

print('DONE')


