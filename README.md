# FuLeakage

This repository contains the supplementary files to the paper "FuLeakage: Breaking FuLeeca by Learning Attacks", by Felicitas Hörmann & Wessel van Woerden.

The main attack script is available and documented in `attack/full_attack.py`.
We provide pre-generated FuLeeca signatures for one fixed key per FuLeeca parameter set at https://zenodo.org/records/10653492, and we supply a shell script to download these. 
In addition we provide a shell script to run the attack on the three corresponding instances.

## Running the attack

To run the attack clone or download this repository and move into the `attack` folder.
First, execute `attack/1_download_sigs.sh` to download the signature samples.
Note that unpacked the signature files take a total of about 6GB of disk space.
Then, run `attack/2_run_attack.sh` to start the learning attack and see how instances of all FuLeeca parameter sets are broken in real time.

```
git clone https://github.com/WvanWoerden/FuLeakage.git
cd FuLeakage/attack
./1_download_sigs.sh
./2_run_attack.sh
```
