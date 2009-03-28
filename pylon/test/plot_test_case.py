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

""" Test case for Pylon's plots.
"""

#------------------------------------------------------------------------------
#  Imports:
#------------------------------------------------------------------------------

from os.path import join, dirname
import unittest

from pylon.readwrite.api import read_matpower
from pylon.ui.plot.cost_plot import CostPlot

#------------------------------------------------------------------------------
#  Constants:
#------------------------------------------------------------------------------

DATA_FILE = join(dirname(__file__), "data", "case6ww.m")

#------------------------------------------------------------------------------
#  "CostPlotTest" class:
#------------------------------------------------------------------------------

class CostPlotTest(unittest.TestCase):
    """ Defines a test case for the cost plot.
    """

    plot = None

    def setUp(self):
        """ The test runner will execute this method prior to each test.
        """
        self.plot = plot = CostPlot(network=read_matpower(DATA_FILE))

    def test_create_plot(self):
        """ Test creation of a cost plot.
        """
        self.plot.configure_traits()

# EOF -------------------------------------------------------------------------
