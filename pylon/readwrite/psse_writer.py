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

""" Defines a writer for creating PSS/E data files.
"""

#------------------------------------------------------------------------------
#  Imports:
#------------------------------------------------------------------------------

from pylon.readwrite.common import CaseWriter

from pylon import PQ, PV, REFERENCE, ISOLATED

#------------------------------------------------------------------------------
#  "PSSEWriter" class:
#------------------------------------------------------------------------------

class PSSEWriter(CaseWriter):
    """ Defines a class for writing a case in PSS/E format.
    """

    def write_case_data(self, file):
        """ Writes case data to file.
        """
        change_code = 0
        s_base = self.case.base_mva
        file.write("%d, %8.2f\n" % (change_code, s_base))
        file.write("\n")
        file.write("\n")


    def write_bus_data(self, file):
        """ Writes bus data to file.
        """
        type_code = {PQ: 1, PV: 2, REFERENCE: 3, ISOLATED: 4}

        for i, bus in enumerate(self.case.buses):
            name = bus.name[:8]
            base = bus.v_base
            type = type_code[bus.type]
            cond = bus.g_shunt
            susc = bus.b_shunt
            area = 1
            zone = 1
            vmag = bus.v_magnitude
            vang = bus.v_angle
            ownr = 1

            file.write("%6d, '%8s', %10.4f, %d, %10.4f, %10.4f, %6d, %6d, "
                "%10.4f, %10.4f, %6d\n" % (i, name, base, type, cond, susc,
                                           area, zone, vmag, vang, ownr))


    def write_branch_data(self, file):
        """ Writes branch data to file.
        """
        pass


    def write_generator_data(self, file):
        """ Writes generator data to file.
        """
        pass


if __name__ == "__main__":
    import sys
    from os.path import join, dirname
    from pylon import Case
    DATA_FILE = join(dirname(__file__), "..", "test", "data", "case6ww.pkl")
    PSSEWriter(Case.load(DATA_FILE)).write(sys.stdout)

# EOF -------------------------------------------------------------------------
