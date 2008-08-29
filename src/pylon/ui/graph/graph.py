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

""" Interactive graph of a pylon network """

#------------------------------------------------------------------------------
#  Imports:
#------------------------------------------------------------------------------

from os.path import join, dirname

from enthought.traits.api import HasTraits, Instance, Property, Enum
from enthought.traits.ui.api import View, Group, Item
from enthought.pyface.image_resource import ImageResource

from enthought.enable.api import \
    Window, Viewport, Scrolled, Canvas, Container, Component

from enthought.enable.tools.api import ViewportPanTool
from enthought.enable.component_editor import ComponentEditor

from pylon.api import Network
from pylon.ui.graph.network_dot import NetworkDot
from pylon.ui.graph.pydot.pydot import Dot, graph_from_dot_data

from xdot_parser import XDotParser

from graph_editor import GraphEditor

#-----------------------------------------------------------------------------
#  Constants:
#-----------------------------------------------------------------------------

ICON_LOCATION = join(dirname(__file__), "../images")

frame_icon = ImageResource(join(ICON_LOCATION, "frame.ico"))

#------------------------------------------------------------------------------
#  "Graph" class:
#------------------------------------------------------------------------------

class Graph(HasTraits):
    """ Interactive graph of a Pylon network """

    #--------------------------------------------------------------------------
    #  Trait definitions:
    #--------------------------------------------------------------------------

    network = Instance(
        Network,
#        allow_none=False,
        desc="the network being graphed"
    )

    # Graphviz dot representation of the Network
    network_dot = Instance(
        NetworkDot, NetworkDot(),
        allow_none=False,
        desc="dot representation of the network"
    )

    # An XDot representation of the network.  XDot is an extended version of
    # the dot format with drawing information taken from the output of the
    # Graphviz layout program.
    xdot = Property(
        Instance(Dot),
        depends_on=["network_dot.updated", "program"],
        desc="xdot representation with additional layout information"
    )

    # Graphviz layout program
    program = Enum(
        "dot", "circo", "fdp", "neato", "twopi",
        desc="graph layout engine"
    )

    # Parser of XDot code
    parser = Instance(
        XDotParser, XDotParser(),
        desc=" the parser of xdot code that returns or populates a container"
    )

#    container = Property(
#        Instance(Container),
#        depends_on=["xdot"],
#        desc="container of network components"
#    )

    # The canvas on which the network graph is drawn
    canvas = Instance(
        Canvas, Canvas(bgcolor="lightsteelblue"),#, draw_axes=True),
        desc="the canvas on to which network components are drawn"
    )

    # A view into a sub-region of the canvas
    viewport = Instance(
        Viewport, desc="a view into a sub-region of the canvas"
    )

    #--------------------------------------------------------------------------
    #  Views:
    #--------------------------------------------------------------------------

    config = View(
        Item(name="program"),
        Item(name="network_dot", style="custom", show_label=False),
        title="Configuration",
        icon=frame_icon,
        buttons=["OK"],
        close_result=True
    )

    traits_view=View(
#        Item(name="program", show_label=False),
#        Item(name="network_dot", style="custom", show_label=False),
        Item(
            name="viewport", editor=ComponentEditor(),
            show_label=False, id='.graph_container'
        ),
        id="pylon.ui.graph.graph.view",
        resizable=True,
        width=.4, height=.4
    )

    #--------------------------------------------------------------------------
    #  "Graph" interface:
    #--------------------------------------------------------------------------

    def _viewport_default(self):
        """ Trait initialiser """

        vp = Viewport(component=self.canvas, enable_zoom=True)
        vp.view_position = [0,0]
        vp.tools.append(ViewportPanTool(vp))
        return vp


    def _network_changed(self, new):
        """ Handle the network changing """

        if self.network_dot is not None:
            self.network_dot.network = new


    def _get_xdot(self):
        """ Property getter that is called when the network dot is
        updated or a new layout program is selected.

        """

        code = self.network_dot.dot.create(self.program, "xdot")
        return graph_from_dot_data(code)


    def _xdot_changed(self, new):
        """ Removes all components from the canvas and gets the
        xdot parser to repopulate it.

        """

        # Empty the canvas of components
#        print "COMPONENTS (START)", self.canvas.components
#        for component in self.canvas.components:
#            self.canvas.remove(component)
#
#        print "COMPONENTS (MIDDLE)", self.canvas.components
#        for component in self.canvas.components:
#            self.canvas.remove(component)
#
#        print "COMPONENTS (END)", self.canvas.components

#        self.parser.parse(new, self.canvas)
        self.canvas = canvas = self.parser.parse(new)
        canvas.bgcolor="lightsteelblue"
        self.viewport.component = canvas

#        from enthought.enable.primitives.api import Box
#        box = Box(color="red", bounds=[50, 50], position=self.pos, resizable="")
#        self.canvas.add(box)
#        self.pos[0] += 50
#        self.pos[1] += 50

        self.viewport.request_redraw()

#------------------------------------------------------------------------------
#  Standalone call:
#------------------------------------------------------------------------------

if __name__ == "__main__":
    from pylon.api import Network, Bus, Branch
    import sys
    import logging
    logger = logging.getLogger()
    logger.addHandler(logging.StreamHandler(sys.stdout))
    logger.setLevel(logging.DEBUG)

    from pylon.api import Network, Bus, Branch
    n = Network()
    v1 = Bus(name="v_1")
    v2 = Bus(name="v_2")
    v3 = Bus(name="v_3")
    e1 = Branch(network=n, source_bus=v1, target_bus=v2, name="e_1")
    e2 = Branch(network=n, source_bus=v1, target_bus=v3, name="e_2")
    e3 = Branch(network=n, source_bus=v2, target_bus=v3, name="e_3")
    n.buses=[v1, v2, v3]
    n.branches=[e1, e2, e3]

    graph = Graph(network=n)
    graph.configure_traits()

# EOF -------------------------------------------------------------------------
