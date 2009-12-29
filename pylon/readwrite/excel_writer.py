#------------------------------------------------------------------------------
# Copyright (C) 2009 Richard Lincoln
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

""" For writing case data to an Excel file.
"""

#------------------------------------------------------------------------------
#  Imports:
#------------------------------------------------------------------------------

from pyExcelerator import Workbook

from common import CaseWriter, BUS_ATTRS, BRANCH_ATTRS, GENERATOR_ATTRS

#------------------------------------------------------------------------------
#  "ExcelWriter" class:
#------------------------------------------------------------------------------

class ExcelWriter(CaseWriter):
    """ Writes case data to file in Excel format.
    """

    def write(self, file_or_filename):
        """ Writes case data to file in Excel format.
        """
        self.book = Workbook()
        self._write_data(None)
        self.book.save(file_or_filename)


    def write_case_data(self, file):
        """ Writes the header to file.
        """
        case_sheet = self.book.add_sheet("Case")
        case_sheet.write(0, 0, "Name")
        case_sheet.write(0, 1, self.case.name)
        case_sheet.write(1, 0, "base_mva")
        case_sheet.write(1, 1, self.case.base_mva)


    def write_bus_data(self, file):
        """ Writes bus data to an Excel spreadsheet.
        """
        bus_sheet = self.book.add_sheet("Buses")

        for i, bus in enumerate(self.case.buses):
            for j, attr in enumerate(BUS_ATTRS):
                bus_sheet.write(i, j, getattr(bus, attr))


    def write_branch_data(self, file):
        """ Writes branch data to an Excel spreadsheet.
        """
        branch_sheet = self.book.add_sheet("Branches")

        for i, branch in enumerate(self.case.branches):
            for j, attr in enumerate(BRANCH_ATTRS):
                branch_sheet.write(i, j, getattr(branch, attr))


    def write_generator_data(self, file):
        """ Write generator data to file.
        """
        generator_sheet = self.book.add_sheet("Generators")

        for j, generator in enumerate(self.case.generators):
            i = self.case.buses.index(generator.bus)
            for k, attr in enumerate(GENERATOR_ATTRS):
                generator_sheet.write(j, 0, i)
                # FIXME: Cast p_cost tuple.
#                generator_sheet.write(j, k + 1, getattr(generator, attr))

# EOF -------------------------------------------------------------------------
