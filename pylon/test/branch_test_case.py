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

""" Test case for the Branch class. """

#------------------------------------------------------------------------------
#  Imports:
#------------------------------------------------------------------------------

from unittest import TestCase, main

from pylon.api import Bus, Branch

#------------------------------------------------------------------------------
#  "BranchTest" class:
#------------------------------------------------------------------------------

class BranchTest(TestCase):
    """ Test case for the Branch class. """


    def test_v_ratio(self):
        """ Test the voltage ratio property. """

        sb = Bus(v_amplitude=0.9)
        tb = Bus(v_amplitude=1.1)
        e = Branch(sb, tb)

        self.assertAlmostEqual(e.v_ratio, 0.81818, places=5)


    def test_mode(self):
        """ Test the mode property. """

        sb = Bus(v_amplitude=1.0)
        tb = Bus(v_amplitude=1.0)
        e = Branch(sb, tb)

        self.assertEqual(e.mode, "Line")

        sb.v_amplitude = 2.0
        tb.v_amplitude = 0.5

        self.assertEqual(e.mode, "Transformer")


    def test_losses(self):
        """ Test the power loss properties. """

        e = Branch(Bus(), Bus())
        e.p_source = 1.0
        e.p_target = 0.9

        self.assertAlmostEqual(e.p_losses, 0.1, places=4)

        e.q_source = 0.3
        e.q_target = 0.1

        self.assertAlmostEqual(e.q_losses, 0.2, places=4)


    def test_id(self):
        """ Test that the id attribute is unique and suitably long. """

        e = Branch(Bus(), Bus())
        e2 = Branch(Bus(), Bus())

        self.assertNotEqual(e.id, e2.id)

        self.assertTrue(len(e.id) > 6)

# EOF -------------------------------------------------------------------------
