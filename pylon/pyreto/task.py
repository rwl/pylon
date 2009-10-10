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

""" Defines a profit maximisation task.
"""

#------------------------------------------------------------------------------
#  Imports:
#------------------------------------------------------------------------------

import logging
from scipy import array
from pybrain.rl.environments import Task

logger = logging.getLogger(__name__)

BIGNUM = 1e06

#------------------------------------------------------------------------------
#  "ProfitTask" class:
#------------------------------------------------------------------------------

class ProfitTask(Task):
    """ Defines the task of maximising profit.
    """

    def __init__(self, environment):
        """ Initialises the task.
        """
        Task.__init__(self, environment)

        # Limits for scaling of sensors.
        self.sensor_limits = self.getSensorLimits()

        # Limits for scaling of actors.
        self.actor_limits = self.getActorLimits()


    def getSensorLimits(self):
        """ Returns a list of 2-tuples, e.g. [(-3.14, 3.14), (-0.001, 0.001)],
            one tuple per parameter, giving min and max for that parameter.
        """
        g = self.env.asset
        mkt = self.env.market
        case = mkt.case

        sensor_limits = []
        sensor_limits.append((0.0, BIGNUM)) # f
        sensor_limits.append((0.0, g.rated_pmax)) # quantity
        sensor_limits.append((0.0, BIGNUM)) # price
        sensor_limits.append((0.0, g.total_cost(g.rated_pmax))) # variable
        c_startup = 2.0 if g.c_startup == 0.0 else g.c_startup
        sensor_limits.append((0.0, c_startup)) # startup
        c_shutdown = 2.0 if g.c_shutdown == 0.0 else g.c_shutdown
        sensor_limits.append((0.0, c_shutdown)) # shutdown

        sensor_limits.extend([(0.0, b.s_max) for b in case.branches])
        sensor_limits.extend([(-BIGNUM, BIGNUM) for b in case.branches]) # mu_flow

        sensor_limits.extend([(-180.0, 180.0) for b in case.buses]) #angle
        sensor_limits.extend([(0.0, BIGNUM) for b in case.buses]) #p_lambda
#        sensor_limits.extend([(b.v_min, b.v_max) for b in case.buses]) #mu_vmin
#        sensor_limits.extend([(b.v_min, b.v_max) for b in case.buses]) #mu_vmax

        sensor_limits.extend([(0., b.rated_pmax) for b in case.all_generators]) #pg
        sensor_limits.extend([(-BIGNUM, BIGNUM) for g in case.all_generators]) #g_pmax
        sensor_limits.extend([(-BIGNUM, BIGNUM) for g in case.all_generators]) #g_pmin

        return sensor_limits


    def getActorLimits(self):
        """ Returns a list of 2-tuples, e.g. [(-3.14, 3.14), (-0.001, 0.001)],
            one tuple per parameter, giving min and max for that parameter.
        """
        g = self.env.asset
        n_offbids = self.env.n_offbids
        offbid_qty = self.env.offbid_qty
        mkt = self.env.market

        actor_limits = []
        for i in range(n_offbids):
            if offbid_qty:
                actor_limits.append((0.0, g.rated_pmax))
            actor_limits.append((0.0, mkt.price_cap))

        return actor_limits


#    def performAction(self, action):
#        """ A filtered mapping of the .performAction() method of the underlying
#            environment.
#        """
#        logger.debug("Profit task [%s] filtering action: %s" %
#                     (self.env.asset.name, action))
#        logger.debug("Profit task [%s] denormalised action: %s" %
#                     (self.env.asset.name, self.denormalize(action)))
#        Task.performAction(self, action)


#    def getObservation(self):
#        """ A filtered mapping to the .getSample() method of the underlying
#            environment.
#        """
#        sensors = Task.getObservation(self)
#        logger.debug("Profit task [%s] normalised sensors: %s" %
#                     (self.env.asset.name, sensors))
#        return sensors


    def getReward(self):
        """ Computes and returns the reward corresponding to the last action
            performed.
        """
        g = self.env.asset
        mkt = self.env.market

        d = mkt.settlement[g]
        logger.debug("Profit task [%s] reward: %s" % (g.name, d.earnings))

        return d.earnings

# EOF -------------------------------------------------------------------------
