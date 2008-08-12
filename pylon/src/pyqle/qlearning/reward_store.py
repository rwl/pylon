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
Framework defining  methods to store, retrieve, enumerate state/action values.

"""

#------------------------------------------------------------------------------
#  Imports:
#------------------------------------------------------------------------------

# Standard library imports.
import logging

# Enthought library imports
from enthought.traits.api import HasTraits, Long

# Application imports:
from pyqle.environment.environment import Environment

# Setup a logger for this module.
logger = logging.getLogger(__name__)

#------------------------------------------------------------------------------
#  "RewardStore" class:
#------------------------------------------------------------------------------

class RewardStore(HasTraits):
    """
    Framework defining  methods to store, retrieve, enumerate state/action
    values.

    """

    serial_version_uid = Long

    def get(self, s, a):
        """
        The state/action value

        """

        raise NotImplementedError()


    def put(self, s, a, sp, qsa):
        """
        Store a state/action value. We sometimes need the new state (sp)...

        """

        raise NotImplementedError()


    def extract_dataset(self):
        """
        Extract all the (state,action,value) vectors in a format suitable for use with Neural Networks.

        @see neuralnetwork.NeuralNetwork
        @see dataset.Dataset
        @see dataset.Sample

        """

        raise NotImplementedError()

# EOF -------------------------------------------------------------------------
