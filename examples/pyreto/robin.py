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


def main():
    case6ww1()


if __name__ == "__main__":
    main()
