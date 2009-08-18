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

""" For writing network data to file as Comma Separated Values (CSV).
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
    """ Writes network data to file as CSV.
    """

    def __call__(self, network, file_or_filename):
        """ Calls the writer with the given network.
        """
        self.write(network, file_or_filename)


    def write(self, network, file_or_filename):
        """ Writes network data to file as CSV.
        """
        self.network = network
        self.file_or_filename = file_or_filename

        if isinstance(file_or_filename, basestring):
            file = open(file_or_filename, "wb")
        else:
            file = file_or_filename

        writer = csv.writer(file)

        # Bus -----------------------------------------------------------------

        writer.writerow(bus_attrs)

        for bus in network.buses:
            values = [getattr(bus, attr) for attr in bus_attrs]
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

# EOF -------------------------------------------------------------------------
