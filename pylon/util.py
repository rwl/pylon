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

""" Defines various utility functions and classes for Pylon.
"""

#------------------------------------------------------------------------------
#  Imports:
#------------------------------------------------------------------------------

import os.path

from itertools import count

#from pylon.readwrite import MATPOWERReader, PickleWriter

#------------------------------------------------------------------------------
#  "Named" class:
#------------------------------------------------------------------------------

class Named(object):
    """ Base class for objects guaranteed to have a unique name.
    """

    _name_ids = count(0)

    def _get_name(self):
        """ Returns the name, which is generated if it has not been already.
        """
        if self._name is None:
            self._name = self._generate_name()
        return self._name


    def _set_name(self, value):
        """ Changes name to 'value'. Uniquity no longer guaranteed.
        """
        self._name = value


    _name = None
    name = property(_get_name, _set_name)


    def _generate_name(self):
        """ Return a unique name for this object.
        """
        return "%s-%i" % (self.__class__.__name__, self._name_ids.next())


#    def __repr__(self):
#        """ The default representation of a named object is its name.
#        """
#        return "<%s '%s'>" % (self.__class__.__name__, self.name)

#------------------------------------------------------------------------------
#  Return the complex conjugate:
#------------------------------------------------------------------------------

def conj(A):
    """ Returns the complex conjugate of A as a new matrix.
    """
    return A.ctrans().trans()

#------------------------------------------------------------------------------
#  Pickles MATPOWER case files:
#------------------------------------------------------------------------------

def pickle_matpower_cases(case_paths):
    """ Parses the MATPOWER case files at the given paths and pickles the
        resulting Case objects to the same directory.
    """
    import pylon.readwrite

    if isinstance(case_paths, basestring):
        case_paths = [case_paths]

    for case_path in case_paths:
        # Read the MATPOWER case file.
        case = pylon.readwrite.MATPOWERReader().read(case_path)

        # Give the new file the same name, but with a different extension.
        dir_path = os.path.dirname(case_path)
        case_basename = os.path.basename(case_path)
        root, extension = os.path.splitext(case_basename)
        pickled_case_path = os.path.join(dir_path, root + '.pkl')

        # Pickle the resulting Pylon Case object.
        pylon.readwrite.PickleWriter().write(case, pickled_case_path)

#------------------------------------------------------------------------------
#  'atan2' function:
#------------------------------------------------------------------------------

#def atan2(X, Y):
#    """ atan2 function.
#    """
#    matrix([math.arctan2(Y, X) for k in xrange(nrows * ncols)],
#           (nrows, ncols), 'd')

#------------------------------------------------------------------------------
#  Returns the angle of the complex argument:
#------------------------------------------------------------------------------

#def angle(z, deg=0):
#    """ Returns the angle of the complex argument.
#
#        Parameters
#        ----------
#        z : array_like
#            A complex number or sequence of complex numbers.
#        deg : bool, optional
#            Return angle in degrees if True, radians if False (default).
#
#        Returns
#        -------
#        angle : {ndarray, scalar}
#            The counterclockwise angle from the positive real axis on
#            the complex plane, with dtype as numpy.float64.
#
#        See Also
#        --------
#        arctan2
#
#        Examples
#        --------
#        >>> np.angle([1.0, 1.0j, 1+1j])               # in radians
#        array([ 0.        ,  1.57079633,  0.78539816])
#        >>> np.angle(1+1j, deg=True)                  # in degrees
#        45.0
#    """
#    if deg:
#        fact = 180 / math.pi
#    else:
#        fact = 1.0
##    z = asarray(z)
#    if z.typecode is "z":
#        zimag = z.imag()
#        zreal = z.real()
#    else:
#        zimag = 0
#        zreal = z
#
#    matrix([math.arctan2(z[i].imag(), z[i].real()) for x in z])
#
#    return atan2(zimag, zreal) * fact

# EOF -------------------------------------------------------------------------
