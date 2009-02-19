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

from pybrain.tools.shortcuts import buildNetwork
from pybrain.rl.agents import FiniteDifferenceAgent, PolicyGradientAgent
from pybrain.rl.learners import SPLA, ENAC
from pybrain.structure.modules import SigmoidLayer

from pylon.readwrite.api import read_matpower

from environment import ParticipantEnvironment
from experiment import MarketExperiment
from profit_task import ProfitTask

#------------------------------------------------------------------------------
#  Constants:
#------------------------------------------------------------------------------

DATA_FILE = "/home/rwl/python/aes/Pylon/pylon/test/data/case6ww.m"

#------------------------------------------------------------------------------
#  Simulate trade:
#------------------------------------------------------------------------------

# Read network data.
power_sys = read_matpower(DATA_FILE)
generators = power_sys.in_service_generators

# Create tasks.
tasks = []
agents = []
for generator in generators:
    # Create environment.
    env = ParticipantEnvironment( asset=generator )

    # Create controller network (min, 50%, max).
    net = buildNetwork( 3, 6, 1, bias=False, outclass=SigmoidLayer )

    # Create a task for the agent.
    task = ProfitTask( env )
    # Create agent.
    agent = FiniteDifferenceAgent( modules=net, learner=ENAC() )

    tasks.append( task )
    agents.append( agent )

experiment = MarketExperiment( tasks, agents, power_sys )
experiment.doInteractions( number = 2 )

# EOF -------------------------------------------------------------------------
