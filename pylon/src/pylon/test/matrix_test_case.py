#------------------------------------------------------------------------------
# Copyright (C) 2007 Richard W. Lincoln
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

from unittest import TestCase

from enthought.traits.api import HasTraits, Bool

from cvxopt.base import matrix, spmatrix, sparse

from numpy.random import random

from pylon.traits import Matrix, SparseMatrix

#------------------------------------------------------------------------------
#  "Foo" class:
#------------------------------------------------------------------------------

class Foo(HasTraits):
    m = Matrix(value=6, size=(3,4))
    s = SparseMatrix(range(6), range(6), range(6), size=(12,6), tc="z")
    event_fired = Bool(False)

    def _m_changed(self):
        self.event_fired = True

    def _s_changed(self):
        self.event_fired = True

#------------------------------------------------------------------------------
#  "MatrixTestCase" class
#------------------------------------------------------------------------------

class MatrixTestCase(TestCase):
    """ A test case for Matrix traits """

    def test_zero_to_one_element(self):
        """ Test that an event fires when a Matrix trait changes from zero to
        one element.
        """

        f = Foo()
#        f.m = matrix(random((6, 6)))
        f.event_fired = False

        # Change the matrix.
        f.m = matrix(random((6, 6)))

        # Confirm that the static trait handler was invoked.
        self.assertEqual(f.event_fired, True)

        return

#------------------------------------------------------------------------------
#  "SparseMatrixTestCase" class
#------------------------------------------------------------------------------

class SparseMatrixTestCase(TestCase):
    """ A test case for SparseMatrix traits """

    def test_assignment(self):
        """ Test assigning a value to a SparseMatrix trait """

        f = Foo()
        f.event_fired = False

        f.s = spmatrix([], [], [])

        self.assertEqual(f.event_fired, True)

# EOF -------------------------------------------------------------------------
