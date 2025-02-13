#!/bin/bash
# NB: When defining Slurm SBATCH parameters, there is only one "#" before "SBATCH", if there are 2, this line is commented.
#SBATCH --job-name=delete_miniseed  # create a name for your job
#SBATCH --partition=public-cpu,shared-cpu,shared-bigmem #,public-cpu,public-bigmem # list of partitions to use (remember each partition has their own constraints!)
##SBATCH --ntasks=1              # total number of parallel tasks in MPI (increase for more speed, but see below)
#SBATCH --cpus-per-task=2        # cpu-cores per task (always choose 1 here)
###SBATCH --mem-per-cpu=20G               # Total memory requested, shared among all CPUs (divide mem 
##SBATCH --mem=100G                # by ntasks to get memory allocated per task) also option to use mem = 800G (total mem needed for all ntasks in 1 node)
#SBATCH --time=12:00:00          # total run time limit (HH:MM:SS) (keep in mind limits of partition requested)
#SBATCH --output="%x-%j.out"   # Path where to write output files. Change as you want. %j is job ID, %x is job-name defined above.
#SBATCH --mail-type=BEGIN,END         # if you want to get an email when your job is done
##SBATCH --mail-user=michail.henry@etu.unige.ch

source /opt/ebsofts/Anaconda3/2022.05/etc/profile.d/conda.sh
conda activate noisepy

python mika_scripts/rename_station2SN.py > rename.txt
cat rename.txt
