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

""" Defines a class for creating Network objects from M3 data files

Reference:
    http://www.openm3.org/

"""

#------------------------------------------------------------------------------
#  Imports:
#------------------------------------------------------------------------------

import logging

try:
    import xml.etree.ElementTree as etree
except ImportError:
    import elementtree.ElementTree as etree

from pylon.network import Network
from pylon.bus import Bus
from pylon.branch import Branch
from pylon.generator import Generator
from pylon.load import Load

#from pylon.pypylon import Network, Bus, Branch, Generator, Load

#------------------------------------------------------------------------------
#  Logging:
#------------------------------------------------------------------------------

logger = logging.getLogger(__name__)

#------------------------------------------------------------------------------
#  "M3Importer" class:
#------------------------------------------------------------------------------

class M3Importer:
    """ Creates Network objects from M3 data files """

    M3_NS = "http://www.openM3.org/m3"

    OP_NS = "http://www.ia.pw.edu.pl/m3/13node"

    def parse_file(self, file):
        """
        Parse M3 data files and push data into a Pylon Network instance

        file: Path to data file in M3 XML format
        return: Network instance

        """

        self.network = network = Network()

        tree = etree.parse(file)

        network_elements = tree.findall(".//{%s}Network" % self.M3_NS)

        n_network_elements = len(network_elements)

        if n_network_elements == 0:
            logger.error("No Network elements found in data file")
            return
        elif n_network_elements > 1:
            logger.info(
                "More than one Network element found in data file. Using "
                "the first one."
            )

        ne = network_elements[0]

        network.name = ne.findtext("{%s}name" % self.M3_NS)

        for node in ne.findall("{%s}node" % self.M3_NS):
            bus = self.create_bus(node)
            network.buses.append(bus)

        for arc in ne.findall("{%s}arc" % self.M3_NS):
            branch = self.create_branch(arc)
            network.add_branch(branch)

        # Market entities:
        me_elements = tree.findall(".//{%s}MarketEntity" % self.M3_NS)

        for me in me_elements:
            dref = self._unqualify(me.get("dref"))
            print "GENERATOR", dref

            if dref == "simpleGenerator":
                self.push_simple_generator(me)
            elif dref == "LVEnergySupplier" or dref == "MVEnergySupplier":
                self.push_lv_mv_supplier(me)

        return network


    def create_bus(self, element):
        """ Creates a bus object using a node element """

        v = Bus()

        # ID
        id = self._unqualify(element.get("id"))
        v.id = id

        # Name
        name = element.findtext("{%s}name" % self.M3_NS)
        if name is not None:
            v.name = name
        else:
            v.name = id

        for parm in element.findall("{%s}parameter" % self.M3_NS):
            dref = parm.get("dref")
            uq_dref = self._unqualify(dref)
            if uq_dref == "baseVoltage":
                v.v_base = float(parm.text)

        return v


    def create_branch(self, element):
        """ Creates a branch object with data from an edge element """

        e = Branch(network=self.network)

        pred = element.find("{%s}predecessor" % self.M3_NS)
        pred_ref = self._unqualify(pred.get("ref"))

        succ = element.find("{%s}successor" % self.M3_NS)
        succ_ref = self._unqualify(succ.get("ref"))

        buses = self.network.buses
        ids = [v.id for v in buses]

        pred_idx = ids.index(pred_ref)
        succ_idx = ids.index(succ_ref)

        e.source_bus = buses[pred_idx]
        e.target_bus = buses[succ_idx]

        return e


    def push_simple_generator(self, element):
        """ Creates a generator object from a simpleGenerator element """

        g = Generator()

        g.id = self._unqualify(element.get("id"))

        for parm in element.findall("{%s}parameter" % self.M3_NS):
            pass

        # Parent bus:
        relation = element.find("{%s}relatedTo" % self.M3_NS)
        rel_ref = self._unqualify(relation.get("ref"))

        buses = self.network.buses
        ids = [v.id for v in buses]

        v_idx = ids.index(rel_ref)
        buses[v_idx].generators.append(g)

        return g


    def push_lv_mv_supplier(self, element):
        """
        Creates a generator object from a MVEnergySupplier or
        LVEnergySupplier element

        """


    def _unqualify(self, name):
        """ Returns an unqualified name from a qualified name """

        if ":" in name:
            unqualified = name.rsplit(":", 1)
            return unqualified[-1]
        else:
            return name

#------------------------------------------------------------------------------
#  Convenience function for PSAT import
#------------------------------------------------------------------------------

def import_m3(file):
    """ Convenience function for import of a PSAT data file """

    return M3Importer().parse_file(file_or_filename)

#------------------------------------------------------------------------------
#  Standalone call:
#------------------------------------------------------------------------------

if __name__ == "__main__":
    DATA_FILE = "/home/rwl/python/aes/model/m3/lv_feeder_with_sources/" \
    "LVfeeder-with sources.xml"

    n = M3Importer().parse_file(DATA_FILE)
    print n.n_buses

# EOF -------------------------------------------------------------------------
