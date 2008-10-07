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

"""
This kind of environments is only able to produce a list of possible
actions : all other computations are made inside a Environment

"""

#------------------------------------------------------------------------------
#  Imports:
#------------------------------------------------------------------------------

from enthought.traits.api import Interface

#------------------------------------------------------------------------------
#  "IElementaryEnvironment" class:
#------------------------------------------------------------------------------

class IElementaryEnvironment(Interface):
    """
    This kind of environments is only able to produce a list of possible
    actions : all other computations are made inside an IEnvironment

    """

    def _get_action_list(self, state):
        """
        Gives the list of possible actions from a given state. The only
        useful method in this class

        """

# EOF -------------------------------------------------------------------------
