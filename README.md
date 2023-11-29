# vpmb-tr
Optimizing MR temporal resolution for Neurofeedback

**Does increasing temporal resolution of fMRI improve estimates of real-time feedback information?**

- Are offline estimates/conclusions any different?
  - Beta and t-values of ROIs
- Is the feedback more immersive (faster reaction) or more erratic/variable/discrete?
  - Estimate the latency between perceptual change and bold response using the beta estimate of the GLM - with predictors for coherent and incoherent trials - per TR
  - Estimate the latency between the perceptual change and the BOLD response (time course) - bold changes faster for the lower TR?
- Does the feedback signal (estimated based on BOLD percent signal change of a ROI) change depending on the temporal resolution?
- Estimate inter-hemispheric correlation to use as feedback - how does it change depending on the TR?
  - Feedback of perceptual switch based on a rule - identification ratio and lag (How fast can we inform the participant about the perceptual change?)
