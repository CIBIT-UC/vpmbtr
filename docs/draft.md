# Methods

## fMRI data processing
The dataset was organized according to the BIDS specification. The data was converted to NifTI using dcm2niix and then translated to BIDS using BIDSkit.

The anatomical and functional images were preprocessed using fmriprep (v23.0.2).

The activation maps were generated using nilearn.


