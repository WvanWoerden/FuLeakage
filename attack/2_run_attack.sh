#!/bin/bash

echo "Starting attacks, please first run 1_download_sigs.sh to download signatures."

echo ""
echo "-------------------------------------------------------------------------------"
echo "----------------- Attack category 1 with 50,000 signatures --------------------"
echo "-------------------------------------------------------------------------------"
test -f downloads/cat1_sigs.txt || echo "Signature file doesn't exist, skipping"
test -f downloads/cat1_sigs.txt && python3 run_attack.py downloads/cat1_sigs.txt 1 50000

echo ""
echo "-------------------------------------------------------------------------------"
echo "----------------- Attack category 3 with 100,000 signatures -------------------"
echo "-------------------------------------------------------------------------------"
test -f downloads/cat3_sigs.txt || echo "Signature file doesn't exist, skipping"
test -f downloads/cat3_sigs.txt && python3 run_attack.py downloads/cat3_sigs.txt 3 100000

echo ""
echo "-------------------------------------------------------------------------------"
echo "----------------- Attack category 5 with 100,000 signatures -------------------"
echo "-------------------------------------------------------------------------------"
test -f downloads/cat5_sigs.txt || echo "Signature file doesn't exist, skipping"
test -f downloads/cat5_sigs.txt && python3 run_attack.py downloads/cat5_sigs.txt 5 100000
