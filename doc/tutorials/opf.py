#------------------------------------------------------------------------------
# Pylon Tutorial "Optimal Power Flow"
#
# Author: Richard Lincoln, r.w.lincoln@gmail.com
#------------------------------------------------------------------------------

__author__ = 'Richard Lincoln, r.w.lincoln@gmail.com'

import sys
from pylon import Case, Bus, Branch, Generator, DCOPF

""" This tutorial provides a guide for solving an Optimal Power
Flow problem using Pylon.

First create two generators with different costs: """

g1 = Generator(p_min=0.0, p_max=80.0, p_cost=(0.0, 6.0, 0.0))
g2 = Generator(p_min=0.0, p_max=60.0, p_cost=(0.0, 9.0, 0.0))


""" Add these to a network with the desired connectivity. """

bus1 = Bus(generators=[g1], p_demad=100.0)
bus2 = Bus(generators=[g2])
line = Branch(bus1, bus2, r=0.05)
case = Case(buses=[bus1, bus2], branches=[line])

""" Pass the case to the OPF routine and solve. """

DCOPF().solve(case)

""" View the results as ReStructuredText tables. """
case.save_rst(sys.stdout)
