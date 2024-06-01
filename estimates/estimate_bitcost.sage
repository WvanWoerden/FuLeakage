# requires lattice-estimator sage module:
# https://github.com/malb/lattice-estimator
from estimator.reduction import RC, cost
import numpy as np

estimates = np.loadtxt("../attack/data/blocksize_estimates.txt", dtype="int")
bit_estimates = []

print("{0:15} {1:15}".format("security Level", "bitcost"))
for i in range(estimates.shape[0]):
	cat, dim, beta = map(int, list(estimates[i]))
	bitcost = np.log2(cost(RC.MATZOV, beta, dim).get("rop"))
	print("{0:15} {1:.3f}".format(str(cat), bitcost))
	bit_estimates += [(cat, dim, beta, bitcost)]

np.savetxt("../attack/data/bitcost_estimates.txt", bit_estimates)
