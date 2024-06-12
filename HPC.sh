#!/bin/bash

#SBATCH --job-name DDauto4
#SBATCH --nodes 1
#SBATCH --cpus-per-task 40
#SBATCH --mem 60gb
#SBATCH --time 72:00:00
#SBATCH --constraint interconnect_fdr
#SBATCH --constraint cpu_gen_cascadelake

# change the operating directory
cd $SLURM_SUBMIT_DIR

sandBoxDir="/home/${USER}/apptainer/archDDD.sandbox"

apptainer exec $sandBoxDir python main.py

