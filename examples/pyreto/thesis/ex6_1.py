__author__ = 'Richard Lincoln, r.w.lincoln@gmail.com'

""" This script runs the first experiment from chapter 6 of Learning to Trade
Power by Richard Lincoln. """

import random
from numpy import zeros, c_

import pyreto.continuous

from pyreto.roth_erev import VariantRothErev

from pybrain.rl.explorers import BoltzmannExplorer #@UnusedImport
from pybrain.rl.learners import Q, QLambda, SARSA #@UnusedImport
from pybrain.rl.learners import ENAC, Reinforce #@UnusedImport

from common import \
    get_case24_ieee_rts, setup_logging, run_experiment, save_result, \
    get_continuous_task_agent, get_full_year, get_zero_task_agent

setup_logging()

decommit = False
cap = 100.0
profile = [1.0] * 7
nOffer = 1
manual_sigma = True
markupMax = 30.0

def get_portfolios():
    g1 = range(0, 4)
    g2 = range(4, 8)
    g7 = range(8, 11)
    g13 = range(11, 14)
    g14 = [14] # sync cond
    g15 = [15, 21]
    g16 = [21]
    g18 = [22]
    g21 = [23]
    g22 = range(24, 30)
    g23 = range(30, 33)

    portfolios = [g1 + g2 + g7,
                  g13 + g23,
                  g15 + g16,
                  g18 + g21 + g22]

    sync_cond = g14

    return portfolios, sync_cond


#def weighted_choice(lst):
#    """ Makes weighted choices.  Accepts a list of tuples with the item and
#    probability as a pair like:
#    >>> x = [('one', 0.25), ('two', 0.25), ('three', 0.5)]
#    >>> y=windex(x) """
#    n = random.uniform(0, 1)
#    for item, weight in lst:
#        if n < weight:
#            break
#        n = n - weight
#    return item
#
#
#def do_outages(case):
#    # Outage rate (outages/year).
#    rate = [0.24, 0.51, 0.33, 0.39, 0.48, 0.38, 0.02, 0.36, 0.34, 0.33, 0.3,
#            0.44, 0.44, 0.02, 0.02, 0.02, 0.02, 0.4, 0.39, 0.4, 0.52,
#            0.49, 0.38, 0.33, 0.41, 0.41, 0.41, 0.35, 0.34, 0.32, 0.54,
#            0.35, 0.35, 0.38, 0.38, 0.34, 0.34, 0.45]
#
#    per = 365
#    weights = [[(False, r / per), (True, 1 - (r / per))] for r in rate]
#
#    for i, ln in enumerate(case.branches):
#        ln.online = weighted_choice(weights[i])


def get_enac_experiment(case):

    market = pyreto.SmartMarket(case, priceCap=cap, decommit=decommit)

    # Outage rate (outages/year).
    rate = [0.24, 0.51, 0.33, 0.39, 0.48, 0.38, 0.02, 0.36, 0.34, 0.33, 0.3,
            0.44, 0.44, 0.02, 0.02, 0.02, 0.02, 0.4, 0.39, 0.4, 0.52,
            0.49, 0.38, 0.33, 0.41, 0.41, 0.41, 0.35, 0.34, 0.32, 0.54,
            0.35, 0.35, 0.38, 0.38, 0.34, 0.34, 0.45]

    per = 365
    outage_rate = [r / per for r in rate]

    experiment = pyreto.continuous.MarketExperiment([], [], market,
                                                    outages=outage_rate)

    portfolios, sync_cond = get_portfolios()

    for gidx in portfolios:
        g = [case.generators[i] for i in gidx]

        task, agent = get_continuous_task_agent(
            g, market, nOffer, markupMax, profile, ENAC())

#        if manual_sigma:
#            sigma = [-5.0] * task.env.indim
#            agent.learner.explorer.sigma = sigma

        experiment.tasks.append(task)
        experiment.agents.append(agent)

    # Have an agent bid at marginal cost (0.0) for the sync cond.
    task, agent = get_zero_task_agent(sync_cond, market, nOffer, profile)

    return experiment


def run_experiment(experiment):
    """ Runs the given experiment and returns the results.
    """
    # Fixed number of roleouts and samples due to profile data.
    roleouts = 52
    samples = 7 # number of samples per learning step

    na = len(experiment.agents)
    all_action = zeros((na, 0))
    all_reward = zeros((na, 0))

    full_year = get_full_year()

    for roleout in range(roleouts):
        # Apply new load profile before each episode (week).
        i = roleout * samples # index of first profile value
        experiment.profile = full_year[i: i + samples]

        experiment.doEpisodes(samples)

        epi_action = zeros((0, samples))
        epi_reward = zeros((0, samples))

        for agent in experiment.agents:
            epi_action = c_[epi_action.T, agent.history["action"]].T
            epi_reward = c_[epi_reward.T, agent.history["reward"]].T

            agent.learn()
            agent.reset()

        all_action = c_[all_action, epi_action]
        all_reward = c_[all_reward, epi_reward]

    return all_action, all_reward


def main():
    case = get_case24_ieee_rts()

    do_outages(case)

    enac_experiment = get_enac_experiment(case)

    in_cloud = False

    if in_cloud:
        import cloud
        job_id = cloud.call(run_experiment, enac_experiment, _high_cpu=False)
        result = cloud.result(job_id)
        action, reward = result
    else:
        action, reward = run_experiment(enac_experiment)

    save_result(action, "./out/ex6_1_enac_action.mtx",
                "Experiment 6.1 ENAC actions.")
    save_result(reward, "./out/ex6_1_enac_reward.mtx",
                "Experiment 6.1 ENAC rewards.")


if __name__ == "__main__":
    main()
