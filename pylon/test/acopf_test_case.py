#------------------------------------------------------------------------------
# Copyright (C) 2008 Richard W. Lincoln
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

""" Test case for the AC OPF routine. """

#------------------------------------------------------------------------------
#  Imports:
#------------------------------------------------------------------------------

import unittest
from os.path import join, dirname

from pylon.readwrite.api import read_matpower
from pylon.routine.api import ACOPFRoutine

#------------------------------------------------------------------------------
#  Constants:
#------------------------------------------------------------------------------

DATA_FILE = join(dirname(__file__), "data/case6ww.m")

#------------------------------------------------------------------------------
#  "ACOPFTest" class:
#------------------------------------------------------------------------------

class ACOPFTest(unittest.TestCase):
    """ We use a MATPOWER data file and validate the results against those
    obtained from running the MATPOWER runopf.m script with the same data
    file and the FMINCON (fmincopf.m) algorithm.

    See reader_test_case.py for validation of MATPOWER data file parsing.

    """

    routine = ACOPFRoutine

    def setUp(self):
        """ The test runner will execute this method prior to each test. """

        network = read_matpower(DATA_FILE)
        self.routine = ACOPFRoutine(network)


    def test_mismatch(self):
        """ Test AC OPF. """

#------------------------------------------------------------------------------
#  Stand-alone call:
#------------------------------------------------------------------------------

if __name__ == "__main__":
    import logging, sys
    logger = logging.getLogger()
    logger.addHandler(logging.StreamHandler(sys.stdout))
    logger.setLevel(logging.DEBUG)

    unittest.main()

# EOF -------------------------------------------------------------------------
