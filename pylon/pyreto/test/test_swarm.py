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

""" Defines tests for the Pyreto swarm.
"""

#------------------------------------------------------------------------------
#  Imports:
#------------------------------------------------------------------------------

import sys
import logging
import pickle
from os.path import join, expanduser

from pylon.readwrite.api import read_matpower
from pylon.pyreto.market_environment import MarketEnvironment
from pylon.pyreto.participant_environment import ParticipantEnvironment

from pyqle.api import ElementaryAgent, Swarm, HumanSelector

#------------------------------------------------------------------------------
#  logging:
#------------------------------------------------------------------------------

logger = logging.getLogger()
logger.addHandler(logging.StreamHandler(sys.stdout))
logger.setLevel(logging.DEBUG)

#------------------------------------------------------------------------------
#  Constants:
#------------------------------------------------------------------------------

data_file = "/home/rwl/python/aes/Pylon/pylon/test/data/case6ww.m"

#------------------------------------------------------------------------------
#
#------------------------------------------------------------------------------

n = read_matpower( data_file )

env = MarketEnvironment( network = n, name = "Market Environment" )

swarm = Swarm( environment = env, name = "Participant Swarm" )

for p in n.generators + n.loads:
    env_name = "Env (%s)" % p.name
    p_env = ParticipantEnvironment( name = env_name, asset = p )

    a_name = "Agent (%s)" % p.name
    a = ElementaryAgent( environment = p_env, name = a_name)
    swarm.elementary_agents.append(a)

swarm.configure_traits()
#env.start = True

#fd = None
#try:
#    fd = open(join(expanduser("~"), "swarm.pyr"), "wb")
#    pickle.dump(swarm, fd)
#finally:
#    if fd is not None:
#        fd.close()

# EOF -------------------------------------------------------------------------
