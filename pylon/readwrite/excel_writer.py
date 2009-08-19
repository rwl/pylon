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

""" For writing network data to an Excel file.
"""

#------------------------------------------------------------------------------
#  Imports:
#------------------------------------------------------------------------------

from pyExcelerator import Workbook, Font, XFStyle, Borders

from common import bus_attrs, branch_attrs, generator_attrs, load_attrs

#------------------------------------------------------------------------------
#  "ExcelWriter" class:
#------------------------------------------------------------------------------

class ExcelWriter(object):
    """ Writes network data to file in Excel format.
    """

    def __call__(self, network, file_or_filename):
        """ Calls the writer with the given network.
        """
        self.write(network, file_or_filename)


    def write(self, network, file_or_filename):
        """ Writes network data to file in Excel format.
        """
        self.network = network
        self.file_or_filename = file_or_filename

        self.book = Workbook()

        self.write_generator_data(network, file)
        self.write_branch_data(network, file)
        self.write_generator_data(network, file)
        self.write_load_data(network, file)

        book.save(file_or_filename)


    def write_header(self, network, file):
        """ Writes the header to file.
        """
        pass


    def write_bus_data(self, network, file):
        """ Writes bus data to file.
        """
        bus_sheet = book.add_sheet("Buses")

        for i, bus in enumerate(network.buses):
            for j, attr in enumerate(bus_attrs):
                bus_sheet.write(i, j, getattr(bus, attr))


    def write_branch_data(self, network, file):
        """ Writes branch data to file.
        """
        branch_sheet = book.add_sheet("Branches")

        for i, branch in enumerate(network.branches):
            for j, attr in enumerate(branch_attrs):
                branch_sheet.write(i, j, getattr(branch, attr))


    def write_generator_data(self, network, file):
        """ Write generator data to file.
        """
        generator_sheet = book.add_sheet("Generators")

        for i, bus, in enumerate(network.buses):
            for j, generator in enumerate(bus.generators):
                for k, attr in enumerate(generator_attrs):
                    generator_sheet.write(j, 0, i)
#                    generator_sheet.write(j, k+1, getattr(generator, attr))


    def write_load_data(self, network, file):
        """ Writes load data to file.
        """
        load_sheet = book.add_sheet("Loads")

        for i, attr in enumerate(load_attrs):
            load_sheet.write(0, i, attr)

        for i, bus, in enumerate(network.buses):
            for j, load in enumerate(bus.loads):
                for k, attr in enumerate(load_attrs):
                    load_sheet.write(j+1, 0, i)
                    load_sheet.write(j+1, k+1, getattr(load, attr))


    def write_generator_cost_data(self, network, file):
        """ Writes generator cost data to file.
        """
        pass

# EOF -------------------------------------------------------------------------
