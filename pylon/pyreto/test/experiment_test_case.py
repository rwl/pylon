#------------------------------------------------------------------------------
# Copyright (C) 2009 Richard W. Lincoln
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; version 2 dated June, 1991.
#
# This software is distributed in the hope that it will be useful, but
# WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANDABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the GNU
# General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software Foundation,
# Inc., 51 Franklin St, Fifth Floor, Boston, MA 02110-1301 USA
#------------------------------------------------------------------------------

""" Defines a test case for the Pyreto market experiment.
"""

#------------------------------------------------------------------------------
#  Imports:
#------------------------------------------------------------------------------

import sys
import logging
import unittest

from os.path import dirname, join

from scipy import array

from pylon import Network, Bus, Generator, Load
from pylon.readwrite import MATPOWERReader

from pylon.pyreto import MarketExperiment, ParticipantEnvironment, ProfitTask
from pylon.pyreto.renderer import ParticipantRenderer
from pylon.pyreto.main import one_for_one

from pybrain.tools.shortcuts import buildNetwork
from pybrain.rl.experiments import ContinuousExperiment
from pybrain.rl.agents import LearningAgent, PolicyGradientAgent
from pybrain.rl.learners import ENAC

#------------------------------------------------------------------------------
#  Constants:
#------------------------------------------------------------------------------

DATA_FILE = join(dirname(__file__), "data", "auction_case.m")

#------------------------------------------------------------------------------
#  Returns a test power system:
#------------------------------------------------------------------------------

def get_test_network():
    """ Returns a test power system network.
    """
    # Read network from data file.
    reader = MATPOWERReader()
    power_sys = reader(DATA_FILE)

    return power_sys

#------------------------------------------------------------------------------
#  "MarketExperimentTest" class:
#------------------------------------------------------------------------------

class MarketExperimentTest(unittest.TestCase):
    """ Defines a test case for the Pyreto market experiment.
    """

    def setUp(self):
        """ The test runner will execute this method prior to each test.
        """
        # Build one bus test network.
        self.generator1 = Generator(name        = "G1",
                                    p_max       = 60.0,
                                    p_min       = 0.0,
                                    cost_model  = "polynomial",
                                    cost_coeffs = (0.0, 10.0, 0.0))

        self.generator2 = Generator(name        = "G2",
                                    p_max       = 100.0,
                                    p_min       = 0.0,
                                    cost_model  = "polynomial",
                                    cost_coeffs = (0.0, 20.0, 0.0))

        load = Load(name="L1", p=100.0, q=0.0)

        self.bus1 = Bus(name="Bus 1")
        self.bus1.generators.append(self.generator1)
        self.bus1.generators.append(self.generator2)
        self.bus1.loads.append(load)

        self.power_sys = Network(name="1bus")
        self.power_sys.buses.append(self.bus1)


    def test_learning(self):
        """ Test maximisation of marginal generator offer.
        """
        # Create agent for generator 1.
        env = ParticipantEnvironment(self.power_sys, self.generator1)
        env.setRenderer(ParticipantRenderer())
        env.getRenderer().start()

        task = ProfitTask(env)

        net = buildNetwork(1, 1, bias=False)
        net._setParameters(array([0.1]))

#        agent = LearningAgent(net, None)

        agent = PolicyGradientAgent(module=net, learner=ENAC())
        # initialize parameters (variance)
        agent.setSigma([-1.5])
        # learning options
        agent.learner.alpha = 2.0
        # agent.learner.rprop = True
        agent.actaspg = False
#        agent.disableLearning()

#        experiment = ContinuousExperiment(task1, agent1)
        experiment = MarketExperiment([task], [agent], self.power_sys)

        # Experiment event sequence:
        #   task.getObservation()
        #     env.getSensors()
        #     task.normalize()
        #   agent.integrateObservation()
        #     Stores the observation received in a temporary variable until
        #     action is called and reward is given.
        #   agent.getAction()
        #     module.activate(lastobs)
        #   task.performAction()
        #     task.denormalize(action)
        #     env.performAction(action)
        #   task.getReward()
        #   agent.giveReward()
        #   agent.learn()
        experiment.doInteractions(250)

        env.getRenderer().stop()

        self.assertAlmostEqual(self.generator1.cost_coeffs[1], 20.0, places=2)


#    def test_contracts_market(self):
#        """ Test trading through a bilateral contracts market.
#        """
#        market = ContractsMarket()
#        buyer = Agent()
#        market.add_buyer(buyer)
#        seller = Agent()
#        market.add_seller(seller)
#
#        bids = market.get_bids(seller)
#        offers = market.get_quotes(buyer)
#
#        market.submit_bid(buyer, (100.0, 12.6, 48))
#        market.request_quote(buyer, (80.0, 9.0, 24))
#
#        market.submit_quote(seller, (80.0, 9.0, 24))
#
#
#    def test_over_the_counter_trading(self):
#        """ Test trading through shorter-term bilateral contracts.
#        """
#        otc = OTCMarket()
#
#
#    def test_power_exchange(self):
#        """ Test trading through exchange facilities constructed for the
#            purpose of trading.
#        """
#        px = PowerExchange()
#
#
#    def test_balancing_mechanism(self):
#        """ Test system balancing using a reserve market.
#        """
#        bm = BalancingMechanism()


#    def test_opf(self):
#        """ Examine the DC OPF routine output.
#        """
#        routine = DCOPF()
#        routine(power_sys)
#        writer = ReSTWriter()
#        writer.write_generator_data(power_sys, sys.stdout)


if __name__ == "__main__":
#    logging.basicConfig(stream=sys.stdout, level=logging.DEBUG,
#        format="%(levelname)s: %(message)s")

    logger = logging.getLogger()

    # Remove PyBrain handlers.
    for handler in logger.handlers:
        logger.removeHandler(handler)

    logger.addHandler(logging.StreamHandler(sys.stdout))
    logger.setLevel(logging.DEBUG)

    unittest.main()

# EOF -------------------------------------------------------------------------
