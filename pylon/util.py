#------------------------------------------------------------------------------
# Copyright (C) 2009 Richard W. Lincoln
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; version 2 dated June, 1991.
#
# This software is distributed in the hope that it will be useful, but
# WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANDABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the GNU
# General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software Foundation,
# Inc., 51 Franklin St, Fifth Floor, Boston, MA 02110-1301 USA
#------------------------------------------------------------------------------

""" Defines utility functions for use with CVXOPT.
"""

#------------------------------------------------------------------------------
#  Imports:
#------------------------------------------------------------------------------

import math
import cmath

from cvxopt.base import matrix, spmatrix, sparse, spdiag, gemv, exp, mul, div

#------------------------------------------------------------------------------
#  Convenient conjugate function:
#------------------------------------------------------------------------------

def conj(A):
    """ Returns the complex conjugate of A as a new matrix.
    """
    return A.ctrans().trans()


def atan2(X, Y):
    """ atan2 function.
    """
    matrix([math.arctan2(Y, X) for k in xrange(nrows*ncols)],
           (nrows, ncols), 'd')


def angle(z, deg=0):
    """ Return the angle of the complex argument.

        Parameters
        ----------
        z : array_like
            A complex number or sequence of complex numbers.
        deg : bool, optional
            Return angle in degrees if True, radians if False (default).

        Returns
        -------
        angle : {ndarray, scalar}
            The counterclockwise angle from the positive real axis on
            the complex plane, with dtype as numpy.float64.

        See Also
        --------
        arctan2

        Examples
        --------
        >>> np.angle([1.0, 1.0j, 1+1j])               # in radians
        array([ 0.        ,  1.57079633,  0.78539816])
        >>> np.angle(1+1j, deg=True)                  # in degrees
        45.0
    """
    if deg:
        fact = 180/pi
    else:
        fact = 1.0
#    z = asarray(z)
    if z.typecode is "z":
        zimag = z.imag()
        zreal = z.real()
    else:
        zimag = 0
        zreal = z

    matrix([math.arctan2(z[i].imag(), z[i].real()) for x in z])

    return atan2(zimag, zreal) * fact

# EOF -------------------------------------------------------------------------
