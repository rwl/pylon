from enthought.traits.api import HasTraits, Instance, List, ListStr

from enthought.enable.api import Canvas

from pylon.ui.graph.component.node import DiagramNode

class CanvasMapping(HasTraits):

    # A list of the names of the traits of the domain model that correspond to
    # the nodes on the canvas.
    node_lists = ListStr

    diagram_canvas = Instance(Canvas)

    domain_model = Instance(HasTraits)

#    palette

#    node_mappings = List(Instance(NodeMapping))


class LabelMapping(HasTraits):

    diagram_label = Instance(HasTraits)

    node_mapping = Instance(HasTraits)


class NodeMapping(HasTraits):

    element = Instance(HasTraits, allow_none=False)

    diagram_node = Instance(DiagramNode, ())

    tool = Instance(HasTraits)

    label = Instance(LabelMapping)


class LinkMapping(HasTraits):

    element = Instance(HasTraits)

    diagram_link = Instance(HasTraits)

    tool = Instance(HasTraits)

    label = Instance(LabelMapping)


class Mapping(HasTraits):

    diagram = Instance(CanvasMapping)

    nodes = List(Instance(NodeMapping))

    links = List(Instance(LinkMapping))

    def _domain_model_changed_for_diagram(self, obj, name, old, new):
        """ Handles the domain model changing """

        node_mappings = []

        obj.diagram_canvas = Canvas()

        for label in obj.node_lists:
            elements = getattr(new, label)
            for element in elements:
                nm = NodeMapping(element=element)
                node_mappings.append(nm)

        self.nodes = node_mappings


    def _nodes_changed(self, new):
        """ Handles a new list of node mappings """

        for node_mapping in new:
            self.diagram.diagram_canvas.add(node_mapping.diagram_node)


if __name__ == "__main__":
    from pylon.dss.common.api import Circuit
    circuit = Circuit()
    lists = ["buses", "lines", "transformers", "generators", "loads", "faults",
             "voltage_sources", "current_sources", "shunt_capacitors",
             "cap_controls", "reg_controls"]
    diagram = CanvasMapping(domain_model=circuit, trait_names=lists)
    mapping = Mapping(diagram=diagram)

# EOF -------------------------------------------------------------------------
