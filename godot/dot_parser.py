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

""" Defines a Graphviz dot language parser.

The parser parses graphviz files dot code and files and transforms them
into a class representation defined by Godot.

References:
    Michael Krause, Ero Carrera, "pydot"

"""

#------------------------------------------------------------------------------
#  Imports:
#------------------------------------------------------------------------------

from pyparsing import __version__ as pyparsing_version

from pyparsing import \
    Literal, CaselessLiteral, Word, Upcase, OneOrMore, ZeroOrMore, Forward, \
    NotAny, delimitedList, oneOf, Group, Optional, Combine, alphas, nums, \
    restOfLine, cStyleComment, nums, alphanums, printables, empty, \
    quotedString, ParseException, ParseResults, CharsNotIn, _noncomma, \
    dblQuotedString, QuotedString, ParserElement, Suppress, Regex, \
    removeQuotes, nestedExpr, Suppress, Or

from parsing_util import \
    colon, lbrace, rbrace, lbrack, rbrack, lparen, rparen, equals, comma, \
    dot, slash, bslash, star, semi, at, minus, pluss, double_quoted_string, \
    quoted_string, nsplit, windows, graph_attr, node_attr#, edge_attr, all_attr

from godot.graph import Graph
from godot.node import Node
from godot.edge import Edge

#------------------------------------------------------------------------------
#  "DotParser" class:
#------------------------------------------------------------------------------

class DotParser:
    """ Defines a Graphviz dot language parser. """

    parser = None

    graph = None

    #--------------------------------------------------------------------------
    #  "object" interface:
    #--------------------------------------------------------------------------

    def __init__(self):
        self.parser = self.define_parser()

    #--------------------------------------------------------------------------
    #  Public interface:
    #--------------------------------------------------------------------------

    def parse_dot_data(self, data):
        """ Parses dot data and returns a godot.Graph instance. """

        parser = self.parser

        if pyparsing_version >= "1.2":
            parser.parseWithTabs()

        self.graph = Graph()

        tokens = parser.parseString(data)

        print "TOKENS:", tokens

        return self.graph

    #--------------------------------------------------------------------------
    #  Define the dot parser
    #--------------------------------------------------------------------------

    def define_parser(self):
        """ Defines dot grammar.

        @see: http://www.graphviz.org/doc/info/lang.html """

        # keywords
        strict_ = CaselessLiteral("strict").setResultsName("strict")
        graph_ = CaselessLiteral("graph").setResultsName("directed")
        digraph_ = CaselessLiteral("digraph").setResultsName("directed")
        subgraph_ = CaselessLiteral("subgraph").setResultsName("subgraph")
        node_ = CaselessLiteral("node").setResultsName("node")
        edge_ = CaselessLiteral("edge").setResultsName("edge")

#        graph_.setParseAction(self._push_digraph)

        # token definitions
        identifier = Word(alphanums + "_").setName("identifier")

        alphastring_ = OneOrMore(CharsNotIn(_noncomma))

        def parse_html(s, loc, toks):
            return "<<%s>>" % "".join(toks[0])

        opener = "<"
        closer = ">"
        try:
            html_text = nestedExpr(
                opener, closer,
                CharsNotIn(opener + closer).setParseAction(lambda t:t[0])
            ).setParseAction(parse_html)
        except:
            log.debug("nestedExpr not available.")
            log.warning(
                "Old version of pyparsing detected. Version 1.4.8 or "
                "later is recommended. Parsing of html labels may not "
                "work properly."
            )
            html_text = Combine(Literal("<<") + OneOrMore(CharsNotIn(",]")))

        ID = (
            identifier | html_text | quoted_string | alphastring_
        ).setName("ID")

        # Portnames (node1:port1 -> node2:port5:nw;)
        port_angle = (at + ID).setName("port_angle")

        port_location = (
            (OneOrMore(Group(colon + ID)) |
            Group(colon + lparen + ID + comma + ID + rparen))
        ).setName("port_location")

        port = Combine(
            (Group(port_location + Optional(port_angle)) |
            Group(port_angle + Optional(port_location)))
        ).setName("port")

        node_id = ID + Optional(port)

        # Attribute lists.
        a_list = OneOrMore(
            Or([(CaselessLiteral(attr.resultsName) +
                Optional(equals.suppress() + attr, True) +
                Optional(comma.suppress())) for attr in node_attr])
        ).setName("a_list")

        attr_list = OneOrMore(
            lbrack.suppress() + Optional(a_list) + rbrack.suppress()
        ).setName("attr_list").setResultsName("attrlist")

        attr_stmt = ((graph_ | node_ | edge_) + attr_list).setName("attr_stmt")

        # Graph statement.
        stmt_list = Forward()
        graph_stmt = (
            lbrace + Optional(stmt_list) + rbrace + Optional(semi.suppress())
        ).setName("graph_stmt")

        # Edge statement.
        edgeop = Suppress((Literal("--") | Literal("->"))).setName("edgeop")
        edge_point = Forward() # (node_id | subgraph)
        edgeRHS = OneOrMore(edgeop + edge_point)
        edge_stmt = edge_point + edgeRHS + Optional(attr_list)

        subgraph = (
            Optional(subgraph_, "") + Optional(ID, "") + Group(graph_stmt)
        ).setName("subgraph").setResultsName("ssubgraph")

        edge_point << (subgraph | graph_stmt | node_id )

        # Node statement.
        node_stmt = (
            node_id + Optional(attr_list) + Optional(semi.suppress())
        ).setName("node_stmt")

        # Graph attribute assignment.
        assignment = (
            Or([(CaselessLiteral(attr.resultsName) + Suppress(equals) + attr) \
                for attr in graph_attr])
        ).setName("assignment")

        stmt = (
            assignment | edge_stmt | attr_stmt | subgraph | graph_stmt |
            node_stmt
        ).setName("stmt")

        stmt_list << OneOrMore(stmt + Optional(semi.suppress()))

        # A strict graph is an unweighted, undirected graph containing no
        # graph loops or multiple edges.
        strict = Optional(strict_, "notstrict").setResultsName("strict")
        # Do edges have direction?
        directed = ((graph_ | digraph_))
        # Optional graph identifier.
        graph_id = Optional(ID, "").setResultsName("graph_id")

        # Parser for graphs defined in the DOT language.
        graphparser = (
            strict + directed + graph_id +
            lbrace + Group(Optional(stmt_list)) + rbrace
        ).setResultsName("graph")

        # Ignore comments.
        singleLineComment = Group("//" + restOfLine) | Group("#" + restOfLine)
        graphparser.ignore(singleLineComment)
        graphparser.ignore(cStyleComment)

        # Actions
        node_id.setParseAction(self.push_node_id)
        assignment.setParseAction(self.push_attr_assignment)
        a_list.setParseAction(self.push_attr_list)
        edge_stmt.setParseAction(self.push_edge_stmt)
        node_stmt.setParseAction(self.push_node_stmt)
        attr_stmt.setParseAction(self.push_default_attr_stmt)
        attr_list.setParseAction(self.push_attr_list_combine)
        subgraph.setParseAction(self.push_subgraph_stmt)
        #graph_stmt.setParseAction(self.push_graph_stmt)

        strict.setParseAction(self._push_strict)
        directed.setParseAction(self._push_directed)
        graph_id.setParseAction(self._push_graph_id)
#        graphparser.setParseAction(self._push_main_graph)

        return graphparser

    #--------------------------------------------------------------------------
    #  Parser actions
    #--------------------------------------------------------------------------

    def _push_strict(self, tokens):
        """ Sets the 'strict' attribute of the graph. """

        graph = self.graph
        strict = tokens["strict"]

        if strict == "strict":
            graph.strict = True
        elif strict == "notstrict":
            graph.strict = False
        else:
            raise ValueError


    def _push_directed(self, tokens):
        """ Do edges have direction? """

        graph = self.graph
        directed = tokens["directed"]

        if directed == "graph":
            graph.directed = False
        elif directed == "digraph":
            graph.directed = True
        else:
            raise ValueError


    def _push_graph_id(self, tokens):
        """ Optional graph identifier. """

        print "GRAPH ID:", tokens

        graph = self.graph
        graph_id = tokens["graph_id"]

        graph.ID = graph_id


    def _push_main_graph(self, tokens):
        """ Starts a new Graph. """

        print "GRAPH:", tokens

        self.graph = Graph()


    def push_attr_assignment(self, tokens):
        """ Sets the graph attribute to the parsed value. """

        print "ASSIGNMENT:", tokens

        graph = self.graph
        setattr(graph, tokens[0], tokens[1])

        return ("set_graph_attr", dict(nsplit(tokens, 2)))


    def push_node_id(self, tokens):
        """ Returns a tuple if more than one id exists. """

        print "NODE ID:", tokens

        if len(tokens) > 1:
            return (tokens[0], tokens[1]) # ID, port
        else:
            return tokens


    def push_attr_list(self, tokens):
        """ Splits the attributes into tuples and returns a dictionary using
        the first tuple value as the key and the second as the value.

        """

        print "ATTR LIST:", tokens

        return dict(nsplit(tokens, 2))


    def push_attr_list_combine(self, tokens):
        """ Combines a list of dictionaries, overwriting existing keys """

        print "ATTR LIST COMBINE:", tokens

        if tokens:
            first_dict = tokens[0]
            for d in tokens:
                first_dict.update(d)
            return first_dict

        return tokens


    def push_node_stmt(self, tokens):
        """ Returns tuple of the form (ADD_NODE, node_name, options) """

        print "NODE STMT:", tokens

        graph = self.graph
        name = tokens[0]

        if len(tokens) == 2:
            opts = tokens[1]
            node = Node(ID=name, **opts)
        else:
            node = Node(ID=name)
            options = {}
        # Set the attributes of the node.
#        for option in options:
#            setattr(node, option, options[option])
        # Add the node to the graph.
        graph.nodes.append(node)

        if len(tokens) == 2:
            return tuple(["add_node"] + list(tokens))
        else:
            return tuple(["add_node"] + list(tokens) + [{}])


    def push_edge_stmt(self, tokens):
        """ Returns tuple of the form (ADD_EDGE, src, dst, options) """

        print "EDGE STMT:", tokens

        graph = self.graph
        edgelist = []
        opts = tokens[-1]
        if not isinstance(opts, dict):
            opts = {}
        else:
            # Remove any attribute dictionary from the token list.
            tokens = tokens[:-1]

        print "EDGE STMT:", tokens

        for src, dst in windows(tokens, length=2, overlap=1, padding=False):
            print "WINDOW:", src, dst
            # Is src or dst a subgraph?
#            srcgraph = destgraph = False
#            if len(src) > 1 and src[0] == "add_subgraph":
#                edgelist.append(src)
#                srcgraph = True
#            if len(dest) > 1 and dest[0] == "add_subgraph":
#                edgelist.append(dest)
#                destgraph = True
#            if srcgraph or destgraph:
#                if srcgraph and destgraph:
#                    edgelist.append(
#                        ("add_graph_to_graph_edge", src[1], dest[1], opts)
#                    )
#                elif srcgraph:
#                    edgelist.append(("add_graph_to_node_edge",src[1],dest,opts))
#                else:
#                    edgelist.append(("add_node_to_graph_edge",src,dest[1],opts))
#            else:
#                # Ordinary edge
#                edgelist.append(("add_edge",src,dest,opts))

            # Ordinary edge.
            # Ports specified in the node ID take precendence over assignments.
            if isinstance(src, tuple):
                opts["tailport"] = src[1]
                src = src[0]
            if isinstance(dst, tuple):
                opts["headport"] = dst[1]
                dst = dst[0]

            # If a node didn't exist we would have to create one.
            from_node = graph.get_node(src)
            if from_node is None:
                from_node = Node(ID=src)
                graph.nodes.append(from_node)
            to_node = graph.get_node(dst)
            if to_node is None:
                to_node = Node(ID=dst)
                graph.nodes.append(to_node)

            edge = Edge(from_node, to_node, **opts)
            edgelist.append(edge)

        graph.edges.extend(edgelist)

        return tokens


    def push_default_attr_stmt(self, toks):
        """ If a default attribute is defined using a node, edge, or graph
        statement, or by an attribute assignment not attached to a node or
        edge, any object of the appropriate type defined afterwards will
        inherit this attribute value. This holds until the default attribute
        is set to a new value, from which point the new value is used. """

        print "DEFAULT ATTR STMT:", toks

        if len(toks)== 1:
            gtype = toks;
            attr = {}
        else:
            gtype, attr = toks
        if gtype == "node":
            return ("set_def_node_attr", attr)
        elif gtype == "edge":
            return ("set_def_edge_attr", attr)
        elif gtype == "graph":
            return ("set_def_graph_attr", attr)
        else:
            return ("unknown", toks)


    def push_subgraph_stmt(self, toks):
        """ Returns a tuple of the form (ADD_SUBGRAPH, name, elements) """
        print "SUBGRAPH:", toks

        return ("add_subgraph", toks[1], toks[2].asList())


    def _main_graph_stmt(self, toks):
        print "MAIN GRAPH:", toks

        return (toks[0], toks[1], toks[2], toks[3])#.asList())

# EOF -------------------------------------------------------------------------
