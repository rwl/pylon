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

        # Make title
        file.write("="*len(network.name))
        file.write("\n")
        file.write(network.name)
        file.write("\n")
        file.write("="*len(network.name))
        file.write("\n")

        # Section I
        file.write("System Summary\n")
        file.write("--------------")
        file.write("\n")

        self._write_how_many(file)
        self._write_how_much(file)
        self._write_min_max(file)

        file.close()


    def _write_how_many(self, file):
        """ Writes component numbers to a table """

        network = self.network

        # Map component labels to attribute names
        components = [("Bus", "n_buses"), ("Generator", "n_generators"),
            ("Committed Generator", "n_committed_generators"),
            ("Load", "n_loads"), ("Fixed Load", "n_fixed"),
            ("Despatchable Load", "n_despatchable"), ("Shunt", "n_shunts"),
            ("Branch", "n_branches"), ("Transformer", "n_transformers"),
            ("Inter-tie", "n_inter_ties"), ("Area", "n_areas")]

        # Column 1 width
        longest = max([len(c[0]) for c in components])

        col1_header = "Object"
        col1_width = longest
        col2_header = "Quantity"
        col2_width = len(col2_header)

        # Row separator
        sep = "="*col1_width + " " + "="*col2_width + "\n"

        # Row headers
        file.write(sep)

        file.write(col1_header.center(col1_width))
        file.write(" ")
        file.write("%s\n" % col2_header.center(col2_width))

        file.write(sep)

        # Rows
        for label, attr in components:
            col2_value = str(getattr(network, attr))
            file.write("%s %s\n" %
                (label.ljust(col1_width), col2_value.rjust(col2_width))
            )
        else:
            file.write(sep)
            file.write("\n")


    def _write_how_much(self, file):
        """ Write component quantities to a table """

        network = self.network

        col1_header = "Attribute"
        col1_width = 24
        col2_header = "P (MW)"
        col3_header = "Q (MW)"
        col_width = 8

        sep = "="*col1_width +" "+ "="*col_width +" "+ "="*col_width + "\n"

        # Row headers
        file.write(sep)

        file.write("%s" % col1_header.center(col1_width))
        file.write(" ")
        file.write("%s" % col2_header.center(col_width))
        file.write(" ")
        file.write("%s" % col3_header.center(col_width))
        file.write("\n")

        file.write(sep)

        # Rows
        val = getattr(network, "total_gen_capacity")
        file.write("%s %8.1f %8.1f\n" %
            ("Total Gen Capacity".ljust(col1_width), val.real, val.imag))

        val = getattr(network, "online_capacity")
        file.write("%s %8.1f %8.1f\n" %
            ("On-line Capacity".ljust(col1_width), val.real, val.imag))

        val = getattr(network, "generation_actual")
        file.write("%s %8.1f %8.1f\n" %
            ("Generation (actual)".ljust(col1_width), val.real, val.imag))

        val = getattr(network, "load")
        file.write("%s %8.1f %8.1f\n" %
            ("Load".ljust(col1_width), val.real, val.imag))

        val = getattr(network, "fixed_load")
        file.write("%s %8.1f %8.1f\n" %
            ("  Fixed".ljust(col1_width), val.real, val.imag))

        val = getattr(network, "despatchable_load")
        file.write("%s %8.1f %8.1f\n" %
            ("  Despatchable".ljust(col1_width), val.real, val.imag))

        val = getattr(network, "shunt_injection")
        file.write("%s %8.1f %8.1f\n" %
            ("Shunt (inj)".ljust(col1_width), val.real, val.imag))

        val = getattr(network, "losses")
        file.write("%s %8.1f %8.1f\n" %
            ("Losses".ljust(col1_width), val.real, val.imag))

        val = getattr(network, "branch_charging")
        file.write("%s %8.1f %8.1f\n" %
            ("Branch Charging (inj)".ljust(col1_width), val.real, val.imag))

        val = getattr(network, "total_inter_tie_flow")
        file.write("%s %8.1f %8.1f\n" %
            ("Total Inter-tie Flow".ljust(col1_width), val.real, val.imag))

        file.write(sep)
        file.write("\n")


    def _write_min_max(self, file):
        """ Writes minimum and maximum values to a table """

        network = self.network

        col1_header = "Attribute"
        col1_width = 19
        col2_header = "Minimum"
        col3_header = "Maximum"
        col_width = 16

        sep = "="*col1_width +" "+ "="*col_width +" "+ "="*col_width + "\n"

        # Row headers
        file.write(sep)

        file.write("%s" % col1_header.center(col1_width))
        file.write(" ")
        file.write("%s" % col2_header.center(col_width))
        file.write(" ")
        file.write("%s" % col3_header.center(col_width))
        file.write("\n")

        file.write(sep)

        # Rows
        min_val = getattr(network, "min_voltage_amplitude")
        max_val = getattr(network, "max_voltage_amplitude")
        file.write("%s %16.1f %16.1f\n" %
            ("Voltage Amplitude".ljust(col1_width), min_val, max_val))

        min_val = getattr(network, "min_voltage_phase")
        max_val = getattr(network, "max_voltage_phase")
        file.write("%s %16.1f %16.1f\n" %
            ("Voltage Phase Angle".ljust(col1_width), min_val, max_val))

        file.write(sep)
        file.write("\n")

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
