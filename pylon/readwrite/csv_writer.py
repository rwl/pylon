#------------------------------------------------------------------------------
# Copyright (C) 2008 Richard W. Lincoln
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

""" For writing network data to file as Comma Separated Values (CSV). """

#------------------------------------------------------------------------------
#  Imports:
#------------------------------------------------------------------------------

import csv

#------------------------------------------------------------------------------
#  "CSVWriter" class:
#------------------------------------------------------------------------------

class CSVWriter:
    """ Writes network data to file as CSV. """

    network = None

    file_or_filename = ""

    def __init__(self, network, file_or_filename):
        """ Initialises a new CSVWriter instance. """

        self.network = network
        self.file_or_filename = file_or_filename


    def write(self):
        """ Writes network data to file as CSV. """

        network = self.network
        file_or_filename = self.file_or_filename

        if isinstance(file_or_filename, basestring):
            file = open(file_or_filename, "wb")
        else:
            file = file_or_filename

        writer = csv.writer(file)

        # Bus -----------------------------------------------------------------

        bus_attrs = ["name", "mode", "slack", "v_base", "v_amplitude_guess",
            "v_phase_guess", "v_max", "v_min", "v_amplitude", "v_phase",
            "g_shunt", "b_shunt", "zone"]

        writer.writerow(bus_attrs)

        for bus in network.buses:
            values = [getattr(bus, attr) for attr in bus_attrs]
            print "BUS:", values
            writer.writerow(values)
            del values

        # Branch --------------------------------------------------------------

        branch_attrs = ["source_bus_idx", "target_bus_idx", "name", "mode",
            "in_service", "r", "x", "b", "s_max", "phase_shift",
            "phase_shift_max", "phase_shift_min", "in_service"]

        writer.writerow(branch_attrs)

        for branch in network.branches:
            values = [getattr(branch, attr) for attr in branch_attrs]
            writer.writerow(values)
            del values

        # Generator -----------------------------------------------------------

        generator_attrs = ["name", "base_mva", "v_amplitude", "p", "p_max",
            "p_min", "q", "q_max", "q_min", "c_startup", "c_shutdown",
            "cost_model", "cost_coeffs", "pwl_points", "p_cost", "u",
            "rate_up", "rate_down", "min_up", "min_down", "initial_up",
            "initial_down"]

        writer.writerow(["bus"] + generator_attrs)

        for i, bus in enumerate(network.buses):
            for generator in bus.generators:
                values = [getattr(generator, attr) for attr in generator_attrs]
                writer.writerow([i] + values)
                del values

        # Load ----------------------------------------------------------------

        load_attrs = ["name", "p", "q", "in_service"]

        writer.writerow(["bus"] + load_attrs)

        for i, bus in enumerate(network.buses):
            for load in bus.loads:
                values = [getattr(load, attr) for attr in load_attrs]
                writer.writerow([i] + values)
                del values

        file.close()

if __name__ == "__main__":
    from pylon.api import Network, Bus, Branch, Generator, Load
    n = Network(name="network", mva_base=100.0)
    bus1 = Bus(name="Bus 1")
    bus2 = Bus(name="Bus 2")
    bus1.generators.append(Generator(name="G"))
    bus2.loads.append(Load(name="L"))
    branch1 = Branch(bus1, bus2, name="Branch 1")
    n.buses.extend([bus1, bus2])
    n.branches.append(branch1)
    writer = CSVWriter(n, "/tmp/network.csv")
    writer.write()

# EOF -------------------------------------------------------------------------
