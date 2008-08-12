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

""" Defines contributions to workspace wizards """

#------------------------------------------------------------------------------
#  Imports:
#------------------------------------------------------------------------------

from os.path import dirname

from enthought.pyface.api import ImageResource
from enthought.plugins.workspace.wizard_extension import WizardExtension

#------------------------------------------------------------------------------
#  "MATPOWERImportWizardExtension" class:
#------------------------------------------------------------------------------

class MATPOWERImportWizardExtension(WizardExtension):
    """ Contributes a MATPOWER import wizard """

    # The wizard contribution's globally unique identifier.
    id = "pylon.plugin.filter.matpower.import_wizard"

    # Human readable identifier
    name = "MATPOWER"

    # The wizards's image (displayed on selection etc)
    image = ImageResource("matpower")

    # The class of contributed wizard
    wizard_class = "pylon.plugin.filter.matpower.matpower_import_wizard:" \
    "MATPOWERImportWizard"

    # A longer description of the wizard's function
    description = "Import a MATPOWER data file"

#------------------------------------------------------------------------------
#  "MATPOWERExportWizardExtension" class:
#------------------------------------------------------------------------------

class MATPOWERExportWizardExtension(WizardExtension):
    """ Contributes a MATPOWER export wizard """

    # The wizard contribution's globally unique identifier.
    id = "pylon.plugin.filter.matpower.export_wizard"

    # Human readable identifier
    name = "MATPOWER"

    # The wizards's image (displayed on selection etc)
    image = ImageResource("matpower")

    # The class of contributed wizard
    wizard_class = "pylon.plugin.filter.matpower.matpower_export_wizard:" \
    "MATPOWERExportWizard"

    # A longer description of the wizard's function
    description = "Export resource to a MATPOWER data file"

# EOF -------------------------------------------------------------------------
