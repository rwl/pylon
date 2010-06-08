__author__ = 'Richard Lincoln, r.w.lincoln@gmail.com'

""" This example demonstrates how use Pylon with PiCloud. """

import cloud

import pylon

def upload():
    cloud.files.put("data/case6ww.pkl")
#upload()


def pf():
    cloud.files.get("case6ww.pkl", "case6ww.pkl")

    # Data files format if recognised according to file extension.
    case = pylon.Case.load("case6ww.pkl")

    # Pass the case to the solver and solve.
#    sol = pylon.NewtonPF(case, iter_max=20).solve()
#    sol = pylon.FastDecoupledPF(case, method=pylon.XB).solve()
    sol = pylon.OPF(case, dc=False).solve()

    return sol

job_id = cloud.call(pf,_high_cpu=False)

solution = cloud.result(job_id)

if solution["converged"]:
    print "Completed in %.3fs." % solution["elapsed"]
else:
    print "Failed!"
