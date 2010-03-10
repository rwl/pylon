__author__ = 'Richard Lincoln, r.w.lincoln@gmail.com'

""" This example demonstrates how to profile an OPF problem. """

from os.path import join, dirname

from hotshot import Profile
from hotshot import stats

import pylon.case
from pylon import Case, OPF

# Define a path to the data file.
CASE_FILE = join(dirname(pylon.case.__file__), "test", "data", "case30pwl.pkl")

# Load the data file.
case = Case.load(CASE_FILE)

prof = Profile("hotshot_opf_stats")
prof.runcall(OPF(case, dc=False, opt={"verbose": True}).solve)
prof.close()

st = stats.load("hotshot_opf_stats")
st.strip_dirs()
st.sort_stats('time', 'calls')
st.print_stats()
