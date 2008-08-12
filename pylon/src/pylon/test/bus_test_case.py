#-------------------------------------------------------------------------------
# Copyright (C) 2007 Richard W. Lincoln
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

"""
Test case for the Bus class

"""

#-------------------------------------------------------------------------------
#  Imports:
#-------------------------------------------------------------------------------

from unittest import TestCase, main

from pylon.bus import Bus

#-------------------------------------------------------------------------------
#  "BusTest" class:
#-------------------------------------------------------------------------------

class BusTest(TestCase):
    """
    Test case for the Bus class

    """

    def setUp(self):
        """
        The test runner will execute this method prior to each test

        """

        self.v = Bus()


    def test_id(self):
        """
        Test that the id attribute is unique

        """

        v2 = Bus()

        self.assertNotEqual(
            self.v.id, v2.id,
            "IDs [%s, %s] of two buses found equal" %
            (self.v.id, v2.id)
        )

        self.assertTrue(
            len(self.v.id) > 6,
            "ID [%s] of bus is of insufficient length" %
            (self.v.id)
        )

if __name__ == "__main__":
    main()

# EOF -------------------------------------------------------------------------
