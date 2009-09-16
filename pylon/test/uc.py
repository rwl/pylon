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

""" Test case for the DC Power Flow routine.
"""

#------------------------------------------------------------------------------
#  Imports:
#------------------------------------------------------------------------------

import unittest

from pylon import Case
from pylon import UnitCommitmentRoutine

#------------------------------------------------------------------------------
#  "UnitCommitmentTest" class:
#------------------------------------------------------------------------------

class UnitCommitmentTest(unittest.TestCase):
    """ Tests the unit commitment routine.
    """

    def test_time_horizon(self):
        """ Test that the number of periods is made > 0.
        """
        r = UnitCommitmentRoutine(Case(), periods=0)
        r.solve()

        self.assertEqual(r.periods, 1)


    def test_vector_slicing(self):
        """ Test slicing of the demand vector to match the time horizon.
        """
        p = 2
        d = [10.0, 20.0, 30.0]
        rsrv = [1.0, 2.0, 3.0, 4.0]
        r = UnitCommitmentRoutine(Case(), periods=p, demand=d, reserve=rsrv)
        r.solve()

        self.assertTrue(len(r.demand) == p)
        self.assertTrue(len(r.reserve) == p)


    def test_vector_extension(self):
        """ Test extension of the demand vector to match the time horizon.
        """
        p = 6
        d = [10.0, 20.0]
        rsrv = []
        r = UnitCommitmentRoutine(Case(), periods=p, demand=d, reserve=rsrv)
        r.solve()

        self.assertTrue(len(r.demand) == p)
        self.assertTrue(len(r.reserve) == p)


if __name__ == "__main__":
    import logging, sys
    logging.basicConfig(stream=sys.stdout, level=logging.DEBUG)

    unittest.main()

# EOF -------------------------------------------------------------------------
