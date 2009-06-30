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

""" Defines a test case for the Load class.
"""

#------------------------------------------------------------------------------
#  Imports:
#------------------------------------------------------------------------------

import unittest

from pylon.api import Load

#------------------------------------------------------------------------------
#  "LoadTest" class:
#------------------------------------------------------------------------------

class LoadTest(unittest.TestCase):
    """ Defines a test case for the Load class.
    """

    def test_profile(self):
        """ Test profiled active power output.
        """
        profile = [100.0, 50.0, 20.0, 90.0]

        load = Load(p_min=0.1, p_max=0.9, p_profile=profile)

        places = 2

        self.assertAlmostEqual(load.p_profiled, 0.80, places)
        self.assertAlmostEqual(load.p_profiled, 0.40, places)
        self.assertAlmostEqual(load.p_profiled, 0.16, places)
        self.assertAlmostEqual(load.p_profiled, 0.72, places)
        self.assertAlmostEqual(load.p_profiled, 0.80, places)

        # Set new profile.
        profile2 = [10.0, 20.0]
        load.p_profile = profile2

        self.assertAlmostEqual(load.p_profiled, 0.08, places)
        self.assertAlmostEqual(load.p_profiled, 0.16, places)
        self.assertAlmostEqual(load.p_profiled, 0.08, places)

        # Change profile items.
        load.p_profile.append(50.0)

        self.assertAlmostEqual(load.p_profiled, 0.08, places)
        self.assertAlmostEqual(load.p_profiled, 0.16, places)
        self.assertAlmostEqual(load.p_profiled, 0.40, places)
        self.assertAlmostEqual(load.p_profiled, 0.08, places)

if __name__ == "__main__":
    unittest.main()

# EOF -------------------------------------------------------------------------
