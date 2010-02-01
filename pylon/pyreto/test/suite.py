#------------------------------------------------------------------------------
# Copyright (C) 2010 Richard Lincoln
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

""" Pyreto test suite.
"""

#------------------------------------------------------------------------------
#  Imports:
#------------------------------------------------------------------------------

import unittest

from pylon.test.suite import suite as pylon_suite

from market_test import SimpleMarketTestCase
from experiment_test import MarketExperimentTest

#------------------------------------------------------------------------------
#  "suite" function:
#------------------------------------------------------------------------------

def suite():
    """ Returns the Pyreto test suite.
    """
    # Pyreto tests are in addition to the Pylon tests.
    suite = pylon_suite()

    suite.addTest(unittest.makeSuite(SimpleMarketTestCase))
    suite.addTest(unittest.makeSuite(MarketExperimentTest))

    return suite


if __name__ == '__main__':
    unittest.TextTestRunner(verbosity=2).run(suite())

# EOF -------------------------------------------------------------------------
