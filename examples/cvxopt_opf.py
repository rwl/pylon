__author__ = 'Richard Lincoln, r.w.lincoln@gmail.com'

""" This example demonstrates how to solve an OPF problem using CVXOPT. """

import sys
import logging

from os.path import join, dirname

import pylon
import contrib.cvxopf as cvxopf

# Set up basic logging.
logging.basicConfig(stream=sys.stdout, level=logging.DEBUG)

# Define a path to a data file.
CASE_FILE = join(dirname(pylon.__file__), "test", "data", "case6ww.pkl")

# Load the data file.
case = pylon.Case.load(CASE_FILE)

# Pass the solver class to the solve method.
opf = pylon.OPF(case, dc=False, opt={"verbose": True})
solution = opf.solve(cvxopf.CVXOPTSolver)

# Analyse the solution.
print solution["status"]
print solution["x"]
#if solution["converged"]:
#    print "Completed in %.3fs." % solution["elapsed"]
#else:
#    print "Failed!"
