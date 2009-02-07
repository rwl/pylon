#------------------------------------------------------------------------------
#  Copyright (c) 2008 Richard W. Lincoln
#
#  Permission is hereby granted, free of charge, to any person obtaining a copy
#  of this software and associated documentation files (the "Software"), to
#  deal in the Software without restriction, including without limitation the
#  rights to use, copy, modify, merge, publish, distribute, sublicense, and/or
#  sell copies of the Software, and to permit persons to whom the Software is
#  furnished to do so, subject to the following conditions:
#
#  The above copyright notice and this permission notice shall be included in
#  all copies or substantial portions of the Software.
#
#  THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
#  IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
#  FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
#  AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
#  LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING
#  FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS
#  IN THE SOFTWARE.
#------------------------------------------------------------------------------

""" Defines a view model for Graphs. """

#------------------------------------------------------------------------------
#  Imports:
#------------------------------------------------------------------------------

import sys
from os.path import join, dirname, expanduser, isfile
import logging
import pickle

from enthought.traits.api import \
    HasTraits, Instance, File, Bool, Str, List, on_trait_change, \
    Float, Tuple, Property, Delegate, Code, Button

from enthought.traits.ui.api import \
    View, Handler, UIInfo, Group, Item, TableEditor, InstanceEditor, \
    Label, Tabbed, HGroup, VGroup, ModelView, FileEditor, StatusItem, \
    spring, TextEditor

from enthought.traits.ui.menu import NoButtons, OKCancelButtons, Separator
from enthought.pyface.api import error, confirm, YES, FileDialog, OK
from enthought.pyface.image_resource import ImageResource
from enthought.naming.unique_name import make_unique_name
from enthought.logger.api import add_log_queue_handler
from enthought.logger.log_queue_handler import LogQueueHandler

#------------------------------------------------------------------------------
#  Local imports:
#------------------------------------------------------------------------------

from godot.base_graph import BaseGraph
from godot.api import Graph, Cluster, Node, Edge, DotParser, Subgraph
from godot.graph_menu import menubar, toolbar
from graph_view import nodes_view, edges_view, attr_view, about_view
from godot.graph_tree import graph_tree_editor
from godot.dot_writer import write_dot_graph

#------------------------------------------------------------------------------
#  Constants:
#------------------------------------------------------------------------------

frame_icon = ImageResource("dot.ico")

#------------------------------------------------------------------------------
#  "GraphViewModel" class:
#------------------------------------------------------------------------------

class GraphViewModel(ModelView):
    """ Defines a view model for Graphs.  """

    #--------------------------------------------------------------------------
    #  Trait definitions:
    #--------------------------------------------------------------------------

    # File path to to use for saving.
    save_file = File

    # Is the tree view of the network displayed?
    show_tree = Bool(True, desc="that the network tree view is visible")

    # All graphs, subgraphs and clusters.
#    all_graphs = Property(List(Instance(HasTraits)))
    all_graphs = Delegate("model")

    # Select graph when adding to the graph?
    select_graph = Bool(True)

    # Working graph instance.
    selected_graph = Instance(BaseGraph, allow_none=False)

    # Exit confirmation.
    prompt_on_exit = Bool(False, desc="exit confirmation request")

    # Representation of the graph in the Dot language.
    dot_code = Code

    # Parse the dot_code and replace the existing model.
    parse_dot_code = Button("Parse", desc="dot code parsing action that "
        "replaces the existing model.")

    #--------------------------------------------------------------------------
    #  Views:
    #--------------------------------------------------------------------------

    # Default model view.
    traits_view = View(
        HGroup(
            Item(
                name="model", editor=graph_tree_editor,
                show_label=False, id=".tree_editor",
                visible_when="show_tree==True", width=.14
            ),
            Item("model", show_label=False),
        ),
        id="graph_view_model.graph_view", title="Godot", icon=frame_icon,
        resizable=True, style="custom", width=.81, height=.81, kind="live",
        buttons=NoButtons, menubar=menubar,
#        toolbar=toolbar,
        dock="vertical",
#        statusbar=[StatusItem(name="status", width=0.5),
#            StatusItem(name="versions", width=200)]
    )

    # File selection view.
#    file_view = View(
#        Item(name="file", id="file"),#, editor=FileEditor(entries=6)),
#        id="graph_view_model.file_view", title="Select a file",
#        icon=frame_icon, resizable=True, width=.3, kind="livemodal",
#        buttons=OKCancelButtons
#    )

    # Graph selection view.
    all_graphs_view = View(
        Item(name   = "selected_graph",
             editor = InstanceEditor( name     = "all_graphs",
                                      editable = False),
             label  = "Graph"),
        Item("select_graph", label="Always ask?"),
        icon = frame_icon, kind = "livemodal", title = "Select a graph",
        buttons = OKCancelButtons, close_result = False
    )

    # Model view options view.
    options_view = View(
        Item("prompt_on_exit"),
        "_",
        Item("select_graph"),
        Item("selected_graph",
             enabled_when = "not select_graph",
             editor       = InstanceEditor( name     = "all_graphs",
                                            editable = False ),
             label        = "Graph" ),
        icon = frame_icon, kind = "livemodal", title = "Options",
        buttons = OKCancelButtons, close_result = True
    )

    # Text representation of the graph viewed in a text editor
    dot_code_view = View(
        Item("dot_code", show_label=False, style="custom"),
        Item("parse_dot_code", show_label=False),
        id="godot.view_model.dot_code",
        icon = frame_icon, kind = "livemodal",
        title = "Dot Code", resizable = True,
        buttons = [], height = .3, width = .3
    )

    #--------------------------------------------------------------------------
    #  Trait intialisers:
    #--------------------------------------------------------------------------

    def _selected_graph_default(self):
        """ Trait intialiser.
        """
        return self.model


    def _parse_dot_code_fired(self):
        """ Parses the dot_code string and replaces the existing model.
        """
        parser = DotParser()
        graph  = parser.parse_dot_data(self.dot_code)
        if graph is not None:
            self.model = graph

    #--------------------------------------------------------------------------
    #  Event handlers:
    #--------------------------------------------------------------------------

    def _model_changed(self, old, new):
        """ Handles the model changing.
        """
        self.selected_graph = new

    #--------------------------------------------------------------------------
    #  Action handlers:
    #--------------------------------------------------------------------------

    def new_model(self, info):
        """ Handles the new Graph action. """

        if info.initialized:
            retval = confirm(parent  = info.ui.control,
                             message = "Replace existing graph?",
                             title   = "New Graph",
                             default = YES)
            if retval == YES:
                self.model = Graph()


    def open_file(self, info):
        """ Handles the open action. """

        if not info.initialized: return # Escape.

#        retval = self.edit_traits(parent=info.ui.control, view="file_view")

        dlg = FileDialog( action = "open",
            wildcard = "Graphviz Files (*.dot, *.xdot, *.txt)|"
                "*.dot, *.xdot, *.txt|Dot Files (*.dot)|*.dot|"
                "All Files (*.*)|*.*|")

        if dlg.open() == OK:
            parser = DotParser()
            self.model = parser.parse_dot_file(dlg.path)

            self.save_file = dlg.path

        del dlg

#            fd = None
#            try:
#                fd = open(self.file, "rb")
#                parser = DotParser()
#                self.model = parser.parse_dot_file(self.file)
##            except:
##                error(parent=info.ui.control, title="Load Error",
##                    message="An error was encountered when loading\nfrom %s"
##                    % self.file)
#            finally:
#                if fd is not None:
#                    fd.close()


    def save(self, info):
        """ Handles saving the current model to the last file.
        """
        save_file = self.save_file

        if not isfile(save_file):
            self.save_as(info)
        else:
            fd = None
            try:
                fd = open(save_file, "wb")
                dot_code = write_dot_graph(self.model)
                fd.write(dot_code)
            finally:
                if fd is not None:
                    fd.close()


    def save_as(self, info):
        """ Handles saving the current model to file.
        """
        if not info.initialized:
            return

#        retval = self.edit_traits(parent=info.ui.control, view="file_view")

        dlg = FileDialog( action = "save as",
            wildcard = "Graphviz Files (*.dot, *.xdot, *.txt)|" \
                "*.dot, *.xdot, *.txt|Dot Files (*.dot)|*.dot|" \
                "All Files (*.*)|*.*|")

        if dlg.open() == OK:
            fd = None
            try:
                fd = open(dlg.path, "wb")
                dot_code = write_dot_graph(self.model)
                fd.write(dot_code)

                self.save_file = dlg.path

#            except:
#                error(
#                    parent=info.ui.control, title="Save Error",
#                    message="An error was encountered when saving\nto %s"
#                    % self.file
#                )
            finally:
                if fd is not None:
                    fd.close()

        del dlg


    def configure_graph(self, info):
        """ Handles display of the graph dot traits. """

        if info.initialized:
            self.model.edit_traits(parent=info.ui.control,
                kind="live", view=attr_view)


    def configure_nodes(self, info):
        """ Handles display of the nodes editor. """

        if info.initialized:
            self.model.edit_traits(parent=info.ui.control,
                kind="live", view=nodes_view)


    def configure_edges(self, info):
        """ Handles display of the edges editor. """

        if info.initialized:
            self.model.edit_traits(parent=info.ui.control,
                kind="live", view=edges_view)


    def about_godot(self, info):
        """ Handles displaying a view about Godot. """

        if info.initialized:
            self.edit_traits(parent=info.ui.control,
                kind="livemodal", view=about_view)


    def add_node(self, info):
        """ Handles adding a Node to the graph. """

        if not info.initialized:
            return

        graph = self._request_graph(info.ui.control)

        if graph is None:
            return

        IDs = [v.ID for v in graph.nodes]
        node = Node(ID=make_unique_name("node", IDs))
        graph.nodes.append(node)

        retval = node.edit_traits(parent=info.ui.control, kind="livemodal")

        if not retval.result:
            graph.nodes.remove(node)


    def add_edge(self, info):
        """ Handles adding an Edge to the graph. """

        if not info.initialized:
            return

        graph = self._request_graph(info.ui.control)

        if graph is None:
            return

        n_nodes = len(graph.nodes)
        IDs = [v.ID for v in graph.nodes]

        if n_nodes == 0:
            from_node = Node(ID=make_unique_name("node", IDs))
            to_node = Node(ID=make_unique_name("node", IDs + [from_node.ID]))
        elif n_nodes == 1:
            from_node = graph.nodes[0]
            to_node = Node(ID=make_unique_name("node", IDs))
        else:
            from_node = graph.nodes[0]
            to_node = graph.nodes[1]

        edge = Edge(from_node, to_node, _nodes=graph.nodes)

        retval = edge.edit_traits(parent=info.ui.control, kind="livemodal")

        if retval.result:
            graph.edges.append(edge)


    def add_subgraph(self, info):
        """ Handles adding a Subgraph to the main graph. """

        if not info.initialized:
            return

        graph = self._request_graph(info.ui.control)

        if graph is not None:
            subgraph = Subgraph()#root=graph, parent=graph)
            retval = subgraph.edit_traits(parent = info.ui.control,
                                          kind   = "livemodal")
            if retval.result:
                graph.subgraphs.append(subgraph)


    def add_cluster(self, info):
        """ Handles adding a Cluster to the main graph. """

        if not info.initialized:
            return

        graph = self._request_graph(info.ui.control)

        if graph is not None:
            cluster = Cluster()#root=graph, parent=graph)
            retval = cluster.edit_traits(parent = info.ui.control,
                                         kind   = "livemodal")
            if retval.result:
                graph.clusters.append(cluster)


    def _request_graph(self, parent=None):
        """ Displays a dialog for graph selection if more than one exists.
            Returns None if the dialog is canceled.
        """

        if (len(self.all_graphs) > 1) and (self.select_graph):
            retval = self.edit_traits(parent = parent,
                                      view   = "all_graphs_view")
            if not retval.result:
                return None

        if self.selected_graph is not None:
            return self.selected_graph
        else:
            return self.model


    def toggle_tree(self, info):
        """ Handles displaying the tree view """

        if info.initialized:
            self.show_tree = not self.show_tree


    def godot_options(self, info):
        """ Handles display of the options menu. """

        if info.initialized:
            self.edit_traits( parent = info.ui.control,
                              kind   = "livemodal",
                              view   = "options_view" )


    def configure_dot_code(self, info):
        """ Handles display of the dot code in a text editor.
        """
        if not info.initialized:
            return

        self.dot_code = write_dot_graph(self.model)
        retval = self.edit_traits( parent = info.ui.control,
                                   kind   = "livemodal",
                                   view   = "dot_code_view" )
#        if retval.result:
#            parser = DotParser()
#            graph  = parser.parse_dot_data(self.dot_code)
#            if graph is not None:
#                self.model = graph

    #---------------------------------------------------------------------------
    #  Handle the user attempting to exit Godot:
    #---------------------------------------------------------------------------

    def on_exit(self, info):
        """ Handles the user attempting to exit Godot.
        """
        if self.prompt_on_exit:# and (not is_ok):
            retval = confirm(parent  = info.ui.control,
                             message = "Exit Godot?",
                             title   = "Confirm exit",
                             default = YES)
            if retval == YES:
                self._on_close( info )
        else:
            self._on_close( info )

#------------------------------------------------------------------------------
#  Stand-alone call:
#------------------------------------------------------------------------------

if __name__ == "__main__":
    import sys
    logger = logging.getLogger()
    logger.addHandler(logging.StreamHandler(sys.stdout))
    logger.setLevel(logging.DEBUG)

    graph = Graph(ID="G")
    sg1 = Subgraph(ID="SG1")
    graph.subgraphs.append(sg1)
    sg2 = Subgraph(ID="SG2")
    sg1.subgraphs.append(sg2)

    n1 = Node(ID="N1")
    sg2.nodes = [n1]

    view_model = GraphViewModel(model=graph)
    view_model.configure_traits()

# EOF -------------------------------------------------------------------------
