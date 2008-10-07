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
A base class for many states.

A state must define accurately a given configuration of the environment.

"""

#------------------------------------------------------------------------------
#  Imports:
#------------------------------------------------------------------------------

# Standard library imports.
import logging

# Enthought library imports
from enthought.traits.api import \
    HasTraits, Any, Instance, Int

# Local imports:
#from abstract_environment_single import AbstractEnvironmentSingle

# Setup a logger for this module.
logger = logging.getLogger(__name__)

#------------------------------------------------------------------------------
#  "State" class:
#------------------------------------------------------------------------------

class State(HasTraits):
    """
    A base class for many states

    A state must define accurately a given configuration of the environment.

    """

    environment = Instance("pyqle.environment.Environment", allow_none=False)


    def __eq__(self, o):
        """
        It is up to the programmer to define when two states are declared equal

        """

        raise NotImplementedError()

#    def is_final(self):
#        return self.environment.is_final(self)
#
#
#    def get_action_list(self):
#        # TODO:Test Delegate
#        return self.environment.get_action_list(self)
#
#
#    def modify(self, action):
#        return self.environment.successor_state(self, action)
#
#
#    def get_reward(self, old, action):
#        return self.environment.get_reward(old, self, action)
#
#
#    def get_winner(self):
#        return self.environment.who_wins(self)


    def copy(self):
        pass


    def nnCodingSize(self):
        pass


    def nnCoding(self):
        pass

# EOF -------------------------------------------------------------------------
