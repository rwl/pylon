#------------------------------------------------------------------------------
# Copyright (C) 2007-2010 Richard Lincoln
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#------------------------------------------------------------------------------

""" Pyreto test suite.
"""

#------------------------------------------------------------------------------
#  Imports:
#------------------------------------------------------------------------------

import unittest

from pylon.test.suite import suite as pylon_suite

from market_test import DCMarketTestCase
from experiment_test import MarketExperimentTest

#------------------------------------------------------------------------------
#  "suite" function:
#------------------------------------------------------------------------------

def suite():
    """ Returns the Pyreto test suite.
    """
    # Pyreto tests are in addition to the Pylon tests.
    suite = pylon_suite()

    suite.addTest(unittest.makeSuite(DCMarketTestCase))
    suite.addTest(unittest.makeSuite(MarketExperimentTest))

    return suite


if __name__ == '__main__':
    unittest.TextTestRunner(verbosity=2).run(suite())

# EOF -------------------------------------------------------------------------
