__author__ = 'Richard Lincoln, r.w.lincoln@gmail.com'

""" This example demonstrates how to use the state estimator using data from
Problem 6.7 in 'Computational Methods for Electric Power Systems' by Mariesa
Crow."""

import sys
from cvxopt import matrix

from pylon.readwrite import PickleReader, ReSTWriter
from pylon.estimator import StateEstimator, Measurement, PF, PT, PG, VM

DATA_FILE = "case3bus_P6_6.pkl"

case = PickleReader().read(DATA_FILE)
measurements = [
    Measurement(case.branches[0], PF, 0.12),
    Measurement(case.branches[1], PF, 0.10),
    Measurement(case.branches[2], PT, -0.04),
    Measurement(case.buses[0], PG, 0.58),
    Measurement(case.buses[1], PG, 0.30),
    Measurement(case.buses[2], PG, 0.14),
    Measurement(case.buses[1], VM, 1.04),
    Measurement(case.buses[2], VM, 0.98)
]

# Measurement variances.
#sigma = {PF: 0.02, PT: 0.02, QF: 0.0, QT: 0.0, PG: 0.015, QG: 0.0, VM: 0.01, VA:0.0}
sigma = matrix([0.02, 0.02, 0,0, 0.015, 0, 0.01, 0])

StateEstimator(case, measurements, sigma).run()

ReSTWriter(case).write(sys.stdout)
