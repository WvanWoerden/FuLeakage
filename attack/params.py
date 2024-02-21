def get_fuleeca_parameters(sec_lvl):
    # [p, n, w_key, hamming_wt_key, squared_norm_key, s]
    if sec_lvl == 1:
        return [65521, 1318, 31102, 1212, 2844258, 3 / 64]
    elif sec_lvl == 3:
        return [65521, 1982, 46552, 1848, 4430100, 9 / 256]
    elif sec_lvl == 5:
        return [65521, 2638, 61918, 2638, 6048442, 3 / 128]
    return NotImplementedError("No FuLeeca parameters for the given security level available. Valid inputs: 1, 3, 5.")
