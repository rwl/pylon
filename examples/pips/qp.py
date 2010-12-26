# Copyright (C) 1996-2010 Power System Engineering Research Center (PSERC)
# Copyright (C) 2007-2010 Richard Lincoln

__author__ = 'Richard Lincoln, r.w.lincoln@gmail.com'

""" This example demonstrates how to use the Quadratic Program Solver using
a problem from http://www.uc.edu/sashtml/iml/chap8/sect12.htm. """

from numpy import array, zeros, Inf
from scipy.sparse import csr_matrix

from pips import qps_pips

H = csr_matrix(array([[1003.1,  4.3,     6.3,     5.9],
                      [4.3,     2.2,     2.1,     3.9],
                      [6.3,     2.1,     3.5,     4.8],
                      [5.9,     3.9,     4.8,     10 ]]))

c = zeros(4)


A = csr_matrix(array([[   1,       1,       1,       1   ],
                      [   0.17,    0.11,    0.10,    0.18]]))

l = array([1, 0.10])
u = array([1, Inf])

xmin = zeros(4)
xmax = None

x0 = array([1, 0, 0, 1])

solution = qps_pips(H, c, A, l, u, xmin, xmax, x0, {"verbose": True})
