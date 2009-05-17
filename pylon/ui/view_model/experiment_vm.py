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

""" Defines a model for viewing market experiments.
"""

#------------------------------------------------------------------------------
#  Imports:
#------------------------------------------------------------------------------

import sys
import logging
from os.path import join, dirname, expanduser

from enthought.traits.api \
    import HasTraits, Instance, File, Bool, Str, List, on_trait_change, \
    DelegatesTo, Float, Tuple

from enthought.traits.ui.api \
    import View, Handler, UIInfo, Group, Item, TableEditor, InstanceEditor, \
    Label, Tabbed, HGroup, VGroup, ModelView, FileEditor, StatusItem, spring

from enthought.traits.ui.menu \
    import NoButtons, OKCancelButtons, Separator

from enthought.pyface.image_resource \
    import ImageResource

from pylon.pyreto.experiment \
    import MarketExperiment

from pylon.ui.plot.experiment_plot \
    import ExperimentPlot

from network_vm \
    import NetworkViewModel

from network_menu \
    import network_menubar, network_toolbar

#------------------------------------------------------------------------------
#  Constants:
#------------------------------------------------------------------------------

IMAGE_LOCATION = join(dirname(__file__), "../images")

frame_icon = ImageResource("frame.ico", search_path=[IMAGE_LOCATION])

#------------------------------------------------------------------------------
#  "ExperimentViewModel" class:
#------------------------------------------------------------------------------

class ExperimentViewModel(NetworkViewModel):
    """ Defines a model for viewing market experiments.
    """

    #--------------------------------------------------------------------------
    #  Trait definitions:
    #--------------------------------------------------------------------------

    # Market experiment that uses the network model.
    experiment = Instance(MarketExperiment)

    # Plot of experiment state, action and reward values.
    experiment_plot = Instance(ExperimentPlot)

    # The default view
    traits_view = View(
        Item(name="experiment_plot", style="custom", show_label=False,
             id=".experiment_plot"),
        id="pylon.experiment_vm.view", title="Pyreto", icon=frame_icon,
        resizable=True, style="custom",
        width=.81, height=.81, kind="live",
        buttons=NoButtons,
        menubar=network_menubar, toolbar=network_toolbar,
#        statusbar=[StatusItem(name="status"),
#                   StatusItem(name="versions", width=200)],
        dock="vertical"
    )

    #--------------------------------------------------------------------------
    #  Trait initialisers:
    #--------------------------------------------------------------------------

    def _experiment_default(self):
        """ Trait initialiser.
        """
        return MarketExperiment(agents=[], tasks=[], power_system=self.model)

    #--------------------------------------------------------------------------
    #  Event handlers:
    #--------------------------------------------------------------------------

    def _model_changed(self, new):
        """ Handles a new model being set. Updates the experiment reference.
        """
        if new is not None:
            self.experiment.power_system = new

    #--------------------------------------------------------------------------
    #  Action handlers:
    #--------------------------------------------------------------------------

    def new_experiment(self, info):
        """ Handles the new experiment action.
        """
        if info.initialized:
            self.experiment = MarketExperiment([], [], self.model)

#------------------------------------------------------------------------------
#  Stand-alone call:
#------------------------------------------------------------------------------

if __name__ == "__main__":
    import sys
    from pylon.network import Network
    logger = logging.getLogger()
    logger.addHandler(logging.StreamHandler(sys.stdout))
    logger.setLevel(logging.DEBUG)

    view_model = ExperimentViewModel(model=Network())
    view_model.configure_traits()

# EOF -------------------------------------------------------------------------
