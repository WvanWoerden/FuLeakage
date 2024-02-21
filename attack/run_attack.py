# @2024 Felicitas Hörmann & Wessel van Woerden
# helper script to run attack on signature file
# python3 run_attack.py file cat sigs
# example: python3 run_attack.py downloads/cat3_sigs.txt 3 100000

import time
import sys
from full_attack import attack

assert (len(sys.argv) >= 3)
file = sys.argv[1]
cat = int(sys.argv[2])
if len(sys.argv) == 4:
    sigs = int(sys.argv[3])
else:
    sigs = None

start_time = time.time()
attack(file, cat, sigs)
print("--- %s seconds ---" % (time.time() - start_time))
