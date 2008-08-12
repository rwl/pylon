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
Test case for the Generator class

"""

#-------------------------------------------------------------------------------
#  Imports:
#-------------------------------------------------------------------------------

from unittest import TestCase, main

from pylon.generator import Generator

#-------------------------------------------------------------------------------
#  "GeneratorTest" class:
#-------------------------------------------------------------------------------

class GeneratorTest(TestCase):
    """
    Test case for the Generator class

    """

    def setUp(self):
        """
        The test runner will execute this method prior to each test

        """

        self.g = Generator()


    def test_id(self):
        """
        Test that the id attribute is unique

        """

        g2 = Generator()

        self.assertNotEqual(
            self.g.id, g2.id,
            "IDs [%s, %s] of two generators found equal" %
            (self.g.id, g2.id)
        )

        self.assertTrue(
            len(self.g.id) > 6,
            "ID [%s] of generator is of insufficient length" %
            (self.l.id)
        )


    def test_polynomial_cost(self):
        """
        Test the computation of cost arrays when using polynomial
        cost curve coefficients

        """

        self.g.cost_model = "Polynomial"

        p_max = 10
        p_min = 2
        c0 = 6.0
        c1 = 0.6
        c2 = 0.06
        c3 = 0.006

        self.g.p_max = p_max
        self.g.p_min = p_min
        self.g.polynomial = [c0, c1, c2, c3]

        self.validate_xdata(self.g.xdata)

        ydata = self.g.ydata

        # Final point
        y_final = c0 + c1*p_max + c2*p_max**2 + c3*p_max**3
        self.assertEqual(
            ydata[ydata.size-1], y_final,
            "Final point in ydata [%d] should be %d" %
            (ydata[ydata.size-1], y_final)
        )

        # First point
        y_first = c0 + c1*p_min + c2*p_min**2 + c3*p_min**3
        self.assertEqual(
            ydata[0], y_first,
            "First point in ydata [%d] should be %d" %
            (ydata[0], y_first)
        )


    def test_piecewise_linear_cost(self):
        """
        Test the computation of cost arrays when using piecewise
        linear cost curve coordinates

        """

        self.g.cost_model = "Piecewise Linear"

        p_max = 10
        p_min = 2
        p0 = (0.0, 0.0)
        p1 = (0.4, 0.6)
        p2 = (1.0, 1.2)

        self.g.p_max = p_max
        self.g.p_min = p_min
        self.g.pw_linear = [p0, p1, p2]


    def validate_xdata(self, xdata):
        self.assertTrue(
            xdata.size > 1,
            "xdata array not suitably long [%d]" % (xdata.size)
        )

        self.assertEqual(
            xdata.max(), self.g.p_max,
            "Max value of xdata [%d] should equal the maximum power [%d]" %
            (xdata.max(), self.g.p_max)
        )

        self.assertEqual(
            xdata.min(), self.g.p_min,
            "Min value of xdata [%d] should equal the minimum power [%d]" %
            (xdata.min(), self.g.p_min)
        )


if __name__ == "__main__":
    main()

# EOF -------------------------------------------------------------------------
