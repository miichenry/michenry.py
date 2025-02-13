#!/bin/bash
#SBATCH --partition=public-cpu,shared-cpu,shared-bigmem,public-bigmem #,public-cpu,public-bigmem
#SBATCH --job-name=symmetric_stack_time
#SBATCH --ntasks=20           
#SBATCH --cpus-per-task=1 
#SBATCH --mem=300G          
#SBATCH --time=12:00:00   
#SBATCH --output="outslurm/%x-%j.out"
#SBATCH --mail-type=BEGIN,END
##SBATCH --mail-user=michail.henry@etu.unige.ch
###SBATCH --mem-per-cpu=20G               # Total memory requested, shared among all CPUs (divide mem 

source /opt/ebsofts/Anaconda3/2022.05/etc/profile.d/conda.sh
conda activate noisepy

PARAMS="symmetric_stack_time_para.yaml"
SCRIPT="symmetric_stack_time.py"

python -u $SCRIPT $PARAMS
