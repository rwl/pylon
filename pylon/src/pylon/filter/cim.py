#------------------------------------------------------------------------------
# Copyright (C) 2007 Richard W. Lincoln
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

""" Adapt CIM into Network model.
"""

#------------------------------------------------------------------------------
#  Imports:
#------------------------------------------------------------------------------

from rdflib.Graph import ConjunctiveGraph

from rdflib.Namespace import Namespace

from iec61970.core.geographical_region import GeographicalRegion

class iec61970(HasTraits):
    core = Instance(Core)
    domain = Instance(Domain)
    equivalents = Instance(Equivalents)
    generation = Instance(Generation)
    load_model = Instance(LoadModel)
    meas = Instance(Meas)
    outage = Instance(Outage)
    protection = Instance(Protection)
    scada = Instance(SCADA)
    topology = Instance(Topology)
    wires = Instance(Wires)

#------------------------------------------------------------------------------
#  "CIMAdapter" class:
#------------------------------------------------------------------------------

class CIMAdapter:
    """
    Adapt CIM/XML to Pylon model

    """

    region = "iec61970.core.geographical_region.GeographicalRegion"

    def parse(self, file):

        ns_cim = Namespace("http://iec.ch/TC57/2006/CIM-schema-cim10#")
        ns_rdf = Namespace("http://www.w3.org/1999/02/22-rdf-syntax-ns#")
        ns_ngt = Namespace("http://com.ngtuk/2005/NGT-schema-cim11#")

        cg = ConjunctiveGraph()

        context = cg.parse(file)
        print context.identifier
        print dir(context)

#        f=open('/tmp/workfile', 'w')
#
#        for subject, predicate, object in cg:
##            print "SUBJECT:", subject
##            print "PREDICATE:", predicate
##            print "OBJECT:", object
#            f.write("SUBJECT: " + subject + "\n")
#            f.write("PREDICATE: " + predicate + "\n")
#            f.write("OBJECT: " + object + "\n")
#
#        f.close()

#        for s, o in cg.subject_objects(ns_rdf["type"]):
#            print "NAME:", o

        for s in cg.subjects(ns_rdf["type"], ns_cim["SubGeographicalRegion"]):
            print s

            for p, o in cg.predicate_objects(s):
                print p, o


if __name__ == "__main__":

    ca = CIMAdapter()

    #ca.parse("/tmp/edf_cpsm.xml")
    ca.parse("/tmp/cdpsm.xml")

# EOF -------------------------------------------------------------------------
