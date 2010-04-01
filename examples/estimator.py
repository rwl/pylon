__author__ = 'Richard Lincoln, r.w.lincoln@gmail.com'

""" This example demonstrates how to use the state estimator by using data from
Problem 6.7 in 'Computational Methods for Electric Power Systems' by Mariesa
Crow."""

import sys

from pylon import Case, StateEstimator, Measurement, PF, PT, PG, VM

from numpy import array

DATA_FILE = "../pylon/test/data/case3bus_P6_6.m"

# Load the case file.
case = Case.load(DATA_FILE)

# Specify the measurements.
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

# Specify measurement variances (ordered: PF, PT, QF, QT, PG, QG, VM, VA).
sigma = array([0.02, 0.02, 0.0, 0.0, 0.015, 0.0, 0.01, 0.0])

# Create a state estimator...
se = StateEstimator(case, measurements, sigma)
# ...and run it.
sol = se.run()

# Write out the power flow solution...
case.save_rst(sys.stdout)

# ...and a measurement comparison.
se.output_solution(sys.stdout, sol["z"], sol["z_est"], sol["error_sqrsum"])
