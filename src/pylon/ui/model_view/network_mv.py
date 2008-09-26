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

""" Defines a controller for network models """

#------------------------------------------------------------------------------
#  Imports:
#------------------------------------------------------------------------------

try:
    import enthought.sweet_pickle as pickle
except ImportError:
    import pickle

from os.path import join, dirname, expanduser

from enthought.traits.api import Instance, File, Bool

from enthought.traits.ui.api import \
    View, Handler, UIInfo, Group, Item, TableEditor, InstanceEditor, \
    Label, Tabbed, HGroup, VGroup, ModelView, FileEditor, StatusItem, \
    spring

from enthought.traits.ui.menu import NoButtons, OKCancelButtons, Separator
from enthought.pyface.api import error
from enthought.pyface.image_resource import ImageResource
from enthought.naming.unique_name import make_unique_name

from pylon.api import Network, Bus, Branch
from pylon.routine.api import DCPFRoutine, DCOPFRoutine

from pylon.filter.api import \
    MATPOWERImporter, PSSEImporter, PSATImporter, MATPOWERExporter

from pylon.ui.network_tree import network_tree_editor
from pylon.ui.graph.graph_image import GraphImage
from pylon.ui.graph.graph_editor import GraphEditor
from pylon.ui.graph.graph import Graph
from pylon.ui.about_view import about_view

from network_menu import menubar, toolbar

import pylon.ui.api

#------------------------------------------------------------------------------
#  Constants:
#------------------------------------------------------------------------------

ICON_LOCATION = dirname(pylon.ui.api.__file__)

frame_icon = ImageResource("frame.ico", search_path=[ICON_LOCATION])

#------------------------------------------------------------------------------
#  Traits:
#------------------------------------------------------------------------------

graph_file_trait = File(
    value=expanduser("~"),
    filter=[
        "By Extension|*.*|"
        "Windows Bitmap Format (*.bmp)|*.bmp|"
        "Prettyprinted dot files (*.canon)|*.canon|"
        "Dot files (*.dot)|*.dot|"
        "XDot files (*.xdot)|*.xdot|"
        "Dia files (*.dia)|*.dia|"
        "Encapsulated PostScript (*.eps)|*.eps|"
        "Xfig files (*.fig)|*.fig|"
        "GD format files (*.gd)|*.gd|"
        "GD2 format files (.gd2)|*.gd2|"
        "GIF files (*.gif)|*.gif|"
        "GTK canvas (*.gtk)|*.gtk|"
        "HP-GL/2 format files (*.hpgl)|*.hpgl|"
        "Icon Image File Format (*.ico)|*.ico|"
        "Server and client-side imagemaps (*.cmapx, *.imap)|*.cmapx;*.imap|"
        "Server and client-side rectangular imagemaps (*.cmapx_np, *.imap_np)|"
            "*.cmapx_np;*.imap_np|"
        "JPEG files (*.jpe, *.jpeg, *.jpg)|*.jpe;*.jpeg;*.jpg|"
        "FrameMaker MIF files (*.mif)|*.mif|"
        "MetaPost files (*.mp)|*.mp|"
        "PCL files (*.pcl)|*.pcl|"
        "Portable Document Format files (*.pdf)|*.pdf|"
        "PIC files (*.pic)|*.pic|"
        "Simple text files (*.plain, *.plain-ext)|*.plain;*.plain-ext|"
        "Portable Network Graphics files (*.png)|*.png|"
        "PostScript files (*.ps)|*.ps|"
        "PostScript for PDF files (*.ps2)|*.ps2|"
        "Scalable Vector Graphics files (*.svg, *.svgz)|*.svg;*.svgz|"
        "Truevision Targa Format files (*.tga)|*.tga|"
        "Tag Image File Format files (*.tif, *.tiff)|*.tif;*.tiff|"
        "Vector Markup Language files (*.vml, *.vmlz)|*.vml;*.vmlz|"
        "Virtual Reality Modeling Language files (*.vrml)|*.vrml|"
        "Visual Thought files (*.vtx)|*.vtx|"
        "Wireless BitMap (*.wbmp)|*.wbmp|"
        "Xlib canvas files (*.xlib)|*.xlib"
    ],
    desc="location of graph export"
)

#------------------------------------------------------------------------------
#  "NetworkModelView" class:
#------------------------------------------------------------------------------

class NetworkModelView(ModelView):
    """ Defines a handler for network models """

    #--------------------------------------------------------------------------
    #  Trait definitions:
    #--------------------------------------------------------------------------

    # A graph representation of the network model as a scrollable image
    graph_image = Instance(GraphImage, GraphImage(), desc="image of the graph")

    # Interactive graph representaion of the network
    graph = Instance(Graph, Graph(), desc="interactive graph")

    # Is the interactive version fo the graph displayed?
    is_interactive = Bool(True, desc="disables the interactive graph")

    # Is the tree view of the network displayed?
    show_tree = Bool(True, desc="that the network tree view is visible")

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
                name="model", editor=network_tree_editor,
                show_label=False, id=".tree_editor",
                visible_when="show_tree==True", width=.2
            ),
            Item(
                name="graph_image", show_label=False,
                visible_when="is_interactive==True", width=.8
            ),
            Item(
                name="graph", show_label=False,
                visible_when="is_interactive==False", width=.8
            ),
            id=".split"#, layout="split"
        ),
        id="network_vm.view", title="Pylon", icon=frame_icon,
        resizable=True, style="custom",
        width=.81, height=.81, kind="live",
        buttons=NoButtons,
        menubar=menubar, toolbar=toolbar#, statusbar=[
#            StatusItem(name="file", width=0.5),
#            StatusItem(name="info.ui.title", width=85)
#        ],
#        dock="vertical"
    )

    # A file selection view
    file_view = View(
        Item(name="file", id="file", editor=FileEditor(entries=6)),
        id="network_mv.file_view", title="Select a file",
        icon=frame_icon, resizable=True, width=.3, kind="livemodal",
        buttons=OKCancelButtons
    )

    def _is_interactive_changed(self, is_interactive):
        """ Removes the reference to the model from the appropriate
        graph to prevent it from listening to further changes.

        """

        if is_interactive:
            self.graph.network = self.model
            self.graph_image.network = None
        else:
            self.graph.network = None
            self.graph_image.network = self.model


    def _model_changed(self, new):
        """ Handles new models by updating the graph references """

        if self.is_interactive:
            self.graph_image.network = new
        else:
            self.graph.network = new


    def new(self, info):
        """ Handles creation of a new network model """

        if info.initialized:
            self.model = Network()


    def open(self, info):
        """ Handles opening an existing network model """

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


    def _import_data_file(self, filter):
        """ Imports a data file using a filter """

        retval = self.edit_traits(
            parent=info.ui.control, view="file_view", kind="livemodal"
        )

        if retval.result:
            self.model = filter.parse_file(self.file)


    def import_matpower(self, info):
        """ Handles importing MATPOWER data files """

        if info.initialized:
            self._import_data_file(filter=MATPOWERImporter())


    def import_psse(self, info):
        """ Handles importing PSS/E data files """

        if info.initialized:
            self._import_data_file(filter=PSSEImporter())


    def import_psat(self, info):
        """ Handles importing PSAT data files """

        if info.initialized:
            self._import_data_file(filter=PSATImporter())


    def _export_network(self, filter):
        """ Exports the current network using a filter """

        retval = self.edit_traits(
                parent=info.ui.control, view="file_view", kind="livemodal"
        )

        if retval.result:
            filter.export_network(self.model, self.file)


    def export_matpower(self, info):
        """ Handles exporting to a MATPOWER data file """

        self._export_network(filter=MATPOWERExporter())


    def toggle_tree(self, info):
        """ Handles displaying the tree view """

        if info.initialized:
            self.show_tree = not self.show_tree


    def toggle_interactive(self, info):
        """ Handles switching between interactive and passive graphs """

        if info.initialized:
            self.is_interactive = not self.is_interactive


    def show_table(self, info):
        """ Handles display of the table view """

        if info.initialized:
            self.model.edit_traits(
                view="buses_view", parent=info.ui.control, kind="livemodal"
            )


    def add_bus(self, info):
        """ Handles adding a bus to the network """

        if info.initialized:
            name = make_unique_name("v", self.model.bus_names)
            self.model.buses.append(Bus(name=name))


    def add_branch(self, info):
        """ Handles adding a branch to the network """

        if not info.initialized:
            return

        network = self.model

        if len(network.buses) < 2:
            print "For branch addition two or more buses are a prerequisite"
        else:
            name = make_unique_name("e", network.branch_names)

            branch = Branch(
                name=name,
                network=network,
                source_bus=network.buses[0],
                target_bus=network.buses[1]
            )
            network.add_branch(branch)


    def dcopf(self, info):
        """ Runs the model using a DC OPF routine """

        routine = DCOPFRoutine(network=self.model)
        routine.edit_traits(parent=info.ui.control, kind="livemodal")

        del routine


    def about(self, info):
        """ Handles displaying a view about Pylon """

        if info.initialized:
            self.edit_traits(
                view=about_view, parent=info.ui.control, kind="livemodal"
            )

# EOF -------------------------------------------------------------------------
