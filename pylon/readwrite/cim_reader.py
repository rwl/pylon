#------------------------------------------------------------------------------
# Copyright (C) 2009 Richard W. Lincoln
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

""" Defines a reader for RDF/XML files with CIM data.
"""

#------------------------------------------------------------------------------
#  Imports:
#------------------------------------------------------------------------------

from rdflib.Graph import ConjunctiveGraph

from rdflib.Namespace import Namespace

from CIM13.Generation.Production import GeneratingUnit

#class iec61970(HasTraits):
#    core = Instance(Core)
#    domain = Instance(Domain)
#    equivalents = Instance(Equivalents)
#    generation = Instance(Generation)
#    load_model = Instance(LoadModel)
#    meas = Instance(Meas)
#    outage = Instance(Outage)
#    protection = Instance(Protection)
#    scada = Instance(SCADA)
#    topology = Instance(Topology)
#    wires = Instance(Wires)

#------------------------------------------------------------------------------
#  "CIMReader" class:
#------------------------------------------------------------------------------

class CIMReader:
    """ Reads RDF/XML files with CIM data.
    """

    filename = ""

    model = None

    region = "iec61970.core.geographical_region.GeographicalRegion"

    def __init__(self, filename):
        """ Returns a new MATPOWERReader instance """

        self.filename = filename


    def parse_file(self, filename=None):
        """ Parses an RDF?XML file and returns a model containing CIM elements.
        """
        if filename is None:
            filename = self.filename
        else:
            self.filename = filename
#
#        if isinstance(file_or_filename, basestring):
#            file = open(file_or_filename, "wb")
#        else:
#            file = file_or_filename

        ns_cim = Namespace("http://iec.ch/TC57/2009/CIM-schema-cim14#")
        ns_rdf = Namespace("http://www.w3.org/1999/02/22-rdf-syntax-ns#")
        ns_ngt = Namespace("http://com.ngtuk/2005/NGT-schema-cim11#")

        store = ConjunctiveGraph()

        context = store.parse(filename)
        print context.identifier
        print dir(context)

        for subject, predicate, object in store:
            print "SUBJECT:", subject
            print "PREDICATE:", predicate
            print "OBJECT:", object

#        for s, o in store.subject_objects(ns_rdf["type"]):
#            print "NAME:", o

        for s in store.subjects(ns_rdf["type"], ns_cim["GeneratingUnit"]):
            print "SUBJECT:", type(s), s
            unit = GeneratingUnit()

            for p, o in store.predicate_objects(s):
                print "PREDICATE:", type(p), p
                print "OBJECT:", type(o), o


if __name__ == "__main__":
    reader = CIMReader("/tmp/10bus.xml")
    reader.parse_file()

# EOF -------------------------------------------------------------------------
