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
    quoted_string, nsplit, windows, graph_attr

from godot.graph import Graph

#------------------------------------------------------------------------------
#  "Parser" class:
#------------------------------------------------------------------------------

class Parser:
    """ Defines a Graphviz dot language parser. """

    parser = None

    graph = None

    #--------------------------------------------------------------------------
    #  "object" interface:
    #--------------------------------------------------------------------------

    def __init__(self):
        self.parser = self.define_parser()


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

        # An ID is one of the following:
        #  * Any string of alphabetic ([a-zA-Z\200-\377]) characters,
        #    underscores ('_') or digits ([0-9]), not beginning with a digit;
        #  * a number [-]?(.[0-9]+ | [0-9]+(.[0-9]*)? );
        #  * any double-quoted string ("...") possibly containing escaped
        #    quotes (\")1;
        #  * an HTML string (<...>).
        ID = (
            identifier | html_text |
            quoted_string | #.setParseAction(strip_quotes) |
            alphastring_
        ).setName("ID")

        float_number = Combine(
            Optional(minus) + OneOrMore(Word(nums + "."))
        ).setName("float_number")

        righthand_id = (float_number | ID ).setName("righthand_id")

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
        a_list = OneOrMore(
            ID + Optional(equals + righthand_id) + Optional(comma.suppress())
        ).setName("a_list")

        attr_list = OneOrMore(
            lbrack + Optional(a_list) + rbrack
        ).setName("attr_list").setResultsName("attrlist")

        attr_stmt = ((graph_ | node_ | edge_) + attr_list).setName("attr_stmt")

        edgeop = (Literal("--") | Literal("->")).setName("edgeop")

        stmt_list = Forward()
        graph_stmt = (
            lbrace + Optional(stmt_list) + rbrace + Optional(semi)
        ).setName("graph_stmt")

        edge_point = Forward()

        edgeRHS = OneOrMore(edgeop + edge_point)
        edge_stmt = edge_point + edgeRHS + Optional(attr_list)

        subgraph = (
            Optional(subgraph_, "") + Optional(ID, "") + Group(graph_stmt)
        ).setName("subgraph").setResultsName("ssubgraph")

        edge_point << (subgraph | graph_stmt | node_id )

        node_stmt = (
            node_id + Optional(attr_list) + Optional(semi)
        ).setName("node_stmt")

#        assignment = (ID + equals + righthand_id).setName("assignment")
        assignment = (
            Or([(CaselessLiteral(attr.resultsName) + Suppress(equals) + attr) \
                for attr in graph_attr])
        )

        stmt = (
            assignment | edge_stmt | attr_stmt | subgraph | graph_stmt |
            node_stmt
        ).setName("stmt")

        stmt_list << OneOrMore(stmt + Optional(semi))

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

        graph = self.graph
        graph_id = tokens["graph_id"]

        graph.ID = graph_id


    def _push_main_graph(self, tokens):
        """ Starts a new Graph. """

        print "Graph:", tokens

        self.graph = Graph()


    def push_node_id(self, tokens):
        """ Returns a tuple if more than one id exists """

        print "NODE ID:", tokens

        if len(toks) > 1:
            return (toks[0], toks[1])
        else:
            return toks


    def push_attr_list(self, tokens):
        """ Splits the attributes into tuples and returns a dictionary using
        the first tuple value as the key and the second as the value.

        """

        print "ATTR LIST:", tokens

        return dict(nsplit(toks, 2))


    def push_attr_list_combine(self, tokens):
        """ Combines a list of dictionaries, overwriting existing keys """

        if toks:
            first_dict = toks[0]
            for d in toks:
                first_dict.update(d)

            return first_dict
        return toks


    def push_attr_assignment(self, tokens):
        """ Sets the graph attribute to the parsed value. """

        graph = self.graph
        setattr(graph, tokens[0], tokens[1])

        return ("set_graph_attr", dict(nsplit(tokens, 2)))


    def push_node_stmt(self, toks):
        """ Returns tuple of the form (ADD_NODE, node_name, options) """

        if len(toks) == 2:
            return tuple(["add_node"] + list(toks))
        else:
            return tuple(["add_node"] + list(toks) + [{}])


    def push_edge_stmt(self, toks):
        """ Returns tuple of the form (ADD_EDGE, src, dest, options) """

        edgelist = []
        opts = toks[-1]
        if not isinstance(opts, dict):
            opts = {}
        for src, op, dest in windows(toks, length=3, overlap=1, padding=False):
            # is src or dest a subgraph?
            srcgraph = destgraph = False
            if len(src) > 1 and src[0] == "add_subgraph":
                edgelist.append(src)
                srcgraph = True
            if len(dest) > 1 and dest[0] == "add_subgraph":
                edgelist.append(dest)
                destgraph = True
            if srcgraph or destgraph:
                if srcgraph and destgraph:
                    edgelist.append(
                        ("add_graph_to_graph_edge",src[1],dest[1],opts)
                    )
                elif srcgraph:
                    edgelist.append(("add_graph_to_node_edge",src[1],dest,opts))
                else:
                    edgelist.append(("add_node_to_graph_edge",src,dest[1],opts))
            else:
                # ordinary edge
                edgelist.append(("add_edge",src,dest,opts))

        return edgelist


    def push_default_attr_stmt(self, toks):
        """ Returns a tuple of the form (ADD_DEFAULT_NODE_ATTR, options) """

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


    def push_subgraph_stmt(self,toks):
        """ Returns a tuple of the form (ADD_SUBGRAPH, name, elements) """

        return ("add_subgraph", toks[1], toks[2].asList())


    def _main_graph_stmt(self,toks):

        return (toks[0], toks[1], toks[2], toks[3])#.asList())

# EOF -------------------------------------------------------------------------
