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

""" Defines a test case for the combined unit decommitment / OPF routine.
"""

#------------------------------------------------------------------------------
#  Imports:
#------------------------------------------------------------------------------

import sys
import logging
import unittest

from os.path import dirname, join

from pylon.readwrite import MATPOWERReader
from pylon.ud_opf import UDOPF

#------------------------------------------------------------------------------
#  Constants:
#------------------------------------------------------------------------------

DATA_FILE = join(dirname(__file__), "data", "case6ww.m")

#------------------------------------------------------------------------------
#  "UOPFTestCase" class:
#------------------------------------------------------------------------------

class UOPFTestCase(unittest.TestCase):
    """ Defines a test case for the UOPF routine.
    """

    def setUp(self):
        """ The test runner will execute this method prior to each test.
        """
        self.network = MATPOWERReader().read(DATA_FILE)
        self.routine = UDOPF(dc=True)

    def test_dc(self):
        """ Test routine using DC formulation.
        """
        solution = self.routine(self.network)
        generators = self.network.all_generators

        self.assertFalse(generators[0].online)
        self.assertAlmostEqual(generators[1].p, 110.80, places=2)
        self.assertAlmostEqual(generators[2].p,  99.20, places=2)

        self.assertAlmostEqual(solution[''], 2841.59, places=2)


if __name__ == "__main__":
    logging.basicConfig(stream=sys.stdout, level=logging.DEBUG,
        format="%(levelname)s: %(message)s")

    unittest.main()

# EOF -------------------------------------------------------------------------
