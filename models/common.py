import moments
import numpy as np

def equilibrium(n):
    return moments.Spectrum(moments.LinearSystem_1D.steady_state_1D(n))

def integrate_two(fs, T, nu1, nu2, m):
    fs.integrate([nu1, nu2], T, m=np.array([[0, m], [m, 0]]))

def integrate_three(fs, T, nus, m12, m13, m23):
    mat = np.array([[0, m12, m13], [m12, 0, m23], [m13, m23, 0]])
    fs.integrate(nus, T, m=mat)

