#------------------------------------------------------------------------------
# Copyright (C) 2008 Richard W. Lincoln
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

""" For writing network data to file as Comma Separated Values (CSV). """

#------------------------------------------------------------------------------
#  Imports:
#------------------------------------------------------------------------------

import csv

from common import bus_attrs, branch_attrs, generator_attrs, load_attrs

#------------------------------------------------------------------------------
#  "CSVWriter" class:
#------------------------------------------------------------------------------

class CSVWriter:
    """ Writes network data to file as CSV. """

    network = None

    file_or_filename = ""

    def __init__(self, network, file_or_filename):
        """ Initialises a new CSVWriter instance. """

        self.network = network
        self.file_or_filename = file_or_filename


    def write(self):
        """ Writes network data to file as CSV. """

        network = self.network
        file_or_filename = self.file_or_filename

        if isinstance(file_or_filename, basestring):
            file = open(file_or_filename, "wb")
        else:
            file = file_or_filename

        writer = csv.writer(file)

        # Bus -----------------------------------------------------------------

        writer.writerow(bus_attrs)

        for bus in network.buses:
            values = [getattr(bus, attr) for attr in bus_attrs]
            print "BUS:", values
            writer.writerow(values)
            del values

        # Branch --------------------------------------------------------------

        writer.writerow(branch_attrs)

        for branch in network.branches:
            values = [getattr(branch, attr) for attr in branch_attrs]
            writer.writerow(values)
            del values

        # Generator -----------------------------------------------------------

        writer.writerow(["bus"] + generator_attrs)

        for i, bus in enumerate(network.buses):
            for generator in bus.generators:
                values = [getattr(generator, attr) for attr in generator_attrs]
                writer.writerow([i] + values)
                del values

        # Load ----------------------------------------------------------------

        writer.writerow(["bus"] + load_attrs)

        for i, bus in enumerate(network.buses):
            for load in bus.loads:
                values = [getattr(load, attr) for attr in load_attrs]
                writer.writerow([i] + values)
                del values

        file.close()

if __name__ == "__main__":
    from pylon.api import Network, Bus, Branch, Generator, Load
    n = Network(name="network", base_mva=100.0)
    bus1 = Bus(name="Bus 1")
    bus2 = Bus(name="Bus 2")
    bus1.generators.append(Generator(name="G"))
    bus2.loads.append(Load(name="L"))
    branch1 = Branch(bus1, bus2, name="Branch 1")
    n.buses.extend([bus1, bus2])
    n.branches.append(branch1)
    writer = CSVWriter(n, "/tmp/network.csv")
    writer.write()

# EOF -------------------------------------------------------------------------
