__author__ = "Richard Lincoln, r.w.lincoln@gmail.com"

import sys

""" The "pylon" package contains the power system model classes and the
routines used to solve particular cases. """
from pylon import Case, Bus, Branch, Generator, Load, NewtonRaphson

""" The "readwrite" subpackage contains classes that will parse power system
data files and return a populated Case object.  It also contains classes that
will write a case to file in particular formats.  These can be used to export
the data to another program or, in this case, view the results of a simulation
run. """
from pylon.readwrite import ReSTWriter

""" Start by building up a one branch case with a generator at on end """
g = Generator(p=80.0, q=10.0)
bus1 = Bus(generators=[g])

""" and a load at the other. """
l = Load(p=60.0, q=4.0)
bus2 = Bus(loads=[l])

""" Connect the two buses """
line = Branch(bus1, bus2, r=0.05, x=0.01)

""" and add it all to a new case. """
case = Case(buses=[bus1, bus2], branches=[line])

""" Pass the newly created case to the routine of your choice """
NewtonRaphson().solve(case)

""" and then write the case out to view the results. """
ReSTWriter().write(case, sys.stdout)
