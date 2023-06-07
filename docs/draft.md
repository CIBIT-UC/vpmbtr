---
title: Optimizing MR temporal resolution for Neurofeedback
subject: Paper
subtitle: 
short_title: 
authors:
  - name: Alexandre Sayal
    affiliations:
      - CIBIT, University of Coimbra, Portugal
    orcid: 0000-0002-0476-9533
    email: alexandre.campos@uc.pt
license: CC-BY-4.0
keywords: fmri, temporal resolution, neurofeedback
exports:
  - format: pdf
    output: exports/paper.pdf
  - format: docx
    output: exports/paper.docx
---

+++ {"part": "abstract"}


We introduce, a set of open-source, community-driven ...


+++
# Introduction

## Research questions

**Does increasing temporal resolution of fMRI improve estimates of real-time feedback information?**

- How is the SNR affected?
- Is the feedback more immersive or more erractic?
- Does the feedback signal change depending on the temporal resolution?
- Are offline estimates/conclusions any different?
- Is ROI location the same?

# Methods

## Participants
Fifteen healthy participants were recruited for this experiment (6 female, mean age 29.7 $\pm$ 8.4 years), with normal or corrected-to-normal vision and no history of neurological or psychiatric diseases. All participants were right-handed, as confirmed by a handedness questionnaire adapted from (Oldfield, 1971): mean laterality index of 85.0 $\pm$ 9.0. All gave informed written consent before participating in accordance with the declaration of Helsinki, and the study followed the safety guidelines for magnetic resonance imaging research on humans. The work was approved by the Ethics Committee of the Faculty of Medicine of the University of Coimbra.

## fMRI data acquisition
Scanning was performed on a 3T Siemens Magnetom Prismafit, using a 64-channel head coil, at the Institute of Nuclear Sciences Applied to Health (ICNAS), University of Coimbra, Portugal. The scanning session started with the acquisition of one 3D anatomical magnetization-prepared rapid acquisition gradient echo (MPRAGE) pulse sequence (TR = 2530 ms, echo time (TE) = 3.42 ms, flip angle (FA) = 7°, 176 slices, voxel size 1.0 × 1.0 × 1.0 mm, field of view (FOV) = 256 × 256 mm).

A total of seven functional runs were acquired using a 2D multi-band (MB) gradient-echo (GE) echo-planar imaging (EPI) sequence from the Center for Magnetic Resonance Research, University of Minnesota (Release R016a). We tested four different resolutions: TR = 500 ms (MB factor = 6, FA = 53°), TR = 750 ms (MB factor = 4, FA = 63°), TR = 1000 ms (MB factor = 3, FA = 68°), TR = 2500 ms (MB factor = 0, FA = 85°). The remaining parameters were matched: TE = 30.2 ms, 42 interleaved slices with 0.5 mm gap, voxel size 2.5 × 2.5 × 2.5 mm, FoV 192 × 192 mm.

To allow susceptibility artifact correction, we acquired a pair of spin-echo images with anterior-posterior (AP) and posterior-anterior (PA) phase encoding polarity with matching geometry and echo-spacing to each of the functional scans. These were acquired before the functional runs.

## fMRI data processing
The dataset was organized according to the BIDS specification. The data was converted to NifTI using dcm2niix and then translated to BIDS using BIDSkit.

The anatomical and functional images were preprocessed using fmriprep (v23.0.2) [](doi:10.1145/3411764.3445648).

The activation maps were generated using nilearn.

# Results

## Impact on the image quality

## Impact on the feedback signal

## Impact on the ROI location

## Offline ROI estimates


# Discussion



