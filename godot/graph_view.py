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

""" Defines a representation of a graph in Graphviz"s dot language """

#------------------------------------------------------------------------------
#  Imports:
#------------------------------------------------------------------------------

from enthought.traits.ui.api import View, Group, Item, Tabbed, Label
from enthought.pyface.image_resource import ImageResource
from enthought.enable.component_editor import ComponentEditor

from node import node_table_editor
from edge import edge_table_editor
#------------------------------------------------------------------------------
#  Images:
#------------------------------------------------------------------------------

frame_icon = ImageResource("dot")

#------------------------------------------------------------------------------
#  Items:
#------------------------------------------------------------------------------

view_port_item = Item(name="vp", editor=ComponentEditor(), show_label=False,
    id=".viewport")

nodes_item = Item(name="nodes", editor=node_table_editor, show_label=False)
edges_item = Item(name="edges", editor=edge_table_editor, show_label=False)

#------------------------------------------------------------------------------
#  Groups:
#------------------------------------------------------------------------------

# # TODO: For want of a better word.
appearance_group = Group(
    ["bgcolor", "colorscheme"],
    Group(
        ["charset", "fontcolor", "fontname", "fontnames", "fontpath",
         "fontsize"], label="Font", show_border=True
    ),
    Group(
        ["label", "labelloc", "labeljust", "lp", "nojustify"],
        label="Label", show_border=True
    ),
    Group(["layers", "layersep"], label="Layer", show_border=True),
    label="Appearance"
)

layout_group = Group(
    ["center", "dim", "normalize", "outputorder", "overlap", "pack",
     "packmode", "pad", "rankdir", "ranksep", "ratio", "root",
     "voro_margin"],
     label="Layout"
)

algorithm_group = Group(
    ["epsilon", "levelsgap", "maxiter", "mclimit", "mode",
     "model", "mosek", "nslimit", "nslimit1", "remincross",
     "searchsize"],
    label="Algorithm"
)

children_group = Group(
    Group(
        ["clusterrank", "compound"], label="Cluster",
        show_border=True
    ),
    Group(
        ["Damping", "defaultdist", "mindist", "nodesep", "quantum",
         "sep", "start"], label="Node", show_border=True
    ),
    Group(
        ["concentrate", "diredgeconstraints", "esep", "K",
         "ordering", "splines"], label="Edge", show_border=True
    ),
    label="Children"
)

output_group = Group(
    ["dpi", "landscape", "margin", "pagedir", "resolution",
     "rotate", "showboxes", "size", "stylesheet"],
    Group(
        ["comment", "target", "URL"], label="Misc",
        show_border=True
    ),
    label="Output"
)

#------------------------------------------------------------------------------
#  Views:
#------------------------------------------------------------------------------

graph_view = View(
    view_port_item, id="godot.graph",
    buttons=["OK", "Cancel", "Help"],
    resizable=True, icon=frame_icon
)

tabbed_view = View(
    Tabbed(
        Group(view_port_item, label="Graph"),
        Group(nodes_item, label="Nodes"),
        Group(edges_item, label="Edges"),
        appearance_group, layout_group,
        algorithm_group, children_group,
        output_group
    ), dock="tab",
    id="godot.graph.tabbed_view",
    buttons=["OK", "Cancel", "Help"],
    resizable=True, icon=frame_icon
)

nodes_view = View(nodes_item, title="Nodes", icon=frame_icon,
    buttons=["OK", "Cancel", "Undo"])
edges_view = View(edges_item, title="Edges", icon=frame_icon,
    buttons=["OK", "Cancel", "Undo"])

attr_view = View(
    Tabbed(appearance_group, layout_group, algorithm_group,
        children_group, output_group), dock="tab",
    id="godot.graph.attr_view", title="Dot Attributes",
    buttons=["OK", "Cancel", "Help"],
    resizable=True, icon=frame_icon
)

license_label = \
"""
Copyright (c) 2008 Richard W. Lincoln

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to
deal in the Software without restriction, including without limitation the
rights to use, copy, modify, merge, publish, distribute, sublicense, and/or
sell copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in
all copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING
FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS
IN THE SOFTWARE.

"""

contact_label = """
http://github.com/rwl/godot
"""

about_view = View(
    Group(Label(license_label), label="License"),
    Group(Label(contact_label), label="Contribute"),
#    Group(Label(credits_label), label="Credits"),
    title="About", buttons=["OK"],
    icon=frame_icon
)

# EOF -------------------------------------------------------------------------
