__author__ = 'Richard Lincoln, r.w.lincoln@gmail.com'

""" This example demonstrates how to solve an OPF problem. """

import sys
from os.path import join, dirname

import pylon.case
from pylon import Case, OPF

# Define a path to the data file.
CASE_FILE = join(dirname(pylon.case.__file__), "test", "data", "case30pwl.pkl")

# Load the data file.
case = Case.load(CASE_FILE)

# Use DC formulation?
dc = False

# Solve DC optimal power flow.
OPF(case, dc, opt={"verbose": True}).solve()

# Print a report to screen.
case.save_rst(sys.stdout)
