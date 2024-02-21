#!/bin/bash

# This script downloads FuLeeca signatures for a single key and all three security levels
# Data available for manual download at https://zenodo.org/records/10653492
# The format starts with the secret key a,b on the first two rows.
# Then followed by signatures v = (x|y) with x,y on two separate rows.

mkdir -p downloads
cd downloads
echo "Downloading signatures files from Zenodo"
test -f cat1_sigs.tar.gz || wget -O cat1_sigs.tar.gz "https://zenodo.org/records/10653492/files/cat1_sigs.tar.gz?download=1"
test -f cat3_sigs.tar.gz || wget -O cat3_sigs.tar.gz "https://zenodo.org/records/10653492/files/cat3_sigs.tar.gz?download=1"
test -f cat5_sigs.tar.gz || wget -O cat5_sigs.tar.gz "https://zenodo.org/records/10653492/files/cat5_sigs.tar.gz?download=1"

echo "Unpacking signature files"
test -f cat1_sigs.txt || tar -xf cat1_sigs.tar.gz
test -f cat3_sigs.txt || tar -xf cat3_sigs.tar.gz
test -f cat5_sigs.txt || tar -xf cat5_sigs.tar.gz

cd ../
