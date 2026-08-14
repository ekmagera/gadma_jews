from common import equilibrium, integrate_two, integrate_three
import moments

def model_func(params, ns):
    nuA, nuG, nuM, Tbetween, Trecent, mold, mAG, mAM, mGM = params
    nA, nG, nM = ns
    fs = equilibrium(nA + nG + nM)
    fs = moments.Manips.split_1D_to_2D(fs, nM, nA + nG)
    integrate_two(fs, Tbetween, nuM, (nuA + nuG) / 2, mold)
    fs = moments.Manips.split_2D_to_3D_2(fs, nA, nG).transpose([1, 2, 0])
    integrate_three(fs, Trecent, [nuA, nuG, nuM], mAG, mAM, mGM)
    return fs
