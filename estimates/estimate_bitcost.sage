# This scripts turns the blocksize estimates from estimate_reduction.sage
# into a bitcost estimate using the lattice-estimator library.

# requires lattice-estimator sage module:
# https://github.com/malb/lattice-estimator
from estimator.reduction import RC, cost
import numpy as np

estimates = np.loadtxt("../attack/data/blocksize_estimates.txt", dtype="int")
bit_estimates = []

print("Bitcost estimates for a lattice reduction attack on the full and leaked sublattice.")
print("These attacks do not run in polynomial time, but only require a few signatures as opposed to the full learning attack.")
print("{0:15} {1:15}".format("security level", "bitcost"))
for i in range(estimates.shape[0]):
	cat, dim, beta = map(int, list(estimates[i]))
	bitcost = np.log2(cost(RC.MATZOV, beta, dim).get("rop"))
	print("{0:15} {1:.3f}".format(str(cat), bitcost))
	bit_estimates += [(cat, dim, beta, bitcost)]

np.savetxt("../attack/data/bitcost_estimates.txt", bit_estimates)
