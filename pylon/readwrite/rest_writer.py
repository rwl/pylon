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

""" Defines a class for writing network data to a ReStructuredText file """

#------------------------------------------------------------------------------
#  Imports:
#------------------------------------------------------------------------------

#------------------------------------------------------------------------------
#  "ReSTWriter" class:
#------------------------------------------------------------------------------

class ReSTWriter:
    """ Write network data to a file in ReStructuredText format """

    network = None

    def write(self, network, file_or_filename):
        """ Writes network data to file in ReStructuredText format """

        self.network = network

        if isinstance(file_or_filename, basestring):
            file = open(file_or_filename, "wb")
        else:
            file = file_or_filename

        file.write(network.name)
        file.write("\n")
        file.write("="*len(network.name))
        file.write("\n")

        file.write("System Summary\n")
        file.write("--------------\n")

        file.close()

#------------------------------------------------------------------------------
#  Standalone call:
#------------------------------------------------------------------------------

if __name__ == "__main__":
    import sys
    import logging
    logger = logging.getLogger()
    logger.addHandler(logging.StreamHandler(sys.stdout))
    logger.setLevel(logging.DEBUG)

    from matpower_reader import read_matpower
    data_file = "/home/rwl/python/aes/matpower_3.2/case6ww.m"

    n = read_matpower(data_file)

    RSTWriter().write(n, "/tmp/test.m")

# EOF -------------------------------------------------------------------------
