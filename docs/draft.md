---
title: Optimizing MR temporal resolution for Neurofeedback
subject: Paper draft
subtitle: 
short_title: 
date: 2023-06-07
authors:
  - name: Alexandre Sayal
    affiliations:
      - CIBIT, University of Coimbra, Portugal
    orcid: 0000-0002-0476-9533
    email: alexandre.campos@uc.pt
  - name: Bruno Direito
    affiliations:
      - CIBIT, University of Coimbra, Portugal
    orcid: 
    email: 
  - name: Teresa Sousa
    affiliations:
      - CIBIT, University of Coimbra, Portugal
    orcid: 
    email:
  - name: Miguel Castelo-Branco
    affiliations:
      - CIBIT, University of Coimbra, Portugal
    orcid: 
    email: 
license: CC-BY-4.0
keywords: fmri, temporal resolution, neurofeedback
exports:
  - format: pdf
    output: exports/paper.pdf
  - format: docx
    output: exports/paper.docx
bibliography:
  - docs/my_references.bib
---

+++ {"part": "abstract"}

ABSTRACT

+++

## Introduction

### Research questions

**Does increasing temporal resolution of fMRI improve estimates of real-time feedback information?**

- How is the SNR affected?
- Is the feedback more immersive or more erractic?
- Does the feedback signal change depending on the temporal resolution?
- Are offline estimates/conclusions any different?
- Is ROI location the same?

## Methods

### Participants
Fifteen healthy participants were recruited for this experiment (6 female, mean age 29.7 $\pm$ 8.4 years), with normal or corrected-to-normal vision and no history of neurological or psychiatric diseases. All participants were right-handed, as confirmed by a handedness questionnaire adapted from (Oldfield, 1971): mean laterality index of 85.0 $\pm$ 9.0. All gave informed written consent before participating in accordance with the declaration of Helsinki, and the study followed the safety guidelines for magnetic resonance imaging research on humans. The work was approved by the Ethics Committee of the Faculty of Medicine of the University of Coimbra.

### fMRI data acquisition
Scanning was performed on a 3T Siemens Magnetom Prismafit, using a 64-channel head coil, at the Institute of Nuclear Sciences Applied to Health (ICNAS), University of Coimbra, Portugal. The scanning session started with the acquisition of one 3D anatomical magnetization-prepared rapid acquisition gradient echo (MPRAGE) pulse sequence (TR = 2530 ms, echo time (TE) = 3.42 ms, flip angle (FA) = 7°, 176 slices, voxel size 1.0 × 1.0 × 1.0 mm, field of view (FOV) = 256 × 256 mm).

A total of seven functional runs were acquired using a 2D multi-band (MB) gradient-echo (GE) echo-planar imaging (EPI) sequence from the Center for Magnetic Resonance Research, University of Minnesota (Release R016a). We tested four different resolutions: TR = 500 ms (MB factor = 6, FA = 53°), TR = 750 ms (MB factor = 4, FA = 63°), TR = 1000 ms (MB factor = 3, FA = 68°), TR = 2500 ms (MB factor = 0, FA = 85°). The remaining parameters were matched: TE = 30.2 ms, 42 interleaved slices with 0.5 mm gap, voxel size 2.5 × 2.5 × 2.5 mm, FoV 192 × 192 mm.

To allow susceptibility artifact correction, we acquired a pair of spin-echo images with anterior-posterior (AP) and posterior-anterior (PA) phase encoding polarity with matching geometry and echo-spacing to each of the functional scans. These were acquired before the functional runs.

### Stimulus
The stimulus used in this experiment is a moving plaid, created by superimposing two moving gratings ([](#stimulus_img) B). This superimposition creates an intrinsically ambiguous and bistable stimulus that can be perceived as moving coherently or incoherently ([](#stimulus_img) C and D) ([](doi:10.1016/j.neuroimage.2018.06.075)).
To force the perception of one of these equally possible motion interpretations, we added dots to the plaid, which help disambiguate motion ([](#stimulus_img) E). Depending on the relative percentage of dots that move vertically or horizontally, we induce a given level of coherence, and hence a perceptual interpretation to the observer. The complete description of the stimulus properties is provided in ([](doi:10.1016/j.neuroimage.2018.06.075)).

:::{figure} ./images/stimulus.png
:name: stimulus_img
Stimuli used in this experiment. A) Functional localizer used to map V1 and hMT+ in each participant's visual cortex. Moving dots were shown inside a circular aperture at the center of a black screen. Panels B, C, and D illustrate a plaid stimulus. By superimposing two gratings (B), moving orthogonally to the lines, a bistable stimulus is created, which can be perceived moving coherently (C) as a single surface or incoherently (D) as two separate surfaces sliding over each other. The arrows illustrate the direction of perceived motion. E) Plaid stimulus used during the unambiguous runs. Depending on the moving dots' direction, the otherwise ambiguous stimulus was readily perceived as a plaid moving coherently or incoherently. Adapted from ([](doi:10.1016/j.neuroimage.2018.06.075)).
:::

### Paradigm

The acquisition session comprised one anatomical sequence, three types of field map sequences, one functional localizer, and four pairs of functional task runs ([](#session_img)). In total, the scanning session lasted for approximately 70 minutes.

:::{figure} ./images/sessionprotocol.drawio.svg
:name: session_img
Overview of the acquisition session (A). The session starts with the acquisition of an anatomical T1w image, followed by the localizer run (trial shown in panel B). Then, for each TR (0.5, 0.75, 1, 2.5 s), both SpinEcho field maps are acquired, followed by one ambiguous and one unambiguous task run (trial shown in panel C).
:::

#### Functional localizer for the visual regions
The goal of this run was to localize the two regions of interest in each participant's visual cortex - V1 and hMT+. For this purpose, 350 white dots (diameter of 0.08º) were shown inside a 9º circular aperture at the center of a black screen ([](#stimulus_img) A). Blocks of 6 s with dots moving (3º/s) in all eight cardinal and intermediate directions were interleaved with 6 s blocks of fixation (only the fixation cross was shown) and 6 s blocks of static dots. A central red cross (width of 0.67º) was displayed as a fixation target at the visual midline. The run lasted for 2.9 min, composed of nine trials.

#### Ambiguous and Unambiguous tasks
The trial in these runs is composed of three conditions: 'static' (static plaid), 'motion' (ambiguous or unambiguous moving plaid), and 'MAE' (a period during which motion aftereffect is expected) - ([](#session_img) C). During the ambiguous runs, the 'motion' condition showed the participants the moving plaid without any overlaid dots. As such, the stimulus is entirely ambiguous (the percept alternates between coherent and incoherent). Here, the participants were instructed to report the perceived type of motion (coherent or incoherent) using two buttons of a response box.
During the unambiguous runs, the plaid is shown with overlaid dots moving either coherently down or incoherently inwards, which disambiguates the percept. Based on the responses given by the participant in the previous ambiguous run, we manipulated the switches between coherent and incoherent motion to match the previous responses precisely. This matched the time of each percept across both types of run. The participants received the same instruction - to report the perceived type of motion at all times.


### fMRI data preprocessing
- The dataset was organized according to the BIDS specification. The data was converted to NifTI using dcm2niix and then translated to BIDS using BIDSkit.

- The anatomical and functional images were preprocessed using fmriprep (v23.0.2).

- mriqc was used to estimate a number of quality metrics for the anatomical and functional images.

- The activation maps were generated using nilearn.

### fMRI data analysis

Regarding the localizer data, the regions of interest V1 and hMT+ were functionally localized using a standard GLM analysis, considering the contrast 'Static > Fixation' and 'Motion > Static', respectively, at the group level.

## Results

### Localizer results - ROI definition

:::{figure} #loc_singlesubject
:name: loc_singlesubject_plot
A very cool image.
:::

A very interesting analysis performed on jupyter notebooks and exported here in [](#loc_group_interactive_plot).

:::{figure} #loc_group_interactive
:name: loc_group_interactive_plot
A very cool image.
:::

### Impact on the image quality

### Impact on the feedback signal

### Impact on the ROI location

### Offline ROI estimates


## Discussion


