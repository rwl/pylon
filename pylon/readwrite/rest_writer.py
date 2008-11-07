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
#  "ReSTWriter" class:
#------------------------------------------------------------------------------

class ReSTWriter:
    """ Write network data to a file in ReStructuredText format """

    network = None

    file_or_filename = ""

    def __init__(self, network, file_or_filename):
        self.network = network
        self.file_or_filename = file_or_filename


    def write(self):
        """ Writes network data to file in ReStructuredText format """

        network = self.network
        file_or_filename = self.file_or_filename

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

        self._write_how_many(file)

        file.close()


    def _write_how_many(self, file):
        """ Writes component numbers to a table """

        network = self.network

        components = [("Bus", "n_buses"), ("Generator", "n_generators"),
            ("Committed Generator", "n_committed_generators"),
            ("Load", "n_loads"), ("Fixed Load", "n_fixed"),
            ("Despatchable Load", "n_despatchable"), ("Shunt", "n_shunts"),
            ("Branch", "n_branches"), ("Transformer", "n_transformers"),
            ("Inter-tie", "n_inter_ties"), ("Area", "n_areas")]

        longest = max([len(c[0]) for c in components])

        sep = "="*longest + " " + "="*len("Quantity") + "\n"

        file.write(sep)
        file.write("Object")
        file.write(" "*(longest-len("Object")+1))
        file.write("Quantity\n")
        file.write(sep)

        for label, attr in components:
            col1 = label + " "*(longest-len(label))
            file.write("%s %d\n" % (col1, getattr(network, attr)))
        else:
            file.write(sep)

#------------------------------------------------------------------------------
#  Standalone call:
#------------------------------------------------------------------------------

if __name__ == "__main__":
    import sys, logging
    logger = logging.getLogger()
    logger.addHandler(logging.StreamHandler(sys.stdout))
    logger.setLevel(logging.DEBUG)

    from matpower_reader import read_matpower
    data_file = "/home/rwl/python/aes/matpower_3.2/case6ww.m"

    n = read_matpower(data_file)

    ReSTWriter(n, "/tmp/test.rst").write()

# EOF -------------------------------------------------------------------------
