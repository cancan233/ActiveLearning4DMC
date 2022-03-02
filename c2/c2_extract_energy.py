from ase.io import read, write
from ase import Atoms
from ase.io.trajectory import TrajectoryReader as tr
from ase.io.trajectory import TrajectoryWriter as tw

import numpy as np
import os
import sys
import subprocess
import copy
from pathlib import Path


def extract_structure(filename):
    structure = []
    lookup = "ATOMIC_POSITIONS bohr"
    with open(filename, "r") as f:
        content = f.readlines()
        for i in range(len(content)):
            if lookup in content[i]:
                break
        structure.append(content[i + 1].split())
        structure.append(content[i + 2].split())

    return structure


def main():
    """
    usage: python extract_energy.py [targetdir] [dmc]
            e.g. python extract_energy.py ./dft/scale
    """
    targetdir = sys.argv[1]
    parentdir = "/".join(targetdir.split("/")[:-2])
    datadir = sorted(os.listdir(targetdir))
    print(datadir)

    dft_traj = tw(parentdir + os.sep + "dft.traj")
    if sys.argv[2] == "dmc":
        dmc_traj = tw(parentdir + os.sep + "dmc.traj")

    fake_force = [[0.1, 0.1, 0.1], [0.1, 0.1, 0.1], [0.1, 0.1, 0.1]]

    for scale in datadir[:-2]:
        # for scale in datadir:
        print(scale)
        structure = extract_structure(targetdir + os.sep + scale + os.sep + "scf.in")
        c2 = Atoms(
            "C2",
            positions=[
                (
                    float(structure[0][1]) * 0.529177,
                    float(structure[0][2]) * 0.529177,
                    float(structure[0][3]) * 0.529177,
                ),
                (
                    float(structure[1][1]) * 0.529177,
                    float(structure[1][2]) * 0.529177,
                    float(structure[1][3]) * 0.529177,
                ),
            ],
            cell=[
                28.34589199 * 0.529177,
                28.34589199 * 0.529177,
                28.34589199 * 0.529177,
            ],
        )
        with open(targetdir + os.sep + scale + os.sep + "scf.out") as file:
            lines = file.readlines()
        dft_output_energy = 0
        dft_output_forces = []
        dmc_energy, uncertainty = 0, 0
        for i in range(len(lines)):
            if "!" == lines[i][0]:
                dft_output_energy = float(lines[i].split()[4]) * 13.605662285137
            if "Forces acting on atoms (cartesian axes, Ry/au)" in lines[i]:
                dft_output_forces.append(
                    [float(i) * 25.71104309541616 for i in lines[i + 2].split()[-3:]]
                )
                dft_output_forces.append(
                    [float(i) * 25.71104309541616 for i in lines[i + 3].split()[-3:]]
                )
        dft_traj.write(
            c2, energy=dft_output_energy, forces=dft_output_forces,
        )
        if sys.argv[2] == "dmc":
            dmc_output = subprocess.check_output(
                "qmca -e 50 -q e -u eV "
                + targetdir
                + os.sep
                + scale
                + os.sep
                + "qmc.s001.scalar.dat",
                shell=True,
            )
            dmc_energy, uncertainty = (
                float(dmc_output.split()[5]),
                float(dmc_output.split()[7]),
            )

            c2.info["uncertainty"] = uncertainty
            dmc_traj.write(c2, energy=dmc_energy, forces=fake_force)

    dft_traj = tr(parentdir + os.sep + "dft.traj")
    for traj in dft_traj:
        print(traj.get_potential_energy())
    print("DFT: {}".format(len(dft_traj)))

    if sys.argv[2] == "dmc":
        dmc_traj = tr(parentdir + os.sep + "dmc.traj")
        for traj in dmc_traj:
            print(traj.get_potential_energy())
            print(traj.info["uncertainty"])
        print("DMC: {}".format(len(dmc_traj)))


if __name__ == "__main__":
    main()
