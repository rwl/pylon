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

""" Test case for the AC OPF routine.
"""

#------------------------------------------------------------------------------
#  Imports:
#------------------------------------------------------------------------------

import unittest
from os.path import join, dirname

from pylon.readwrite import PickleReader
from pylon import ACOPF

#------------------------------------------------------------------------------
#  Constants:
#------------------------------------------------------------------------------

DATA_FILE = join(dirname(__file__), "data", "case6ww.pkl")

#------------------------------------------------------------------------------
#  "ACOPFTest" class:
#------------------------------------------------------------------------------

class ACOPFTest(unittest.TestCase):
    """ We use a MATPOWER data file and validate the results against those
        obtained from running the MATPOWER runopf.m script with the same data
        file and the FMINCON (fmincopf.m) algorithm.

        See reader_test_case.py for validation of MATPOWER data file parsing.
    """

    def setUp(self):
        """ The test runner will execute this method prior to each test.
        """
        self.case = PickleReader().read(DATA_FILE)
        self.routine = ACOPF()


    def test_mismatch(self):
        """ Test AC OPF.
        """
        success = self.routine(self.case)

#------------------------------------------------------------------------------
#  Stand-alone call:
#------------------------------------------------------------------------------

if __name__ == "__main__":
    import logging, sys
    logging.basicConfig(stream=sys.stdout, level=logging.DEBUG)

    unittest.main()

# EOF -------------------------------------------------------------------------
