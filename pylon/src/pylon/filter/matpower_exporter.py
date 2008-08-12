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

""" Defines classes for importing and exporting MATPOWER data files """

#------------------------------------------------------------------------------
#  Imports:
#------------------------------------------------------------------------------

from os.path import basename, splitext

#------------------------------------------------------------------------------
#  "MATPOWERExporter" class:
#------------------------------------------------------------------------------

class MATPOWERExporter:
    """ Write network data to a file in MATPOWER format """

    def export_network(self, network, file_or_filename):
        """ Writes network data to file in MATPOWER format """

        self.network = network

        if isinstance(file_or_filename, basestring):
            file = open(file_or_filename, "wb")
            f_name, ext = splitext(basename(file_or_filename))
        else:
            file = file_or_filename
            f_name, ext = splitext(file.name)

        # Header
        file.write("function [baseMVA, bus, gen, branch, areas, gencost] = ")
        file.write(f_name + "\n")

        file.write("\n")

        file.write("%%-----  Power Flow Data  -----%%\n")
        file.write("%% system MVA base\n")
        file.write("baseMVA = %.1f;\n" % network.mva_base)

        file.write("\n")

        self._export_buses(network.buses, file, network.mva_base)
        file.write("\n")
        self._export_generators(network.generators, file, network.buses)
        file.write("\n")
        self._export_branches(
            network.branches, file, network.mva_base, network.buses
        )
        file.write("\n")
        file.write("%%-----  OPF Data  -----%%\n")
        self._export_areas(None, file)
        file.write("\n")
        self._export_gencost(file)

        file.close()


    def _export_buses(self, buses, file, base_mva):
        """ Writes bus data to file """

        labels = [
            "bus_id", "type", "Pd", "Qd", "Gs", "Bs", "area", "Vm", "Va",
            "baseKV", "zone", "Vmax", "Vmin"
        ]

        buses_data = []
        for i, v in enumerate(buses):
            v_data = {}
            v_data["bus_id"] = i+1
            if v.type == "PQ":
                type = 1
            elif v.type == "PV":
                type = 2
            elif v.type == "Slack":
                type = 3
            else:
                raise ValueError
            v_data["type"] = type
            v_data["Pd"] = sum([l.p for l in v.loads]) * base_mva
            v_data["Qd"] = sum([l.q for l in v.loads]) * base_mva
            v_data["Gs"] = v.g_shunt
            v_data["Bs"] = v.b_shunt
            # TODO: Implement areas
            v_data["area"] = 1
            v_data["Vm"] = v.v_amplitude_guess
            v_data["Va"] = v.v_phase_guess
            v_data["baseKV"] = v.v_base
            v_data["zone"] = v.zone
            v_data["Vmax"] = v.v_max
            v_data["Vmin"] = v.v_min

            # Convert all values to strings
            for key in v_data.keys():
                v_data[key] = str(v_data[key])

            buses_data.append(v_data)

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


    def _export_generators(self, generators, file, buses):
        """ Write generator data to file """

        labels = [
            "bus", "Pg", "Qg", "Qmax", "Qmin", "Vg", "mBase", "status",
            "Pmax", "Pmin"
        ]

        generators_data = []
        for g in generators:
            g_data = {}
            g_base = g.base_mva
            # FIXME: Need faster way to find generator bus index
            g_data["bus"] = 1 # Failsafe value
            for v in buses:
                if g in v.generators:
                    g_data["bus"] = buses.index(v) + 1
                    break
            g_data["Pg"] = g.p * g_base
            g_data["Qg"] = g.q * g_base
            g_data["Qmax"] = g.q_max * g_base
            g_data["Qmin"] = g.q_min * g_base
            g_data["Vg"] = g.v_amplitude
            g_data["mBase"] = g.base_mva
            if g.in_service:
                in_service = 1
            else:
                in_service = 0
            g_data["status"] = in_service
            g_data["Pmax"] = g.p_max * g_base
            g_data["Pmin"] = g.p_min * g_base

            # Convert all values to strings
            for key in g_data.keys():
                g_data[key] = str(g_data[key])

            generators_data.append(g_data)

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


    def _export_branches(self, branches, file, base_mva, buses):
        """ Writes branch data to file """

        labels = [
            "fbus", "tbus", "r", "x", "b", "rateA", "rateB", "rateC",
            "ratio", "angle", "status"
        ]

        branches_data = []
        for e in branches:
            e_data = {}
            e_data["fbus"] = buses.index(e.source_bus) + 1
            e_data["tbus"] = buses.index(e.target_bus) + 1
            e_data["r"] = e.r
            e_data["x"] = e.x
            e_data["b"] = e.b
            e_data["rateA"] = e.s_max * base_mva
            # TODO: Implement short term and emergency ratings
            e_data["rateB"] = e.s_max * base_mva
            e_data["rateC"] = e.s_max * base_mva
            e_data["ratio"] = e.ratio
            e_data["angle"] = e.phase_shift
            if e.in_service:
                in_service = 1
            else:
                in_service = 0
            e_data["status"] = in_service

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


    def _export_areas(self, areas, file):
        """ Writes area data to file """

        file.write("%% area data" + "\n")
        file.write("%\tno.\tprice_ref_bus" + "\n")
        file.write("areas = [" + "\n")
        # TODO: Implement areas
        file.write("\t1\t1;" + "\n")

        file.write("];" + "\n")


    def _export_gencost(self, file):
        """ Writes generator cost data to file """

        file.write("%% generator cost data" + "\n")
        file.write("%\n")
        file.write("% Piecewise linear:" + "\n")
        file.write("%\t1\tstartup\tshutdwn\tn_point\tx1\ty1\t...\txn\tyn\n")
        file.write("%\n")
        file.write("% Polynomial:" + "\n")
        file.write("%\t2\tstartup\tshutdwn\tn_coeff\tc(n-1)\t...\tc0\n")

        file.write("gencost = [" + "\n")
        file.write("];" + "\n")

#------------------------------------------------------------------------------
#  Convenience function for MATPOWER export
#------------------------------------------------------------------------------

def export_matpower(network, file_or_filename):
    """ Convenience function for network export to a MATPOWER data file """

    return MATPOWERExporter().export_file(network, file_or_filename)

#------------------------------------------------------------------------------
#  Standalone call:
#------------------------------------------------------------------------------

if __name__ == "__main__":
    import sys
    import logging
    logger = logging.getLogger()
    logger.addHandler(logging.StreamHandler(sys.stdout))
    logger.setLevel(logging.DEBUG)

    data_file = "/home/rwl/python/aes/matpower_3.2/rwl_003.m"
    #data_file = "/home/rwl/python/aes/model/matpower/case30.m"

    from matpower_importer import MATPOWERImporter

    n = MATPOWERImporter().parse_file(data_file)

    MATPOWERExporter().export_network(n, "/tmp/test.m")

# EOF -------------------------------------------------------------------------
