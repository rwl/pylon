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

""" Defines a wizard for swarm resource creation.
"""

#------------------------------------------------------------------------------
#  Imports:
#------------------------------------------------------------------------------

from os.path import join, dirname

from enthought.io.api import File as IOFile

from enthought.traits.api import \
    HasTraits, Directory, Bool, Str, Float, Property, Instance

from enthought.pyface.api import ImageResource

from envisage.resource.wizard.new_resource_wizard import NewResourceWizard
from envisage.resource.resource_adapter import PickleFileIResourceAdapter
from envisage.resource.wizard_extension import WizardExtension

from pylon.pyreto.experiment import MarketExperiment

#------------------------------------------------------------------------------
#  Constants:
#------------------------------------------------------------------------------

IMAGE_LOCATION = join(dirname(__file__), "..", "..", "ui", "images")

#------------------------------------------------------------------------------
#  "ExperimentWizard" class:
#------------------------------------------------------------------------------

class ExperimentWizard(NewResourceWizard):
    """ A wizard for experiment resource creation.
    """
    # The dialog title
    title = Str("New Experiment")

    extensions = [".pkl"]

    def get_resource(self, file):
        """ Returns the new adapted resource. Override in subclasses.
        """
        return PickleFileIResourceAdapter(file)


    def get_content(self, name):
        """ Returns the content for the new resource. Override in subclasses.
        """
        return MarketExperiment(name=name)

#------------------------------------------------------------------------------
#  "ExperimentWizardExtension" class:
#------------------------------------------------------------------------------

class ExperimentWizardExtension(WizardExtension):
    """ Contributes a new experiment wizard.
    """

    # The wizard contribution's globally unique identifier.
    id = "pylon.plugin.pyreto.new_experiment_wizard"

    # Human readable identifier
    name = "Experiment"

    # The wizards's image (displayed on selection etc)
    image = ImageResource("psse", search_path=[IMAGE_LOCATION])

    # The class of contributed wizard
    wizard_class = "pylon.plugin.pyreto.experiment_wizard:ExperimentWizard"

    # A longer description of the wizard's function
    description = "Create a new Pyreto experiment resource"

# EOF -------------------------------------------------------------------------
