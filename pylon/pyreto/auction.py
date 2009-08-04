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

""" Defines an auction based on OPF results.

    References:
        Ray Zimmerman, "extras/smartmarket/auction.m", MATPOWER, PSERC Cornell,
        version 3.2, http://www.pserc.cornell.edu/matpower/, June 2007
"""

#------------------------------------------------------------------------------
#  Imports:
#------------------------------------------------------------------------------

import time
import logging

#------------------------------------------------------------------------------
#  Logging:
#------------------------------------------------------------------------------

logger = logging.getLogger(__name__)
#logger.setLevel(logging.INFO)

#------------------------------------------------------------------------------
#  "Auction" class:
#------------------------------------------------------------------------------

class Auction(object):
    """ Defines an auction based on OPF results.

        References:
            R. Zimmerman, "extras/smartmarket/auction.m", MATPOWER, PSERC
            Cornell, version 3.2, http://www.pserc.cornell.edu/matpower/, 2007
    """

    #--------------------------------------------------------------------------
    #  "object" interface:
    #--------------------------------------------------------------------------

    def __init__(self, offers, bids, auction_type):
        """ Initialises the new Auction instance.
        """

# EOF -------------------------------------------------------------------------
