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

""" Defines a given configuration of the market environment """

#------------------------------------------------------------------------------
#  Imports:
#------------------------------------------------------------------------------

from enthought.traits.api import Instance, Int

from pyqle.environment.state import State

#------------------------------------------------------------------------------
#  "MarketState" class:
#------------------------------------------------------------------------------

class MarketState(State):
    """ Defines a given configuration of the market environment. The
    states contains the information about the environment the agents
    may use in making their choice of action.

    """

    # Override to force SwarmEnvironment usage
    environment = Instance(
        "pylon.pyreto.market_environment.MarketEnvironment",
        allow_none=False
    )

    # The time period for which this state applies:
    period = Int

#    demand = Int(0, desc="Total system demand")


    def __eq__(self, o):
        """ Defines when two states are declared equal """

#        if self.demand == o.demand:
#            return True
#        else:
#            return False
        return True


    def copy(self):
        """ Return a copy of this state """

        new = MarketState(environment=self.environment)

        new.period = self.period
#        new.demand = self.demand

        return new

# EOF -------------------------------------------------------------------------
