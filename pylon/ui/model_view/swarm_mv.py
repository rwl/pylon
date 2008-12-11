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

""" Defines a viewer for Pyreto swarms """

#------------------------------------------------------------------------------
#  Imports:
#------------------------------------------------------------------------------

from logging import Logger, getLogger, DEBUG

try:
    import enthought.sweet_pickle as pickle
except ImportError:
    import pickle

from os.path import join, dirname, expanduser

from enthought.traits.api import \
    HasTraits, Instance, File, Bool, Str, List, on_trait_change, DelegatesTo

from enthought.traits.ui.api import \
    View, Handler, UIInfo, Group, Item, TableEditor, InstanceEditor, \
    Label, Tabbed, HGroup, VGroup, ModelView, FileEditor, StatusItem, \
    spring

from enthought.traits.ui.menu import NoButtons, OKCancelButtons, Separator
from enthought.pyface.api import error
from enthought.pyface.image_resource import ImageResource
from enthought.naming.unique_name import make_unique_name
from enthought.logger.api import add_log_queue_handler
from enthought.logger.log_queue_handler import LogQueueHandler

#------------------------------------------------------------------------------
#  Local imports:
#------------------------------------------------------------------------------

from pylon.readwrite.api import \
    MATPOWERReader, PSSEReader, PSATReader, MATPOWERWriter

from pylon.api import Network, Bus, Branch

#from pylon.routine.api import \
#    DCPFRoutine, DCOPFRoutine, NewtonPFRoutine, ACOPFRoutine

from pylon.ui.routine.dc_pf_view_model import DCPFViewModel
from pylon.ui.routine.dc_opf_view_model import DCOPFViewModel
from pylon.ui.routine.ac_pf_view_model import ACPFViewModel
from pylon.ui.routine.ac_opf_view_model import ACOPFViewModel

from pylon.ui.network_tree import network_tree_editor
from pylon.ui.graph.graph_image import GraphImage
from pylon.ui.graph.graph_editor import GraphEditor
from pylon.ui.graph.graph import Graph
from pylon.ui.about_view import about_view
from pylon.ui.report_view import pf_report_view, opf_report_view

from pyrenees.map import Map
from pyrenees.layer.osm import OSM

from pylon.pyreto.api import MarketEnvironment, ParticipantEnvironment
from pyqle.api import Swarm

from network_menu import menubar, toolbar

import pylon.ui.api

#------------------------------------------------------------------------------
#  Constants:
#------------------------------------------------------------------------------

ICON_LOCATION = dirname(pylon.ui.api.__file__)

frame_icon = ImageResource("frame.ico", search_path=[ICON_LOCATION])

LOG_LEVEL = DEBUG

#------------------------------------------------------------------------------
#  "LogEntry" class:
#------------------------------------------------------------------------------

class LogEntry(HasTraits):
    level_name = Str
    time = Str
    message = Str

#------------------------------------------------------------------------------
#  "SwarmModelView" class:
#------------------------------------------------------------------------------

class SwarmModelView(ModelView):
    """ Defines a viewer for Pyreto swarms """

    #--------------------------------------------------------------------------
    #  Trait definitions:
    #--------------------------------------------------------------------------

    network = Instance(Network)
#    network = DelegatesTo("model.environment")

    # A graph representation of the network model as a scrollable image
    graph_image = Instance(GraphImage, GraphImage(), desc="image of the graph")

    # Interactive graph representation of the network
    graph = Instance(Graph, Graph(), desc="interactive graph")

    # Is the interactive version fo the graph displayed?
    is_interactive = Bool(True, desc="disables the interactive graph")

    # Is the tree view of the network displayed?
    show_tree = Bool(True, desc="that the network tree view is visible")

    # Interactive map representation of the domain model
    network_map = Instance(Map)

    # The current status of the model
    status = Str

    # Buffers up the log messages so that they can be displayed later
    handler = Instance(LogQueueHandler)

    # Log history
    log_entries = List(Instance(LogEntry))

    # Path to a file for loading/saving/importing/exporting
    file = File(
        filter=[
            "All Files (*.*)|*.*|Pylon Files (*.pyl)|*.pyl|"
            "MATPOWER Files (*.m)|*.m|PSAT Files (*.m)|*.m|"
            "PSS/E Files (.raw)|*.raw|"
        ]
    )

    # The default view
    traits_view = View(
        HGroup(
            Item(
                name="network", editor=network_tree_editor,
                show_label=False, id=".tree_editor",
                visible_when="show_tree==True", width=.2
            ),
            Item(
                name="graph_image", show_label=False,
                visible_when="is_interactive==False", width=.8
            ),
            Item(
                name="graph", show_label=False,
                visible_when="is_interactive==True", width=.8
            ),
            id=".split"#, layout="split"
        ),
        id="swarm_vm.view", title="Pylon", icon=frame_icon,
        resizable=True, style="custom",
        width=.81, height=.81, kind="live",
        buttons=NoButtons,
        menubar=menubar, toolbar=toolbar,
#        statusbar=[
#            StatusItem(name="status", width=0.5),
#            StatusItem(name="status", width=200)
#        ],
        dock="vertical"
    )

    # A file selection view
    file_view = View(
        Item(name="file", id="file"),#, editor=FileEditor(entries=6)),
        id="swarm_mv.file_view", title="Select a file",
        icon=frame_icon, resizable=True, width=.3, kind="livemodal",
        buttons=OKCancelButtons
    )

    #--------------------------------------------------------------------------
    #  Trait initialisers:
    #--------------------------------------------------------------------------

    def _network_default(self):
        """ Trait initialiser """

        return self.model.environment.network


    def _network_map_default(self):
        """ Trait initialiser """

        return Map(layer_types=[OSM])


    def _handler_default(self):
        """ Trait initialiser """

        logger = getLogger()#__name__)
        handler = add_log_queue_handler(logger, level=LOG_LEVEL)
        # set the view to update when something is logged.
#        handler._view = self

        return handler

    #--------------------------------------------------------------------------
    #  Event handlers:
    #--------------------------------------------------------------------------

    def update(self):
        """ Update the table if new records are available """



        if self.handler.has_new_records():

            records = self.handler.get()

            self.log_entries = []
            for record in records[:]:
                print "BLAPP ", record.message

#                level_name = record.levelname
#                time=record.asctime
#                message=record.message

                entry = LogEntry(level_name="name", time="12:00", message="foo")
                print entry
                self.log_entries.append(entry)

            print "RECORDS", len(records), len(self.log_entries)


            if self.log_entries:
                self.status = self.log_entries[-1].message


    def _is_interactive_changed(self, is_interactive):
        """ Removes the reference to the model from the appropriate
        graph to prevent it from listening to further changes.

        """

        n = self.model.environment.network

        if is_interactive:
            self.graph.network = n
            self.graph_image.network = None
        else:
            self.graph.network = None
            self.graph_image.network = n


    def _model_changed(self, new):
        """ Handles new models by updating the graph references """

        n = new.environment.network

        if self.is_interactive:
            self.graph.network = n
        else:
            self.graph_image.network = n


    @on_trait_change("model.environment.network")
    def clear_assets(self):
        """ Handles the network changing

        Handles clearing all assets from participant environments when
        the network is changed

        """

        for agent in self.model.elementary_agents:
            agent.environment.asset = None

        self.network = self.model.environment.network


    @on_trait_change("model.environment.network")
    def graph_network(self):
        """ Handles the network reference for the graph """

        n = self.model.environment.network

        if self.is_interactive:
            self.graph.network = n
            self.graph_image.network = None
        else:
            self.graph.network = None
            self.graph_image.network = n

    #--------------------------------------------------------------------------
    #  Action handlers:
    #--------------------------------------------------------------------------

    def new_model(self, info):
        """ Handles creation of a new swarm model """

        if info.initialized:
            env = MarketEnvironment(network=Network())
            self.model = Swarm(environment=env)


    def new_network(self, info):
        """ Handles adding a new network to the existing swarm """

        if info.initialised:
            self.model.environment.network = Network()


    def open_file(self, info):
        """ Handles opening an existing network model """
        print dir(info)
        if not info.initialized:
            return

        retval = self.edit_traits(parent=info.ui.control, view="file_view")

        if retval.result:
            fd = None
            try:
                fd = open(self.file, "rb")
                self.model = pickle.load(fd)
            except:
                error(
                    parent=info.ui.control, title="Load Error",
                    message="An error was encountered when loading\nfrom %s"
                    % self.file
                )
            finally:
                if fd is not None:
                    fd.close()


    def save(self, info):
        """ Handles saving the current model to file """

        if not info.initialized:
            return

        retval = self.edit_traits(parent=info.ui.control, view="file_view")

        if retval.result:
            fd = None
            try:
                fd = open(self.file, "wb")
                pickle.dump(self.model, fd)
            except:
                error(
                    parent=info.ui.control, title="Save Error",
                    message="An error was encountered when saving\nto %s"
                    % self.file
                )
            finally:
                if fd is not None:
                    fd.close()


    def _import_data_file(self, parent, filter):
        """ Imports a data file using a filter """

        retval = self.edit_traits(parent=info.ui.control, view="file_view",
            kind="livemodal")

        if retval.result:
            self.model.environment.network = filter.parse_file(self.file)


    def import_matpower(self, info):
        """ Handles importing MATPOWER data files """

        if info.initialized:
            retval = self.edit_traits(parent=info.ui.control, view="file_view",
                kind="livemodal")

            if retval.result:
                reader = MATPOWERReader(self.file)
                self.model.environment.network = reader.network


    def import_psse(self, info):
        """ Handles importing PSS/E data files """

        if info.initialized:
            retval = self.edit_traits(parent=info.ui.control, view="file_view",
                kind="livemodal")

            if retval.result:
                reader = PSSEReader(self.file)
                self.model.environment.network = reader.network


    def import_psat(self, info):
        """ Handles importing PSAT data files """

        if info.initialized:
            retval = self.edit_traits(parent=info.ui.control, view="file_view",
                kind="livemodal")

            if retval.result:
                reader = PSATReader(self.file)
                self.model.environment.network = reader.network


    def _export_network(self, parent, filter):
        """ Exports the current network using a filter """

        retval = self.edit_traits(
            parent=parent, view="file_view", kind="livemodal"
        )

        if retval.result:
            filter.export_network(self.model.environment.network, self.file)


    def export_matpower(self, info):
        """ Handles exporting to a MATPOWER data file """

        self._export_network(info.ui.control, MATPOWERWriter())


    def toggle_tree(self, info):
        """ Handles displaying the tree view """

        if info.initialized:
            self.show_tree = not self.show_tree


    def toggle_interactive(self, info):
        """ Handles switching between interactive and passive graphs """

        if info.initialized:
            self.is_interactive = not self.is_interactive


    def show_swarm_table(self, info):
        """ Handles display of the swarm in a table view """

        if info.initialized:
            self.model.edit_traits(parent=info.ui.control, kind="livemodal")


    def show_network_table(self, info):
        """ Handles display of the network in a table view """

        if info.initialized:
            n = self.model.environment.network
            n.edit_traits(parent=info.ui.control, kind="livemodal")


    def show_map_view(self, info):
        """ Handles display of the map view """

        if info.initialized:
            m = self.network_map
            m.edit_traits(parent=info.ui.control, kind="livemodal")


    def add_bus(self, info):
        """ Handles adding a bus to the network """

        if info.initialized:
            n = self.model.environment.network
            bus_names = [v.name for v in n.buses]
            bus = Bus(name=make_unique_name("bus", bus_names))
            n.buses.append(bus)
#            retval = bus.edit_traits(parent=info.ui.control, kind="livemodal")
#            if not retval.result:
#                n.buses.remove(bus)


    def add_branch(self, info):
        """ Handles adding a branch to the network """

        if not info.initialized:
            return

        n = self.model.environment.network

        if len(n.buses) < 2:
            print "For branch addition two or more buses are a prerequisite"
        else:
            branch_names = [e.name for e in n.branches]
            name = make_unique_name("branch", branch_names)

            branch = Branch(
                name=name, network=n,
                source_bus=n.buses[0],
                target_bus=n.buses[1]
            )
            n.branches.append(branch)
            retval = branch.edit_traits(
                parent=info.ui.control, kind="livemodal"
            )
            if not retval.result:
                n.branches.remove(branch)


    def dcpf(self, info):
        """ Runs the model using a DC Power Flow routine. """

        n = self.model.environment.network

        vm = DCPFViewModel(network=n)
        retval = vm.edit_traits(parent=info.ui.control, kind="livemodal")

        if retval.result:
            n.edit_traits(view=pf_report_view, parent=info.ui.control,
                kind="livemodal")


    def dcopf(self, info):
        """ Runs the model using a DC OPF routine. """

        n = self.model.environment.network

        vm = DCOPFViewModel(network=n)
        retval = vm.edit_traits(parent=info.ui.control, kind="livemodal")

        if retval.result:
            n.edit_traits(view=opf_report_view, parent=info.ui.control,
                kind="livemodal")


    def acpf(self, info):
        """ Runs the model using a DC Power Flow routine. """

        n = self.model.environment.network

        vm = ACPFViewModel(network=n)
        retval = vm.edit_traits(parent=info.ui.control, kind="livemodal")

        if retval.result:
            n.edit_traits(view=pf_report_view, parent=info.ui.control,
                kind="livemodal")


    def acopf(self, info):
        """ Runs the model using a AC OPF routine. """

        n = self.model.environment.network

        vm = ACOPFViewModel(network=n)
        retval = vm.edit_traits(parent=info.ui.control, kind="livemodal")

        if retval.result:
            n.edit_traits(view=opf_report_view, parent=info.ui.control,
                kind="livemodal")


    def about(self, info):
        """ Handles displaying a view about Pylon """

        if info.initialized:
            self.edit_traits(
                view=about_view, parent=info.ui.control, kind="livemodal"
            )

# EOF -------------------------------------------------------------------------
