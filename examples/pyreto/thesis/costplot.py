__author__ = 'Richard Lincoln, r.w.lincoln@gmail.com'

""" This example demonstrates how to produce a publication plot of generator
costs using matplotlib. """

import matplotlib
#matplotlib.use('WXAgg')#'TkAgg')

#matplotlib.rc('font', **{'family': 'sans-serif',
#                         'sans-serif': ['Computer Modern Sans serif']})
matplotlib.rc('font', **{'family': 'serif', 'serif': ['Computer Modern Roman']})
matplotlib.rc('text', usetex=True)

from os.path import join, dirname

import scipy
import pylab
import pylon

DATA_DIR = join(dirname(pylon.case.__file__), "test", "data")
CASE = join(DATA_DIR, "case24_ieee_rts", "case24_ieee_rts.pkl")
#DATA_DIR = join(dirname(__file__), "data")
#CASE = join(DATA_DIR, "case24_ieee_rts3.pkl")

paper = False

if not paper:
    #matplotlib.rcParams['lines.linewidth'] = 0.5
    matplotlib.rcParams['axes.linewidth'] = 0.7

# Set up publication quality graphs.
#fig_width_pt = 246.0  # Get this from LaTeX using \showthe\columnwidth
#inches_per_pt = 1.0 / 72.27               # Convert pt to inch
golden_mean = (pylab.sqrt(5) - 1.0) / 2.0 # Aesthetic ratio
fig_width = 5.5#fig_width_pt * inches_per_pt  # width in inches
fig_height = fig_width * golden_mean      # height in inches
fig_size = [fig_width, fig_height]
if paper:
    params = {'backend': 'ps',
              'axes.titlesize': 12,
              'axes.labelsize': 12,
              'text.fontsize': 12,
              'legend.fontsize': 10,
              'xtick.labelsize': 10,
              'ytick.labelsize': 10,
              'text.usetex': True,
              'figure.figsize': fig_size}
    pylab.rcParams.update(params)
else:
    params = {'backend': 'ps',
              'axes.titlesize': 10,
              'axes.labelsize': 10,
              'text.fontsize': 10,
              'legend.fontsize': 8,
              'xtick.labelsize': 8,
              'ytick.labelsize': 8,
              'text.usetex': True,
    #          'markup': 'tex',
    #          'text.latex.unicode': True,
              'figure.figsize': fig_size}
    pylab.rcParams.update(params)

case = pylon.Case.load(CASE)

#g = [0,2,8,11,15,20,22,24,32]
g = [24,2,8,20,11,32,22]
#g = [(9, 50), (0, 76), (2, 100), (5, 155), (3, 197), (11, 350), (7, 400)]

style = [('black', '-'), ('0.5', '-'), ('black', ':'), ('0.5', ':'),
    ('black', '--'), ('0.5', '--'), ('black', '-.'), ('0.5', '-.'), ('0.8', '-')]
ns = len(style)

fig = pylab.figure()
pylab.title("IEEE RTS Generator Cost Functions")
for i, gi in enumerate(g):
    generator = case.generators[gi]
    if generator.pcost_model == pylon.PW_LINEAR:
        x = [x for x, _ in generator.p_cost]
        y = [y for _, y in generator.p_cost]
    elif generator.pcost_model == pylon.POLYNOMIAL:
        x = scipy.arange(generator.p_min, generator.p_max, 0.1)
        y = scipy.polyval(scipy.array(generator.p_cost), x)
    else:
        raise
    clr, ls = style[i]
    pylab.plot(x, y, linestyle=ls, color=clr,
                            label="U%s" % int(generator.p_max))
    pylab.xlabel("Generator set-point (MW)")
#    pylab.ylabel(r"Cost (\verb+$+/h)")
    pylab.ylabel(r"Cost (USD/h)")

l = pylab.legend(loc="upper right")
if not paper:
    l.get_frame().set_linewidth(0.7)


fig = fig.gca().ticklabel_format(style='sci', scilimits=(0,0), axis='y')

pylab.annotate("Oil", (90, 7000))
pylab.annotate("Coal", (170, 3600))
pylab.annotate("Nuclear", (210, 1800))

pylab.subplots_adjust(bottom=0.12)

#pylab.show()

#pylab.savefig('./out/ieee_rts_gencosts.pdf')
pylab.savefig('/tmp/ieee_rts_gencosts.eps')
