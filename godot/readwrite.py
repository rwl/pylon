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


""" Functions for reading and writing graphs.

References:
	python-graph by Pedro Matiello <pmatiello@gmail.com>
	pydot by Michael Krause, Ero Carrera

@sort: read_xml, write_xml, write_dot_graph, write_dot_digraph

"""

#------------------------------------------------------------------------------
#  Imports:
#------------------------------------------------------------------------------

from xml.dom.minidom import Document, parseString

#------------------------------------------------------------------------------
#  XML:
#------------------------------------------------------------------------------

def write_xml(graph):
	"""
	Return a string specifying the given graph as a XML document.

	@type  graph: graph
	@param graph: Graph.

	@rtype:  string
	@return: String specifying the graph as a XML document.

	"""

	# Document root
	grxml = Document()
	grxmlr = grxml.createElement('graph')
	grxml.appendChild(grxmlr)

	# Each node...
	for each_node in graph.nodes:
		node = grxml.createElement('node')
		node.setAttribute('id', each_node.name)
		grxmlr.appendChild(node)
		for each_attr in each_node.get_node_attributes():
			attr = grxml.createElement('attribute')
			attr.setAttribute('attr', each_attr[0])
			attr.setAttribute('value', each_attr[1])
			node.appendChild(attr)

	# Each edge...
	for each_edge in graph.edges():
		edge = grxml.createElement('edge')
		edge.setAttribute('from', str(each_edge.from_node))
		edge.setAttribute('to', str(each_edge.to_node))
#		edge.setAttribute('wt', str(each_edge.weight))
#		edge.setAttribute('label', str(each_edge.label))
		grxmlr.appendChild(edge)
		for attr_name, attr_value in each_edge.get_edge_attributes():
			attr = grxml.createElement('attribute')
			attr.setAttribute('attr', attr_name)
			attr.setAttribute('value', attr_value)
			edge.appendChild(attr)

	return grxml.toprettyxml()


def read_xml(graph, string):
	""" Read a graph from a XML document. Nodes and edges specified in the
	input will be added to the current graph.

	@type  graph: graph
	@param graph: Graph

	@type  string: string
	@param string: Input string in XML format specifying a graph.

	"""

	dom = parseString(string)

	# Read nodes...
	for each_node in dom.getElementsByTagName("node"):
		node = Node(name=each_node.getAttribute('id'))
		for each_attr in each_node.getElementsByTagName("attribute"):
			node.set_attr(
				each_attr.getAttribute('attr'), each_attr.getAttribute('value')
			)

	# Read edges...
	for each_edge in dom.getElementsByTagName("edge"):
		edge = Edge(
			from_node=each_edge.getAttribute('from'),
			to_node=each_edge.getAttribute('to')
		)
		for each_attr in each_edge.getElementsByTagName("attribute"):
			attr_tuple = (
				each_attr.getAttribute('attr'), each_attr.getAttribute('value')
			)
			if (attr_tuple not in each_edge.get_edge_attributes()):
				each_edge.set_attr(attr_tuple[0], attr_tuple[1])

#------------------------------------------------------------------------------
#  DOT Language:
#------------------------------------------------------------------------------

def _dot_node_str(graph, node):
	line = '\t"%s" [ ' % str(node)
	attrlist = node.get_node_attributes()
	for each in attrlist:
		attr = '%s="%s" ' % (each[0], each[1])
		line = line + attr
	line = line + ']\n'
	return line


def _dot_edge_str(graph, edge):
	line = '\t"%s" -- "%s" [ ' % (str(edge.from_node), str(edge.to_node))
	attrlist = edge.get_edge_attributes()
	for each in attrlist:
		attr = '%s="%s" ' % (each[0], each[1])
		line = line + attr
	line = line + ']\n'
	return line


def _dot_arrow_str(graph, edge):
	line = '\t"%s" -> "%s" [ ' % (str(u), str(v))
	attrlist = edge.get_edge_attributes()
	for each in attrlist:
		attr = '%s="%s" ' % (each[0], each[1])
		line = line + attr
	line = line + ']\n'
	return line


def write_dot_graph(graph):
	""" Return a string specifying the given graph in DOT Language.

	@type  graph: graph
	@param graph: Graph.

	@rtype:  string
	@return: String specifying the graph in DOT Language.

	"""

	doc = 'graph graphname \n{\n'
	for node in graph.nodes:
		doc = doc + _dot_node_str(graph, node)
		for edge in graph.edges:
			doc = doc + _dot_edge_str(graph, node, edge)
	doc = doc + '}'
	return doc


def write_dot_digraph(graph):
	""" Return a string specifying the given digraph in DOT Language.

	@type  graph: graph
	@param graph: Graph.

	@rtype:  string
	@return: String specifying the graph in DOT Language.

	"""

	doc = 'digraph graphname \n{\n'
	for node in graph.nodes:
		doc = doc + _dot_node_str(graph, node)
		for edge in graph.edges:
			doc = doc + _dot_arrow_str(graph, node, edge)
	doc = doc + '}'
	return doc


def read_dot_graph(doc, graph=None):
	""" Read a graph from a DOT file. Nodes and edges specified in the
	input will be added to a given graph.  Otherwise, a new graph will
	be returned.

	@type  string: string
	@param string: Input string in DOT format specifying a graph.

	@type  graph: graph
	@param graph: Graph

	@rtype: Graph
	@return: A graph of the nodes and edges specified in the input.

	"""

# EOF -------------------------------------------------------------------------
