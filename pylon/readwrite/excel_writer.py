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

from pyExcelerator import Workbook, Font, XFStyle, Borders

from pylon.bus import bus_attrs
from pylon.branch import branch_attrs
from pylon.generator import generator_attrs
from pylon.load import load_attrs

#------------------------------------------------------------------------------
#  "ExcelWriter" class:
#------------------------------------------------------------------------------

class ExcelWriter:
    """ Writes network data to file in Excel format. """

    network = None

    file_or_filename = ""

    def __init__(self, network, file_or_filename):
        """ Initialises a new ExcelWriter instance. """

        self.network = network
        self.file_or_filename = file_or_filename


    def write(self):
        """ Writes network data to file in Excel format. """

        network = self.network
        file_or_filename = self.file_or_filename

        if isinstance(file_or_filename, basestring):
            file = open(file_or_filename, "wb")
        else:
            file = file_or_filename

        book = Workbook()
        bus_sheet = book.add_sheet("Buses")

        for i, bus in enumerate(network.buses):
            for j, attr in enumerate(bus_attrs):
                bus_sheet.write(i, j, getattr(bus, attr))

        branch_sheet = book.add_sheet("Branches")

        for i, branch in enumerate(network.branches):
            for j, attr in enumerate(branch_attrs):
                branch_sheet.write(i, j, getattr(branch, attr))


        book.save(file_or_filename)

        file.close()

#------------------------------------------------------------------------------
#  Stand-alone call:
#------------------------------------------------------------------------------

if __name__ == "__main__":
    from pylon.api import Network, Bus, Branch, Generator, Load
    n = Network(name="network", mva_base=100.0)
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
