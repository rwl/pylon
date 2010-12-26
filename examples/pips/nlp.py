# Copyright (C) 1996-2010 Power System Engineering Research Center (PSERC)
# Copyright (C) 2007-2010 Richard Lincoln

__author__ = 'Richard Lincoln, r.w.lincoln@gmail.com'

""" This example demonstrates how to use the Python Interior Point Solver using
the problem from http://en.wikipedia.org/wiki/Nonlinear_programming. """

from numpy import array, r_, float64, dot
from scipy.sparse import csr_matrix
from pips import pips

def f2(x):
    f = -x[0] * x[1] - x[1] * x[2]
    df = -r_[x[1], x[0] + x[2], x[1]]
    # actually not used since 'hess_fcn' is provided
    d2f = -array([[0, 1, 0], [1, 0, 1], [0, 1, 0]], float64)
    return f, df, d2f

def gh2(x):
    h = dot(array([ [1, -1, 1], [1, 1, 1] ]), x**2) + array([-2.0, -10.0])
    dh = 2 * csr_matrix( array([ [x[0], x[0]], [-x[1], x[1]], [x[2], x[2]] ]) )
    g = array([])
    dg = None
    return h, g, dh, dg

def hess2(x, lam):
    mu = lam["ineqnonlin"]
    Lxx = csr_matrix( array([ r_[dot(2 * array([1, 1]), mu), -1, 0],
                              r_[-1, dot(2 * array([-1, 1]), mu), -1],
                              r_[0, -1, dot(2 * array([1, 1]), mu)] ]) )
    return Lxx

x0 = array([1, 1, 0], float64)
opt = {"verbose": True}

solution = pips(f2, x0, gh_fcn=gh2, hess_fcn=hess2, opt=opt)

print solution["output"]["iterations"], "F:", solution["x"], solution["f"]
