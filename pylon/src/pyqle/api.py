#------------------------------------------------------------------------------
# Copyright (C) 2008 Richard W. Lincoln
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

""" Use this module for importing Pyqle names into your namespace.

For example:
    from pyqle.api import Agent

"""

#------------------------------------------------------------------------------
#  Agents:
#------------------------------------------------------------------------------

from pyqle.agent.agent import Agent

from pyqle.agent.elementary_agent import ElementaryAgent

from pyqle.agent.swarm import Swarm

#------------------------------------------------------------------------------
#  Selectors:
#------------------------------------------------------------------------------

from pyqle.selector.random_selector import RandomSelector

from pyqle.selector.human_selector import HumanSelector

# EOF -------------------------------------------------------------------------
