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

""" Simulates energy trade in a test power system.
"""

#------------------------------------------------------------------------------
#  Imports:
#------------------------------------------------------------------------------

import sys
from os.path import dirname, join

from numpy import array

from pybrain.tools.shortcuts import buildNetwork
from pybrain.rl.agents import LearningAgent, PolicyGradientAgent
from pybrain.rl.learners import SPLA, ENAC
from pybrain.structure.modules import SigmoidLayer

from pylon.readwrite.api import read_matpower, ReSTWriter
from pylon.network import Network
from pylon.bus import Bus
from pylon.generator import Generator
from pylon.load import Load
from pylon.routine.api import DCOPFRoutine

from environment import ParticipantEnvironment
from experiment import MarketExperiment
from profit_task import ProfitTask

from pylon.ui.plot.experiment_plot import ExperimentPlot

from pylon.readwrite.rst_writer import ReSTExperimentWriter

#------------------------------------------------------------------------------
#  Constants:
#------------------------------------------------------------------------------

# FIXME: Relative path.
DATA_FILE = join( dirname(__file__), "..", "test", "data", "case6ww.m" )

#------------------------------------------------------------------------------
#  Simulate trade:
#------------------------------------------------------------------------------

def get_power_sys():
    # Read network data.
#    power_sys = read_matpower( DATA_FILE )

    # One bus test network.
    power_sys = Network( name = "1 Bus", base_mva = 100.0 )

    bus1 = Bus( name = "Bus 1" )

    generator = Generator( name        = "G1",
                           p_max       = 2.0,
                           p_min       = 0.0,
                           cost_model  = "Polynomial",
                           cost_coeffs = ( 0.0, 6.0, 0.0 ) )

    generator2 = Generator( name        = "G2",
                            p_max       = 6.0,
                            p_min       = 0.0,
                            cost_model  = "Polynomial",
                            cost_coeffs = ( 0.0, 10.0, 0.0 ) )

    load = Load( name = "L1", p = 1.0, q = 0.0 )

    bus1.generators.append( generator )
    bus1.generators.append( generator2 )
    bus1.loads.append( load )
    power_sys.buses = [ bus1 ]

#    solution = DCOPFRoutine(power_sys).solve()
#    writer = ReSTWriter(power_sys, sys.stdout)
#    writer.write_generator_data()

    return power_sys


def main(power_sys):
    # Create tasks.
    tasks = []
    agents = []
    for generator in power_sys.online_generators:
        # Create the world in which the trading agent acts.
        env = ParticipantEnvironment( power_system = power_sys,
                                      asset        = generator )

        # Create a task that connects each agent to it's environment. The task
        # defines what the goal is for an agent and how the agent is rewarded
        # for it's actions.
        task = ProfitTask( env )

        # Create a linear controller network. Each agent needs a controller
        # that maps the current state to an action.
#        net = buildNetwork( 3, 6, 1, bias = False, outclass = SigmoidLayer )
        net = buildNetwork( 1, 1, bias = False )

        net._setParameters( array([0.5]) )

        # Create agent. The agent is where the learning happens. For continuous
        # problems a policy gradient agent is required.  Each agent has a
        # module (network) and a learner, that modifies the module.
#        agent = LearningAgent( module = net, learner = ENAC() )
#        agent.name = "LearningAgent-%s" % generator.name
        agent = PolicyGradientAgent( module = net, learner = ENAC() )
        agent.name = "PolicyGradientAgent-%s" % generator.name

        # Backpropagation parameters.
        gradient_descent = agent.learner.gd
        # Learning rate (0.1-0.001, down to 1e-7 for RNNs).
        agent.alpha = 0.1

        # Alpha decay (0.999; 1.0 = disabled).
#        gradient_descent.alphadecay = 1.0
#
#        # momentum parameters (0.1 or 0.9)
#        gradient_descent.momentum = 0.0
#        gradient_descent.momentumvector = None
#
#        # --- RProp parameters ---
#        gradient_descent.rprop = False
#        # maximum step width (1 - 20)
#        gradient_descent.deltamax = 5.0
#        # minimum step width (0.01 - 1e-6)
#        gradient_descent.deltamin = 0.01

        # Collect tasks and agents.
        tasks.append( task )
        agents.append( agent )

    experiment = MarketExperiment( tasks, agents, power_sys )
#    experiment.doInteractions( number = 3 )

#    plot = ExperimentPlot(experiment)
#    plot.configure_traits()

    writer = ReSTExperimentWriter(experiment, sys.stdout)
#    writer.write_state_data()
    writer.write_action_data()
#    writer.write_reward_data()

    experiment.configure_traits()

    return experiment


if __name__ == "__main__":
    import logging
    logger = logging.getLogger()
    for handler in logger.handlers:
        logger.removeHandler( handler )
    logger.addHandler( logging.StreamHandler(sys.stdout) )
    logger.setLevel(logging.DEBUG)

    power_sys = get_power_sys()
    main( power_sys )

# EOF -------------------------------------------------------------------------
