#-------------------------------------------------------------------------------
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
#-------------------------------------------------------------------------------

""" Very important test case for the DC Power Flow routine """

#-------------------------------------------------------------------------------
#  Imports:
#-------------------------------------------------------------------------------

from os.path import join, dirname
from unittest import TestCase

from pylon.filter.api import MATPOWERImporter
from pylon.routine.dc_pf import DCPFRoutine

#-------------------------------------------------------------------------------
#  Constants:
#-------------------------------------------------------------------------------

DATA_FILE = join(dirname(__file__), "data/3bus.m")

#-------------------------------------------------------------------------------
#  "DCPFTest" class:
#-------------------------------------------------------------------------------

class DCPFTest(TestCase):
    """ Uses a MATPOWER data file and validates the results against those
    obtained from running the MATPOWER rundcpf.m script with the same
    data file. See filter_test_case.py for validation of MATPOWER data
    file parsing.

    """

    network = None

    def setUp(self):
        """
        The test runner will execute this method prior to each test

        """

        mf = MATPOWERImporter()
        self.network = mf.parse_file(DATA_FILE)


    def test_v_phase_guess_vector(self):
        """ Test the voltage phase guess trait of a bus """

        dcpf = DCPFRoutine()
        dcpf.network = self.network
        guesses = dcpf._build_v_phase_guess_vector()


# EOF -------------------------------------------------------------------------
