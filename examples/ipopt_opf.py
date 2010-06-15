__author__ = 'Richard Lincoln, r.w.lincoln@gmail.com'

""" This example demonstrates how to use the IPOPT OPF solver. """

import sys
import logging

from os.path import join, dirname

import pylon.ipopf

logging.basicConfig(stream=sys.stdout, level=logging.DEBUG)

# Define a path to the data file.
CASE_FILE = join(dirname(pylon.__file__), "test", "data", "case6ww.pkl")

# Load the data file.
case = pylon.Case.load(CASE_FILE)

# Solve DC optimal power flow.
opf = pylon.OPF(case, dc=False, opt={"verbose": True})
solution = opf.solve(pylon.ipopf.IPOPFSolver)

# Analyse the solution.
if solution["converged"]:
    print "Completed in %.3fs." % solution["elapsed"]
else:
    print "Failed!"
