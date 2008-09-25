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
into a class representation defined by dott.

"""

#------------------------------------------------------------------------------
#  Imports:
#------------------------------------------------------------------------------

from pyparsing import \
    Literal, CaselessLiteral, Word, Upcase, OneOrMore, ZeroOrMore, Forward, \
    NotAny, delimitedList, oneOf, Group, Optional, Combine, alphas, nums, \
    restOfLine, cStyleComment, nums, alphanums, printables, empty, \
    quotedString, ParseException, ParseResults, CharsNotIn, _noncomma, \
    dblQuotedString, QuotedString, ParserElement, Suppress,Regex, \
    removeQuotes, nestedExpr

#------------------------------------------------------------------------------
#  Constants:
#------------------------------------------------------------------------------

ADD_NODE = "add_node"
ADD_EDGE = "add_edge"
ADD_GRAPH_TO_NODE_EDGE = "add_graph_to_node_edge"
ADD_NODE_TO_GRAPH_EDGE = "add_node_to_graph_edge"
ADD_GRAPH_TO_GRAPH_EDGE = "add_graph_to_graph_edge"
ADD_SUBGRAPH = "add_subgraph"
SET_DEF_NODE_ATTR = "set_def_node_attr"
SET_DEF_EDGE_ATTR = "set_def_edge_attr"
SET_DEF_GRAPH_ATTR = "set_def_graph_attr"
SET_GRAPH_ATTR = "set_graph_attr"

#------------------------------------------------------------------------------
#  "nsplit" function:
#------------------------------------------------------------------------------

def nsplit(seq, n=2):
    """ Split a sequence into pieces of length n

    If the length of the sequence isn't a multiple of n, the rest is discarded.
    Note that nsplit will split strings into individual characters.

    Examples:
    >>> nsplit("aabbcc")
    [("a", "a"), ("b", "b"), ("c", "c")]
    >>> nsplit("aabbcc",n=3)
    [("a", "a", "b"), ("b", "c", "c")]

    # Note that cc is discarded
    >>> nsplit("aabbcc",n=4)
    [("a", "a", "b", "b")]

    """

    return [xy for xy in izip(*[iter(seq)]*n)]

#------------------------------------------------------------------------------
#  "windows" function:
#------------------------------------------------------------------------------

def windows(iterable, length=2, overlap=0, padding=True):
    """ Code snippet from Python Cookbook, 2nd Edition by David Ascher,
    Alex Martelli and Anna Ravenscroft; O'Reilly 2005

    """

    it = iter(iterable)
    results = list(itertools.islice(it, length))
    while len(results) == length:
        yield results
        results = results[length-overlap:]
        results.extend(itertools.islice(it, length-overlap))
    if padding and results:
        results.extend(itertools.repeat(None, length-len(results)))
        yield results

#------------------------------------------------------------------------------
#  "Parser" class:
#------------------------------------------------------------------------------

class Parser:
    """ Defines a Graphviz dot language parser. """

    def __init__(self):
        self.parser = self.define_parser()

    #--------------------------------------------------------------------------
    #  Define the dot parser
    #--------------------------------------------------------------------------

    def define_parser(self):
        """ Defines dot grammar """

        # punctuation
        colon  = Literal(":")
        lbrace = Suppress("{")
        rbrace = Suppress("}")
        lbrack = Suppress("[")
        rbrack = Suppress("]")
        lparen = Literal("(")
        rparen = Literal(")")
        equals = Suppress("=")
        comma  = Literal(",")
        dot    = Literal(".")
        slash  = Literal("/")
        bslash = Literal("\\")
        star   = Literal("*")
        semi   = Suppress(";")
        at     = Literal("@")
        minus  = Literal("-")
        plus  = Suppress("+")

        # keywords
        strict_    = CaselessLiteral("strict")
        graph_     = CaselessLiteral("graph")
        digraph_   = CaselessLiteral("digraph")
        subgraph_  = CaselessLiteral("subgraph")
        node_      = CaselessLiteral("node")
        edge_      = CaselessLiteral("edge")

        # token definitions
        identifier = Word(alphanums + "_" ).setName("identifier")

        #double_quoted_string = QuotedString('"', multiline=True,escChar="\\",
        #    unquoteResults=True) # dblQuotedString
        double_quoted_string = Regex(r'\"(?:\\\"|\\\\|[^"])*\"', re.MULTILINE)
        double_quoted_string.setParseAction(removeQuotes)
        quoted_string = Combine(
            double_quoted_string+
            Optional(OneOrMore(plus+double_quoted_string)), adjacent=False
        )

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
            Optional(subgraph_,"") + Optional(ID,"") + Group(graph_stmt)
        ).setName("subgraph").setResultsName("ssubgraph")

        edge_point << (subgraph | graph_stmt | node_id )

        node_stmt = (
            node_id + Optional(attr_list) + Optional(semi)
        ).setName("node_stmt")

        assignment = (ID + equals + righthand_id).setName("assignment")
        stmt =  (
            assignment | edge_stmt | attr_stmt | subgraph | graph_stmt |
            node_stmt
        ).setName("stmt")
        stmt_list << OneOrMore(stmt + Optional(semi))

        graphparser = (
            Optional(strict_,"notstrict") + ((graph_ | digraph_)) +
            Optional(ID,"") + lbrace + Group(Optional(stmt_list)) +rbrace
        ).setResultsName("graph")

        singleLineComment = Group("//" + restOfLine) | Group("#" + restOfLine)

        # actions
        graphparser.ignore(singleLineComment)
        graphparser.ignore(cStyleComment)
        node_id.setParseAction(self.push_node_id)
        assignment.setParseAction(self.push_attr_assignment)
        a_list.setParseAction(self.push_attr_list)
        edge_stmt.setParseAction(self.push_edge_stmt)
        node_stmt.setParseAction(self.push_node_stmt)
        attr_stmt.setParseAction(self.push_default_attr_stmt)
        attr_list.setParseAction(self.push_attr_list_combine)
        subgraph.setParseAction(self.push_subgraph_stmt)
        #graph_stmt.setParseAction(self.push_graph_stmt)
        graphparser.setParseAction(self._main_graph_stmt)

        return graphparser

    #--------------------------------------------------------------------------
    #  Parser actions
    #--------------------------------------------------------------------------

    def push_node_id(self, toks):
        """ Returns a tuple if more than one id exists """

        if len(toks) > 1:
            return (toks[0], toks[1])
        else:
            return toks


    def push_attr_list(self, toks):
        """ Splits the attributes into tuples and returns a dictionary using
        the first tuple value as the key and the second as the value.

        """

        return dict(nsplit(toks, 2))


    def push_attr_list_combine(self, toks):
        """ Combines a list of dictionaries, overwriting existing keys """

        if toks:
            first_dict = toks[0]
            for d in toks:
                first_dict.update(d)

            return first_dict
        return toks


    def push_attr_assignment(self, toks):
        return (SET_GRAPH_ATTR, dict(nsplit(toks, 2)))


    def push_node_stmt(self, toks):
        """ Returns tuple of the form (ADD_NODE, node_name, options) """

        if len(toks) == 2:
            return tuple([ADD_NODE] + list(toks))
        else:
            return tuple([ADD_NODE] + list(toks) + [{}])


    def push_edge_stmt(self, toks):
        """ Returns tuple of the form (ADD_EDGE, src, dest, options) """

        edgelist = []
        opts = toks[-1]
        if not isinstance(opts, dict):
            opts = {}
        for src, op, dest in windows(toks, length=3, overlap=1, padding=False):
            # is src or dest a subgraph?
            srcgraph = destgraph = False
            if len(src) > 1 and src[0] == ADD_SUBGRAPH:
                edgelist.append(src)
                srcgraph = True
            if len(dest) > 1 and dest[0] == ADD_SUBGRAPH:
                edgelist.append(dest)
                destgraph = True
            if srcgraph or destgraph:
                if srcgraph and destgraph:
                    edgelist.append(
                        (ADD_GRAPH_TO_GRAPH_EDGE,src[1],dest[1],opts)
                    )
                elif srcgraph:
                    edgelist.append((ADD_GRAPH_TO_NODE_EDGE,src[1],dest,opts))
                else:
                    edgelist.append((ADD_NODE_TO_GRAPH_EDGE,src,dest[1],opts))
            else:
                # ordinary edge
                edgelist.append((ADD_EDGE,src,dest,opts))

        return edgelist


    def push_default_attr_stmt(self, toks):
        """ Returns a tuple of the form (ADD_DEFAULT_NODE_ATTR, options) """

        if len(toks)== 1:
            gtype = toks;
            attr = {}
        else:
            gtype, attr = toks
        if gtype == "node":
            return (SET_DEF_NODE_ATTR, attr)
        elif gtype == "edge":
            return (SET_DEF_EDGE_ATTR, attr)
        elif gtype == "graph":
            return (SET_DEF_GRAPH_ATTR, attr)
        else:
            return ("unknown", toks)


    def push_subgraph_stmt(self,toks):
        """ Returns a tuple of the form (ADD_SUBGRAPH, name, elements) """

        return ("add_subgraph", toks[1], toks[2].asList())


    def _main_graph_stmt(self,toks):

        return (toks[0], toks[1], toks[2],toks[3].asList())

# EOF -------------------------------------------------------------------------
