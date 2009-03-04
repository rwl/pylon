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

""" Defines a class for writing network data to a ReStructuredText file.
"""

#------------------------------------------------------------------------------
#  Imports:
#------------------------------------------------------------------------------

from pylon.network import Network, NetworkReport

#------------------------------------------------------------------------------
#  "ReSTWriter" class:
#------------------------------------------------------------------------------

class ReSTWriter:
    """ Write network data to a file in ReStructuredText format """

    network = None

    file_or_filename = ""

    _report = None

    def __init__(self, network, file_or_filename):
        assert isinstance(network, Network)

        self.network = network
        self.file_or_filename = file_or_filename
        self._report = NetworkReport(network)


    def write(self):
        """ Writes network data to file in ReStructuredText format """

        network = self.network
        file_or_filename = self.file_or_filename

        if isinstance(file_or_filename, basestring):
            file = open(file_or_filename, "wb")
        else:
            file = file_or_filename

        # Document title
        title = "Power Flow Solution"
        file.write("=" * len(title))
        file.write("\n")
        file.write(title)
        file.write("\n")
        file.write("=" * len(title))
        file.write("\n")

        # Document subtitle
        subtitle = network.name
        file.write("-" * len(subtitle))
        file.write("\n")
        file.write(subtitle)
        file.write("\n")
        file.write("-" * len(subtitle))
        file.write("\n")

        # Section I
        file.write("System Summary\n")
        file.write("-" * 14)
        file.write("\n")

        self._write_how_many(file)
        self._write_how_much(file)
        self._write_min_max(file)

        # Section II
        file.write("Bus Data\n")
        file.write("-" * 8 + "\n")
        self._write_bus_data(file)
        file.write("\n")

        # Section III
        file.write("Branch Data\n")
        file.write("-" * 11 + "\n")
        self._write_branch_data(file)
        file.write("\n")

        # Section IV
        file.write("Generator Data\n")
        file.write("-" * 14 + "\n")
        self._write_generator_data(file)
        file.write("\n")

        # Only close if passed a file name.
        if isinstance(file_or_filename, basestring):
            file.close()


    def _write_how_many(self, file):
        """ Writes component numbers to a table.
        """
        report = self._report

        # Map component labels to attribute names
        components = [("Bus", "n_buses"), ("Generator", "n_generators"),
            ("Committed Generator", "n_committed_generators"),
            ("Load", "n_loads"), ("Fixed Load", "n_fixed"),
            ("Despatchable Load", "n_despatchable"),# ("Shunt", "n_shunts"),
            ("Branch", "n_branches"), ("Transformer", "n_transformers"),
#            ("Inter-tie", "n_inter_ties"), ("Area", "n_areas")
        ]

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
            col2_value = str(getattr(report, attr))
            file.write("%s %s\n" %
                (label.ljust(col1_width), col2_value.rjust(col2_width)))
        else:
            file.write(sep)
            file.write("\n")


    def _write_how_much(self, file):
        """ Write component quantities to a table.
        """
        report = self._report

        col1_header = "Attribute"
        col1_width  = 24
        col2_header = "P (MW)"
        col3_header = "Q (MVAr)"
        col_width   = 8

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
        val = getattr(report, "total_gen_capacity")
        file.write("%s %8.1f %8.1f\n" %
            ("Total Gen Capacity".ljust(col1_width), val.real, val.imag))

        val = getattr(report, "online_capacity")
        file.write("%s %8.1f %8.1f\n" %
            ("On-line Capacity".ljust(col1_width), val.real, val.imag))

        val = getattr(report, "generation_actual")
        file.write("%s %8.1f %8.1f\n" %
            ("Generation (actual)".ljust(col1_width), val.real, val.imag))

        val = getattr(report, "load")
        file.write("%s %8.1f %8.1f\n" %
            ("Load".ljust(col1_width), val.real, val.imag))

        val = getattr(report, "fixed_load")
        file.write("%s %8.1f %8.1f\n" %
            ("  Fixed".ljust(col1_width), val.real, val.imag))

        val = getattr(report, "despatchable_load")
        file.write("%s %8.1f %8.1f\n" %
            ("  Despatchable".ljust(col1_width), val.real, val.imag))

#        val = getattr(report, "shunt_injection")
#        file.write("%s %8.1f %8.1f\n" %
#            ("Shunt (inj)".ljust(col1_width), val.real, val.imag))

        val = getattr(report, "losses")
        file.write("%s %8.1f %8.1f\n" %
            ("Losses".ljust(col1_width), val.real, val.imag))

        val = getattr(report, "branch_charging")
        file.write("%s %8.1f %8.1f\n" %
            ("Branch Charging (inj)".ljust(col1_width), val.real, val.imag))

#        val = getattr(report, "total_inter_tie_flow")
#        file.write("%s %8.1f %8.1f\n" %
#            ("Total Inter-tie Flow".ljust(col1_width), val.real, val.imag))

        file.write(sep)
        file.write("\n")


    def _write_min_max(self, file):
        """ Writes minimum and maximum values to a table.
        """
        report = self._report

        col1_header = "Attribute"
        col1_width  = 19
        col2_header = "Minimum"
        col3_header = "Maximum"
        col_width   = 16

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
        min_val = getattr(report, "min_voltage_amplitude")
        max_val = getattr(report, "max_voltage_amplitude")
        file.write("%s %16.1f %16.1f\n" %
            ("Voltage Amplitude".ljust(col1_width), min_val, max_val))

        min_val = getattr(report, "min_voltage_phase")
        max_val = getattr(report, "max_voltage_phase")
        file.write("%s %16.1f %16.1f\n" %
            ("Voltage Phase Angle".ljust(col1_width), min_val, max_val))

        file.write(sep)
        file.write("\n")


    def _write_bus_data(self, file):
        """ Writes bus data to a ReST table.
        """
        network = self.network
        buses   = network.buses
        report  = self._report

        col_width = 8
        col_width_2 = col_width*2+1
        col1_width = 6

        sep = "="*6 + " " + ("="*col_width + " ")*6 + "\n"

        file.write(sep)

        # Line one of column headers
        file.write("Name".center(col1_width) + " ")
        file.write("Voltage (pu)".center(col_width_2) + " ")
        file.write("Generation".center(col_width_2) + " ")
        file.write("Load".center(col_width_2) + " ")
        file.write("\n")

        file.write("-"*col1_width +" "+ ("-"*col_width_2 +" ")*3 + "\n")

        # Line two of column header
        file.write("..".ljust(col1_width) + " ")
        file.write("Amp".center(col_width) + " ")
        file.write("Phase".center(col_width) + " ")
        file.write("P (MW)".center(col_width) + " ")
        file.write("Q (MVAr)".center(col_width) + " ")
        file.write("P (MW)".center(col_width) + " ")
        file.write("Q (MVAr)".center(col_width) + " ")
        file.write("\n")

        file.write(sep)

        # Bus rows
        for bus in buses:
            file.write(bus.name[:col1_width].ljust(col1_width) + " ")
            file.write("%8.3f" % bus.v_amplitude + " ")
            file.write("%8.3f" % bus.v_phase + " ")
            file.write("%8.2f" % bus.p_supply + " ")
            file.write("%8.2f" % bus.q_supply + " ")
            file.write("%8.2f" % bus.p_demand + " ")
            file.write("%8.2f" % bus.q_demand + " ")
            file.write("\n")

        # Totals
#        file.write("..".ljust(col1_width) + " ")
#        file.write(("..".ljust(col_width) + " ")*2)
#        file.write(("_"*col_width + " ")*4 + "\n")
        file.write("..".ljust(col1_width) + " " + "..".ljust(col_width) + " ")
        file.write("*Total:*".rjust(col_width) + " ")
        val = report.total_gen_capacity
        file.write("%8.2f" % val.real + " ")
        file.write("%8.2f" % val.imag + " ")
        val = report.load
        file.write("%8.2f" % val.real + " ")
        file.write("%8.2f" % val.imag + " ")
        file.write("\n")

        file.write(sep)


    def _write_branch_data(self, file):
        """ Writes branch data to a ReST table.
        """
        network  = self.network
        branches = network.branches
        report   = self._report

        col_width   = 8
        col_width_2 = col_width*2+1
        col1_width  = 7

        sep = ("="*7 + " ")*3 + ("="*col_width + " ")*6 + "\n"

        file.write(sep)

        # Line one of column headers
        file.write("Name".center(col1_width) + " ")
        file.write("Source".center(col1_width) + " ")
        file.write("Target".center(col1_width) + " ")
        file.write("Source Bus Inj".center(col_width_2) + " ")
        file.write("Target Bus Inj".center(col_width_2) + " ")
        file.write("Loss (I^2 * Z)".center(col_width_2) + " ")
        file.write("\n")

        file.write(("-"*col1_width +" ")*3)
        file.write(("-"*col_width_2 +" ")*3 + "\n")

        # Line two of column header
        file.write("..".ljust(col1_width) + " ")
        file.write("Bus".center(col1_width) + " ")
        file.write("Bus".center(col1_width) + " ")
        file.write("P (MW)".center(col_width) + " ")
        file.write("Q (MVAr)".center(col_width) + " ")
        file.write("P (MW)".center(col_width) + " ")
        file.write("Q (MVAr)".center(col_width) + " ")
        file.write("P (MW)".center(col_width) + " ")
        file.write("Q (MVAr)".center(col_width) + " ")
        file.write("\n")

        file.write(sep)

        # Branch rows
        for each in branches:
            file.write(each.name[:col1_width].ljust(col1_width) + " ")
            file.write(each.source_bus.name[:col1_width].ljust(col1_width)+" ")
            file.write(each.target_bus.name[:col1_width].ljust(col1_width)+" ")
            file.write("%8.2f" % each.p_source + " ")
            file.write("%8.2f" % each.q_source + " ")
            file.write("%8.2f" % each.p_target + " ")
            file.write("%8.2f" % each.p_target + " ")
            file.write("%8.2f" % each.p_losses + " ")
            file.write("%8.2f" % each.q_losses + " ")
            file.write("\n")

        # Totals
#        file.write("..".ljust(col1_width) + " ")
#        file.write(("..".ljust(col_width) + " ")*2)
#        file.write(("_"*col_width + " ")*4 + "\n")
        file.write(("..".ljust(col1_width) + " ")*3)
        file.write(("..".ljust(col_width) + " ")*3)
        file.write("*Total:*".rjust(col_width) + " ")
        val = report.losses
        file.write("%8.2f" % val.real + " ")
        file.write("%8.2f" % val.imag + " ")
        file.write("\n")

        file.write(sep)


    def _write_generator_data(self, file):
        """ Writes generator data to a ReST table.
        """
        network    = self.network
        generators = network.all_generators
        report     = self._report

        col_width   = 8
        col_width_2 = col_width*2+1
        col1_width  = 6

        sep = ("=" * col1_width + " ") * 3 + ("=" * col_width + " ") * 4 + "\n"

        file.write(sep)

        # Line one of column headers
        file.write("Name".center(col1_width) + " ")
        file.write("Bus".center(col1_width) + " ")
        file.write("Status".center(col1_width) + " ")
        file.write("Pg".center(col_width) + " ")
        file.write("Qg".center(col_width) + " ")
        file.write("Lambda ($/MVA-hr)".center(col_width_2) + " ")
        file.write("\n")

        file.write(("-" * col1_width + " ") * 3)
        file.write(("-" * col_width + " ") * 2)
        file.write(("-" * col_width_2 + " ") * 1 + "\n")

        # Line two of column header
        file.write("..".ljust(col1_width) + " ")
        file.write("..".ljust(col1_width) + " ")
        file.write("..".ljust(col1_width) + " ")
        file.write("(MW)".center(col_width) + " ")
        file.write("(MVAr)".center(col_width) + " ")
        file.write("P".center(col_width) + " ")
        file.write("Q".center(col_width) + " ")
        file.write("\n")

        file.write(sep)

        # Branch rows
        for each in generators:
            file.write(each.name[:col1_width].ljust(col1_width) + " ")
            file.write("..".ljust(col1_width) + " ")
            file.write(str(each.online)[:col1_width].ljust(col1_width) + " ")
            file.write("%8.2f" % each.p + " ")
            file.write("%8.2f" % each.q + " ")
            file.write("..".ljust(col_width) + " ")
            file.write("..".ljust(col_width) + " ")
            file.write("\n")

        file.write(sep)

        # Totals
        file.write(("..".ljust(col1_width) +  " ") * 2)
        file.write("*Tot:*".rjust(col1_width) + " ")
        capacity = getattr(report, "online_capacity")
        file.write("%8.2f" % capacity.real + " ")
        file.write("%8.2f" % capacity.imag + " ")
        file.write(("..".ljust(col_width) + " ") * 2)
        file.write("\n")

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
