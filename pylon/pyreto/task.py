#------------------------------------------------------------------------------
# Copyright (C) 2009 Richard Lincoln
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

""" Defines a profit maximisation task.
"""

#------------------------------------------------------------------------------
#  Imports:
#------------------------------------------------------------------------------

import logging
from scipy import array, linspace
from pybrain.rl.environments import Task

logger = logging.getLogger(__name__)

BIGNUM = 1e06

#------------------------------------------------------------------------------
#  "StatelessTask" class:
#------------------------------------------------------------------------------

class StatelessTask(Task):
    """ Defines a task that uses no state information.
    """

    #--------------------------------------------------------------------------
    #  "Task" interface:
    #--------------------------------------------------------------------------

    def getObservation(self):
        """ The vector of sensor values is replaced by a single integer since
            there is only one state.
        """
        return 0


    def performAction(self, action):
        """ The action vector is stripped and the only element is cast to
            integer and given to the super class.
        """
        Task.performAction(self, int(action[0]))


    def getReward(self):
        """ Returns the reward corresponding to the last action performed.
        """
        g = self.env.asset
        d = self.env.market.settlement[g]
        logger.debug("Profit task [%s] reward: %s" % (g.name, d.earnings))
        return d.earnings

#------------------------------------------------------------------------------
#  "DiscreteTask" class:
#------------------------------------------------------------------------------

class DiscreteTask(StatelessTask):
    """ Defines a task with discrete observations of the clearing price.
    """

    #--------------------------------------------------------------------------
    #  "Task" interface:
    #--------------------------------------------------------------------------

    def getObservation(self):
        """ The agent receives...
        """
        sensors = Task.getObservation(self)
        band_limits = linspace(0.0, self.env.price_cap, self.env.outdim)
        for i in range(len(band_limits) - 1):
            if (band_limits[i] <= sensors[0] < band_limits[i + 1]):
                return array(i)
        else:
            raise ValueError

#------------------------------------------------------------------------------
#  "ContinuousTask" class:
#------------------------------------------------------------------------------

class ContinuousTask(Task):
    """ Defines a task for continuous sensor and action spaces.
    """

    def __init__(self, environment):
        """ Initialises the task.
        """
        super(ContinuousTask, self).__init__(environment)

        # Limits for scaling of sensors.
        self.sensor_limits = self.getSensorLimits()

        # Limits for scaling of actors.
        self.actor_limits = self.getActorLimits()

    #--------------------------------------------------------------------------
    #  "ContinuousTask" interface:
    #--------------------------------------------------------------------------

    def getSensorLimits(self):
        """ Returns a list of 2-tuples, e.g. [(-3.14, 3.14), (-0.001, 0.001)],
            one tuple per parameter, giving min and max for that parameter.
        """
        g = self.env.asset
        mkt = self.env.market
        case = mkt.case

        limits = []
        limits.append((0.0, BIGNUM)) # f
        limits.append((0.0, g.rated_pmax)) # quantity
        limits.append((0.0, BIGNUM)) # price
        limits.append((0.0, g.total_cost(g.rated_pmax))) # variable
        c_startup = 2.0 if g.c_startup == 0.0 else g.c_startup
        limits.append((0.0, c_startup)) # startup
        c_shutdown = 2.0 if g.c_shutdown == 0.0 else g.c_shutdown
        limits.append((0.0, c_shutdown)) # shutdown

        limits.extend([(0.0, b.s_max) for b in case.branches])
        limits.extend([(-BIGNUM, BIGNUM) for b in case.branches]) # mu_flow

        limits.extend([(-180.0, 180.0) for b in case.buses]) # angle
        limits.extend([(0.0, BIGNUM) for b in case.buses]) # p_lambda
#        limits.extend([(b.v_min, b.v_max) for b in case.buses]) # mu_vmin
#        limits.extend([(b.v_min, b.v_max) for b in case.buses]) # mu_vmax

        limits.extend([(0., b.rated_pmax) for b in case.all_generators]) #pg
        limits.extend([(-BIGNUM, BIGNUM) for g in case.all_generators]) #g_pmax
        limits.extend([(-BIGNUM, BIGNUM) for g in case.all_generators]) #g_pmin

        return limits


    def getActorLimits(self):
        """ Returns a list of 2-tuples, e.g. [(-3.14, 3.14), (-0.001, 0.001)],
            one tuple per parameter, giving min and max for that parameter.
        """
        g = self.env.asset
        n_offbids = self.env.n_offbids
        offbid_qty = self.env.offbid_qty
        mkt = self.env.market

        actor_limits = []
        for _ in range(n_offbids):
            if offbid_qty:
                actor_limits.append((0.0, g.rated_pmax))
            actor_limits.append((0.0, mkt.price_cap))

        return actor_limits

# EOF -------------------------------------------------------------------------
