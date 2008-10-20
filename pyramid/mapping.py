from enthought.traits.api import HasTraits, Instance

from enthought.enable.api import Canvas

class CanvasMapping(HasTraits):

    diagram_canvas = Instance(Canvas)

    domain_model = Instance(HasTraits)

    palette


class LabelMapping(HasTraits):

    diagram_label = Instance

    node_mapping = Instance


class NodeMapping(HasTraits):

    element = Instance(HasTraits)

    diagram_node = Instance

    tool = Instance

    label = Instance(LabelMapping)


class LinkMapping(HasTraits):

    element = Instance(HasTraits)

    diagram_link = Instance

    tool = Instance

    label = Instance(LabelMapping)


class Mapping(HasTraits):

    diagram = Instance(CanvasMapping)

    nodes = List(Instance(NodeMapping))

    links = List(Instance(LinkMapping))