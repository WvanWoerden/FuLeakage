# FuLeakage

This repository contains the supplementary files to the paper "FuLeakage: Breaking FuLeeca by Learning Attacks", by Felicitas Hörmann & Wessel van Woerden.

The main attack script is available and documented in `attack/full_attack.py`.
We provide pre-generated FuLeeca signatures for one fixed key per FuLeeca parameter set at https://zenodo.org/records/10653492, and we supply a shell script to download these. 
In addition we provide a shell script to run the attack on the three corresponding instances.

## Dependencies
Dependencies required to run the attack including the version on which the script has been tested.

- Python 3 (3.12.3)
- Numpy (1.26.4)
- Scipy (1.13.0)
- Bash (5.2.26)

We expect that recent but older versions are also sufficient to run the attack. For Windows we recommend to run the scripts in Windows Subsystem for Linux (WSL).
Furthermore, for the estimator scripts in `estimates/` one requires

- SageMath (10.3)
- lattice-estimator https://github.com/malb/lattice-estimator (commit 25f9e887700442f8bbaac4079c2f9f1e444cb146)

The script `estimate_bitcost.sage` assumes that the lattice-estimator is available in the same directory or installed as a Sage module.

## Running the attack

To run the attack clone or download this repository and move into the `attack` folder.
First, execute `attack/1_download_sigs.sh` to download the signature samples.
Note that the unpacked signature files take a total of about 6GB of disk space.
Then, run `attack/2_run_attack.sh` to start the learning attack and see how instances of all FuLeeca parameter sets are broken in real time.

```
git clone https://github.com/WvanWoerden/FuLeakage.git
cd FuLeakage/attack
./1_download_sigs.sh
./2_run_attack.sh
```

## Running the estimate scripts
To run the estimate scripts clone or download this repository and move into the `estimates` folder.
Make sure the lattice-estimator sage module is installed or that the `estimator` folder of the lattice-estimator is copied to the `estimates` folder.

```
git clone https://github.com/WvanWoerden/FuLeakage.git
git clone https://github.com/malb/lattice-estimator.git
cp -r lattice-estimator/estimator FuLeakage/estimates/
cd FuLeakage/estimates
sage estimate_reduction.sage
sage estaimte_bitcost.sage
```

The script `estimates/estimate_reduction.sage` computes the required BKZ blocksize for all three parameter sets for the full construction-A lattice and the leaked sublattice. 
This information is then stored in `attack/data/blocksize_estimates.txt`.

The script `estimates/estimate_bitcost.sage` takes these blocksize estimates and gives a bitcost estimate using the lattice-estimator. The resulting bitcost estimates are stored in `attack/data/bitcost_estimates.txt`.

## Organization of files

```
/attack                         # attack scripts
/attack/data/D*.txt             # precomputed Avg[x_i^2].
/attack/full_attack.py          # main attack script
/attack/run_attack.py           # helper script to run the attack
/attack/1_download_sigs.sh      # shell script to download signatures
/attack/2_run_attack.sh         # shell script that runs the attack
/attack/params.py               # FuLeeca parameters
/attack/estimates               # estimation scripts
/attack/estimate_reduction.sage # BKZ blocksize estimator
/attack/estimate_bitcost.sage   # bitcost estimator
```
