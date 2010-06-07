__author__ = 'Richard Lincoln, r.w.lincoln@gmail.com'

""" This example demonstrates how to solve an OPF problem. """

import sys
import logging
import numpy
import scipy.io

from os.path import join, dirname

import pylon

logging.basicConfig(stream=sys.stdout, level=logging.DEBUG)

# Define a path to the data file.
CASE_FILE = join(dirname(pylon.__file__), "test", "data", "case6ww.pkl")

# Load the data file.
case = pylon.Case.load(CASE_FILE)

# Assume initial demand is peak and save it.
Pd0 = [b.p_demand for b in case.buses if b.type == pylon.PQ]

# Define a 24-hour load profile with hourly values.
p1h = [0.52, 0.54, 0.52, 0.50, 0.52, 0.57, 0.60, 0.71, 0.89, 0.85, 0.88, 0.94,
       0.90, 0.88, 0.88, 0.82, 0.80, 0.78, 0.76, 0.68, 0.68, 0.68, 0.65, 0.58]

# Scale it up a bit.
p1h = [x + 0.7 * (1.0 - x) for x in p1h]

# Define some arrays for storing OPF results.
n = len(p1h)
ng = len(case.generators)
f_dc = numpy.zeros(n)
f_ac = numpy.zeros(n)
Pg_dc = numpy.zeros((ng, n))
Pg_ac = numpy.zeros((ng, n))
Qg_ac = numpy.zeros((ng, n))

# Determine minimum cost and generator set-points using the DC formulation.
for i, fraction in enumerate(p1h):
    for j, bus in enumerate([b for b in case.buses if b.type == pylon.PQ]):
        bus.p_demand = p1h[i] * Pd0[j]
    s = pylon.OPF(case, opt={"verbose": False}).solve()

    print "Converged:", s["converged"]
    f_dc[i] = s["f"]
    Pg_dc[:, i] = numpy.array([g.p for g in case.generators])

ac_min_cost = numpy.zeros(len(p1h))
for i, fraction in enumerate(p1h):
    for j, bus in enumerate([b for b in case.buses if b.type == pylon.PQ]):
        bus.p_demand = p1h[i] * Pd0[j]
    s = pylon.OPF(case, dc=False, opt={"verbose": True}).solve()
    f_ac[i] = s["f"]
    Pg_ac[:, i] = numpy.array([g.p for g in case.generators])
    Qg_ac[:, i] = numpy.array([g.q for g in case.generators])

# Save the results in Matrix Market format.
scipy.io.mmwrite("./data/fDC.mtx", numpy.matrix(f_dc))
scipy.io.mmwrite("./data/PgDC.mtx", numpy.matrix(Pg_dc))
scipy.io.mmwrite("./data/fAC.mtx", numpy.matrix(f_ac))
scipy.io.mmwrite("./data/PgAC.mtx", numpy.matrix(Pg_ac))
scipy.io.mmwrite("./data/QgAC.mtx", numpy.matrix(Qg_ac))
