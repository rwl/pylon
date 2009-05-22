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

from os.path import join, dirname, splitext

from enthought.io.api import File as IOFile

from enthought.traits.api import \
    HasTraits, Directory, Bool, Str, Float, Property, Instance

from enthought.pyface.api import ImageResource

from puddle.resource.i_workspace import IWorkspace
from puddle.resource.wizard.new_resource_wizard import NewResourceWizard
from puddle.resource.resource_adapter import PickleFileIResourceAdapter
from puddle.resource.wizard_extension import WizardExtension

from puddle.resource.wizard.resource_selection_page \
    import ResourceSelectionPage

from puddle.resource.wizard.container_selection_page \
    import ContainerSelectionPage

from puddle.resource.wizard.new_resource_wizard \
    import NewResourceWizardPage

#from pylon.pyreto.experiment import MarketExperiment
from pylon.pyreto import simulate_trade

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

    #--------------------------------------------------------------------------
    #  "object" interface:
    #--------------------------------------------------------------------------

    def __init__(self, window, **traits):
        """ Initialises the wizard.
        """
        self.window = window
        workspace = window.application.get_service(IWorkspace)

        rsp = ResourceSelectionPage(id="selection_page", workspace=workspace)
        csp = ContainerSelectionPage(id="container_page", workspace=workspace)
        nwp = NewResourceWizardPage(id="resource_page",
            extensions=self.extensions, csp=csp)

        self.pages = [rsp, csp, nwp]

        super(NewResourceWizard, self).__init__(**traits)

    #--------------------------------------------------------------------------
    #  "NewResourceWizard" interface:
    #--------------------------------------------------------------------------

    def get_resource(self, file):
        """ Returns the new adapted resource. Override in subclasses.
        """
        return PickleFileIResourceAdapter(file)


#    def get_content(self, name):
#        """ Returns the content for the new resource. Override in subclasses.
#        """
#        return MarketExperiment(name=name)


    def _finished_fired(self):
        """ Performs the resource creation if the wizard is
            finished successfully.
        """
        workspace = self.window.application.get_service(IWorkspace)

        rsp = self.pages[0]
        csp = self.pages[1]
        nrp = self.pages[2]

        file = IOFile(join(csp.directory, nrp.resource_name))

        if not file.exists:
            name, ext = splitext( nrp.resource_name )

            network_resource = PickleFileIResourceAdapter(rsp.resource)
            power_sys = network_resource.load()

            experiment = simulate_trade.main(power_sys)
            resource = self.get_resource(file)

            resource.save( experiment )

        self._open_resource(file)

        self._refresh_container(workspace)

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
