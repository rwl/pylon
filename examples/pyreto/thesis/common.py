__author__ = 'Richard Lincoln, r.w.lincoln@gmail.com'

""" Functions common to all experiments. """

import os
import sys
import logging

from numpy import zeros, array, c_, vectorize, copy
from scipy.io import mmwrite

import pylon

from pylon.util import pickle_matpower_cases

import pyreto.discrete
import pyreto.continuous

from pybrain.rl.learners.directsearch.directsearch import DirectSearchLearner
from pybrain.rl.learners.valuebased.valuebased import ValueBasedLearner

from pybrain.rl.agents import LearningAgent
from pybrain.rl.learners.valuebased import ActionValueTable
from pybrain.tools.shortcuts import buildNetwork
from pybrain.structure import TanhLayer, LinearLayer #@UnusedImport


def setup_logging():
    logger = logging.getLogger()
    for handler in logger.handlers:
        logger.removeHandler(handler) # rm pybrain
    logger.addHandler(logging.StreamHandler(sys.stdout))
    logger.setLevel(logging.DEBUG)


def get_case6ww():
    """ Returns the 6 bus case from Wood & Wollenberg PG&C.
    """
    path = os.path.dirname(pylon.__file__)
    path = os.path.join(path, "test", "data")
    path = os.path.join(path, "case6ww", "case6ww.pkl")

    case = pylon.Case.load(path)
    case.generators[0].p_cost = (0.0, 4.0, 200.0)
    case.generators[1].p_cost = (0.0, 3.0, 200.0)

#    case.generators[0].p_cost = (0.0, 5.1, 200.0) # 10%
#    case.generators[1].p_cost = (0.0, 4.5, 200.0) # 30%

    case.generators[2].p_cost = (0.0, 6.0, 200.0) # passive

#    case.generators[0].c_shutdown = 100.0
#    case.generators[1].c_shutdown = 100.0
#    case.generators[2].c_shutdown = 100.0

    case.generators[0].p_min = 0.0 # TODO: Unit-decommitment.
    case.generators[1].p_min = 0.0
    case.generators[2].p_min = 0.0

    case.generators[0].p_max = 110.0
    case.generators[1].p_max = 110.0
    case.generators[2].p_max = 220.0 # passive

    # FIXME: Correct generator naming order.
    for g in case.generators:
        g.name

    #pyreto.util.plotGenCost(case.generators)

    return case


def get_case6ww2():
    """ Returns the 6 bus case from Wood & Wollenberg PG&C.
    """
    path = os.path.dirname(pylon.__file__)
    path = os.path.join(path, "test", "data")
    path = os.path.join(path, "case6ww", "case6ww.pkl")

    case = pylon.Case.load(path)

    case.generators[0].p_cost = (0.0, 5.1, 200.0) # 10%
    case.generators[1].p_cost = (0.0, 4.5, 200.0) # 30%
    case.generators[2].p_cost = (0.0, 6.0, 200.0) # passive

    case.generators[0].c_shutdown = 100.0
    case.generators[1].c_shutdown = 100.0
    case.generators[2].c_shutdown = 100.0

    case.generators[0].p_min = 0.0 # TODO: Unit-decommitment.
    case.generators[1].p_min = 0.0
    case.generators[2].p_min = 0.0

    case.generators[0].p_max = 110.0
    case.generators[1].p_max = 110.0
    case.generators[2].p_max = 220.0 # passive

    # FIXME: Correct generator naming order.
    for g in case.generators:
        g.name

    #pyreto.util.plotGenCost(case.generators)

    return case


def get_case24_ieee_rts():
    """ Returns the 24 bus IEEE Reliability Test System.
    """
    path = os.path.dirname(pylon.__file__)
    path = os.path.join(path, "test", "data")
    path = os.path.join(path, "case24_ieee_rts", "case24_ieee_rts.pkl")

    case = pylon.Case.load(path)

    # FIXME: Correct generator naming order.
    for g in case.generators:
        g.name

    return case


def get_case24_ieee_rts2():
    """ Returns the 24 bus IEEE Reliability Test System with U12 and U20
    generators removed.
    """
    path = os.path.dirname(__file__)
    path = os.path.join(path, 'data', "case24_ieee_rts2.pkl")

    case = pylon.Case.load(path)

    # FIXME: Correct generator naming order.
    for g in case.generators:
        g.name

    return case


def get_case24_ieee_rts3():
    """ Returns the 24 bus IEEE Reliability Test System with U12 and U20
    generators removed and generators of the same type at the same bus
    aggregated.
    """
    path = os.path.dirname(__file__)
    path = os.path.join(path, 'data', "case24_ieee_rts3.pkl")

    case = pylon.Case.load(path)

    # FIXME: Correct generator naming order.
    for g in case.generators:
        g.name

    return case


def pickle_cases():
    data_dir = os.path.dirname(__file__)
    case_paths = [os.path.join(data_dir, 'data', 'case24_ieee_rts2.m'),
                  os.path.join(data_dir, 'data', 'case24_ieee_rts3.m')]

    pickle_matpower_cases(case_paths)


def get_discrete_task_agent(generators, market, nStates, nOffer, markups,
                            maxSteps, learner, Pd0=None, Pd_min=0.0):
    """ Returns a tuple of task and agent for the given learner.
    """
    env = pyreto.discrete.MarketEnvironment(generators, market,
                                            numStates=nStates,
                                            numOffbids=nOffer,
                                            markups=markups,
                                            Pd0=Pd0,
                                            Pd_min=Pd_min)
    task = pyreto.discrete.ProfitTask(env, maxSteps=maxSteps)

    nActions = len(env._allActions)
    module = ActionValueTable(numStates=nStates, numActions=nActions)

    agent = LearningAgent(module, learner)

    return task, agent


def get_continuous_task_agent(generators, market, nOffer, maxMarkup, maxSteps,
                              learner):
    env = pyreto.continuous.MarketEnvironment(generators, market, nOffer)

    task = pyreto.continuous.ProfitTask(env, maxSteps=maxSteps,
                                        maxMarkup=maxMarkup)

    net = buildNetwork(env.outdim,
#                       4,
                       env.indim,
                       bias=False,
#                       outputbias=True,
#                       hiddenclass=TanhLayer,
#                       outclass=TanhLayer
                       )

    net._setParameters(([0.0]))

    agent = LearningAgent(net, learner)
#    agent.name = generators[0].name

    return task, agent


def get_zero_task_agent(generators, market, nOffer, maxSteps):
    """ Returns a task-agent tuple whose action is always zero.
    """
    env = pyreto.discrete.MarketEnvironment(generators, market, nOffer)
    task = pyreto.discrete.ProfitTask(env, maxSteps=maxSteps)
    agent = pyreto.util.ZeroAgent(env.outdim, env.indim)
    return task, agent


def get_neg_one_task_agent(generators, market, nOffer, maxSteps):
    """ Returns a task-agent tuple whose action is always minus one.
    """
    env = pyreto.discrete.MarketEnvironment(generators, market, nOffer)
    task = pyreto.discrete.ProfitTask(env, maxSteps=maxSteps)
    agent = pyreto.util.NegOneAgent(env.outdim, env.indim)
    return task, agent


def get_pd_min(case, profile):
    l = min(profile)
    Pd_min = sum([b.p_demand * l for b in case.buses])
    return Pd_min


def get_pd_max(case, profile):
    u = max(profile)
    Pd_max = sum([b.p_demand * u for b in case.buses])
    return Pd_max


def run_experiment(experiment, roleouts, episodes, in_cloud=False,
                   dynProfile=None):
    """ Runs the given experiment and returns the results.
    """
    def run():
        if dynProfile is None:
            maxsteps = len(experiment.profile) # episode length
        else:
            maxsteps = dynProfile.shape[1]
        na = len(experiment.agents)
        ni = roleouts * episodes * maxsteps

        all_action = zeros((na, 0))
        all_reward = zeros((na, 0))
        epsilon = zeros((na, ni)) # exploration rate

        # Converts to action vector in percentage markup values.
        vmarkup = vectorize(get_markup)

        for roleout in range(roleouts):
            if dynProfile is not None:
                # Apply new load profile before each roleout (week).
                i = roleout * episodes # index of first profile value
                experiment.profile = dynProfile[i:i + episodes, :]

            print "PROFILE:", experiment.profile, episodes

            experiment.doEpisodes(episodes) # number of samples per learning step

            nei = episodes * maxsteps # num interactions per role
            epi_action = zeros((0, nei))
            epi_reward = zeros((0, nei))

            for i, (task, agent) in \
            enumerate(zip(experiment.tasks, experiment.agents)):
                action = copy(agent.history["action"])
                reward = copy(agent.history["reward"])

                for j in range(nei):
                    if isinstance(agent.learner, DirectSearchLearner):
                        action[j, :] = task.denormalize(action[j, :])
                        k = nei * roleout
                        epsilon[i, k:k + nei] = agent.learner.explorer.sigma[0]
                    elif isinstance(agent.learner, ValueBasedLearner):
                        action[j, :] = vmarkup(action[j, :], task)
                        k = nei * roleout
                        epsilon[i, k:k + nei] = agent.learner.explorer.epsilon
                    else:
                        action = vmarkup(action, task)

                # FIXME: Only stores action[0] for all interactions.
                epi_action = c_[epi_action.T, action[:, 0].flatten()].T
                epi_reward = c_[epi_reward.T, reward.flatten()].T

                if hasattr(agent, "module"):
                    print "PARAMS:", agent.module.params

                agent.learn()
                agent.reset()

            all_action = c_[all_action, epi_action]
            all_reward = c_[all_reward, epi_reward]

        return all_action, all_reward, epsilon

    if in_cloud:
        import cloud
        job_id = cloud.call(run, _high_cpu=False)
        result = cloud.result(job_id)
        all_action, all_reward, epsilon = result
    else:
        all_action, all_reward, epsilon = run()

    return all_action, all_reward, epsilon


def get_markup(a, task):
    i = int(a)
    m = task.env._allActions[i]
    return m[0]


def save_results(results, name, version="1_1"):

    expt_action_mean, expt_action_std, \
        expt_reward_mean, expt_reward_std, epsilon = results

    if expt_action_mean is not None:
        mmwrite("./out/ex%s_%s_action_mean.mtx" % (version, name.lower()),
                expt_action_mean,
                "Experiment %s %s actions mean." % (version, name))

    if expt_action_std is not None:
        mmwrite("./out/ex%s_%s_action_std.mtx" % (version, name.lower()),
                expt_action_std,
                "Experiment %s %s actions SD." % (version, name))

    if expt_reward_mean is not None:
        mmwrite("./out/ex%s_%s_reward_mean.mtx" % (version, name.lower()),
                expt_reward_mean,
                "Experiment %s %s rewards mean." % (version, name))

    if expt_reward_std is not None:
        mmwrite("./out/ex%s_%s_reward_std.mtx" % (version, name.lower()),
                expt_reward_std,
                "Experiment %s %s rewards SD." % (version, name))

    if epsilon is not None:
        mmwrite("./out/ex%s_%s_epsilon.mtx" % (version, name.lower()),
                epsilon,
                "Experiment %s %s exploration rates." % (version, name))


def get_weekly():
    """ Returns the percent of annual peak for eack week of a year starting the
    first week of January.  Data from the IEEE RTS.
    """
    weekly = array([
        86.2, 90.0, 87.8, 83.4, 88.0, 84.1, 83.2, 80.6, 74.0, 73.7, 71.5,
        72.7, 75.0, 72.1, 80.0, 70.4, 87.0, 88.0, 75.4, 83.7, 85.6, 81.1,
        90.0, 88.7, 89.6, 86.1, 75.5, 81.6, 80.1, 88.0, 72.2, 80.0, 72.9,
        77.6, 72.6, 70.5, 78.0, 69.5, 72.4, 72.4, 74.3, 74.4, 80.0, 88.1,
        88.5, 90.9, 94.0, 89.0, 94.2, 97.0, 100.0, 95.2
    ])
    return weekly


def get_daily():
    """ Retruns the percent of weekly peak. Week beginning Monday.
    """
    daily = array([93, 100, 98, 96, 94, 77, 75])
    return daily


def get_winter_hourly():
    """ Return the percentage of daily peak, starting at midnight.
    Weeks 1-8 and 44-52.
    """
    hourly_winter_wkdy = array([
        67, 63, 60, 59, 59, 60, 74, 86, 95, 96, 96, 95, 95,
        95, 93, 94, 99, 100, 100, 96, 91, 83, 73, 63
    ])
    hourly_winter_wknd = array([
        78, 72, 68, 66, 64, 65, 66, 70, 80, 88, 90, 91, 90,
        88, 87, 87, 91, 100, 99, 97, 94, 92, 87, 81
    ])
    return hourly_winter_wkdy, hourly_winter_wknd


def get_summer_hourly():
    """ Return the percentage of daily peak, starting at midnight. Weeks 18-30.
    """
    hourly_summer_wkdy = array([
        64, 60, 58, 56, 56, 58, 64, 76, 87, 95, 99, 100, 99,
        100, 100, 97, 96, 96, 93, 92, 92, 93, 87, 72
    ])
    hourly_summer_wknd = array([
        74, 70, 66, 65, 64, 62, 62, 66, 81, 86, 91, 93, 93,
        92, 91, 91, 92, 94, 95, 95, 100, 93, 88, 80
    ])
    return hourly_summer_wkdy, hourly_summer_wknd


def get_spring_autumn_hourly():
    """ Return the percentage of daily peak, starting at midnight.
    Weeks 9-17 and 31-43.
    """
    hourly_spring_autumn_wkdy = array([
        63, 62, 60, 58, 59, 65, 72, 85, 95, 99, 100,
        99, 93, 92, 90, 88, 90, 92, 96, 98, 96, 90, 80, 70
    ])
    hourly_spring_autumn_wknd = array([
        75, 73, 69, 66, 65, 65, 68, 74, 83, 89, 92,
        94, 91, 90, 90, 86, 85, 88, 92, 100, 97, 95, 90, 85
    ])
    return hourly_spring_autumn_wkdy, hourly_spring_autumn_wknd


def get_full_year():
    """ Returns percentages of peak load for all hours of the year.

    @return:
        Numpy array of doubles with length 8736.
    """
    weekly = get_weekly()
    daily = get_daily()
    hourly_winter_wkdy, hourly_winter_wknd = get_winter_hourly()
    hourly_summer_wkdy, hourly_summer_wknd = get_summer_hourly()
    hourly_spring_autumn_wkdy, hourly_spring_autumn_wknd = \
        get_spring_autumn_hourly()

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
    return fullyear


def get_all_days():
    """ Returns percentages of peak load for all days of the year.
    Data from the IEEE RTS.
    """
    weekly = get_weekly()
    daily = get_daily()

    return [w * (d / 100.0) for w in weekly for d in daily]


def get_outages():
    # Outage rate (outages/year).
    rate = [0.24, 0.51, 0.33, 0.39, 0.48, 0.38, 0.02, 0.36, 0.34, 0.33, 0.3,
            0.44, 0.44, 0.02, 0.02, 0.02, 0.02, 0.4, 0.39, 0.4, 0.52,
            0.49, 0.38, 0.33, 0.41, 0.41, 0.41, 0.35, 0.34, 0.32, 0.54,
            0.35, 0.35, 0.38, 0.38, 0.34, 0.34, 0.45]

    per = 365
    outage_rate = [r / per for r in rate]
    return outage_rate
