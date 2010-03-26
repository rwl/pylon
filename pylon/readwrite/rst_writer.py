#------------------------------------------------------------------------------
# Copyright (C) 2010 Richard Lincoln
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

""" Defines a class for writing case data to a ReStructuredText file.
"""

#------------------------------------------------------------------------------
#  Imports:
#------------------------------------------------------------------------------

from pylon.util import CaseReport
from pylon.generator import POLYNOMIAL
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
        self.write_case_data(file)

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
#        title = "Power Flow Solution"
#        file.write("=" * len(title))
#        file.write("\n")
#        file.write("\n%s\n" % title)
#        file.write("=" * len(title))
#        file.write("\n")

        # Document subtitle.
        subtitle = self.case.name
        file.write("-" * len(subtitle))
        file.write("\n%s\n" % subtitle)
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
        col_width_2 = col_width * 2 + 1
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
            file.write(bus.name[:col1_width].ljust(col1_width))
            file.write(" %8.3f" % bus.v_magnitude)
            file.write(" %8.3f" % bus.v_angle)
            file.write(" %8.2f" % self.case.s_supply(bus).real)
            file.write(" %8.2f" % self.case.s_supply(bus).imag)
            file.write(" %8.2f" % self.case.s_demand(bus).real)
            file.write(" %8.2f" % self.case.s_demand(bus).imag)
            file.write("\n")

        # Totals
#        file.write("..".ljust(col1_width) + " ")
#        file.write(("..".ljust(col_width) + " ")*2)
#        file.write(("_"*col_width + " ")*4 + "\n")
        file.write("..".ljust(col1_width) + " " + "..".ljust(col_width) + " ")
        file.write("*Total:*".rjust(col_width) + " ")
        ptot = report.actual_pgen
        qtot = report.actual_qgen
        file.write("%8.2f " % ptot)
        file.write("%8.2f " % qtot)
        file.write("%8.2f " % report.p_demand)
        file.write("%8.2f " % report.q_demand)
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

        sep = ("=" * 7 + " ") * 3 + ("=" * col_width + " ") * 6 + "\n"

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
        loss = report._loss()
        for each in branches:
            file.write(each.name[:col1_width].ljust(col1_width) + " ")
            file.write(each.from_bus.name[:col1_width].ljust(col1_width)+" ")
            file.write(each.to_bus.name[:col1_width].ljust(col1_width)+" ")
            file.write("%8.2f " % each.p_from)
            file.write("%8.2f " % each.q_from)
            file.write("%8.2f " % each.p_to)
            file.write("%8.2f " % each.q_to)
            file.write("%8.2f " % loss.real[each._i])
            file.write("%8.2f " % loss.imag[each._i])
            file.write("\n")

        # Totals
#        file.write("..".ljust(col1_width) + " ")
#        file.write(("..".ljust(col_width) + " ")*2)
#        file.write(("_"*col_width + " ")*4 + "\n")
        file.write(("..".ljust(col1_width) + " ")*3)
        file.write(("..".ljust(col_width) + " ")*3)
        file.write("*Total:*".rjust(col_width) + " ")
        pl, ql = report.losses
        file.write("%8.2f " % pl)
        file.write("%8.2f " % ql)
        file.write("\n")

        file.write(sep)

        del report


    def write_generator_data(self, file):
        """ Writes generator data to a ReST table.
        """
        report = CaseReport(self.case)
        generators = self.case.generators

        col_width = 8
        col_width_2 = col_width*2+1
        col1_width = 6
        col_width_bool = 3
        col_width_poly = 4
        col_width_3 = col_width_poly*3+2

        sep = ("=" * col1_width + " ") * 2 + \
            ("=" * col_width_bool + " ") + \
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
            if each.pcost_model == POLYNOMIAL:
                file.write("%4.2f %4.1f %4.0f" % each.p_cost)
            file.write("\n")

        # Totals.
        file.write(("..".ljust(col1_width) +  " ") * 2)
        file.write(("..".ljust(col_width_bool) +  " "))
        file.write("*Total:*".rjust(col1_width) + " ")
        ptot = getattr(report, "actual_pgen")
        qtot = getattr(report, "actual_qgen")
        file.write("%8.2f " % ptot)
        file.write("%8.2f " % qtot)
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
            ("Committed Generator", "n_online_generators"),
            ("Load", "n_loads"), ("Fixed Load", "n_fixed_loads"),
            ("Despatchable Load", "n_online_vloads"), ("Shunt", "n_shunts"),
            ("Branch", "n_branches"), ("Transformer", "n_transformers"),
            ("Inter-tie", "n_interties"), ("Area", "n_areas")
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
        pgen = getattr(report, "total_pgen_capacity")
        qmin, qmax = getattr(report, "total_qgen_capacity")
        file.write("%s %8.1f %4.1f to %4.1f\n" %
            ("Total Gen Capacity".ljust(col1_width), pgen, qmin, qmax))

        pgen = getattr(report, "online_pgen_capacity")
        qmin, qmax = getattr(report, "online_qgen_capacity")
        file.write("%s %8.1f %4.1f to %4.1f\n" %
            ("On-line Capacity".ljust(col1_width), pgen, qmin, qmax))

        pgen = getattr(report, "actual_pgen")
        qgen = getattr(report, "actual_qgen")
        file.write("%s %8.1f %8.1f\n" %
            ("Generation (actual)".ljust(col1_width), pgen, qgen))

        pd = getattr(report, "p_demand")
        qd = getattr(report, "q_demand")
        file.write("%s %8.1f %8.1f\n" %
            ("Load".ljust(col1_width), pd, qd))

        pd = getattr(report, "fixed_p_demand")
        qd = getattr(report, "fixed_q_demand")
        file.write("%s %8.1f %8.1f\n" %
            ("  Fixed".ljust(col1_width), pd, qd))

        pd, pmin = getattr(report, "vload_p_demand")
        qd = getattr(report, "vload_q_demand")
        file.write("%s %4.1f of %4.1f %8.1f\n" %
            ("  Despatchable".ljust(col1_width), pd, pmin, qd))

        pinj = getattr(report, "shunt_pinj")
        qinj = getattr(report, "shunt_qinj")
        file.write("%s %8.1f %8.1f\n" %
            ("Shunt (inj)".ljust(col1_width), pinj, qinj))

        pl, ql = getattr(report, "losses")
        file.write("%s %8.1f %8.1f\n" %
            ("Losses (I^2 * Z)".ljust(col1_width), pl, ql))

        qinj = getattr(report, "branch_qinj")
        file.write("%s %8s %8.1f\n" %
            ("Branch Charging (inj)".ljust(col1_width), "-", qinj))

        pval = getattr(report, "total_tie_pflow")
        qval = getattr(report, "total_tie_qflow")
        file.write("%s %8.1f %8.1f\n" %
            ("Total Inter-tie Flow".ljust(col1_width), pval, qval))

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
        col_width   = 22

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
        min_val, min_i = getattr(report, "min_v_magnitude")
        max_val, max_i = getattr(report, "max_v_magnitude")
        file.write("%s %7.3f p.u. @ bus %2d %7.3f p.u. @ bus %2d\n" %
            ("Voltage Amplitude".ljust(col1_width),
             min_val, min_i, max_val, max_i))

        min_val, min_i = getattr(report, "min_v_angle")
        max_val, max_i = getattr(report, "max_v_angle")
        file.write("%s %16.3f %16.3f\n" %
            ("Voltage Phase Angle".ljust(col1_width), min_val, max_val))

        file.write(sep)
        file.write("\n")

        del report

# EOF -------------------------------------------------------------------------
