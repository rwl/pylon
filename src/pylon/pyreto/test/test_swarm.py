#------------------------------------------------------------------------------
# Copyright (C) 2007 Richard W. Lincoln
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

""" Nose test for a Pyreto swarm """

#------------------------------------------------------------------------------
#  Imports:
#------------------------------------------------------------------------------

import pickle
from tempfile import gettemp
from os.path import join, expanduser
import sys
import logging
logger = logging.getLogger()
logger.addHandler(logging.StreamHandler(sys.stdout))
logger.setLevel(logging.DEBUG)

from pylon.filter.api import import_matpower
from pylon.pyreto.market_environment import MarketEnvironment
from pylon.pyreto.participant_environment import ParticipantEnvironment

from pyqle.api import ElementaryAgent, Swarm, HumanSelector

#------------------------------------------------------------------------------
#  Constants:
#------------------------------------------------------------------------------

data_file = "/home/rwl/python/aes/matpower_3.2/rwl_003.m"
#data_file = "/home/rwl/python/aes/matpower_3.2/case14.m"

#------------------------------------------------------------------------------
#
#------------------------------------------------------------------------------

n = import_matpower(data_file)

env = MarketEnvironment(network=n, name="Market Environment")
swarm = Swarm(environment=env, name="Participant Swarm")

for p in n.generators+n.loads:
    p_env = ParticipantEnvironment(asset=p)
    a = ElementaryAgent(environment=p_env, name="Agent "+p.name)
    swarm.elementary_agents.append(a)

fd = None
try:
    fd = open(join(expanduser("~"), "swarm.pyr"), "wb")
    pickle.dump(swarm, fd)
finally:
    if fd is not None:
        fd.close()

# EOF -------------------------------------------------------------------------
