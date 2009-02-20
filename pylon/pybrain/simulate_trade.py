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

from os.path import dirname, join

from pybrain.tools.shortcuts import buildNetwork
from pybrain.rl.agents import FiniteDifferenceAgent, PolicyGradientAgent
from pybrain.rl.learners import SPLA, ENAC
from pybrain.structure.modules import SigmoidLayer

from pylon.readwrite.api import read_matpower
from pylon.network import Network
from pylon.bus import Bus
from pylon.generator import Generator
from pylon.load import Load

from environment import ParticipantEnvironment
from experiment import MarketExperiment
from profit_task import ProfitTask

#------------------------------------------------------------------------------
#  Constants:
#------------------------------------------------------------------------------

# FIXME: Relative path.
DATA_FILE = join( dirname(__file__), "../test/data/case6ww.m" )

#------------------------------------------------------------------------------
#  Simulate trade:
#------------------------------------------------------------------------------

def get_power_sys():
    # Read network data.
    power_sys = read_matpower( DATA_FILE )

    # One bus test network.
#    power_sys = Network( name = "1bus", mva_base = 100.0 )
#
#    bus1 = Bus( name = "Bus 1" )
#
#    generator = Generator( name        = "G1",
#                           p_max       = 6.0,
#                           p_min       = 1.0,
#                           cost_model  = "Polynomial",
#                           cost_coeffs = ( 0.0, 0.0, 6.0 ) )
#
#    load = Load( name = "L1",
#                 p    = 5.0,
#                 q    = 0.0 )
#
#    bus1.generators.append( generator )
#    bus1.loads.append( load )
#    power_sys.buses = [ bus1 ]

    return power_sys

def main(power_sys):
    # Create tasks.
    tasks = []
    agents = []
    for generator in power_sys.in_service_generators:
        # Create environment.
        env = ParticipantEnvironment( asset = generator )

        # Create controller network (min, 50%, max).
        net = buildNetwork( 3, 6, 1, bias = False, outclass = SigmoidLayer )

        # Create a task for the agent.
        task = ProfitTask( env )
        # Create agent.
        agent = FiniteDifferenceAgent( module = net, learner = ENAC() )

        tasks.append( task )
        agents.append( agent )

    experiment = MarketExperiment( tasks, agents, power_sys )
#    experiment.doInteractions( number = 2 )
    experiment.configure_traits()

if __name__ == "__main__":
    power_sys = get_power_sys()
    main( power_sys )

# EOF -------------------------------------------------------------------------
