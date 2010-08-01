__author__ = 'Richard Lincoln, r.w.lincoln@gmail.com'

""" This example demonstrates how to compute Nash equilibria. """

import numpy
import pylon

from pyreto import SmartMarket
from pyreto.discrete import MarketEnvironment, ProfitTask

case = pylon.Case.load("../data/case6ww.pkl")
ng = len(case.generators)

mup = [0.0, 10.0, 20.0, 30.0]
nm = len(mup)

r = numpy.zeros([nm] * nm)

mkt = SmartMarket(case, priceCap=999.0, decommit=True)

tsks = []
for g in case.generators:
    e = MarketEnvironment([g], mkt, markups=mup)
    t = ProfitTask(e)
    tsks.append(t)

for tsk in tsks:
    for i in range(nm):
        tsk.env.perfromAction(i)

        for j in range(nm):
            others = [t for t in tsks if t != tsk]
            for t in others:
                t.env.perfromAction(j)

            mkt.run()

            for k, t in enumerate(others):
                r[i, j, k] = t.getReward()