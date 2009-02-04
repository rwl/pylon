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
from os.path import join, dirname, expanduser
import logging
import pickle

from enthought.traits.api import \
    HasTraits, Instance, File, Bool, Str, List, on_trait_change, \
    Float, Tuple, Property

from enthought.traits.ui.api import \
    View, Handler, UIInfo, Group, Item, TableEditor, InstanceEditor, \
    Label, Tabbed, HGroup, VGroup, ModelView, FileEditor, StatusItem, \
    spring

from enthought.traits.ui.menu import NoButtons, OKCancelButtons, Separator
from enthought.pyface.api import error, confirm
from enthought.pyface.image_resource import ImageResource
from enthought.naming.unique_name import make_unique_name
from enthought.logger.api import add_log_queue_handler
from enthought.logger.log_queue_handler import LogQueueHandler

#------------------------------------------------------------------------------
#  Local imports:
#------------------------------------------------------------------------------

from godot.api import Graph, Cluster, Node, Edge, DotParser, Subgraph
from godot.graph_menu import menubar, toolbar
from graph_view import nodes_view, edges_view, attr_view, about_view
from godot.graph_tree import graph_tree_editor

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

    # File path to to use for loading/saving/importing/exporting.
    file = File(filter=["Dot Files (*.dot)|*.dot|All Files (*.*)|*.*|"])

    # Is the tree view of the network displayed?
    show_tree = Bool(True, desc="that the network tree view is visible")

    # All graphs, subgraphs and clusters.
    all_graphs = Property(List(Instance(HasTraits)))

    # Working graph instance.
    selected_graph = Instance(HasTraits)

    #--------------------------------------------------------------------------
    #  Views:
    #--------------------------------------------------------------------------

    # Default model view.
    traits_view = View(
        HGroup(
            Item(
                name="model", editor=graph_tree_editor,
                show_label=False, id=".tree_editor",
                visible_when="show_tree==True", width=.1
            ),
            Item("model", show_label=False),
        ),
        id="graph_view_model.graph_view", title="GODOT", icon=frame_icon,
        resizable=True, style="custom", width=.81, height=.81, kind="live",
        buttons=NoButtons, menubar=menubar,
#        toolbar=toolbar,
        dock="vertical",
#        statusbar=[StatusItem(name="status", width=0.5),
#            StatusItem(name="versions", width=200)]
    )

    # File selection view.
    file_view = View(
        Item(name="file", id="file"),#, editor=FileEditor(entries=6)),
        id="graph_view_model.file_view", title="Select a file",
        icon=frame_icon, resizable=True, width=.3, kind="livemodal",
        buttons=OKCancelButtons
    )

    # Graph selection view.
    all_graphs_view = View(
        Item(name   = "selected_graph",
             editor = InstanceEditor( name     = "all_graphs",
                                      editable = False),
             label  = "Graph"),
        icon = frame_icon, kind = "livemodal", title = "Select a graph",
        buttons = OKCancelButtons
    )

    #--------------------------------------------------------------------------
    #  Trait intialisers:
    #--------------------------------------------------------------------------

    def _selected_graph_default(self):
        """ Trait intialiser.
        """
        return self.model

    #--------------------------------------------------------------------------
    #  Property getters:
    #--------------------------------------------------------------------------

    def _get_all_graphs(self):
        """ Property getter. """

        top_graph = self.model

        def get_subgraphs(graph):
            subgraphs = graph.subgraphs[:]
            for subgraph in graph.subgraphs:
                subsubgraphs = get_subgraphs(subgraph)
                subgraphs.extend(subsubgraphs)
            return subgraphs

        subgraphs = get_subgraphs(top_graph)
        return [top_graph] + subgraphs

    #--------------------------------------------------------------------------
    #  Action handlers:
    #--------------------------------------------------------------------------

    def new_model(self, info):
        """ Handles the new Graph action. """

        if info.initialized:
            self.model = Graph()


    def open_file(self, info):
        """ Handles the open action. """

        if not info.initialized: return # Escape.

        retval = self.edit_traits(parent=info.ui.control, view="file_view")

        if retval.result:
            fd = None
            try:
                fd = open(self.file, "rb")
                parser = DotParser()
                self.model = parser.parse_dot_data(self.file)
#            except:
#                error(parent=info.ui.control, title="Load Error",
#                    message="An error was encountered when loading\nfrom %s"
#                    % self.file)
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
                fd.write(str(self.model))
#            except:
#                error(
#                    parent=info.ui.control, title="Save Error",
#                    message="An error was encountered when saving\nto %s"
#                    % self.file
#                )
            finally:
                if fd is not None:
                    fd.close()


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

        if not info.initialized: return

        graph = self.model
        IDs = [v.ID for v in graph.nodes]
        node = Node(ID=make_unique_name("node", IDs))
        graph.nodes.append(node)
        retval = node.edit_traits(parent=info.ui.control, kind="livemodal")
        if not retval.result:
            graph.nodes.remove(node)


    def add_edge(self, info):
        """ Handles adding an Edge to the graph. """

        if not info.initialized: return

        graph = self.model
        n_nodes = len(graph.nodes)
        IDs = [v.ID for v in graph.nodes]

        if n_nodes == 0:
            from_node = Node(ID=make_unique_name("node", IDs))
            to_node = Node(ID=make_unique_name("node", IDs))
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

        if len(self.all_graphs) > 1:
            retval = self.edit_traits(parent = info.ui.control,
                                      view   = "all_graphs_view")
            if not retval.result:
                return

            graph = self.selected_graph
        else:
            graph = self.model

        subgraph = Subgraph()#root=graph, parent=graph)
        retval = subgraph.edit_traits(parent=info.ui.control, kind="livemodal")
        if retval.result:
            graph.subgraphs.append(subgraph)


    def add_cluster(self, info):
        """ Handles adding a Cluster to the main graph. """

        if not info.initialized: return

        graph = self.model
        cluster = Cluster()#root=graph, parent=graph)
        retval = cluster.edit_traits(parent=info.ui.control, kind="livemodal")
        if retval.result:
            graph.clusters.append(cluster)

#------------------------------------------------------------------------------
#  Stand-alone call:
#------------------------------------------------------------------------------

if __name__ == "__main__":
    import sys
    logger = logging.getLogger()
    logger.addHandler(logging.StreamHandler(sys.stdout))
    logger.setLevel(logging.DEBUG)

    graph = Graph(ID="Main Graph")
    sg1 = Subgraph(ID="SG1")
    graph.subgraphs.append(sg1)
    sg2 = Subgraph(ID="SG2")
    sg1.subgraphs.append(sg2)

    view_model = GraphViewModel(model=graph)
    view_model.configure_traits()

# EOF -------------------------------------------------------------------------
