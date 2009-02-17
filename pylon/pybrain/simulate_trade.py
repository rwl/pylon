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

""" Simulates energy trade in a test network.
"""

#------------------------------------------------------------------------------
#  Imports:
#------------------------------------------------------------------------------

from pybrain.tools.shortcuts import buildNetwork
from pybrain.rl.agents.finitedifference import FiniteDifferenceAgent
from pybrain.rl.learners import SPLA

from pylon.readwrite.api import read_matpower

from environment import MarketEnvironment
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

# Create environment.
env = MarketEnvironment(power_sys)

# create controller network
net = buildNetwork(len(generators), 1)

# Create tasks.
tasks = []
agents = []
for generator in generators:
    task = ProfitTask(env)
    agent = FiniteDifferenceAgent(modules=net, learner=SPLA())

    tasks.append(task)
    agents.append(agent)

experiment = MarketExperiment(tasks, agents)
experiment.doInteractions(number=24)

# EOF -------------------------------------------------------------------------
