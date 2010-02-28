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
