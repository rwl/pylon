#!/usr/bin/env python2.6
__author__ = 'Richard Lincoln, r.w.lincoln@gmail.com'

""" This example demonstrates how a round-robin competition to supply
electricity using a selection of learning methods. """

import sys
import logging
import itertools

from os.path import join

from scipy import array, zeros, r_, c_
from scipy.io import mmwrite

import pylon

from pyreto import SmartMarket
from pyreto import discrete
from pyreto import continuous
from pyreto.continuous import MarketExperiment
from pyreto.roth_erev import RothErev, VariantRothErev

from pybrain.tools.shortcuts import buildNetwork
from pybrain.rl.agents import LearningAgent
from pybrain.rl.explorers import BoltzmannExplorer #@UnusedImport
from pybrain.rl.learners.valuebased import ActionValueTable
from pybrain.rl.learners import Q, QLambda, SARSA #@UnusedImport
from pybrain.rl.learners import ENAC, Reinforce #@UnusedImport
from pybrain.rl.learners.valuebased.valuebased import ValueBasedLearner
from pybrain.rl.learners.directsearch.directsearch import DirectSearchLearner
from pybrain.structure import TanhLayer

logger = logging.getLogger()
for handler in logger.handlers: logger.removeHandler(handler) # rm pybrain
logger.addHandler(logging.StreamHandler(sys.stdout))
logger.setLevel(logging.DEBUG)


def roundrobin(case, learners, profile, m, nb, ns, mx, weeks, days,
               outdir="/tmp", dc=True, trial=0):
    np = len(profile)

    adj = "dc" if dc else "ac"
    market = SmartMarket(case, priceCap=100.0, decommit=True,
                         locationalAdjustment=adj)

    for i, perms in enumerate(itertools.permutations(learners)):
        experiment = MarketExperiment([], [], market, profile)

        for j, learner in enumerate(perms):
            gens = case.generators[j:j + 1]

            if isinstance(learner, ValueBasedLearner):
                # Comment out for stateful Roth-Erev learner.
                nstates = 1 if isinstance(learner, RothErev) else ns

                env = discrete.MarketEnvironment(gens, market,
                                                 markups=m,
                                                 numStates=nstates,
                                                 numOffbids=nb)
                task = discrete.ProfitTask(env, maxSteps=np)

                na = len(env._allActions)
                module = ActionValueTable(numStates=nstates, numActions=na)

            elif isinstance(learner, DirectSearchLearner):
                env = continuous.MarketEnvironment(gens, market, nb)

                task = continuous.ProfitTask(env, maxSteps=np, maxMarkup=mx)

                module = buildNetwork(env.outdim, 2, env.indim,
                                      bias=True, outputbias=True,
                                      hiddenclass=TanhLayer,outclass=TanhLayer)
            else:
                raise ValueError

            agent = LearningAgent(module, learner)
            experiment.tasks.append(task)
            experiment.agents.append(agent)

        all_states = zeros((3, 0))
        all_actions = zeros((3, 0))
        all_rewards = zeros((3, 0))
        comments = ["Trial: %d, Perm: %d" % (trial, i)]
        for task, agent in zip(experiment.tasks, experiment.agents):
            g = task.env.generators[0]
            l = agent.learner.__class__.__name__
            comments.append("(%s, %s)" % (g.name, l))
        c = ", ".join(comments)

        for _ in range(weeks):
            experiment.doEpisodes(days)

            states = zeros((0, days * np))
            actions = zeros((0, days * np))
            rewards = zeros((0, days * np))
            for _, agent in enumerate(experiment.agents):
                states = r_[states, agent.history["state"].T]
                actions = r_[actions, agent.history["action"].T]
                rewards = r_[rewards, agent.history["reward"].T]

                agent.learn()
                agent.reset()

            all_states = c_[all_states, states]
            all_actions = c_[all_actions, actions]
            all_rewards = c_[all_rewards, rewards]

        mmwrite(join(outdir, "state_%d_%d.mtx" % (trial, i)), all_states, c)
        mmwrite(join(outdir, "action_%d_%d.mtx" % (trial, i)), all_actions, c)
        mmwrite(join(outdir, "reward_%d_%d.mtx" % (trial, i)), all_rewards, c)


def case6ww1():
    case = pylon.Case.load(join("..", "data", "case6ww.pkl"))
    case.generators[0].p_cost = (0.0, 5.0, 200.0)
    case.generators[1].p_cost = (0.0, 6.5, 200.0)
    case.generators[2].p_cost = (0.0, 2.0, 200.0)

    case.generators[0].c_shutdown = 100.0

    #case.generators[0].p_min = 0.0 # TODO: Unit-decommitment.
    #case.generators[1].p_min = 0.0
    ##case.generators[2].p_min = 0.0

    case.generators[0].p_max = 100.0
    case.generators[1].p_max = 70.0
    case.generators[2].p_max = 70.0


    vre = VariantRothErev(experimentation=0.55, recency=0.3)
    vre.explorer = BoltzmannExplorer()#tau=100, decay=0.95)
    learners = [vre, Q(), Reinforce()]

    profile = [0.9, 0.6]

    m = (20, 75) # markups
    nb = 1 # no. offers
    ns = 3 # no. states

    mx = 60.0 # max markup

    weeks = 2
    days = 2

    outdir = "/tmp/case6ww1"
    dc = True

    trials = 1
    for i in range(trials):
        roundrobin(case, learners, profile, m, nb, ns, mx, weeks, days,
                   outdir, dc, trial=i)

def case24rts1():
    # Percent of annual peak. Starts first week of January.
    weekly = [86.2, 90.0, 87.8, 83.4, 88.0, 84.1, 83.2, 80.6, 74.0, 73.7, 71.5,
              72.7, 75.0, 72.1, 80.0, 70.4, 87.0, 88.0, 75.4, 83.7, 85.6, 81.1,
              90.0, 88.7, 89.6, 86.1, 75.5, 81.6, 80.1, 88.0, 72.2, 80.0, 72.9,
              77.6, 72.6, 70.5, 78.0, 69.5, 72.4, 72.4, 74.3, 74.4, 80.0, 88.1,
              88.5, 90.9, 94.0, 89.0, 94.2, 97.0, 100.0, 95.2]
    # Percent of weekly peak. Week beginning Monday.
    daily = [93, 100, 98, 96, 94, 77, 75]
    # Percentage of daily peak, starting at midnight. Weeks 1-8 and 44-52:
    hourly_winter_wkdy = [67, 63, 60, 59, 59, 60, 74, 86, 95, 96, 96, 95, 95,
                          95, 93, 94, 99, 100, 100, 96, 91, 83, 73, 63]
    hourly_winter_wknd = [78, 72, 68, 66, 64, 65, 66, 70, 80, 88, 90, 91, 90,
                          88, 87, 87, 91, 100, 99, 97, 94, 92, 87, 81]
    # Weeks 18-30:
    hourly_summer_wkdy = [64, 60, 58, 56, 56, 58, 64, 76, 87, 95, 99, 100, 99,
                          100, 100, 97, 96, 96, 93, 92, 92, 93, 87, 72]
    hourly_summer_wknd = [74, 70, 66, 65, 64, 62, 62, 66, 81, 86, 91, 93, 93,
                          92, 91, 91, 92, 94, 95, 95, 100, 93, 88, 80]
    # Weeks 9-17 and 31-43:
    hourly_spring_autumn_wkdy = [63, 62, 60, 58, 59, 65, 72, 85, 95, 99, 100,
                                 99, 93, 92, 90, 88, 90, 92, 96, 98, 96, 90,
                                 80, 70]
    hourly_spring_autumn_wknd = [75, 73, 69, 66, 65, 65, 68, 74, 83, 89, 92,
                                 94, 91, 90, 90, 86, 85, 88, 92, 100, 97, 95,
                                 90, 85]

    fullyear = zeros(364 * 24)
    c = 0
    l = [(0, 7, hourly_winter_wkdy, hourly_winter_wknd),
         (8, 16, hourly_spring_autumn_wkdy, hourly_spring_autumn_wknd),
         (17, 29, hourly_summer_wkdy, hourly_summer_wknd),
         (30, 42, hourly_spring_autumn_wkdy, hourly_spring_autumn_wknd),
         (43, 51, hourly_winter_wkdy, hourly_winter_wknd)]

    for start, end, wkdy, wknd in l:
        for w in weekly[start:end + 1]:
            for d in daily[:5]:
                for h in wkdy:
                    fullyear[c] = w * (d / 100.0) * (h / 100.0)
                    c += 1
            for d in daily[5:]:
                for h in wknd:
                    fullyear[c] = w * (d / 100.0) * (h / 100.0)
                    c += 1

    alldays = [w * (d / 100.0) for w in weekly for d in daily]


def main():
    case24rts1()


if __name__ == "__main__":
    main()
