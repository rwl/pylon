__author__ = 'Richard Lincoln, r.w.lincoln@gmail.com'

""" This example demonstrates how to compute Nash equilibria. """

import numpy

from scipy.io import mmwrite

from pyreto import SmartMarket, DISCRIMINATIVE
from pyreto.discrete import MarketEnvironment, ProfitTask

from common import setup_logging, get_case6ww

setup_logging()

case = get_case6ww()
gens = case.generators#[0:2]
#passive = case.generators[2:3]
ng = len(gens)

mup = [0.0, 10.0, 20.0, 30.0]
nm = len(mup)


def nash2d():
    r = [numpy.zeros((nm, nm)), numpy.zeros((nm, nm))]# * 2#ng
    #r = numpy.zeros((nm, nm, 2))
    #r = numpy.zeros([ng] + ([nm] * ng))

    mkt = SmartMarket(case, priceCap=999.0, decommit=False,
#                      auctionType=DISCRIMINATIVE
                      )

    #tsks = []
    #for g in generators:
    #    e = MarketEnvironment([g], mkt, markups=mup)
    #    t = ProfitTask(e)
    #    tsks.append(t)
    #ptsks = []
    #for g in passive:
    #    e = MarketEnvironment([g], mkt, markups=mup)
    #    t = ProfitTask(e)
    #    ptsks.append(t)

    t1 = ProfitTask(MarketEnvironment([gens[0]], mkt, markups=mup))
    t2 = ProfitTask(MarketEnvironment([gens[1]], mkt, markups=mup))
    t3 = ProfitTask(MarketEnvironment([gens[2]], mkt, markups=mup))

    for m1 in range(nm):
        for m2 in range(nm):
            t1.env.performAction(m1)
            t2.env.performAction(m2)
            t3.env.performAction(0)

            mkt.run()

    #        r[m1, m2, 0] = t1.getReward()
    #        r[m1, m2, 1] = t2.getReward()

            r[0][m1, m2] = t1.getReward()
            r[1][m1, m2] = t2.getReward()

            mkt.reset()

    #for tsk1 in tsks:
    #    for m1 in range(nm):
    #
    #        for m2 in range(nm):
    #
    #            tsk1.env.performAction(m1)
    #
    #            others = [t for t in tsks if t != tsk1]
    #            for tsk2 in others:
    #                tsk2.env.performAction(m2)
    #
    #            for ptsk in ptsks:
    #                ptsk.env.performAction(0)
    #
    #            mkt.run()
    #
    #            for ti, t in enumerate(tsks):
    #                r[ti, m1, m2] = t.getReward()
    #
    #            mkt.reset()

    print r[0]
    print r[1]
    #for gi in range(2):
    #    mmwrite("/tmp/nash_g%s.mtx" % gi, r[gi, :, :])

    return r


def tex_table(a1, a2, mup):
    assert a1.shape == a2.shape
    m, n = a1.shape
    s = ""
    s += "\\begin{table}\n"
    s += "\\begin{center}\n"
    cols = "cc" + ("|cc" * (n)) + "|"
    s += "\\begin{tabular}{%s}\n" % cols
    s += "\cline{3-10}\n"
    s += " & &\multicolumn{8}{c|}{$G_1$} \\\\\n"
    s += "\cline{3-10}\n"
    s += " &"
    for i in range(n):
#        align = "c" if i == 0 else "c|"
        s += " &\multicolumn{2}{c|}{%s\\%%}" % mup[i]
    s += " \\\\\n"
    s += " &"
    for i in range(n):
        s += " &$r_1$ &$r_2$"
    s += " \\\\\n"
    s += "\hline\n"
    s += "\multicolumn{1}{|c|}{\multirow{4}{*}{$G_2$}}"
    for i in range(m):
        if i != 0:
            s += "\multicolumn{1}{|c|}{}"
        s += " &%.1f\\%%" % mup[i]
        for j in range(n):
            s += " &%.1f" % abs(a1[i, j])
            s += " &%.1f" % abs(a2[i, j])
        s += " \\\\\n"
    s += "\hline\n"
    s += "\end{tabular}\n"
    s += "\caption{Agent reward for Nash equilibrium analysis}\n"
    s += "\label{tbl:nash}\n"
    s += "\end{center}\n"
    s += "\end{table}"

    return s


def main():
    r = nash2d()
#    print tex_table(r[0], r[1], mup)
    table = tex_table(r[1], r[0], mup)
    print table
    fd = open("/tmp/table.tex", "w+b")
    fd.write(table)
    fd.close


if __name__ == "__main__":
    main()
