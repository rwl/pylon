#------------------------------------------------------------------------------
# Copyright (C) 2010 Richard Lincoln
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

""" Defines classes for reading and writing cases.
"""

#------------------------------------------------------------------------------
#  Imports:
#------------------------------------------------------------------------------

import logging

from rdflib.Graph import Graph
from rdflib import URIRef, Literal, BNode, Namespace
from rdflib import RDF

from pylon.readwrite.common import \
    CaseWriter, BUS_ATTRS, BRANCH_ATTRS, GENERATOR_ATTRS

#------------------------------------------------------------------------------
#  Logging:
#------------------------------------------------------------------------------

logger = logging.getLogger(__name__)

#------------------------------------------------------------------------------
#  "RDFWriter" class:
#------------------------------------------------------------------------------

class RDFWriter(CaseWriter):
    """ Writes cases as RDF/XML.
    """

    def __init__(self, case):
        """ Initialises a new CaseWriter instance.
        """
        super(RDFWriter, self).__init__(case)

        self.store = Graph()

        # Map of Bus objects to BNodes.
        self.bus_map = {}


    def _write_data(self, file):
        super(RDFWriter, self)._write_data(file)

        NS_PYLON = Namespace("http://rwl.github.com/pylon/")

        self.store.bind("pylon", "http://rwl.github.com/pylon/")

        for bus in self.case.buses:
            bus_node = BNode()
#            bus_node = URIRef(id(bus))
            self.bus_map[bus] = bus_node
            self.store.add((bus_node, RDF.type, NS_PYLON["Bus"]))
            for attr in BUS_ATTRS:
                self.store.add((bus_node,
                                NS_PYLON[attr],
                                Literal(getattr(bus, attr))))

        for branch in self.case.branches:
            branch_node = BNode()
            self.store.add((branch_node, RDF.type, NS_PYLON["Branch"]))

#            self.store.add((branch_node, NS_PYLON["from_bus"],
#                            self.bus_map[branch.from_bus]))

            for attr in BRANCH_ATTRS:
                self.store.add((branch_node,
                                NS_PYLON[attr],
                                Literal(getattr(branch, attr))))

        for generator in self.case.generators:
            g_node = BNode()
            self.store.add((g_node, RDF.type, NS_PYLON["Generator"]))
            for attr in GENERATOR_ATTRS:
                self.store.add((g_node,
                                NS_PYLON[attr],
                                Literal(getattr(generator, attr))))

        file.write(self.store.serialize(format="pretty-xml", max_depth=3))


if __name__ == "__main__":
    import sys
    from pylon.case import Case, Bus, Branch
    from pylon.generator import Generator
    bus1 = Bus()
    bus2 = Bus()
    case = Case(buses=[bus1, bus2],
                branches=[Branch(bus1, bus2)],
                generators=[Generator(bus1)])
    RDFWriter(case).write(sys.stdout)

# EOF -------------------------------------------------------------------------
