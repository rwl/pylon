#------------------------------------------------------------------------------
# Copyright (C) 2007-2010 Richard Lincoln
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

""" For writing case data to an Excel file or  as Comma Separated Values (CSV).
"""

#------------------------------------------------------------------------------
#  Imports:
#------------------------------------------------------------------------------

import csv

from pyExcelerator import Workbook

from common import _CaseWriter, BUS_ATTRS, BRANCH_ATTRS, GENERATOR_ATTRS

#------------------------------------------------------------------------------
#  "ExcelWriter" class:
#------------------------------------------------------------------------------

class ExcelWriter(_CaseWriter):
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
            i = generator.bus._i
            for k, attr in enumerate(GENERATOR_ATTRS):
                generator_sheet.write(j, 0, i)
                # FIXME: Cast p_cost tuple.
#                generator_sheet.write(j, k + 1, getattr(generator, attr))

#------------------------------------------------------------------------------
#  "CSVWriter" class:
#------------------------------------------------------------------------------

class CSVWriter(_CaseWriter):
    """ Writes case data to file as CSV.
    """

    #--------------------------------------------------------------------------
    #  "object" interface:
    #--------------------------------------------------------------------------

    def __init__(self, case):
        """ Initialises a new CSVWriter instance.
        """
        super(CSVWriter, self).__init__(case)

        #: For writing CSV files.
        self.writer = None

    #--------------------------------------------------------------------------
    #  "_CaseReader" interface:
    #--------------------------------------------------------------------------

    def write(self, file_or_filename):
        """ Writes case data as CSV.
        """
        if isinstance(file_or_filename, basestring):
            file = open(file_or_filename, "wb")
        else:
            file = file_or_filename

        self.writer = csv.writer(file)

        super(CSVWriter, self).write(file)


    def write_case_data(self, file):
        """ Writes the case data as CSV.
        """
        writer = self._get_writer(file)
        writer.writerow(["Name", "base_mva"])
        writer.writerow([self.case.name, self.case.base_mva])


    def write_bus_data(self, file):
        """ Writes bus data as CSV.
        """
        writer = self._get_writer(file)
        writer.writerow(BUS_ATTRS)
        for bus in self.case.buses:
            writer.writerow([getattr(bus, attr) for attr in BUS_ATTRS])


    def write_branch_data(self, file):
        """ Writes branch data as CSV.
        """
        writer = self._get_writer(file)
        writer.writerow(BRANCH_ATTRS)
        for branch in self.case.branches:
            writer.writerow([getattr(branch, a) for a in BRANCH_ATTRS])


    def write_generator_data(self, file):
        """ Write generator data as CSV.
        """
        writer = self._get_writer(file)
        writer.writerow(["bus"] + GENERATOR_ATTRS)

        for g in self.case.generators:
            i = g.bus._i
            writer.writerow([i] + [getattr(g,a) for a in GENERATOR_ATTRS])

    #--------------------------------------------------------------------------
    #  "CSVReader" interface:
    #--------------------------------------------------------------------------

    def _get_writer(self, file):
        if self.writer is None:
            return csv.writer(file)
        else:
            return self.writer

# EOF -------------------------------------------------------------------------
