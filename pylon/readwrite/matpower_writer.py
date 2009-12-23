#------------------------------------------------------------------------------
# Copyright (C) 2009 Richard Lincoln
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

""" Defines classes for writing MATPOWER data files.
"""

#------------------------------------------------------------------------------
#  Imports:
#------------------------------------------------------------------------------

from os.path import basename, splitext

from pylon.readwrite.common import CaseWriter

#------------------------------------------------------------------------------
#  "MATPOWERWriter" class:
#------------------------------------------------------------------------------

class MATPOWERWriter(CaseWriter):
    """ Write case data to a file in MATPOWER format.
    """

    #--------------------------------------------------------------------------
    #  "object" interface:
    #--------------------------------------------------------------------------

    def __init__(self, case):
        """ Initialises a new MATPOWERWriter instance.
        """
        super(MATPOWERWriter, self).__init__(case)

        # Function name must match the file name in MATLAB.
        self.func_name = case.name

    #--------------------------------------------------------------------------
    #  "CaseWriter" interface:
    #--------------------------------------------------------------------------

    def write(self, file_or_filename):
        """ Writes case data to file in MATPOWER format.
        """
        if isinstance(file_or_filename, basestring):
            self.func_name, _ = splitext(basename(file_or_filename))
        else:
            self.func_name = self.case.name

        super(MATPOWERWriter, self).write(file_or_filename)


    def _write_data(self, file):
        super(MATPOWERWriter, self)._write_data(file)
        self.write_area_data(file)
        file.write("return;\n")


    def write_case_data(self, file):
        """ Writes the case data in MATPOWER format.
        """
        file.write("function [baseMVA, bus, gen, branch, areas, gencost] = ")
        file.write("%s\n\n" % self.func_name)

        file.write("%%-----  Power Flow Data  -----%%\n")
        file.write("%% System MVA base\n")
        file.write("baseMVA = %.1f;\n\n" % self.case.base_mva)


    def write_bus_data(self, file):
        """ Writes bus data in MATPOWER format.
        """
        labels = ["bus_id", "type", "Pd", "Qd", "Gs", "Bs", "area", "Vm", "Va",
            "baseKV", "zone", "Vmax", "Vmin"]

        base_mva = self.case.base_mva

        buses_data = [None] * len(self.case.buses)
        for i, v in enumerate(self.case.buses):
            v_data = {}
            v_data["bus_id"] = i + 1
            if v.type == "PQ":
                bustype = 1
            elif v.type == "PV":
                bustype = 2
            elif v.type == "ref":
                bustype = 3
            else:
                raise ValueError
            v_data["type"] = bustype
            v_data["Pd"] = v.p_demand * base_mva
            v_data["Qd"] = v.q_demand * base_mva
            v_data["Gs"] = v.g_shunt
            v_data["Bs"] = v.b_shunt
            # TODO: Implement areas
            v_data["area"] = 1
            v_data["Vm"] = v.v_magnitude_guess
            v_data["Va"] = v.v_angle_guess
            v_data["baseKV"] = v.v_base
            v_data["zone"] = v.zone
            v_data["Vmax"] = v.v_max
            v_data["Vmin"] = v.v_min

            # Convert all values to strings
            for key in v_data.keys():
                v_data[key] = str(v_data[key])

            buses_data[i] = v_data

        file.write("%% bus data" + "\n")

        file.write("%\t")
        for label in labels:
            file.write("%-8s" % label)
        file.write("\n")

        file.write("bus = [" + "\n")

        for v_data in buses_data:
            file.write("\t")
            for label in labels:
                if label != labels[-1]:
                    file.write("%-8s" % v_data[label])
                else:
                    file.write("%s" % v_data[label])
            file.write(";" + "\n")

        file.write("];" + "\n")


    def write_generator_data(self, file):
        """ Writes generator data in MATPOWER format.
        """
        labels = ["bus", "Pg", "Qg", "Qmax", "Qmin", "Vg", "mBase", "status",
            "Pmax", "Pmin"]

        generators_data = [None] * len(self.case.generators)
        for i, g in enumerate(self.case.generators):
            g_data = {}
            g_base = g.base_mva
            # FIXME: Need faster way to find generator bus index
            g_data["bus"] = 1 # Failsafe value
            if g in self.case.generators:
                g_data["bus"] = self.case.buses.index(g.bus) + 1
            g_data["Pg"] = g.p * g_base
            g_data["Qg"] = g.q * g_base
            g_data["Qmax"] = g.q_max * g_base
            g_data["Qmin"] = g.q_min * g_base
            g_data["Vg"] = g.v_magnitude
            g_data["mBase"] = g.base_mva
            if g.online:
                online = 1
            else:
                online = 0
            g_data["status"] = online
            g_data["Pmax"]   = g.p_max * g_base
            g_data["Pmin"]   = g.p_min * g_base

            # Convert all values to strings
            for key in g_data.keys():
                g_data[key] = str(g_data[key])

            generators_data[i] = g_data

        file.write("%% generator data" + "\n")

        file.write("%\t")
        for label in labels:
            file.write("%-8s" % label)
        file.write("\n")

        file.write("gen = [" + "\n")

        for g_data in generators_data:
            file.write("\t")
            for label in labels:
                if label != labels[-1]:
                    file.write("%-8s" % g_data[label])
                else:
                    file.write("%s" % g_data[label])
            file.write(";" + "\n")

        file.write("];" + "\n")


    def write_branch_data(self, file):
        """ Writes branch data to file.
        """
        labels = ["fbus", "tbus", "r", "x", "b", "rateA", "rateB", "rateC",
            "ratio", "angle", "status"]

        base_mva = self.case.base_mva

        branches_data = []
        for e in self.case.branches:
            e_data = {}
            e_data["fbus"] = self.case.buses.index(e.source_bus) + 1
            e_data["tbus"] = self.case.buses.index(e.target_bus) + 1
            e_data["r"] = e.r
            e_data["x"] = e.x
            e_data["b"] = e.b
            e_data["rateA"] = e.s_max * base_mva
            # TODO: Implement short term and emergency ratings
            e_data["rateB"] = e.s_max * base_mva
            e_data["rateC"] = e.s_max * base_mva
            e_data["ratio"] = e.ratio
            e_data["angle"] = e.phase_shift
            if e.online:
                online = 1
            else:
                online = 0
            e_data["status"] = online

            # Convert all values to strings
            for key in e_data.keys():
                e_data[key] = str(e_data[key])

            branches_data.append(e_data)

        file.write("%% branch data" + "\n")

        file.write("%\t")
        for label in labels:
            file.write("%-8s" % label)
        file.write("\n")

        file.write("branch = [" + "\n")

        for e_data in branches_data:
            file.write("\t")
            for label in labels:
                if label != labels[-1]:
                    file.write("%-8s" % e_data[label])
                else:
                    file.write("%s" % e_data[label])
            file.write(";" + "\n")

        file.write("];" + "\n")


    def write_generator_cost_data(self, file):
        """ Writes generator cost data to file.
        """
        file.write("%% generator cost data" + "\n")
        file.write("%\n")
        file.write("% Piecewise linear:" + "\n")
        file.write("%\t1\tstartup\tshutdwn\tn_point\tx1\ty1\t...\txn\tyn\n")
        file.write("%\n")
        file.write("% Polynomial:" + "\n")
        file.write("%\t2\tstartup\tshutdwn\tn_coeff\tc(n-1)\t...\tc0\n")

        file.write("gencost = [" + "\n")
        file.write("];" + "\n")

    #--------------------------------------------------------------------------
    #  "MatpowerWriter" interface:
    #--------------------------------------------------------------------------

    def write_area_data(self, file):
        """ Writes area data to file.
        """
        file.write("%% area data" + "\n")
        file.write("%\tno.\tprice_ref_bus" + "\n")
        file.write("areas = [" + "\n")
        # TODO: Implement areas
        file.write("\t1\t1;" + "\n")

        file.write("];" + "\n")

# EOF -------------------------------------------------------------------------
