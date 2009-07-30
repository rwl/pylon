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

""" Defines forums for trading electric energy.
"""

#------------------------------------------------------------------------------
#  Imports:
#------------------------------------------------------------------------------

import logging
from cvxopt import matrix

logger = logging.getLogger(__name__)

#------------------------------------------------------------------------------
#  "ContractsMarket" class:
#------------------------------------------------------------------------------

class ContractsMarket(object):
    """ Defines a market for the formation of long-term bilateral contracts.
    """
    def __init__(self, buyers, sellers):
        """ Initialises a new ContractsMarket instance.
        """
        # Agents associated with Generator instances operating as dispatchable
        # loads and wishing to buy of electric energy.
        self.buyers = buyers

        self.bids = {}

        # Agents associated with generators that may contract to sell electric
        # energy to buyers.
        self.sellers = sellers

        self.offers = {}


    def get_bids(self, agent):
        """ Returns proposals from buyers bidding to buy electric energy from
            the given seller 'agent'.
        """
        if self.bids.has_key(agent):
            return self.bids[agent]
        else:
            return matrix()

# EOF -------------------------------------------------------------------------
