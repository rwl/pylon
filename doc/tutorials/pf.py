#------------------------------------------------------------------------------
# Pylon Tutorial "Power Flow"
#
# Author: Richard Lincoln, r.w.lincoln@gmail.com
#------------------------------------------------------------------------------

""" The "pylon" package contains classes for defining a power system model and
power flow solvers. """
from pylon import Case, Bus, Branch, Generator, NewtonPF, FastDecoupledPF

""" Import "sys" so the report can be written to stdout. """
import sys

""" Start by building up a one branch case with a generator at one end """
bus1 = Bus()
g = Generator(bus1, p=80.0, q=10.0)

""" and fixed load at the other. """
bus2 = Bus(p_demand=60.0, q_demand=4.0)

""" Connect the two buses """
line = Branch(bus1, bus2, r=0.05, x=0.01)

""" and add it all to a new case. """
case = Case(buses=[bus1, bus2], branches=[line], generators=[g])

""" Choose to solve using either Newton's method """
solver = NewtonPF(case)

""" or Fast Decoupled method """
solver = FastDecoupledPF(case).solve()

""" and then call the solver. """
solver.solve()

""" Write the case out to view the results. """
case.save_rst(sys.stdout)
