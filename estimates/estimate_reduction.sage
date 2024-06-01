# Estimate lattice reduction attack on FuLeeca

from math import lgamma
import numpy as np
import scipy as sc

@CachedFunction
def ball_log_vol(n):
    return float((n/2.) * log(pi) - lgamma(n/2. + 1))

gh_constant = {1:0.00000,2:-0.50511,3:-0.46488,4:-0.39100,5:-0.29759,6:-0.24880,7:-0.21970,8:-0.15748,9:-0.14673,10:-0.07541,11:-0.04870,12:-0.01045,13:0.02298,14:0.04212,15:0.07014,16:0.09205,17:0.12004,18:0.14988,19:0.17351,20:0.18659,21:0.20971,22:0.22728,23:0.24951,24:0.26313,25:0.27662,26:0.29430,27:0.31399,28:0.32494,29:0.34796,30:0.36118,31:0.37531,32:0.39056,33:0.39958,34:0.41473,35:0.42560,36:0.44222,37:0.45396,38:0.46275,39:0.47550,40:0.48889,41:0.50009,42:0.51312,43:0.52463,44:0.52903,45:0.53930,46:0.55289,47:0.56343,48:0.57204,49:0.58184,50:0.58852}
def log_gh(d, logvol=0):
    if d < 49:
        return gh_constant[d] + float(logvol)/d

    return 1./d * float(logvol - ball_log_vol(d))


def delta(k):
    assert(k>=60)
    delta = exp(log_gh(k)/(k-1))
    return float(delta)

small_slope_t8 = {2:0.04473,3:0.04472,4:0.04402,5:0.04407,6:0.04334,7:0.04326,8:0.04218,9:0.04237,10:0.04144,11:0.04054,12:0.03961,13:0.03862,14:0.03745,15:0.03673,16:0.03585,17:0.03477,18:0.03378,19:0.03298,20:0.03222,21:0.03155,22:0.03088,23:0.03029,24:0.02999,25:0.02954,26:0.02922,27:0.02891,28:0.02878,29:0.02850,30:0.02827,31:0.02801,32:0.02786,33:0.02761,34:0.02768,35:0.02744,36:0.02728,37:0.02713,38:0.02689,39:0.02678,40:0.02671,41:0.02647,42:0.02634,43:0.02614,44:0.02595,45:0.02583,46:0.02559,47:0.02534,48:0.02514,49:0.02506,50:0.02493,51:0.02475,52:0.02454,53:0.02441,54:0.02427,55:0.02407,56:0.02393,57:0.02371,58:0.02366,59:0.02341,60:0.02332}

@CachedFunction
def slope(beta):
    if beta<=60:
        return small_slope_t8[beta]
    if beta<=70:
        # interpolate between experimental and asymptotics
        ratio = (70-beta)/10.
        return ratio*small_slope_t8[60]+(1.-ratio)*2*log(delta(70))
    else:
        return 2 * log(delta(beta))

def chi2_CDF(n, x):
    if x > 100 * n:
        return 1.
    return float(1. - gamma(n/2., x/2.)/gamma(n/2.))

# computes probability of finding [kissing_number] vectors of
# unusual length [usvp_norm] in a lattice of dimension [n]
# and determinant 1 with progressive BKZ up to blocksize [beta].
def u_SVP_prob(beta, n, usvp_norm, kissing_number):    
    slope_ = slope(beta)
    threshold = float(log(beta * usvp_norm*usvp_norm / float(n))/2.)

    proba_one = 1.
    for b in range(beta, min(max(n, 300), 3*beta), beta-1):
        threshold = float(log(b * usvp_norm*usvp_norm / float(n))/2.)
        log_len_gs = - slope_ * float(n/2 - b)
        bound_chi2 = b*exp(2*(log_len_gs - threshold))
        proba_one *= chi2_CDF(b, bound_chi2)
    prob_all_not = (1.-proba_one)**kissing_number

    return float(1.-prob_all_not)

def get_fuleeca_parameters(sec_lvl):
    # [p, n, w_key, hamming_wt_key, squared_norm_key, s]
    if sec_lvl == 1:
        return [65521, 1318, 31102, 1212, 2844258, 3 / 64]
    elif sec_lvl == 3:
        return [65521, 1982, 46552, 1848, 4430100, 9 / 256]
    elif sec_lvl == 5:
        return [65521, 2638, 61918, 2638, 6048442, 3 / 128]
    return NotImplementedError("No FuLeeca parameters for the given security level available. Valid inputs: 1, 3, 5.")

# Taken from https://eprint.iacr.org/2021/999.pdf assuming gaussian entries
# matches experimental volume of lattice generated by G=[A;B] closely.
def logvol_circulant_sublattice(n, sigma):
    return n*(np.log(2*n*sigma^2) + sc.special.digamma(1))/2. + (n-1)*(1-np.log(2))/2.

def get_estimate(sec_lvl):
    p, n, w_key, hamming_wt_key, squared_norm_key, s = get_fuleeca_parameters(sec_lvl)

    # # estimate standard attack q-ary code using approximate SVP
    dim=n
    normdeterminant=float(sqrt(p))
    approx_svp_norm=float(sqrt(2*squared_norm_key))
    kissing_number=n//2 
    gh=sqrt(dim/(2*np.pi*np.e)) * normdeterminant
    assert(approx_svp_norm > gh)

    delta_bnd = (approx_svp_norm / normdeterminant )^(1./(dim-1))
    for b in range(200,dim+1):
        if delta(b) <= delta_bnd:
            print("{0:10} {1:15} {2:.8f} {3:15}".format("Lat1", str(sec_lvl), approx_svp_norm / gh, str(b)))
            break

    # estimate leaked lattice
    dim=n//2
    sigma = np.sqrt(squared_norm_key/dim)
    normdeterminant=float(exp(logvol_circulant_sublattice(dim, sigma)/dim))
    usvp_norm=float(sqrt(2*squared_norm_key))
    kissing_number=n//2
    gh = sqrt(dim/(2*pi*e)).n() * normdeterminant
    gh_rat = usvp_norm / gh

    # print(dim, sigma, normdeterminant, usvp_norm, kissing_number)
    for b in range(100, n, 1):
        prob = u_SVP_prob(b, dim, usvp_norm/normdeterminant, kissing_number)
        if prob > 0.99:
            print("{0:10} {1:15} {2:.8f} {3:15}".format("Lat2", str(sec_lvl), gh_rat, str(b)))
            return dim, b, prob

estimates = []
print("{0:10} {1:15} {2:10} {3:15}".format("lattice", "security Level", "norm / gh", "blocksize"))
for cat in [1,3,5]:
    dim, beta, prob = get_estimate(cat)
    estimates += [(cat, dim, beta)]
np.savetxt("../attack/data/blocksize_estimates.txt", estimates, fmt="%d")