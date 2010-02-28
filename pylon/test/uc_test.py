#------------------------------------------------------------------------------
# Copyright (C) 2010 Richard Lincoln
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

""" Test case for the DC Power Flow routine.
"""

#------------------------------------------------------------------------------
#  Imports:
#------------------------------------------------------------------------------

import unittest

from pylon import Case
from pylon import UnitCommitment

#------------------------------------------------------------------------------
#  "UnitCommitmentTest" class:
#------------------------------------------------------------------------------

class UnitCommitmentTest(unittest.TestCase):
    """ Tests the unit commitment routine.
    """

    def test_time_horizon(self):
        """ Test that the number of periods is made > 0.
        """
        r = UnitCommitment(Case(), periods=0)
        r.solve()

        self.assertEqual(r.periods, 1)


    def test_vector_slicing(self):
        """ Test slicing of the demand vector to match the time horizon.
        """
        p = 2
        d = [10.0, 20.0, 30.0]
        rsrv = [1.0, 2.0, 3.0, 4.0]
        r = UnitCommitment(Case(), periods=p, demand=d, reserve=rsrv)
        r.solve()

        self.assertTrue(len(r.demand) == p)
        self.assertTrue(len(r.reserve) == p)


    def test_vector_extension(self):
        """ Test extension of the demand vector to match the time horizon.
        """
        p = 6
        d = [10.0, 20.0]
        rsrv = []
        r = UnitCommitment(Case(), periods=p, demand=d, reserve=rsrv)
        r.solve()

        self.assertTrue(len(r.demand) == p)
        self.assertTrue(len(r.reserve) == p)


if __name__ == "__main__":
    import logging, sys
    logging.basicConfig(stream=sys.stdout, level=logging.DEBUG)

    unittest.main()

# EOF -------------------------------------------------------------------------
