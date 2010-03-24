__author__ = 'Richard Lincoln, r.w.lincoln@gmail.com'

""" This example demonstrates how to use the Python Interior Point Solver using
the problem from http://en.wikipedia.org/wiki/Nonlinear_programming. """

from numpy import r_, c_
from pips import pips

def f2(x):
    f = -x[0] * x[1] - x[1] * x[2]
    df = -r_[x[1], x[0] + x[2], x[1]]
    # actually not used since 'hess_fcn' is provided
    d2f = -c_[ r_[0, 1, 0], r_[1, 0, 1], r_[0, 1, 0] ]
    return f, df, d2f

def gh2(x):
    h = c_[ r_[ 1, -1, 1], r_[1, 1, 1] ] * x**2 + r_[-2, -10]
    dh = 2 * c_[ r_[x[0], x[0]], r_[-x[1], x[1]], r_[x[2], x[2]] ]
    g = None
    dg = None
    return h, g, dh, dg

def hess2(x, lam):
    mu = lam["ineqnonlin"]
    Lxx = c_[ r_[2 * r_[1, 1] * mu, -1, 0],
              r_[-1, 2 * r_[-1, 1] * mu, -1],
              r_[0, -1, 2 * r_[1, 1] * mu] ]
    return Lxx

problem = {"f_fcn": f2,
           "gh_fcn": gh2,
           "hess_fcn": hess2,
           "x0": r_[1, 1, 0],
           "opt": {"verbose": True}}

x, f, exitflag, output, lmbda = pips(problem)

assert f == -7.0711
