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

""" For writing case data to file as Comma Separated Values (CSV).
"""

#------------------------------------------------------------------------------
#  Imports:
#------------------------------------------------------------------------------

import csv

from common import bus_attrs, branch_attrs, generator_attrs, load_attrs

#------------------------------------------------------------------------------
#  "CSVWriter" class:
#------------------------------------------------------------------------------

class CSVWriter(object):
    """ Writes case data to file as CSV.
    """

    def __call__(self, case, file_or_filename):
        """ Calls the writer with the given case.
        """
        self.write(case, file_or_filename)


    def write(self, case, file_or_filename):
        """ Writes case data to file as CSV.
        """
        self.case = case
        self.file_or_filename = file_or_filename

        if isinstance(file_or_filename, basestring):
            file = open(file_or_filename, "wb")
        else:
            file = file_or_filename

        self.writer = csv.writer(file)

        self.write_generator_data(case, file)
        self.write_branch_data(case, file)
        self.write_generator_data(case, file)
        self.write_load_data(case, file)
        self.write_generator_cost_data(case, file)

        file.close()


    def write_header(self, case, file):
        """ Writes the header to file.
        """
        pass


    def write_bus_data(self, case, file):
        """ Writes bus data to file.
        """
        self.writer.writerow(bus_attrs)

        for bus in case.buses:
            values = [getattr(bus, attr) for attr in bus_attrs]
            writer.writerow(values)
            del values


    def write_branch_data(self, case, file):
        """ Writes branch data to file.
        """
        self.writer.writerow(branch_attrs)

        for branch in case.branches:
            values = [getattr(branch, attr) for attr in branch_attrs]
            writer.writerow(values)
            del values


    def write_generator_data(self, case, file):
        """ Write generator data to file.
        """
        self.writer.writerow(["bus"] + generator_attrs)

        for i, bus in enumerate(case.buses):
            for generator in bus.generators:
                values = [getattr(generator, attr) for attr in generator_attrs]
                writer.writerow([i] + values)
                del values


    def write_load_data(self, case, file):
        """ Writes load data to file.
        """
        writer.writerow(["bus"] + load_attrs)

        for i, bus in enumerate(case.buses):
            for load in bus.loads:
                values = [getattr(load, attr) for attr in load_attrs]
                writer.writerow([i] + values)
                del values


    def write_generator_cost_data(self, case, file):
        """ Writes generator cost data to file.
        """
        pass

# EOF -------------------------------------------------------------------------
