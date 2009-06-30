#------------------------------------------------------------------------------
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
#------------------------------------------------------------------------------

""" Test case for the Generator class. """

#------------------------------------------------------------------------------
#  Imports:
#------------------------------------------------------------------------------

from unittest import TestCase, main

from pylon.api import Generator

#------------------------------------------------------------------------------
#  "GeneratorTest" class:
#------------------------------------------------------------------------------

class GeneratorTest(TestCase):
    """ Test case for the Generator class. """

    def test_polynomial_cost(self):
        """ Test cost arrays for polynomial cost curve coefficients. """

        g = Generator(cost_model="Polynomial")

        p_max = 10
        p_min = 2
        c0 = 6.0
        c1 = 0.6
        c2 = 0.06
        c3 = 0.006

        g.p_max = p_max
        g.p_min = p_min
        g.polynomial = [c0, c1, c2, c3]

        # Validate x data.
        xdata = g.xdata

        self.assertTrue(
            xdata.size > 1,
            "xdata array not sufficiently long [%d]" % (xdata.size)
        )

        self.assertEqual(
            xdata.max(), g.p_max,
            "Max value of xdata [%d] should equal the maximum power [%d]" %
            (xdata.max(), g.p_max)
        )

        self.assertEqual(
            xdata.min(), g.p_min,
            "Min value of xdata [%d] should equal the minimum power [%d]" %
            (xdata.min(), g.p_min)
        )

        # Validate y data.
        ydata = g.ydata

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
        """ Test cost arrays for piecewise linear cost curve coordinates. """

        g = Generator(cost_model="Piecewise Linear")

        p_max = 10
        p_min = 2
        p0 = (0.0, 0.0)
        p1 = (0.4, 0.6)
        p2 = (1.0, 1.2)

        g.p_max = p_max
        g.p_min = p_min
        g.pw_linear = [p0, p1, p2]


if __name__ == "__main__":
    main()

# EOF -------------------------------------------------------------------------
