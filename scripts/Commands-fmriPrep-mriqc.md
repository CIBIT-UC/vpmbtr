# Use these commands to run fmriprep and mriqc
- [Use these commands to run fmriprep and mriqc](#use-these-commands-to-run-fmriprep-and-mriqc)
  - [fmriPrep](#fmriprep)
    - [Open screen](#open-screen)
    - [fmriPrep with docker](#fmriprep-with-docker)
    - [Participant 07 needed unstable version to run](#participant-07-needed-unstable-version-to-run)
  - [mriqc](#mriqc)
    - [Open screen](#open-screen-1)
    - [mriqc with docker (participant level)](#mriqc-with-docker-participant-level)
    - [mriqc with docker (group level)](#mriqc-with-docker-group-level)

All paths are specific to the machine where the commands were run (sim01). They should be changed accordingly. Use one screen per participant for fmriPrep.

## fmriPrep

### Open screen

    screen -L -Logfile /DATAPOOL/home/alexandresayal/GitRepos/vpmb-tr/data/fmriprep-logs/vpmb-spe_fmriprep_sub-22.txt -S vpmb-22

### fmriPrep with docker

    docker run -ti --rm \
        -v /DATAPOOL/VPMB/BIDS-VPMB-SPE:/data:ro \
        -v /DATAPOOL/VPMB/BIDS-VPMB-SPE/derivatives/fmriprep23:/out \
        -v /SCRATCH/users/alexandresayal/fmriprep23-work-vpmb:/work \
        -v /SCRATCH/software/freesurfer/license.txt:/license \
        nipreps/fmriprep:23.0.2 \
        /data /out/fmriprep \
        participant \
        -w /work \
        --fs-license-file /license \
        --nprocs 18 \
        --stop-on-first-crash \
        --output-spaces MNI152NLin2009cAsym:res-2 T1w \
        --participant-label 22

### Participant 07 needed unstable version to run

    docker run -ti --rm \
        -v /DATAPOOL/VPMB/BIDS-VPMB-SPE:/data:ro \
        -v /DATAPOOL/VPMB/BIDS-VPMB-SPE/derivatives/fmriprep23:/out \
        -v /SCRATCH/users/alexandresayal/fmriprep23-work-vpmb:/work \
        -v /SCRATCH/software/freesurfer/license.txt:/license \
        nipreps/fmriprep:unstable \
        /data /out/fmriprep \
        participant \
        -w /work \
        --fs-license-file /license \
        --nprocs 18 \
        --stop-on-first-crash \
        --output-spaces MNI152NLin2009cAsym:res-2 T1w \
        --participant-label 07

## mriqc

### Open screen
    screen -L -Logfile /DATAPOOL/home/alexandresayal/GitRepos/vpmb-tr/data/fmriprep-logs/vpmb-spe_mriqc.txt -S vpmb-mriqc

### mriqc with docker (participant level)

    docker run -it --rm \
        -v /DATAPOOL/VPMB/BIDS-VPMB-SPE:/data:ro \
        -v /DATAPOOL/VPMB/BIDS-VPMB-SPE/derivatives/mriqc:/out \
        -v /SCRATCH/users/alexandresayal/mriqc-work:/scratch \
        nipreps/mriqc:23.0.1 \
        /data /out participant \
        --participant_label 01 02 03 05 06 07 08 10 11 12 15 16 21 22 23 \
        --nprocs 30 \
        --omp-nthreads 30 \
        --work-dir /scratch \
        --species human

### mriqc with docker (group level)

    docker run -it --rm \
        -v /DATAPOOL/VPMB/BIDS-VPMB-SPE:/data:ro \
        -v /DATAPOOL/VPMB/BIDS-VPMB-SPE/derivatives/mriqc:/out \
        -v /SCRATCH/users/alexandresayal/mriqc-work:/scratch \
        nipreps/mriqc:23.0.1 \
        /data /out group \
        --nprocs 30 \
        --omp-nthreads 30 \
        --work-dir /scratch \
        --species human