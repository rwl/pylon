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

    def _write_data(self, file):
        self.write_case_data(file)
        self.write_bus_data(file)
        self.write_generator_data(file)
        self.write_branch_data(file)


    def write_case_data(self, file):
        """ Writes case data to file.
        """
        change_code = 0
        s_base = self.case.base_mva
        file.write("%d, %8.2f, 30 / PSS(tm)E-30 RAW created by pylon %s\n" %
                   (change_code, s_base, "date"))
        file.write(" %s\n" % self.case.name)
        file.write("\n")


    def write_bus_data(self, file):
        """ Writes bus data in MATPOWER format.
        """
        # I, 'NAME', BASKV, IDE, GL, BL, AREA, ZONE, VM, VA, OWNER
        bus_attrs = ["_i", "name", "v_base", "type", "g_shunt", "b_shunt",
                     "area", "zone",
                     "v_magnitude_guess", "v_angle_guess"]


        for bus in self.case.buses:
            vals = [getattr(bus, a) for a in bus_attrs]
            d = {PQ: 1, PV: 2, REFERENCE: 3, ISOLATED: 4}
            vals[3] = d[vals[3]]
            vals.append(1)

#            print len(vals), vals

            file.write("%6d,'%10s',%10.4f,%d,%10.3f,%10.3f,%4d,%4d,%10.3f,"
                       "%10.3f%4d\n" % tuple(vals))
        file.write(" 0 / END OF BUS DATA, BEGIN LOAD DATA\n")


        # I, ID, STATUS, AREA, ZONE, PL, QL, IP, IQ, YP, YQ, OWNER
        load_attrs = ["_i", "area", "zone", "p_demand", "q_demand"]

        for bus in self.case.buses:
            vals = [getattr(bus, a) for a in load_attrs]
            vals.insert(1, 1) # STATUS
            vals.insert(1, "1 ") # ID
            vals.extend([0., 0., 0., 0.])
            vals.append(1) # OWNER

            file.write("%6d,'%s',%2d,%2d,%2d,%10.3f,%10.3f,%10.3f,%10.3f,"
                       "%10.3f,%10.3f,%4d\n" % tuple(vals))

        file.write(" 0 / END OF LOAD DATA, BEGIN GENERATOR DATA\n")


    def write_generator_data(self, file):
        """ Writes generator data in MATPOWER format.
        """
        for generator in self.case.generators:
            vals = []
            vals.append(generator.bus._i) # I
            vals.append("1 ") # ID
            vals.append(generator.p)
            vals.append(generator.q)
            vals.append(generator.q_max)
            vals.append(generator.q_min)
            vals.append(generator.v_magnitude)
            vals.append(0) # IREG
            vals.append(generator.base_mva)
            vals.extend([0., 0., 0., 0., 0.])
            vals.append(generator.online)
            vals.append(100.0) # RMPCT
            vals.append(generator.p_max)
            vals.append(generator.p_min)
            vals.extend([1, 1.0]) # O1,F1

            file.write("%d,'%s',%10.3f,%10.3f,%10.3f,%10.3f,%10.3f,%6d,%10.3f,"
                       "%10.5f,%10.5f,%10.5f,%10.5f,%7.5f,%d,%7.1f,%10.3f,"
                       "%10.3f,%4d,%6.4f\n" % tuple(vals))
        file.write(" 0 / END OF GENERATOR DATA, BEGIN NON-TRANSFORMER BRANCH DATA\n")


    def write_branch_data(self, file):
        """ Writes branch data to file.
        """
        # I,J,CKT,R,X,B,RATEA,RATEB,RATEC,GI,BI,GJ,BJ,ST,LEN,O1,F1,...,O4,F4
        branch_attr = ["r", "x", "b", "rate_a", "rate_b", "rate_c"]

        for branch in self.case.branches:
            if branch.ratio == 0.0:
                vals = [getattr(branch, a) for a in branch_attr]

                vals.insert(0, "1 ")
                vals.insert(0, branch.to_bus._i)
                vals.insert(0, branch.from_bus._i)
                vals.extend([0., 0., 0., 0.])
                vals.append(branch.online)
                vals.extend([0.0, 1, 1.0,])

                file.write("%6d,%6d,'%s',%10.3f,%10.3f,%10.3f,%10.3f,%10.3f,"
                    "%10.3f,%10.3f,%10.3f,%10.3f,%10.3f,%d,%10.3f,%4d,%6.4f\n" %
                    tuple(vals))
        file.write(" 0 / END OF NON-TRANSFORMER BRANCH DATA, BEGIN TRANSFORMER DATA\n")

        # I,J,K,CKT,CW,CZ,CM,MAG1,MAG2,NMETR,'NAME',STAT,O1,F1,...,O4,F4
        # R1-2,X1-2,SBASE1-2
        # WINDV1,NOMV1,ANG1,RATA1,RATB1,RATC1,COD1,CONT1,RMA1,RMI1,VMA1,VMI1,NTP1,TAB1,CR1,CX1
        # WINDV2,NOMV2
        for branch in self.case.branches:
            if branch.ratio != 0.0:
                vals = []
                vals.append(branch.from_bus._i)
                vals.append(branch.to_bus._i)
                # K,CKT,CW,CZ,CM,MAG1,MAG2,NMETR
                vals.extend([0, "1 ", 1, 1, 1, 0.0, 0.0, 2])
                vals.append(branch.name)
                vals.append(branch.online)
                vals.extend([1, 1.0]) # O1,F1

                file.write("%6d,%6d,%6d,'%2s',%d,%d,%d,%10.3f,%10.3f,%d,"
                           "'%12s',%d,%4d,%6.4f\n" % tuple(vals))
                file.write("%8.3f,%8.3f,%10.2f\n" % (branch.r, branch.x,
                                                   self.case.base_mva))

                line3 = []
                line3.append(branch.from_bus.v_base)
                line3.append(0.0)
                line3.append(branch.phase_shift)
                line3.append(branch.rate_a)
                line3.append(branch.rate_b)
                line3.append(branch.rate_c)
                # COD1,CONT1,RMA1,RMI1,VMA1,VMI1,NTP1,TAB1,CR1,CX1
                line3.extend([0, 0, 1.1, 0.9, 1.1, 0.9, 33, 0, 0.0, 0.0])

                file.write("%7.5f,%8.3f,%8.3f,%8.2f,%8.2f,%8.2f,%d,%7d,%8.5f,"
                    "%8.5f,%8.5f,%8.5f,%4d,%2d,%8.5f,%8.5f\n" % tuple(line3))

                file.write("%7.5f,%8.3f\n" % (branch.to_bus.v_base, 0.0))

        file.write(""" 0 / END OF TRANSFORMER DATA, BEGIN AREA INTERCHANGE DATA
 0 / END OF AREA INTERCHANGE DATA, BEGIN TWO-TERMINAL DC DATA
 0 / END OF TWO-TERMINAL DC DATA, BEGIN VSC DC LINE DATA
 0 / END OF VSC DC LINE DATA, BEGIN SWITCHED SHUNT DATA
 0 / END OF SWITCHED SHUNT DATA, BEGIN TRANS. IMP. CORR. TABLE DATA
 0 / END OF TRANS. IMP. CORR. TABLE DATA, BEGIN MULTI-TERMINAL DC LINE DATA
 0 / END OF MULTI-TERMINAL DC LINE DATA, BEGIN MULTI-SECTION LINE DATA
 0 / END OF MULTI-SECTION LINE DATA, BEGIN ZONE DATA
 0 / END OF ZONE DATA, BEGIN INTERAREA TRANSFER DATA
 0 / END OF INTERAREA TRANSFER DATA, BEGIN OWNER DATA
 0 / END OF OWNER DATA, BEGIN FACTS DEVICE DATA
 0 / END OF FACTS DEVICE DATA, END OF CASE DATA
""")

# EOF -------------------------------------------------------------------------
