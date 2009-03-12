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

""" Defines a model for viewing for network models.
"""

#------------------------------------------------------------------------------
#  Imports:
#------------------------------------------------------------------------------

import logging
import pickle
from os.path import join, dirname, expanduser

from enthought.traits.api import Instance, File, Bool, Str

from enthought.traits.ui.api import \
    View, Handler, UIInfo, Group, Item, TableEditor, InstanceEditor, \
    Label, Tabbed, HGroup, VGroup, ModelView, FileEditor, StatusItem, \
    spring

from enthought.traits.ui.menu import NoButtons, OKCancelButtons, Separator
from enthought.pyface.api import error, confirm, YES, FileDialog, OK
from enthought.pyface.image_resource import ImageResource
from enthought.naming.unique_name import make_unique_name
from enthought.logger.api import add_log_queue_handler
from enthought.logger.log_queue_handler import LogQueueHandler

from pylon.api import Network, Bus, Branch

from pylon.network import NetworkReport

from pylon.readwrite.api import \
    MATPOWERReader, PSSEReader, PSATReader, \
    MATPOWERWriter, CSVWriter, ExcelWriter, ReSTWriter

from pylon.ui.report_view import pf_report_view, opf_report_view
from pylon.ui.network_tree import network_tree_editor
from pylon.ui.graph.graph_image import GraphImage
from pylon.ui.graph.graph import Graph
from pylon.ui.about_view import about_view

from pylon.ui.routine.dc_pf_view_model \
    import DCPFViewModel

from pylon.ui.routine.dc_opf_view_model \
    import DCOPFViewModel

from pylon.ui.routine.ac_pf_view_model \
    import ACPFViewModel

from pylon.ui.routine.ac_opf_view_model \
    import ACOPFViewModel

from network_menu import \
    network_menubar, network_toolbar

from desktop_vm \
    import DesktopViewModel

logger = logging.getLogger(__name__)

#------------------------------------------------------------------------------
#  Constants:
#------------------------------------------------------------------------------

IMAGE_LOCATION = join(dirname(__file__), "../images")

frame_icon = ImageResource("frame.ico", search_path=[IMAGE_LOCATION])

LOG_LEVEL = logging.DEBUG

#------------------------------------------------------------------------------
#  Traits:
#------------------------------------------------------------------------------

#graph_file_trait = File(
#    value=expanduser("~"),
#    filter=[
#        "By Extension|*.*|"
#        "Windows Bitmap Format (*.bmp)|*.bmp|"
#        "Prettyprinted dot files (*.canon)|*.canon|"
#        "Dot files (*.dot)|*.dot|"
#        "XDot files (*.xdot)|*.xdot|"
#        "Dia files (*.dia)|*.dia|"
#        "Encapsulated PostScript (*.eps)|*.eps|"
#        "Xfig files (*.fig)|*.fig|"
#        "GD format files (*.gd)|*.gd|"
#        "GD2 format files (.gd2)|*.gd2|"
#        "GIF files (*.gif)|*.gif|"
#        "GTK canvas (*.gtk)|*.gtk|"
#        "HP-GL/2 format files (*.hpgl)|*.hpgl|"
#        "Icon Image File Format (*.ico)|*.ico|"
#        "Server and client-side imagemaps (*.cmapx, *.imap)|*.cmapx;*.imap|"
#        "Server and client-side rectangular imagemaps (*.cmapx_np, *.imap_np)|"
#            "*.cmapx_np;*.imap_np|"
#        "JPEG files (*.jpe, *.jpeg, *.jpg)|*.jpe;*.jpeg;*.jpg|"
#        "FrameMaker MIF files (*.mif)|*.mif|"
#        "MetaPost files (*.mp)|*.mp|"
#        "PCL files (*.pcl)|*.pcl|"
#        "Portable Document Format files (*.pdf)|*.pdf|"
#        "PIC files (*.pic)|*.pic|"
#        "Simple text files (*.plain, *.plain-ext)|*.plain;*.plain-ext|"
#        "Portable Network Graphics files (*.png)|*.png|"
#        "PostScript files (*.ps)|*.ps|"
#        "PostScript for PDF files (*.ps2)|*.ps2|"
#        "Scalable Vector Graphics files (*.svg, *.svgz)|*.svg;*.svgz|"
#        "Truevision Targa Format files (*.tga)|*.tga|"
#        "Tag Image File Format files (*.tif, *.tiff)|*.tif;*.tiff|"
#        "Vector Markup Language files (*.vml, *.vmlz)|*.vml;*.vmlz|"
#        "Virtual Reality Modeling Language files (*.vrml)|*.vrml|"
#        "Visual Thought files (*.vtx)|*.vtx|"
#        "Wireless BitMap (*.wbmp)|*.wbmp|"
#        "Xlib canvas files (*.xlib)|*.xlib"
#    ],
#    desc="location of graph export"
#)

#class LogEntry(HasTraits):
#    level_name = Str
#    time = Str
#    message = Str

#------------------------------------------------------------------------------
#  "NetworkViewModel" class:
#------------------------------------------------------------------------------

class NetworkViewModel(DesktopViewModel):
    """ Defines a viewer for network models.
    """

    #--------------------------------------------------------------------------
    #  "DesktopViewModel" interface:
    #--------------------------------------------------------------------------

    _model_factory = Network

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
    show_tree = Bool(False, desc="that the network tree view is visible")

    # The current status of the model
    status = Str

    # A single logging channel
#    logger = Instance(Logger)

    # Buffers up the log messages so that they can be displayed later
#    handler = Instance(LogQueueHandler)

    # Log history
#    log_entries = List(Instance(LogEntry))

    #--------------------------------------------------------------------------
    #  Views:
    #--------------------------------------------------------------------------

    # The default view
    traits_view = View(
        HGroup(
            Item(name="model", editor=network_tree_editor,
                 show_label=False, id=".tree_editor",
                 visible_when="show_tree==True", width=.2),
            Item(name="graph_image", show_label=False,
                 visible_when="is_interactive==False", width=.8),
            Item(name="graph", show_label=False,
                 visible_when="is_interactive==True", width=.8),
            id=".split"#, layout="split"
        ),
        id="network_vm.view", title="Pylon", icon=frame_icon,
        resizable=True, style="custom",
        width=.81, height=.81, kind="live",
        buttons=NoButtons,
        menubar=network_menubar, toolbar=network_toolbar,
#        statusbar=[StatusItem(name="status", width=0.5),
#                   StatusItem(name="status", width=200)],
        dock="vertical"
    )

    #--------------------------------------------------------------------------
    #  Trait initialisers:
    #--------------------------------------------------------------------------

#    def _handler_default(self):
#        """ Trait initialiser.
#        """
#        logger = getLogger()#__name__)
#        handler = add_log_queue_handler(logger, level=LOG_LEVEL)
#        # set the view to update when something is logged.
##        handler._view = self
#
#        return handler


#    def update(self):
#        """ Update the table if new records are available.
#        """
#        if self.handler.has_new_records():
#
#            records = self.handler.get()
#
#            self.log_entries = []
#            for record in records[:]:
#                print "BLAPP ", record.message
#
##                level_name = record.levelname
##                time=record.asctime
##                message=record.message
#
#                entry = LogEntry(level_name="name", time="12:00", message="foo")
#                print entry
#                self.log_entries.append(entry)
#
#            print "RECORDS", len(records), len(self.log_entries)
#
#
#            if self.log_entries:
#                self.status = self.log_entries[-1].message


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
        """ Handles new models by updating the graph references.
        """
        if self.is_interactive:
            self.graph.network = new
        else:
            self.graph_image.network = new

    #--------------------------------------------------------------------------
    #  Action handlers:
    #--------------------------------------------------------------------------

    def _read_data_file(self, reader_factory, wildcard="All Files (*.*)|*.*"):
        """ Imports a data file using the specified reader.
        """
        dialog = FileDialog( action   = "open",
                             wildcard = wildcard,
                             default_directory = self.wd )

        if dialog.open() == OK:
            reader  = reader_factory(dialog.path)
            network = reader.parse_file()
            if network is not None:
                self.model = network


    def read_matpower(self, info):
        """ Handles importing MATPOWER data files """

        if info.initialized:
            self._read_data_file(reader_factory = MATPOWERReader,
                                 wildcard = "MATPOWER Files (*.m)|*.m|" \
                                 "All Files (*.*)|*.*")


    def read_psse(self, info):
        """ Handles importing PSS/E data files.
        """
        if info.initialized:
            self._read_data_file(reader_factory = PSSEReader,
                                 wildcard = "PSSE Files (*.raw)|*.raw|" \
                                 "All Files (*.*)|*.*")


    def read_psat(self, info):
        """ Handles importing PSAT data files.
        """
        if info.initialized:
            self._read_data_file(reader_factory = PSATReader,
                                 wildcard = "PSAT Files (*.m)|*.m|" \
                                 "All Files (*.*)|*.*")

    #--------------------------------------------------------------------------
    #  Export network models:
    #--------------------------------------------------------------------------

    def _write_network(self, writer_factory, wildcard="All Files (*.*)|*.*"):
        """ Exports the network model using the specified writer.
        """
        dialog = FileDialog( action   = "open",
                             wildcard = wildcard,
                             default_directory = self.wd )

        if dialog.open() == OK:
            writer_factory(self.model, self.file)
            writer.write()


    def write_matpower(self, info):
        """ Handles exporting to a MATPOWER data file.
        """
        self._write_network( writer_factory = MATPOWERWriter,
                             wildcard = "MATPOWER Files (*.m)|*.m|" \
                             "All Files (*.*)|*.*" )


    def write_csv(self, info):
        """ Handles exporting to a CSV file.
        """
        self._write_network( writer_factory = CSVWriter,
                             wildcard = "CSV Files (*.csv)|*.csv|" \
                             "All Files (*.*)|*.*" )


    def write_excel(self, info):
        """ Handles exporting to an Excel spreadsheet.
        """
        self._write_network( writer_factory = ExcelWriter,
                             wildcard = "Excel Files (*.xls)|*.xls|" \
                             "All Files (*.*)|*.*" )


    def write_rst(self, info):
        """ Handles exporting to a ReStructured Text file.
        """
        self._write_network( writer_factory = ReSTWriter,
                             wildcard = "ReST Files (*.rst)|*.rst|" \
                             "All Files (*.*)|*.*" )

    #--------------------------------------------------------------------------
    #  View action handlers:
    #--------------------------------------------------------------------------

    def toggle_tree(self, info):
        """ Handles displaying the tree view.
        """
        if info.initialized:
            self.show_tree = not self.show_tree


    def toggle_interactive(self, info):
        """ Handles switching between interactive and passive graphs """

        if info.initialized:
            self.is_interactive = not self.is_interactive


    def show_table(self, info):
        """ Handles display of the table view.
        """
        if info.initialized:
            self.model.edit_traits(parent=info.ui.control, kind="livemodal")


    def display_pf_report(self, info):
        """ Handles display of the power flow report view.
        """
        if info.initialized:
            report = NetworkReport(self.model)
            report.edit_traits(view=pf_report_view, parent=info.ui.control,
                                   kind="livemodal")
            del report


    def display_opf_report(self, info):
        """ Handles display of the OPF report view.
        """
        if info.initialized:
            report = NetworkReport(self.model)
            report.edit_traits(view=opf_report_view,
                                   parent=info.ui.control, kind="livemodal")
            del report

    #--------------------------------------------------------------------------
    #  Network action handlers:
    #--------------------------------------------------------------------------

    def add_bus(self, info):
        """ Handles adding a bus to the network.
        """
        if info.initialized:
            # Provide the new bus with a name unique to the network.
            bus_names = [v.name for v in self.model.buses]
            bus = Bus( name = make_unique_name("v", bus_names) )
            self.model.buses.append(bus)
#            retval = bus.edit_traits(parent=info.ui.control, kind="livemodal")
#            if not retval.result:
#                n.buses.remove(bus)


    def add_branch(self, info):
        """ Handles adding a branch to the network.
        """
        if not info.initialized:
            return

        network = self.model

        if len(network.buses) < 2:
            print "For branch addition two or more buses are requisite."
        else:
            branch_names = [e.name for e in network.branches]
            name = make_unique_name("e", branch_names)

            branch = Branch(name=name, source_bus = network.buses[0],
                                       target_bus = network.buses[1],
                                       buses      = network.buses)
            network.branches.append(branch)

            retval = branch.edit_traits(parent=info.ui.control,
                                        kind="livemodal")
            if not retval.result:
                network.branches.remove(branch)

    #--------------------------------------------------------------------------
    #  Routine action handlers:
    #--------------------------------------------------------------------------

    def dcpf(self, info):
        """ Runs the model using a DC Power Flow routine.
        """
        view_model = DCPFViewModel(network=self.model)
        retval = view_model.edit_traits(parent=info.ui.control,
                                        kind="livemodal")

        if retval.result:
            self.display_pf_report(info)

        del view_model


    def dcopf(self, info):
        """ Runs the model using a DC OPF routine.
        """
        view_model = DCOPFViewModel(network=self.model)
        view_model.solve()
        retval = view_model.edit_traits(parent=info.ui.control,
                                        kind="livemodal")

        if retval.result:
            self.display_opf_report(info)

        del view_model


    def acpf(self, info):
        """ Runs the model using a AC Power Flow routine.
        """
        view_model = ACPFViewModel(network=self.model)
        retval = view_model.edit_traits(parent=info.ui.control,
                                        kind="livemodal")

        if retval.result:
            self.display_pf_report(info)

        del view_model


    def acopf(self, info):
        """ Runs the model using a AC OPF routine.
        """
        view_model = ACOPFViewModel(network=self.model)
        view_model.solve()
        retval = view_model.edit_traits(parent=info.ui.control,
                                        kind="livemodal")

        if retval.result:
            self.display_opf_report(info)

        del view_model

#------------------------------------------------------------------------------
#  Stand-alone call:
#------------------------------------------------------------------------------

if __name__ == "__main__":
    import sys
    logger = logging.getLogger()
    logger.addHandler(logging.StreamHandler(sys.stdout))
    logger.setLevel(logging.DEBUG)

    view_model = NetworkViewModel(model=Network())
    view_model.configure_traits()

# EOF -------------------------------------------------------------------------
