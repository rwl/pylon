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

""" Defines a class for writing case data to a ReStructuredText file.
"""

#------------------------------------------------------------------------------
#  Imports:
#------------------------------------------------------------------------------

from pylon import Case, CaseReport

#------------------------------------------------------------------------------
#  "ReSTWriter" class:
#------------------------------------------------------------------------------

class ReSTWriter(object):
    """ Write case data to a file in ReStructuredText format.
    """

    def __init__(self, include_title=True, include_summary=True,
            include_bus_data=True, include_branch_data=True,
            include_generator_data=True):
        """ Initialises new ReSTWriter instance.
        """
        self.include_title = include_title
        self.include_summary = include_summary
        self.include_bus_data = include_bus_data
        self.include_branch_data = include_branch_data
        self.include_generator_data = include_generator_data

        self.case = None
        self.file_or_filename = ""


    def __call__(self, case, file_or_filename):
        """ Calls the writer with the given case.
        """
        self.write(case, file_or_filename)


    def write(self, case, file_or_filename):
        """ Writes case data to file in ReStructuredText format.
        """
        self.case = case
        self.file_or_filename = file_or_filename

        file = _get_file(file_or_filename)

        self.write_header(case, file)

        # Section II.
        if self.include_bus_data:
            file.write("Bus Data\n")
            file.write("-" * 8 + "\n")
            self.write_bus_data(case, file)
            file.write("\n")

        # Section III.
        if self.include_branch_data:
            file.write("Branch Data\n")
            file.write("-" * 11 + "\n")
            self.write_branch_data(case, file)
            file.write("\n")

        # Section IV
        if self.include_generator_data:
            file.write("Generator Data\n")
            file.write("-" * 14 + "\n")
            self.write_generator_data(case, file)
            file.write("\n")

        # Close if passed the name of a file.
        if isinstance(file_or_filename, basestring):
            file.close()


    def write_header(self, case, file):
        """ Writes the header to file.
        """
        # Document title.
        if self.include_title:
            title = "Power Flow Solution"
            file.write("=" * len(title))
            file.write("\n")
            file.write(title)
            file.write("\n")
            file.write("=" * len(title))
            file.write("\n")

            # Document subtitle.
            subtitle = case.name
            file.write("-" * len(subtitle))
            file.write("\n")
            file.write(subtitle)
            file.write("\n")
            file.write("-" * len(subtitle))
            file.write("\n")

        # Section I.
        if self.include_summary:
            file.write("System Summary\n")
            file.write("-" * 14)
            file.write("\n")

            self.write_how_many(case, file)
            self.write_how_much(case, file)
            self.write_min_max(case, file)


    def write_how_many(self, case=None, file_or_filename=None):
        """ Writes component numbers to a table.
        """
        case = self.case if case is None else case

        report = CaseReport(case)

        if file_or_filename is None:
            file_or_filename = self.file_or_filename

        file = _get_file(file_or_filename)

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

        if isinstance(file_or_filename, basestring):
            file.close()

        del report


    def write_how_much(self, case=None, file_or_filename=None):
        """ Write component quantities to a table.
        """
        case = self.case if case is None else case

        report = CaseReport(case)

        if file_or_filename is None:
            file_or_filename = self.file_or_filename

        file = _get_file(file_or_filename)

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

        if isinstance(file_or_filename, basestring):
            file.close()

        del report


    def write_min_max(self, case=None, file_or_filename=None):
        """ Writes minimum and maximum values to a table.
        """
        case = self.case if case is None else case

        report = CaseReport(case)

        if file_or_filename is None:
            file_or_filename = self.file_or_filename

        file = _get_file(file_or_filename)

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

        if isinstance(file_or_filename, basestring):
            file.close()

        del report


    def write_bus_data(self, case=None, file_or_filename=None):
        """ Writes bus data to a ReST table.
        """
        case = self.case if case is None else case

        report = CaseReport(case)

        buses = case.buses

        if file_or_filename is None:
            file_or_filename = self.file_or_filename

        file = _get_file(file_or_filename)

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
            file.write("%8.3f" % bus.v_magnitude + " ")
            file.write("%8.3f" % bus.v_angle + " ")
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

        if isinstance(file_or_filename, basestring):
            file.close()

        del report


    def write_branch_data(self, case=None, file_or_filename=None):
        """ Writes branch data to a ReST table.
        """
        case = self.case if case is None else case

        report = CaseReport(case)

        branches = case.branches

        if file_or_filename is None:
            file_or_filename = self.file_or_filename

        file = _get_file(file_or_filename)

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

        if isinstance(file_or_filename, basestring):
            file.close()

        del report


    def write_generator_data(self, case=None, file_or_filename=None):
        """ Writes generator data to a ReST table.
        """
        case = self.case if case is None else case

        report = CaseReport(case)

        generators = case.all_generators

        if file_or_filename is None:
            file_or_filename = self.file_or_filename

        file = _get_file(file_or_filename)

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
        file.write("Pmax bid".center(col_width) + " ")
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
            file.write("%8.2f" % each.p_max_bid + " ")
            n2, n1, n = each.cost_coeffs
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

        if isinstance(file_or_filename, basestring):
            file.close()

        del report

#------------------------------------------------------------------------------
#  "ReSTExperimentWriter" class:
#------------------------------------------------------------------------------

class ReSTExperimentWriter(object):
    """ Writes market experiment data to file in ReStructuredText format.
    """

    def __init__(self, include_state=True, include_action=True,
                                           include_reward=True):
        """ Initialises a new ReSTExperimentWriter instance.
        """
        # Sections to include.
        self.include_state  = include_state
        self.include_action = include_action
        self.include_reward = include_reward

        # Market experiment whose data is to be written.
        self.experiment = None

        # File object or name of a file to be written to.
        self.file_or_filename = None


    def __call__(self, experiment, file_or_filename):
        """ Writes market experiment data to file in ReStructuredText format.
        """
        self.experiment = experiment
        self.file_or_filename = file_or_filename

        file = _get_file(file_or_filename)

        # Write environment state data.
        if self.include_state:
            file.write("State\n")
            file.write( ("-" * 5) + "\n")

            self.write_state_data(experiment, file)

        # Write action data.
        if self.include_action:
            file.write("Action\n")
            file.write( ("-" * 6) + "\n")

            self.write_action_data(experiment, file)

        # Write reward data.
        if self.include_reward:
            file.write("Reward\n")
            file.write( ("-" * 6) + "\n")

            self.write_reward_data(experiment, file)

        if isinstance(file_or_filename, basestring):
            file.close()


    def write_state_data(self, experiment, file_or_filename):
        """ Writes the state history for each agent in a market experiment
            to a ReST table.
        """
        file = _get_file(file_or_filename)

        self._write_data_table(experiment, file, type="state")

        if isinstance(file_or_filename, basestring):
            file.close()


    def write_action_data(self, experiment, file_or_filename):
        """ Writes the action history for each agent in a market experiment
            to a ReST table.
        """
        file = _get_file(file_or_filename)

        self._write_data_table(experiment, file, type="action")

        if isinstance(file_or_filename, basestring):
            file.close()


    def write_reward_data(self, experiment, file_or_filename):
        """ Writes the reward history for each agent in a market experiment
            to a ReST table.
        """
        file = _get_file(file_or_filename)

        self._write_data_table(experiment, file, type="reward")

        if isinstance(file_or_filename, basestring):
            file.close()


    def _write_data_table(self, experiment, file_or_filename, type):
        """ Writes agent data to an ReST table.  The 'type' argument may
            be 'state', 'action' or 'reward'.
        """
        agents = experiment.agents
        n_agents = len(experiment.agents)

        file = _get_file(file_or_filename)

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
            rows, cols = agents[0].history.getField( type ).shape
        else:
            rows, cols = (0, 0)

        for sequence in range( min(rows, 999) ):
            file.write( str(sequence + 1).rjust(idx_col_width) + " " )

            for agent in agents:
                field = agent.history.getField( type )
                # FIXME: Handle multiple state values.
                file.write("%8.3f " % field[sequence, 0])

            file.write("\n")

        file.write(sep)


def _get_file(file_or_filename):
    """ Returns an open file from a file or a filename.
    """
    if isinstance(file_or_filename, basestring):
        file = open(file_or_filename, "wb")
    else:
        file = file_or_filename

    return file

# EOF -------------------------------------------------------------------------
