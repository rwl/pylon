__author__ = 'Richard Lincoln, r.w.lincoln@gmail.com'

""" This example demonstrates profiling an OPF problem. """

from os.path import join, dirname

import cProfile
import pstats

import pylon.case
from pylon import Case, OPF #@UnusedImport

# Define a path to the data file.
CASE_FILE = join(dirname(pylon.case.__file__), "test", "data", "case30pwl.pkl")

# Load the data file.
case = Case.load(CASE_FILE)

cProfile.run("OPF(case, dc=False, opt={'verbose': True}).solve()", "opf_prof")

p = pstats.Stats("opf_prof")
#p.sort_stats('name').print_stats()
p.sort_stats('cumulative').print_stats(20)
#p.sort_stats('time').print_stats(20)
#p.sort_stats('time', 'cum').print_stats(.5, 'init')
