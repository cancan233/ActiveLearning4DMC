#!/bin/bash

#SBATCH --account=brubenst-condo

#SBATCH --time=100:00:00
#SBATCH --nodes=1
#SBATCH --tasks-per-node=16
#SBATCH -J c2_dft_lda
#SBATCH --mem=48G

# set environment
module load mpi/openmpi_4.0.5_intel_2020.2_slurm20 intel/2020.2
module load quantumespresso/6.4_openmpi_4.0.5_intel_2020.2_slurm20
module load mpi/hpcx_2.7.0_gcc_10.2_slurm20 gcc/10.2 hdf5/1.10.5_openmpi_4.0.5_gcc_10.2_slurm20 boost/1.69 python/3.7.4 intel/2020.2
module load gcc/10.2 mpi/openmpi_4.0.5_gcc_10.2_slurm20
module load qmcpack/3.9.2_hpcx_2.7.0_gcc_10.2_slurm20
source /gpfs/data/brubenst/chuang25/pythonvirtualenv/ml/bin/activate

# run command
python c2_dft.py
