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
Controllers for network view model.

"""

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

from enthought.pyface.image_resource import ImageResource

from enthought.naming.unique_name import make_unique_name

from pylon.api import Network, Bus, Branch
from pylon.routine.api import DCPFRoutine, DCOPFRoutine
from pylon.filter.api import MATPOWERImporter, PSSEImporter, PSATImporter
from pylon.ui.network_tree import network_tree_editor
from pylon.ui.graph.graph_image import GraphImage
from pylon.ui.graph.graph_editor import GraphEditor
from pylon.ui.graph.graph import Graph

from network_menu import menubar, toolbar

import pylon.ui.api

#------------------------------------------------------------------------------
#  Constants:
#------------------------------------------------------------------------------

ICON_LOCATION = join(dirname(pylon.ui.api.__file__), "images")

frame_icon = ImageResource("frame.ico", search_path=[ICON_LOCATION])

#------------------------------------------------------------------------------
#  "NetworkModelView" class:
#------------------------------------------------------------------------------

class NetworkModelView(ModelView):
    """
    Handler for the "Network" class.

    """

    #--------------------------------------------------------------------------
    #  Trait definitions:
    #--------------------------------------------------------------------------

    graph_image = Instance(GraphImage, GraphImage(), desc="image of the graph")

    graph = Instance(Graph, Graph(), desc="interactive graph")

    fast_draw = Bool(True, desc="disables the interactive graph")

    # "Bitmap files|*.bmp|JPEG files|*.jpg|GIF files|*.gif"
    # filters="Image files (*.gif;*.png;*.jpg)|*.gif;*.png;*.jpg",
    # "MayaVi2 files (*.mv2)|*.mv2|"

#    "canon", "cmap", "cmapx", "cmapx_np", "dia", "dot",
#    "fig", "gd", "gd2", "gif", "hpgl", "imap", "imap_np", "ismap",
#    "jpe", "jpeg", "jpg", "mif", "mp", "pcl", "pdf", "pic", "plain",
#    "plain-ext", "png", "ps", "ps2", "svg", "svgz", "vml", "vmlz",
#    "vrml", "vtx", "wbmp", "xdot", "xlib"

# 'bmp', 'eps', 'gtk', 'ico', 'tga', 'tif', 'tiff'

    file = File(
        value=expanduser("~"),
        desc="location of a pickled Network instance"
    )

    graph_file = File(
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

    show_tree = Bool(True, desc="that the network tree view is visible")

    traits_view = View(
        HGroup(
            Item(
                name="model",
                editor=network_tree_editor,
                show_label=False,
                id=".tree_editor",
                width=.2,
                visible_when="show_tree==True"
            ),
            Item(
                name="graph_image",
                show_label=False,
                width=.8,
                visible_when="fast_draw==True"
            ),
            Item(
                name="graph",
                show_label=False,
                width=.8,
                visible_when="fast_draw==False"
            ),
            id=".split",
#            layout="split"
        ),
        id="network_vm.view",
        title="Pylon",
        icon=frame_icon,
        resizable=True,
        style="custom",
    #    buttons=NoButtons,
        width=.81,
        height=.81,
        kind="live",
        buttons=NoButtons,
        menubar=menubar,
        toolbar=toolbar,
#        statusbar=[
#            StatusItem(name="file", width=0.5),
#            StatusItem(name="info.ui.title", width=85)
#        ],
#        dock="vertical"
    )

    file_view = View(
        Item(
            name="file",
            id="data_file",
            label="File",
#            editor=FileEditor(entries=6)
        ),
        id="network_mv.file_view",
        title="Select a file",
        icon=frame_icon,
        resizable=True,
        style="simple",
        width=.3,
        kind="livemodal",
        buttons=OKCancelButtons
    )

    export_graph_view = View(
        Item(
            name="graph_file",
            id="graph_export_file",
            label="File",
#            editor=FileEditor(entries=6)
        ),
        id="network_mv.export_graph_view",
        title="Select a file",
        icon=frame_icon,
        resizable=True,
        style="simple",
        width=.3,
        kind="livemodal",
        buttons=OKCancelButtons
    )


    def _fast_draw_changed(self, new):
        """
        Removes the reference to the model from the appropriate
        NetworkDot instance to prevent it from listening to
        further changes.

        """

        if new:
            self.graph.network = None
            self.graph_image.network = self.model
        else:
            self.graph.network = self.model
            self.graph_image.network = None


    def _model_changed(self, new):
        """
        Gives any new network model a selection of routines and
        updates the network dot reference.

        """

#        if new is not None:
#            new.pf_routines = PF_ROUTINES
#            new.opf_routines = OPF_ROUTINES

        if self.fast_draw:
            self.graph_image.network = new
        else:
            self.graph.network = new


    def new(self, info):
        if not info.initialized:
            return

        self.model = Network()


    def open(self, info):
        if not info.initialized:
            return
        retval = self.edit_traits(
            parent=info.ui.control,
            view="file_view"
        )
        if retval.result:
            fd = open(self.file, "rb")
            self.model = pickle.load(fd)
            fd.close()


    def save(self, info):
        if not info.initialized:
            return

        retval = self.edit_traits(
            parent=info.ui.control,
            view="file_view"
        )

        if retval.result:
            fd = open(self.file, "wb")
            pickle.dump(self.model, fd)
            fd.close()


    def matpower(self, info):
        if not info.initialized:
            return

        filter = MATPOWERImporter()

        retval = filter.edit_traits(
            parent=info.ui.control,
            kind="livemodal"
        )

        if retval.result:
            n = filter.network
            if n is not None:
                self.model = n

        del filter


    def psse(self, info):
        if not info.initialized:
            return

        filter = PSSEImporter()

        retval = filter.edit_traits(
            parent=info.ui.control,
            kind="livemodal"
        )

        if retval.result:
            n = filter.network
            if n is not None:
                self.model = n

        del filter


    def psat(self, info):
        if not info.initialized:
            return

        filter = PSATImporter()

        retval = filter.edit_traits(
            parent=info.ui.control,
            kind="livemodal"
        )

        if retval.result:
            n = filter.network
            if n is not None:
                self.model = n

        del filter


    def export_graph(self, info):
        """
        Allows the dot represntation of the network to be in exported as:
        "canon", "cmap", "cmapx", "cmapx_np", "dia", "dot",
        "fig", "gd", "gd2", "gif", "hpgl", "imap", "imap_np", "ismap",
        "jpe", "jpeg", "jpg", "mif", "mp", "pcl", "pdf", "pic", "plain",
        "plain-ext", "png", "ps", "ps2", "svg", "svgz", "vml", "vmlz",
        "vrml", "vtx", "wbmp", "xdot", "xlib"

        """

        if not info.initialized:
            return

        retval = self.edit_traits(
            parent=info.ui.control,
            view="export_graph_view"
        )

#        if retval.result:
#            dot = self.graph_image.network_dot.dot
#            if dot is not None:
#                dot.write(
#                    path=self.file,
#                    prog=self.graph_image.program,
#                    format="png"
#                )


    def preferences(self, info):
        if not info.initialized:
            return

        if self.fast_draw:
            self.graph_image.edit_traits(
                view="config",
                parent=info.ui.control,
                kind="livemodal"
            )
        else:
            self.graph.edit_traits(
                view="config",
                parent=info.ui.control,
                kind="livemodal"
            )


    def toggle_tree(self, info):
        if not info.initialized:
            return

        self.show_tree = not self.show_tree


    def draw_fast(self, info):
        if not info.initialized:
            return

        self.fast_draw = not self.fast_draw


    def show_buses(self, info):
        if not info.initialized:
            return

        self.model.edit_traits(
            view="buses_view",
            parent=info.ui.control,
            kind="live"
        )


    def show_branches(self, info):
        if not info.initialized:
            return

        self.model.edit_traits(
            view="branches_view",
            parent=info.ui.control,
            kind="live"
        )


    def add_bus(self, info):
        if not info.initialized:
            return

        network = self.model

        name = make_unique_name("v", network.bus_names)

        bus = Bus(name=name)
        network.buses.append(bus)


    def add_branch(self, info):
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
        """
        Runs the models DC OPF routine

        """

#        self.model.opf_routine = OPF_ROUTINES[0]
#        self.model.solve_opf()

        routine = DCOPFRoutine(network=self.model)
        routine.edit_traits(parent=info.ui.control, kind="livemodal")

        del routine


#    def dot(self, info):
#        if not info.initialized:
#            return
#
#        self.network_vm.png_graph.network_dot.edit_traits(
#            parent=info.ui.control,
#            kind="live"
#        )

    def about(self, info):
        """ Displays the model's about view """

        if not info.initialized:
            return

        from pylon.ui.about_view import about_view

        self.model.edit_traits(
            view=about_view,
            parent=info.ui.control,
            kind="livemodal"
        )

# EOF -------------------------------------------------------------------------
