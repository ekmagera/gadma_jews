from common import equilibrium, integrate_three
import moments

def model_func(params, ns):
    nuA, nuG, nuM, T, mAG, mAM, mGM = params
    nA, nG, nM = ns
    fs = equilibrium(nA + nG + nM)
    fs = moments.Manips.split_1D_to_2D(fs, nA, nG + nM)
    fs = moments.Manips.split_2D_to_3D_2(fs, nG, nM)
    integrate_three(fs, T, [nuA, nuG, nuM], mAG, mAM, mGM)
    return fs
