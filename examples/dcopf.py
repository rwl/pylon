__author__ = 'Richard Lincoln, r.w.lincoln@gmail.com'

""" This example demonstrates how to solve a DC OPF problem. """

import sys
from os.path import join, dirname

import pylon.case
from pylon import Case, DCOPF

# Define a path to the data file.
CASE_FILE = join(dirname(pylon.case.__file__), "test", "data", "case30pwl.pkl")

# Load the data file.
case = Case.load(CASE_FILE)

# Select a solver.
solver = None # Python solver from CVXOPT.
#solver = "glpk"
#solver = "mosek"

# Solve DC optimal power flow.
DCOPF(case, cvxopt=False, solver=solver, show_progress=False).solve()

# Print a report to screen.
case.save_rst(sys.stdout)
