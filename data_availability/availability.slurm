#!/bin/bash
#SBATCH --partition=public-cpu,shared-cpu,shared-bigmem,public-bigmem #,public-cpu,public-bigmem
#SBATCH --job-name=data_availability
#SBATCH --ntasks=1           
#SBATCH --cpus-per-task=2
#SBATCH --time=12:00:00   
#SBATCH --output="outslurm/%x-%j.out"
#SBATCH --mail-type=BEGIN,END

source /opt/ebsofts/Anaconda3/2022.05/etc/profile.d/conda.sh
conda activate noisepy

PARAMS="data_availability_params.yaml"
SCRIPT="data_availability.py"

python -u $SCRIPT $PARAMS
