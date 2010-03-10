__author__ = 'Richard Lincoln, r.w.lincoln@gmail.com'

""" This example demonstrates how to use Pylon to simulate a power echange
auction market . """

#import matplotlib
#matplotlib.use('WXAgg')
#matplotlib.rc('font', **{'family': 'sans-serif',
#                         'sans-serif': ['Computer Modern Sans serif']})
#matplotlib.rc('font', **{'family': 'serif', 'serif': ['Computer Modern Roman']})
#matplotlib.rc('text', usetex=True)

import sys
import logging
import time
import pylab
import scipy

from os.path import join, dirname

import pylon

from pylon.pyreto import \
    MarketExperiment, DiscreteMarketEnvironment, ContinuousMarketEnvironment, \
    SmartMarket, DiscreteProfitTask, ContinuousProfitTask

from pybrain.rl.agents import LearningAgent
from pybrain.rl.learners.valuebased import ActionValueTable#, ActionValueNetwork
from pybrain.rl.learners import Q, QLambda, SARSA, ENAC, Reinforce #@UnusedImport
from pybrain.rl.explorers import BoltzmannExplorer #@UnusedImport
from pybrain.structure import TanhLayer #@UnusedImport
from pybrain.tools.shortcuts import buildNetwork
from pybrain.tools.plotting import MultilinePlotter

# Define a path to the data file.
DATA_DIR = join(dirname(pylon.case.__file__), "pyreto", "test", "data")
AUCTION_CASE = join(DATA_DIR, "t_auction_case.pkl")

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

# Create the market and associate learning agents with each generator.
market = SmartMarket(case)

# Specify the discrete set of possible markups on marginal cost.
markups = (0, 0.25, 0.5, 0.75, 1.0)

# Specify the number of offers/bids each participant can submit.
n_offbids = 2

# Specify the desired number of discrete states.
dim_state = 10

dim_action = len(markups) * n_offbids

# Use value based methods?
value_based = False

# Construct an experiment to test the market.
experiment = MarketExperiment([], [], market)

# Add the agents and their tasks.
for g in case.generators:
    if value_based:
        env = DiscreteMarketEnvironment(g, market, dim_state, markups, n_offbids)
        task = DiscreteProfitTask(env)
        module = ActionValueTable(dim_state, dim_action)
        module.initialize(1.0)
#        learner = SARSA(gamma=0.95)
        learner = Q()
#        learner = QLambda()
#        learner.explorer = BoltzmannExplorer() # default is e-greedy.
        agent = LearningAgent(module, learner)
    else:
        env = ContinuousMarketEnvironment(g, market, n_offbids, False)
        task = ContinuousProfitTask(env)
        net = buildNetwork(env.outdim, env.outdim + 10, env.indim, bias=False)#, hiddenclass=TanhLayer)
        learner = ENAC()
#        learner = Reinforce()
        agent = LearningAgent(net, learner)

    agent.name = g.name
    experiment.tasks.append(task)
    experiment.agents.append(agent)

# Prepare for plotting.
pylab.figure(figsize=(16,8))
pylab.ion()
pl = MultilinePlotter(autoscale=1.1, xlim=[0, 24], ylim=[0, 1],
                      maxLines=len(experiment.agents))
pl.setLineStyle(linewidth=2)
pl.setLegend([a.name for a in experiment.agents], loc='upper left')

# Solve an initial OPF.
pylon.OPF(case, market.loc_adjust=='dc').solve()

# Execute interactions with the environment in batch mode.
t0 = time.time()
x = 0
batch = 2
while x <= 1200:
    experiment.doInteractions(batch)
    for i, a in enumerate(experiment.agents):
        reward = scipy.mean(a.history.getSumOverSequences('reward'))
        pl.addData(i, x, reward)
        a.learn()
        a.reset()
    pl.update()
    x += batch

logger.info("Example completed in %.3fs" % (time.time() - t0))

time.sleep(6)
