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

""" Pyreto workspace wizard extensions """

#------------------------------------------------------------------------------
#  Imports:
#------------------------------------------------------------------------------

from os.path import dirname

from enthought.pyface.api import ImageResource
from enthought.plugins.workspace.wizard_extension import WizardExtension

import pylon.ui.api

#------------------------------------------------------------------------------
#  Constants:
#------------------------------------------------------------------------------

IMAGE_LOCATION = dirname(pylon.ui.api.__file__)

#------------------------------------------------------------------------------
#  "SwarmWizardExtension" class:
#------------------------------------------------------------------------------

class SwarmWizardExtension(WizardExtension):
    """ Contributes a new swarm wizard """

    # The wizard contribution's globally unique identifier.
    id = "pylon.plugin.pyreto.new_swarm_wizard"

    # Human readable identifier
    name = "Swarm"

    # The wizards's image (displayed on selection etc)
    image = ImageResource("new", search_path=[IMAGE_LOCATION])

    # The class of contributed wizard
    wizard_class = "pylon.plugin.pyreto.swarm_wizard:SwarmWizard"

    # A longer description of the wizard's function
    description = "Create a new swarm resource"

# EOF -------------------------------------------------------------------------
