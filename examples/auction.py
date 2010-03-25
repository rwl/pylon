__author__ = 'Richard Lincoln, r.w.lincoln@gmail.com'

""" This example demonstrates how to use Pylon to simulate a power exchange
auction market. """

#import matplotlib
#matplotlib.use('WXAgg')
#matplotlib.rc('font', **{'family': 'sans-serif',
#                         'sans-serif': ['Computer Modern Sans serif']})
#matplotlib.rc('font', **{'family': 'serif', 'serif': ['Computer Modern Roman']})
#matplotlib.rc('text', usetex=True)

import os
import sys
import logging
import time
import tempfile
import shutil
import zipfile
import pylab
import scipy

from os.path import join, dirname, basename

import pylon

from pyreto import \
    MarketExperiment, EpisodicMarketExperiment, DiscreteMarketEnvironment, \
    ContinuousMarketEnvironment, SmartMarket, ProfitTask, EpisodicProfitTask

#from pyreto.tools import plot_gen_cost

from pybrain.rl.agents import LearningAgent
from pybrain.rl.learners.valuebased import ActionValueTable#, ActionValueNetwork
from pybrain.rl.learners import Q, QLambda, SARSA, ENAC, Reinforce #@UnusedImport
from pybrain.rl.explorers import BoltzmannExplorer #@UnusedImport
from pybrain.structure import TanhLayer #@UnusedImport
from pybrain.tools.shortcuts import buildNetwork
from pybrain.tools.plotting import MultilinePlotter

# Define a path to the data file.
# DATA_DIR = join("..", "pyreto", "test", "data")
DATA_DIR = join(dirname(pylon.case.__file__), "test", "data")
# AUCTION_CASE = join(DATA_DIR, "t_auction_case.pkl")
AUCTION_CASE = join(DATA_DIR, "case6ww.pkl")

# Set up publication quality graphs.
#fig_width_pt = 246.0  # Get this from LaTeX using \showthe\columnwidth
#inches_per_pt = 1.0 / 72.27               # Convert pt to inch
#golden_mean = (pylab.sqrt(5) - 1.0) / 2.0 # Aesthetic ratio
#fig_width = fig_width_pt * inches_per_pt  # width in inches
#fig_height = fig_width * golden_mean      # height in inches
#fig_size = [fig_width, fig_height]
#params = {'backend': 'ps',
#          'axes.labelsize': 10,
#          'text.fontsize': 10,
#          'legend.fontsize': 10,
#          'xtick.labelsize': 8,
#          'ytick.labelsize': 8,
#          'text.usetex': True,
#          'figure.figsize': fig_size}
#pylab.rcParams.update(params)

# Set up the logger.
logger = logging.getLogger()
for handler in logger.handlers: logger.removeHandler(handler) #remove pybrain
handler = logging.FileHandler("/tmp/pylon.log", mode="wb")
handler.setFormatter(logging.Formatter("%(message)s"))
logger.addHandler(handler)
logger.addHandler(logging.StreamHandler(sys.stdout))
logger.setLevel(logging.DEBUG)

#logging.basicConfig(stream=sys.stdout, level=logging.DEBUG)
#logger = logging.getLogger()

# Load the case.
case = pylon.Case.load(AUCTION_CASE)

# Inspect generator costs.
#plot_gen_cost(case.generators)

# Create the market and associate learning agents with each generator.
market = SmartMarket(case)

# Specify the discrete set of possible markups on marginal cost.
markups = (0.1, 0.2, 0.33, 0.5, 0.6, 0.75, 1.0)

# Specify the number of offers/bids each participant can submit.
n_offbids = 4

# Specify the desired number of discrete states.
dim_state = 10

dim_action = len(markups) * n_offbids

# Construct an experiment to test the market.
experiment = MarketExperiment([], [], market)

# Add the agents and their tasks.
for g in case.generators:
    env = DiscreteMarketEnvironment(g, market, dim_state, markups, n_offbids)
    task = ProfitTask(env)
    module = ActionValueTable(dim_state, dim_action)
    module.initialize(1.0)
#    learner = SARSA(gamma=0.9)
    learner = Q()
#    learner = QLambda()
#    learner.explorer = BoltzmannExplorer() # default is e-greedy.
    agent = LearningAgent(module, learner)

    agent.name = g.name
    experiment.tasks.append(task)
    experiment.agents.append(agent)

# Prepare for plotting.
pylab.figure(figsize=(16,8))
#pylab.ion()
pl = MultilinePlotter(autoscale=1.1, xlim=[0, 24], ylim=[0, 1],
                      maxLines=len(experiment.agents))
pl.setLineStyle(linewidth=2)
pl.setLegend([a.name for a in experiment.agents], loc='upper left')

# Solve an initial OPF.
# pylon.OPF(case, market.loc_adjust=='dc').solve()

# Save action and reward data for plotting.
agent_map = {}
for agent in experiment.agents:
    agent_map[agent.name] = (scipy.zeros((1,)), scipy.zeros((1,)))

## Save data in tables for plotting with PGF/Tikz.
#table_map = {"state": {}, "action": {}, "reward": {}}
#timestr = time.strftime("%Y%m%d%H%M", time.gmtime())
#table_dir = tempfile.mkdtemp(prefix=timestr)
#for a in experiment.agents:
#    for t in ("state", "action", "reward"):
#        file_name = "%s-%s.table" % (a.name, t)
#        tmp_name = join(table_dir, file_name)
##        tmp_fd, tmp_name = tempfile.mkstemp(".table", prefix, table_dir)
##        os.close(tmp_fd) # gets deleted
#        fd = file(tmp_name, "w+b")
#        fd.write("# %s %s data - %s\n" % (a.name, t, timestr))
#        fd.close()
#        table_map[t][a.name] = tmp_name

# Execute interactions with the environment in batch mode.
t0 = time.time()
x = 0
batch = 10
while x <= 1000:
    experiment.doInteractions(batch)
    for i, agent in enumerate(experiment.agents):
        s, a, r = agent.history.getSequence(agent.history.getNumSequences()-1)
        pl.addData(i, x, scipy.mean(r))

        action, reward = agent_map[agent.name]

        agent_map[agent.name] = (scipy.r_[action, a.flatten()],
                                 scipy.r_[reward, r.flatten()])

#        for n, seq in (("state", s), ("action", a), ("reward", r)):
#            tmp_name = table_map[n][agent.name]
#            fd = file(tmp_name, "a+b")
#            for i in range(batch):
#                fd.write("%.1f %.5f\n" % (x + i, seq[i]))
#            fd.close()

        agent.learn()
        agent.reset()

#    plot_gen_cost(case.generators)

    pl.update()
    x += batch

logger.info("Example completed in %.3fs" % (time.time() - t0))

from pyreto.tools import sparkline_data
sparkline_data(agent_map, "auctiondata.txt")

#table_zip = zipfile.ZipFile("%s.zip" % timestr, "w")
#for a in experiment.agents:
#    for t in ("state", "action", "reward"):
#        tmp_name = table_map[t][a.name]
#        table_zip.write(tmp_name, basename(tmp_name), zipfile.ZIP_DEFLATED)
#table_zip.close()
#shutil.rmtree(table_dir)

#time.sleep(6)
