#------------------------------------------------------------------------------
# Copyright (C) 2010 Richard Lincoln
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

""" Defines a class for writing case data to a ReStructuredText file.
"""

#------------------------------------------------------------------------------
#  Imports:
#------------------------------------------------------------------------------

from pylon import CaseReport
from pylon.readwrite.common import CaseWriter

#------------------------------------------------------------------------------
#  "ReSTWriter" class:
#------------------------------------------------------------------------------

class ReSTWriter(CaseWriter):
    """ Write case data to a file in ReStructuredText format.
    """

    #--------------------------------------------------------------------------
    #  "CaseWriter" interface:
    #--------------------------------------------------------------------------

    def _write_data(self, file):
        """ Writes case data to file in ReStructuredText format.
        """
#        self.write_case_data(file)

        file.write("Bus Data\n")
        file.write("-" * 8 + "\n")
        self.write_bus_data(file)
        file.write("\n")

        file.write("Branch Data\n")
        file.write("-" * 11 + "\n")
        self.write_branch_data(file)
        file.write("\n")

        file.write("Generator Data\n")
        file.write("-" * 14 + "\n")
        self.write_generator_data(file)
        file.write("\n")


    def write_case_data(self, file):
        """ Writes the header to file.
        """
        title = "Power Flow Solution"
        file.write("=" * len(title))
        file.write("\n")
        file.write(title)
        file.write("\n")
        file.write("=" * len(title))
        file.write("\n")

        # Document subtitle.
        subtitle = self.case.name
        file.write("-" * len(subtitle))
        file.write("\n")
        file.write(subtitle)
        file.write("\n")
        file.write("-" * len(subtitle))
        file.write("\n")

        file.write("System Summary\n")
        file.write("-" * 14)
        file.write("\n")

        self.write_how_many(file)
        self.write_how_much(file)
        self.write_min_max(file)


    def write_bus_data(self, file):
        """ Writes bus data to a ReST table.
        """
        report = CaseReport(self.case)

        buses = self.case.buses

        col_width = 8
        col_width_2 = col_width*2+1
        col1_width = 6

        sep = "=" * 6 + " " + ("=" * col_width + " ") * 6 + "\n"

        file.write(sep)

        # Line one of column headers
        file.write("Name".center(col1_width) + " ")
        file.write("Voltage (pu)".center(col_width_2) + " ")
        file.write("Generation".center(col_width_2) + " ")
        file.write("Load".center(col_width_2) + " ")
        file.write("\n")

        file.write("-" * col1_width +" "+ ("-" * col_width_2 + " ") * 3 + "\n")

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
            file.write("%8.3f" % bus.v_magnitude + " ")
            file.write("%8.3f" % bus.v_angle + " ")
            file.write("%8.2f" % self.case.s_supply(bus).real + " ")
            file.write("%8.2f" % self.case.s_supply(bus).imag + " ")
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

        del report


    def write_branch_data(self, file):
        """ Writes branch data to a ReST table.
        """
        report = CaseReport(self.case)

        branches = self.case.branches

        col_width   = 8
        col_width_2 = col_width*2+1
        col1_width  = 7

        sep = ("="*7 + " ")*3 + ("="*col_width + " ")*6 + "\n"

        file.write(sep)

        # Line one of column headers
        file.write("Name".center(col1_width) + " ")
        file.write("From".center(col1_width) + " ")
        file.write("To".center(col1_width) + " ")
        file.write("From Bus Inj".center(col_width_2) + " ")
        file.write("To Bus Inj".center(col_width_2) + " ")
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
            file.write(each.from_bus.name[:col1_width].ljust(col1_width)+" ")
            file.write(each.to_bus.name[:col1_width].ljust(col1_width)+" ")
            file.write("%8.2f" % each.p_from + " ")
            file.write("%8.2f" % each.q_from + " ")
            file.write("%8.2f" % each.p_to + " ")
            file.write("%8.2f" % each.q_to + " ")
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

        del report


    def write_generator_data(self, file):
        """ Writes generator data to a ReST table.
        """
        report = CaseReport(self.case)

        generators = self.case.generators

        col_width   = 8
        col_width_2 = col_width*2+1
        col1_width  = 6
        col_width_bool = 3
        col_width_poly = 4
        col_width_3 = col_width_poly*3+2

        sep = ("=" * col1_width + " ") * 2 + ("=" * col_width_bool + " ") + \
            ("=" * col_width + " ") * 5 + \
            ("=" * col_width_poly + " ") * 3 + "\n"

        file.write(sep)

        # Line one of column headers.
        file.write("Name".center(col1_width) + " ")
        file.write("Bus".center(col1_width) + " ")
        file.write("On".center(col_width_bool) + " ")
        file.write("Voltage".center(col_width) + " ")
        file.write("Pg".center(col_width) + " ")
        file.write("Qg".center(col_width) + " ")
#        file.write("Lambda ($/MVA-hr)".center(col_width_2) + " ")
        file.write("Active Power".center(col_width_2) + " ")
        file.write("Polynomial".center(col_width_3) + " ")
        file.write("\n")

        file.write(("-" * col1_width + " ") * 2)
        file.write(("-" * col_width_bool + " "))
        file.write(("-" * col_width + " ") * 3)
        file.write(("-" * col_width_2 + " "))
        file.write(("-" * col_width_3 + " ") + "\n")

        # Line two of column header
        file.write("..".ljust(col1_width) + " ")
        file.write("..".ljust(col1_width) + " ")
        file.write("..".ljust(col_width_bool) + " ")
        file.write("..".ljust(col_width) + " ")
        file.write("(MW)".center(col_width) + " ")
        file.write("(MVAr)".center(col_width) + " ")
        file.write("Pmax".center(col_width) + " ")
        file.write("Pmin".center(col_width) + " ")
        file.write("c2".center(col_width_poly) + " ")
        file.write("c1".center(col_width_poly) + " ")
        file.write("c0".center(col_width_poly) + " ")
        file.write("\n")

        file.write(sep)

        # Branch rows.
        for each in generators:
            file.write(each.name[:col1_width].ljust(col1_width) + " ")
            file.write("..".ljust(col1_width) + " ")
            if each.online:
                file.write("1".center(col_width_bool) + " ")
            else:
                file.write("0".center(col_width_bool) + " ")
            file.write("%8.2f" % each.v_magnitude + " ")
            file.write("%8.2f" % each.p + " ")
            file.write("%8.2f" % each.q + " ")
#            file.write("..".ljust(col_width) + " ")
#            file.write("..".ljust(col_width) + " ")
            file.write("%8.2f" % each.p_max + " ")
            file.write("%8.2f" % each.p_min + " ")
            n2, n1, n = each.p_cost
            file.write("%4.2f" % n2 + " ")
            file.write("%4.1f" % n1 + " ")
            file.write("%4.0f" % n + " ")
            file.write("\n")

        # Totals.
        file.write(("..".ljust(col1_width) +  " ") * 2)
        file.write(("..".ljust(col_width_bool) +  " "))
        file.write("*Total:*".rjust(col1_width) + " ")
        capacity = getattr(report, "online_capacity")
        file.write("%8.2f" % capacity.real + " ")
        file.write("%8.2f" % capacity.imag + " ")
        file.write(("..".ljust(col_width) + " ") * 2)
        file.write(("..".ljust(col_width_poly) + " ") * 3)
        file.write("\n")

        file.write(sep)

        del report

    #--------------------------------------------------------------------------
    #  "ReSTWriter" interface:
    #--------------------------------------------------------------------------

    def write_how_many(self, file):
        """ Writes component numbers to a table.
        """
        report = CaseReport(self.case)

        # Map component labels to attribute names
        components = [("Bus", "n_buses"), ("Generator", "n_generators"),
            ("Committed Generator", "n_committed_generators"),
            ("Load", "n_loads"), ("Fixed Load", "n_fixed"),
            ("Despatchable Load", "n_despatchable"),# ("Shunt", "n_shunts"),
            ("Branch", "n_branches"),# ("Transformer", "n_transformers"),
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

        del report


    def write_how_much(self, file):
        """ Write component quantities to a table.
        """
        report = CaseReport(self.case)

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

        del report


    def write_min_max(self, file):
        """ Writes minimum and maximum values to a table.
        """
        report = CaseReport(self.case)

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

        del report

#------------------------------------------------------------------------------
#  "ReSTExperimentWriter" class:
#------------------------------------------------------------------------------

class ReSTExperimentWriter(object):
    """ Writes market experiment data to file in ReStructuredText format.
    """

    def __init__(self, experiment):
        """ Initialises a new ReSTExperimentWriter instance.
        """
        # Market experiment whose data is to be written.
        self.experiment = None


    def write(self, file):
        """ Writes market experiment data to file in ReStructuredText format.
        """
        # Write environment state data.
        file.write("State\n")
        file.write( ("-" * 5) + "\n")
        self.write_data_table(file, type="state")

        # Write action data.
        file.write("Action\n")
        file.write( ("-" * 6) + "\n")
        self.write_data_table(file, type="action")

        # Write reward data.
        file.write("Reward\n")
        file.write( ("-" * 6) + "\n")
        self.write_data_table(file, type="reward")


    def write_data_table(self, file, type):
        """ Writes agent data to an ReST table.  The 'type' argument may
            be 'state', 'action' or 'reward'.
        """
        agents = self.experiment.agents
        n_agents = len(self.experiment.agents)

        col_width = 8
        idx_col_width = 3

        sep = ("=" * idx_col_width) + " " + \
            ("=" * col_width + " ") * n_agents + "\n"

        file.write(sep)

        # Table column headers.
        file.write("..".rjust(idx_col_width) + " ")
        for agent in agents:
            # The end of the name is typically the unique part.
            file.write(agent.name[-col_width:].center(col_width) + " ")
        file.write("\n")

        file.write(sep)

        # Table values.
        if agents:
            rows, _ = agents[0].history.getField( type ).shape
        else:
            rows, _ = (0, 0)

        for sequence in range( min(rows, 999) ):
            file.write( str(sequence + 1).rjust(idx_col_width) + " " )

            for agent in agents:
                field = agent.history.getField( type )
                # FIXME: Handle multiple state values.
                file.write("%8.3f " % field[sequence, 0])

            file.write("\n")

        file.write(sep)

# EOF -------------------------------------------------------------------------
