#!/bin/bash

#SBATCH --job-name DDauto5
#SBATCH --nodes 1
#SBATCH --cpus-per-task 40
#SBATCH --mem 60gb
#SBATCH --time 72:00:00
#SBATCH --constraint interconnect_fdr
#SBATCH --constraint cpu_gen_cascadelake

# variables
SANDBOXDIR="/home/${USER}/apptainer/archDDD.sandbox"
MICROSTRUCTEXE=/home/$USER/bin/apptainer_compiled/cascadelake/microstructureGenerator_cascade
DDOMPEXE=/home/$USER/bin/apptainer_compiled/cascadelake/DDomp_cascade

# change the working directory to the directory where the job is submitted
cd $SLURM_SUBMIT_DIR

# copy the binaries compiled on HPC to the MoDELib2 binary directories
cp $MICROSTRUCTEXE ./MoDELib2/tools/DDomp/build/DDomp
cp $DDOMPEXE ./MoDELib2/tools/MicrostructureGenerator/build/microstructureGenerator

# run automation script through a sandbox container
apptainer exec $SANDBOXDIR python main.py

