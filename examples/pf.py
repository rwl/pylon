__author__ = 'Richard Lincoln, r.w.lincoln@gmail.com'

""" This example demonstrates how to solve a power flow problem using data
in PSS/E Raw format. """

import sys
import pylon

# Data files format if recognised according to file extension.
case = pylon.Case.load("data/case30pwl.m")

# Pass the case to the solver and solve.
pylon.NewtonPF(case).solve()
#pylon.FastDecoupledPF(case, method="XB").solve()

# Print a report to screen.
case.save_rst(sys.stdout)
