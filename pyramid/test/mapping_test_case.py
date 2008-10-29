#------------------------------------------------------------------------------
# Copyright (C) 2008 Richard W. Lincoln
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

""" Tests for mapping objects to a diagram """

#------------------------------------------------------------------------------
#  Imports:
#------------------------------------------------------------------------------

from unittest import TestCase

from enthought.traits.api import HasTraits, ListInstance, Str, Instance
from enthought.enable.tools.api import MoveTool

from pyramid.mapping import Mapping, CanvasMapping, NodeMapping
from pyramid.element_tool import ElementTool
from pyramid.component.node import DiagramNode

from godot.node import DotGraphNode

#------------------------------------------------------------------------------
#  Constants:
#------------------------------------------------------------------------------

NODE_SHAPE = "rectangle"
OTHER_NODE_SHAPE = "circle"

#------------------------------------------------------------------------------
#  "DomainModel" class:
#------------------------------------------------------------------------------

class DomainNode(HasTraits):
    name = Str("node")
    
class OtherNode(HasTraits):
    name = Str("other")

class DomainEdge(HasTraits):
    source = Instance(DomainNode)
    target = Instance(DomainNode)

class DomainModel(HasTraits):
    nodes = ListInstance(DomainNode)
    edges = ListInstance(DomainEdge)
    other_nodes = ListInstance(OtherNode)

#------------------------------------------------------------------------------
#  "MappingTestCase" class:
#------------------------------------------------------------------------------

class MappingTestCase(TestCase):
    """ Tests for object mappings """

    mapping = Instance(Mapping)

    model = Instance(DomainModel)

    #--------------------------------------------------------------------------
    #  "TestCase" interface
    #--------------------------------------------------------------------------

    def setUp(self):
        """ Prepares the test fixture before each test method is called. """

        self.mapping = Mapping(
            nodes=[
                NodeMapping(
                    containment_trait="nodes", element=DomainNode,
                    dot_node=DotGraphNode(shape=NODE_SHAPE),
                    tools=[MoveTool, ElementTool]
                ),
                NodeMapping(
                    containment_trait="other_nodes", element=OtherNode,
                    dot_node=DotGraphNode(shape=OTHER_NODE_SHAPE),
                    tools=[MoveTool, ElementTool]
                )
            ]
        )

        node1 = DomainNode(name="node1")
        node2 = DomainNode(name="node2")

        self.model = DomainModel(
            nodes=[node1, node2],
            edges=[DomainEdge(source=node1, target=node2)]
        )

        return


    def tearDown(self):
        """ Called immediately after each test method has been called. """

        return

    #--------------------------------------------------------------------------
    #  Tests
    #--------------------------------------------------------------------------

    def test_model_map(self):
        """ Mapping a model """

        # Set the domain model for the diagram
        diagram = self.mapping.diagram
        diagram.domain_model = self.model

        # Check the number of components on the canvas
        components = diagram.components
        self.assertEqual(len(components), 2)

        for component in components:
            # Diagram components must be associated with a domain element
            element = component.element
            self.assertTrue(element is not None)

            if isinstance(component, DiagramNode):
                # Diagram nodes must be associated with a dot node
                dot_node = component.dot_node
                self.assertTrue(dot_node is not None)

                # The name for the dot node should be the id of the element
                self.assertEqual(dot_node.get_name(), str(id(element)))

                # Check that the node style attributes have been set
                self.assertEqual(dot_node.get_shape(), NODE_SHAPE)

# EOF -------------------------------------------------------------------------
