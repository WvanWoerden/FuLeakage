# @2024 Felicitas Hörmann & Wessel van Woerden
# Full key-recovery attack against FuLeeca
import numpy as np
import scipy as sc
import scipy.linalg
import sys
import time
from params import get_fuleeca_parameters

# Loads the samples from a signature file
# The secret key and each signature consists of two vectors (v,w)
# This function assumes these are stored on two consecutive lines in the comma-separated file'
# The file starts with the secret key, followed by any number of signatures
def load_samples(file, q, n_half, sigs=None):
    print("Loading signatures...")
    if sigs is None:
        S = np.loadtxt(file, delimiter=",", dtype="int")
    else:
        S = np.loadtxt(file, delimiter=",", dtype="int", max_rows=2 * sigs + 2)
    S -= (S > q / 2.) * q  # normalize to (-q/2, q/2]

    # first two lines are the secret vectors a and b
    a_vec = S[0]
    b_vec = S[1]

    # remaining lines are signature vectors v1 \n v2
    V = S[2:]
    if sigs is None:
        sigs = V.shape[0] // 2
    assert (V.shape[1] == n_half)
    assert (V.shape[0] // 2 == sigs)
    V = V.reshape((V.shape[0] // 2, 2 * n_half))
    # only consider first half of signatures for the attack
    V_samples = V[:, :n_half]
    print("Loaded " + str(sigs) + " signatures.")
    return V_samples, a_vec, b_vec


def get_singular_value_guess(V):
    print("Computing approximation of E[v^tv]...")
    sigs = V.shape[0]
    n_half = V.shape[1]
    VV = np.zeros((n_half, n_half))
    for i in range(sigs):
        VV += np.outer(V[i], V[i])
    VV /= sigs

    print("Loading precomputed data...")
    # precomputed values of E[x_i^2] obtained from 2,500,000 signatures
    d = np.loadtxt("data/D" + str(n_half) + ".txt")
    DD = sc.linalg.circulant(d)
    # We know that on expectation E[VV] = A^t*D*A + E, for D = diag((E[x_i^2])_i).
    # Where the (toric) diagonals of E are somewhat constant (but different per diagonal)
    # We thus get a set of approximate equations diag_j(E[VV]) ~= diag_j(A*D*A^t) + c_i
    # from which we can approximately derive the values of a_i * a_{i+j} + c_i' for all i.
    # These equations are of full rank (which would not be the case if D was constant),
    # we thus exploit the bias in the values of E[x_i^2].
    # So we approximately obtain aa := a^t * a + C' with C' somewhat constant on each diagonal
    # Now we extract (an approximation of) a by computing an optimal rank-1 approximation of aa,
    # using the singular-value decomposition
    print("Obtaining guess using singular-value decomposition...")
    aa = np.zeros((n_half, n_half), dtype="double")
    for j in range(n_half):
        c = [VV[i, (i + j) % n_half] for i in range(n_half)]
        b = np.linalg.solve(DD, c)
        for i in range(n_half):
            aa[i, (i + j) % n_half] = b[i]
    a_svd_guesses = np.linalg.svd(aa)[2]
    return a_svd_guesses


# get solution by selecting x_i from multiple signatures that are close to integer already
# not in use at the moment
def get_solution_best_roundings(a_approx, V_samples, a_nrm, statistics):
    # recover from best roundings
    n_half = a_approx.shape[0]
    sigs = V_samples.shape[0]
    Aguess = sc.linalg.circulant(a_approx).transpose()
    Aginv = np.linalg.inv(Aguess)
    X_approx = np.dot(V_samples, Aginv)
    X_exact = np.rint(X_approx)
    Xdists = np.linalg.norm(X_approx - X_exact, axis=1) ** 2

    Vshifts = np.zeros((n_half, n_half), dtype="float")
    xx = np.zeros(n_half, dtype="float")
    bestind = np.argsort(Xdists)[:n_half]
    for i in range(n_half):
        j = np.argmin(np.abs(X_exact[bestind[i]] - X_approx[bestind[i]]))
        xx[i] = X_exact[bestind[i], j]
        Vshifts[i] = np.roll(V_samples[bestind[i]], -j)

    res = np.linalg.solve(Vshifts, xx)
    a_exact = np.linalg.inv(sc.linalg.circulant(res))[0]

    if np.linalg.norm(a_exact - np.rint(a_exact)) < 0.001 and np.abs(np.linalg.norm(np.rint(a_exact)) - a_nrm) < 1:
        print("Best rounding succeeded!")
        statistics["recovered_at"] = "best_rounding"
        a_exact = np.rint(a_exact)
        solved = True

    statistics["a_dist_bestind"] = a_dist(a_exact)
    print("Best indices:", statistics["a_dist_bestind"])
    return a_exact, solved


# This function tries to turn the approximate guess into a full solution by using the short signature vectors
# Let A=circulant(a) be the real secret key, and A'=circulant(a_guess) the approximation.
# For each signature v = x * A we compute an approximation x' = (A')^(-1) * v
# and round x'' = roundtoint(x')
# if x==x'' then we can recover A by solving v = x'' * A for circulant A.
# we check if x==x'' by checking that the solution A is (close to) integral and has the right norm
# which is very unlikely to happen for x!=x''. 
# if it fails it returns that average over all solutions A.
def get_solution_or_averaging(a_approx, V_samples, a_nrm, statistics):
    n_half = a_approx.shape[0]
    sigs = V_samples.shape[0]
    Aguess = sc.linalg.circulant(a_approx).transpose()
    Aginv = np.linalg.inv(Aguess)

    X_approx = np.dot(V_samples, Aginv)
    X_exact = np.rint(X_approx)

    # try to recover a from any signature
    # no early abort for statistics
    avg_a = np.zeros(n_half, dtype="float")
    a_sol = False
    solved = False
    for i in range(sigs):
        a_try = sc.linalg.solve_circulant(X_exact[i], V_samples[i], singular="lstsq")
        a_exact = np.rint(a_try)
        avg_a += a_exact
        if np.all(np.abs(a_try - a_exact) < 0.001) and np.abs(np.linalg.norm(a_exact) - a_nrm) < 1.:
            statistics["recovered_at"] = "all_sigs_averaging"
            a_sol = a_exact
            solved = True

    avg_a /= sigs
    return avg_a, solved, a_sol

# This function runs the learning attack
# Input parameters:
# file: location of file with signatures
# cat:  security level [1,3,5]
# sigs: number of signatures used (<= #signatures in file)
def attack(file, cat=1, sigs=None):
    statistics = {
        "a_dist_singular_value": None,
        "a_dist_typical": None,
        "a_dist_bestind": None,
        "a_dist_average": [],
        "a_dist_average_typical": [],
        "recovered_at": None,
        "averaging_iterations": 0,
        "attempt": None,
        "recovered": False
    }

    print("Loading FuLeeca parameters...")
    p, n, w_key, hamming_wt_key, squared_norm_key, _ = get_fuleeca_parameters(cat)
    q = p
    n_half = n // 2
    a_nrm = np.sqrt(squared_norm_key)  # l2 norm of typical a vec

    V_samples, a_vec, b_vec = load_samples(file, q, n_half, sigs)
    sigs = V_samples.shape[0]

    # get absolute typical vec from a_vec to limit dependencies
    # could also load precomputed value as a_typical is fixed for each category
    a_typical = np.sort(np.abs(a_vec))

    def make_typical(a):
        order = np.argsort(np.abs(a))
        a_ret = np.zeros(a.shape[0], dtype="int")
        for i in range(a.shape[0]):
            a_ret[order[i]] = np.sign(a[order[i]]) * a_typical[i]
        return a_ret

    # get a_dist for statistics, not used in attack
    def a_dist(a_g):
        dist = min(np.linalg.norm(a_g - a_vec), np.linalg.norm(a_g + a_vec))
        return dist

    # ------------- STEP 1: singular-value estimate ---------------------------------
    print("\n------------- STEP 1: singular-value estimate ---------------------------------")
    a_svd_guesses = get_singular_value_guess(V_samples)

    # ------------- STEP 2: exact solution from approximation -----------------------
    print("\n------------- STEP 2: exact solution from approximation -----------------------")
    solved = False
    for attempt in range(0, 5):
        print("------ using singular value", attempt + 1, " ------")
        statistics["attempt"] = attempt
        statistics["a_dist_average_typical"] = []
        statistics["a_dist_average"] = []
        asvd = a_svd_guesses[attempt]
        a_guess = a_nrm * asvd

        statistics["a_dist_singular_value"] = a_dist(a_guess)
        print("Singular guess:", "||a-a_guess|| =", statistics["a_dist_singular_value"])
        a_guess = make_typical(a_guess)
        statistics["a_dist_typical"] = a_dist(a_guess)
        print("Made typical:", "||a-a_typical|| =", statistics["a_dist_typical"])

        avg_a, solved, a_exact = get_solution_or_averaging(a_guess, V_samples, a_nrm, statistics)

        # try again with average a_try
        tries = 0
        while not solved and tries < 20:
            tries += 1
            statistics["averaging_iterations"] = tries
            statistics["a_dist_average"] += [a_dist(avg_a)]
            print(str(tries) + ".", "Try with average:", "||a-avg_a|| =", statistics["a_dist_average"][-1])
            avg_a = make_typical(avg_a)
            statistics["a_dist_average_typical"] += [a_dist(avg_a)]
            print(str(tries) + ".", "Made typical:", "||a-a_typical|| =", statistics["a_dist_average_typical"][-1])

            avg_a, solved, a_exact = get_solution_or_averaging(avg_a, V_samples, a_nrm, statistics)
            if solved:
                break

        # verify that the key recovery was successful
        if np.all(a_exact == a_vec) or np.all(a_exact == -a_vec):
            print("-------------------------------------------------------------------------------")
            print("------------------------ Secret key fully recovered! --------------------------")
            print("-------------------------------------------------------------------------------")
            statistics["recovered"] = True
            break
        else:
            print('Secret-key recovery failed, try next svd vector.')

    print(statistics)
    return statistics
# end of attack function
