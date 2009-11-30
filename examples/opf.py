__author__ = "Richard Lincoln, r.w.lincoln@gmail.com"

import sys
from pylon import Case, Bus, Branch, Generator, Load, DCOPF
from pylon.readwrite import ReSTWriter

""" This tutorial will attempt to guide you through solving and Optimal Power
Flow problem using Pylon.

First we create two generators with different costs: """

g1 = Generator(p_min=0.0, p_max=80.0, cost_coeffs=(0.0, 6.0, 0.0))
g2 = Generator(p_min=0.0, p_max=60.0, cost_coeffs=(0.0, 9.0, 0.0))

""" Next we define the load that they are to supply. """

l = Load(p=100.0)

""" We need to add these to a network with the desired connectivity. """

bus1 = Bus(generators=[g1], loads=[l])
bus2 = Bus(generators=[g2])
line = Branch(bus1, bus2, r=0.05)
case = Case(buses=[bus1, bus2], branches=[line])

""" The case may then be passed to the OPF routine and solved. """

DCOPF().solve(case)

""" We view the results as ReStructuredText tables. """
ReSTWriter().write(case, sys.stdout)
