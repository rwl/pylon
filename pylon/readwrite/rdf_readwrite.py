#------------------------------------------------------------------------------
# Copyright (C) 2010 Richard Lincoln
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#------------------------------------------------------------------------------

""" Defines classes for reading and writing cases.
"""

#------------------------------------------------------------------------------
#  Imports:
#------------------------------------------------------------------------------

import os.path
import logging

from rdflib.Graph import Graph
from rdflib import URIRef, Literal, BNode, Namespace
from rdflib import RDF

from pylon.readwrite.common import \
    CaseWriter, CaseReader, BUS_ATTRS, BRANCH_ATTRS, GENERATOR_ATTRS

#------------------------------------------------------------------------------
#  Logging:
#------------------------------------------------------------------------------

logger = logging.getLogger(__name__)

#------------------------------------------------------------------------------
#  "RDFReader" class:
#------------------------------------------------------------------------------

class RDFReader(CaseReader):
    """ Defines a reader for pickled cases.
    """

    def read(self, file_or_filename):
        """ Loads a case from RDF.
        """
        if isinstance(file_or_filename, basestring):
            fname = os.path.basename(file_or_filename)
            logger.info("Loading RDF case file [%s]." % fname)

            file = None
            try:
                file = open(file_or_filename, "rb")
                case = self._parse_rdf(file)
            except Exception, detail:
                logger.error("Error loading '%s': %s" % (fname, detail))
                return None
            finally:
                if file is not None:
                    file.close()
        else:
            file = file_or_filename
            case = self._parse_rdf(file)

        return case


    def _parse_rdf(self, file):
        """ Returns a case from the given file.
        """
        store = Graph()
        store.parse(file)

        print len(store)

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
