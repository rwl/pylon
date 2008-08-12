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
Test case for the Load class

"""

#-------------------------------------------------------------------------------
#  Imports:
#-------------------------------------------------------------------------------

from unittest import TestCase, main

from pylon.load import Load

#-------------------------------------------------------------------------------
#  "LoadTest" class:
#-------------------------------------------------------------------------------

class LoadTest(TestCase):
    """
    Test case for the Load class

    """

    def setUp(self):
        """
        The test runner will execute this method prior to each test

        """

        self.l = Load()


    def test_id(self):
        """
        Test that the id attribute is unique

        """

        l2 = Load()

        self.assertNotEqual(
            self.l.id, l2.id,
            "IDs [%s, %s] of two loads found equal" %
            (self.l.id, l2.id)
        )

        self.assertTrue(
            len(self.l.id) > 6,
            "ID [%s] of load is of insufficient length" %
            (self.l.id)
        )

if __name__ == "__main__":
    main()

# EOF -------------------------------------------------------------------------
