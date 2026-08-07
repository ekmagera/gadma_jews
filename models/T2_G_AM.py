from common import equilibrium, integrate_two, integrate_three
import moments

def model_func(params, ns):
    nuA, nuG, nuM, Tbetween, Trecent, mold, mAG, mAM, mGM = params
    nA, nG, nM = ns
    fs = equilibrium(nA + nG + nM)
    fs = moments.Manips.split_1D_to_2D(fs, nG, nA + nM)
    integrate_two(fs, Tbetween, nuG, (nuA + nuM) / 2, mold)
    fs = moments.Manips.split_2D_to_3D_2(fs, nG, nA, nM).transpose([1, 0, 2])
    integrate_three(fs, Trecent, [nuA, nuG, nuM], mAG, mAM, mGM)
    return fs

