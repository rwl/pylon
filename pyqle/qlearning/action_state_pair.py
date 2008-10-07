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
Acts like a key to store Q(s,a) values. The key is the union of state and
action

"""

#------------------------------------------------------------------------------
#  Imports:
#------------------------------------------------------------------------------

# Standard library imports.
import logging

# Enthought library imports
from enthought.traits.api import HasTraits, Instance, Long

# Pyqle imports:
from pyqle.environment.abstract_action import AbstractAction

from pyqle.environment.abstract_state import AbstractState

# Setup a logger for this module.
logger = logging.getLogger(__name__)

#------------------------------------------------------------------------------
#  "ActionStatePair" class:
#------------------------------------------------------------------------------

class ActionStatePair(HasTraits):
    """
    Acts like a key to store Q(s,a) values. The key is the union of state and
    action

    """
    
    serial_version_uid = Long
    
    # Action part of the key
    action = Instance(AbstractAction)
    
    # State part of the key
    state = Instance(AbstractState)


    def __init__(self, action, state, **traits):
        self.action = action
        self.state = state
        
        super(ActionStatePair, self).__init__(action=action,
            state=state, **traits)


    def hash_code(self):
        return self.action.hash_code() + self.state.hash_code()


#    def __eq__(self, o):
#        if not isinstance(o, (ActionStatePair)):
#            return False
#        us = o
#        return us.state == self.state and us.action == self.action


    def to_string(self):
        return self.state + " " + self.action

# EOF -------------------------------------------------------------------------
