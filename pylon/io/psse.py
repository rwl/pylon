#------------------------------------------------------------------------------
# Copyright (C) 2007-2010 Richard Lincoln
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

""" Defines a reader for PSS/E data files.
"""

#------------------------------------------------------------------------------
#  Imports:
#------------------------------------------------------------------------------

import os
import time
import logging

from pylon import Case, Bus, Branch, Generator, PQ, PV, REFERENCE, ISOLATED
from pylon.util import feq
from pylon.io.common import _CaseReader, _CaseWriter

#------------------------------------------------------------------------------
#  Logging:
#------------------------------------------------------------------------------

logger = logging.getLogger(__name__)

#------------------------------------------------------------------------------
#  "PSSEReader" class:
#------------------------------------------------------------------------------

class PSSEReader(_CaseReader):
    """ Defines a reader for PSS/E(TM) version 30 Raw files.
    """

    def __init__(self):

        #: Zero impedance line threshold tolerance.
        self.xtol = 0.0001

        self.init()


    def init(self):
        self.bus_map = {}


    def read(self, file_or_filename):
        """ Returns a case from a version 30 PSS/E raw file.

        @param file_or_filename: File name or file like object with PSS/E data
        @return: Case object
        """
        t0 = time.time()
        self.init()
        if isinstance(file_or_filename, basestring):
            fname = os.path.basename(file_or_filename)
            logger.info("Loading PSS/E Raw file [%s]." % fname)

            file = None
            try:
                file = open(file_or_filename, "rb")
            except:
                logger.error("Error opening %s." % fname)
                return None
            finally:
                if file is not None:
                    case = self._parse_file(file)
                    file.close()
        else:
            file = file_or_filename
            case = self._parse_file(file)

        logger.info("PSS/E Raw file parsed in %.2fs." % (time.time() - t0))

        return case


    def _parse_file(self, file):
        """ Parses the given file.
        """
        case = Case()
        file.seek(0)
        case.base_mva = float(file.next().split(",")[1].split("/")[0])
        case.name = "%s %s" % (file.next().strip(), file.next().strip())

        bustype_map = {1: "PQ", 2: "PV", 3: "ref", 4: "isolated"}

        # I, 'NAME', BASKV, IDE, GL, BL, AREA, ZONE, VM, VA, OWNER
        bus_data = file.next().split(",")
        while bus_data[0].strip()[0] != "0":
            bus = Bus()
            i = int(bus_data[0].strip())
            self.bus_map[i] = bus
            bus._i = i
            bus.name =  bus_data[1].strip("'").strip()
            bus.v_base = float(bus_data[2])
            bus.type = bustype_map[int(bus_data[3])]
            bus.g_shunt = float(bus_data[4])
            bus.b_shunt = float(bus_data[5])
            bus.v_magnitude = float(bus_data[8])
            bus.v_angle = float(bus_data[9])
            case.buses.append(bus)
            bus_data = file.next().split(",")

        # I, ID, STATUS, AREA, ZONE, PL, QL, IP, IQ, YP, YQ, OWNER
        load_data = file.next().split(",")
        while load_data[0].strip()[0] != "0":
            bus = self.bus_map[int(load_data[0].strip())]
            bus.p_demand += float(load_data[5])
            bus.q_demand += float(load_data[6])
            load_data = file.next().split(",")

        #I,ID,PG,QG,QT,QB,VS,IREG,MBASE,ZR,ZX,RT,XT,GTAP,STAT,RMPCT,PT,PB,O1,F1
        gen_data = file.next().split(",")
        while gen_data[0].strip()[0] != "0":
            bus = self.bus_map[int(gen_data[0].strip())]
            g = Generator(bus)
            g.p = float(gen_data[2])
            g.q = float(gen_data[3])
            g.q_max = float(gen_data[4])
            g.q_min = float(gen_data[5])
            g.v_magnitude = float(gen_data[6])
            g.base_mva = float(gen_data[8])
            g.online = bool(int(gen_data[14]))
            g.p_max = float(gen_data[16])
            g.p_min = float(gen_data[17])
            case.generators.append(g)
            gen_data = file.next().split(",")

        # I,J,CKT,R,X,B,RATEA,RATEB,RATEC,GI,BI,GJ,BJ,ST,LEN,O1,F1,...,O4,F4
        branch_data = file.next().split(",")
        while branch_data[0].strip()[0] != "0":
            from_bus = self.bus_map[abs(int(branch_data[0]))]
            to_bus = self.bus_map[abs(int(branch_data[1]))]
            l = Branch(from_bus, to_bus)
            l.r = float(branch_data[3])
            l.x = float(branch_data[4])
            l.b = float(branch_data[5])
            l.rate_a = float(branch_data[6])
            l.rate_b = float(branch_data[7])
            l.rate_c = float(branch_data[8])
#            l.online = bool(int(branch_data[13]))
            case.branches.append(l)
            branch_data = file.next().split(",")

        # I,J,K,CKT,CW,CZ,CM,MAG1,MAG2,NMETR,'NAME',STAT,O1,F1,...,O4,F4
        # R1-2,X1-2,SBASE1-2
        # WINDV1,NOMV1,ANG1,RATA1,RATB1,RATC1,COD1,CONT1,RMA1,RMI1,VMA1,VMI1,NTP1,TAB1,CR1,CX1
        # WINDV2,NOMV2
        trx_data = file.next().split(",")
        while trx_data[0].strip()[0] != "0":
            trx_data2 = file.next().split(",")
            trx_data3 = file.next().split(",")
            trx_data4 = file.next().split(",") # second winding
            if len(trx_data2) < 5:
                from_bus = self.bus_map[abs(int(trx_data[0]))]
                to_bus = self.bus_map[abs(int(trx_data[1]))]
                l = Branch(from_bus, to_bus)
                l.name = trx_data[10].strip("'").strip()
                l.online = bool(int(trx_data[11]))
                l.b = float(trx_data[8])
                l.r = float(trx_data2[0])
                l.x = float(trx_data2[1])
                l.ratio = float(trx_data3[0])
                l.phase_shift = float(trx_data3[2])
                rate_a = float(trx_data3[3])
                if rate_a != 0.0:
                    l.rate_a = rate_a
                rate_b = float(trx_data3[4])
                if rate_b != 0.0:
                    l.rate_b = rate_b
                rate_c = float(trx_data3[5])
                if rate_c != 0.0:
                    l.rate_c = rate_c
                case.branches.append(l)
                trx_data = file.next().split(",")
            else:
                # I,J,K,CKT,CW,CZ,CM,MAG1,MAG2,NMETR,'NAME',STAT,O1,F1,...,O4,F4
                # R1-2,X1-2,SBASE1-2,R2-3,X2-3,SBASE2-3,R3-1,X3-1,SBASE3-1,VMSTAR,ANSTAR
                # WINDV1,NOMV1,ANG1,RATA1,RATB1,RATC1,COD1,CONT1,RMA1,RMI1,VMA1,VMI1,NTP1,TAB1,CR1,CX1
                # WINDV2,NOMV2,ANG2,RATA2,RATB2,RATC2,COD2,CONT2,RMA2,RMI2,VMA2,VMI2,NTP2,TAB2,CR2,CX2
                # WINDV3,NOMV3,ANG3,RATA3,RATB3,RATC3,COD3,CONT3,RMA3,RMI3,VMA3,VMI3,NTP3,TAB3,CR3,CX3

                trx_data5 = file.next().split(",") # third winding
                # Three-winding transformers are modelled as a group of three
                # two-winding transformers with a fictitious neutral bus.
                tmp_bus = Bus()
                tmp_bus.name = "n" + tmp_bus.name
                tmp_bus._i = len(case.buses) + 1

                bus1 = self.bus_map[abs(int(trx_data[0]))]
                bus2 = self.bus_map[abs(int(trx_data[1]))]
                bus3 = self.bus_map[abs(int(trx_data[2]))]
                l1 = Branch(tmp_bus, bus1)
                l2 = Branch(tmp_bus, bus2)
                l3 = Branch(tmp_bus, bus3)

                b = float(trx_data[8]) # MAG2
                l1.b = b# / 3.0
#                l2.b = b / 3.0
#                l3.b = b / 3.0

                on = bool(int(trx_data[11]))
                l1.online = on
                l2.online = on
                l3.online = on

                r12 = float(trx_data2[0])
                x12 = float(trx_data2[1])
                r23 = float(trx_data2[3])
                x23 = float(trx_data2[4])
                r31 = float(trx_data2[6])
                x31 = float(trx_data2[7])

                l1.r = 0.5 * (r12 + r31 - r23)
                l1.x = 0.5 * (x12 + x31 - x23)
                l2.r = 0.5 * (r12 + r23 - r31)
                l2.x = 0.5 * (x12 + x23 - x31)
                l3.r = 0.5 * (r23 + r31 - r12)
                l3.x = 0.5 * (x23 + x31 - x12)

                for l in [l1, l2, l3]:
                    if abs(l.x) < 1e-5:
                        logger.warning("Zero branch reactance [%s]." % l.name)
                        l.x = self.xtol
                    if abs(complex(l.r, l.x)) < 0.00001:
                        logger.warning("Zero branch impedance [%s]." % l.name)

                l1.ratio = float(trx_data3[0])
                l1.phase_shift = float(trx_data3[2])
                l2.ratio = float(trx_data4[0])
                l2.phase_shift = float(trx_data4[2])
                l3.ratio = float(trx_data5[0])
                l3.phase_shift = float(trx_data5[2])

                rate_a1 = float(trx_data3[3])
                rate_b1 = float(trx_data3[4])
                rate_c1 = float(trx_data3[5])
                if rate_a1 > 0.0:
                    l1.rate_a = rate_a1
                if rate_b1 > 0.0:
                    l1.rate_b = rate_b1
                if rate_c1 > 0.0:
                    l1.rate_c = rate_c1

                rate_a2 = float(trx_data4[3])
                rate_b2 = float(trx_data4[4])
                rate_c2 = float(trx_data4[5])
                if rate_a2 > 0.0:
                    l2.rate_a = rate_a2
                if rate_b2 > 0.0:
                    l2.rate_b = rate_b2
                if rate_c2 > 0.0:
                    l2.rate_c = rate_c2

                rate_a3 = float(trx_data5[3])
                rate_b3 = float(trx_data5[4])
                rate_c3 = float(trx_data5[5])
                if rate_a3 > 0.0:
                    l3.rate_a = rate_a3
                if rate_b2 > 0.0:
                    l3.rate_b = rate_b3
                if rate_c2 > 0.0:
                    l3.rate_c = rate_c3

                case.buses.append(tmp_bus)
                case.branches.append(l1)
                case.branches.append(l2)
                case.branches.append(l3)

                trx_data = file.next().split(",")

        # Area interchange data.
        # I, ISW, PDES, PTOL, 'ARNAME'
        trx_data = file.next().split(",")
        while trx_data[0].strip()[0] != "0":
            logger.warning("Ignoring area interchange data.")
            trx_data = file.next().split(",")

        # Two-terminal DC line data.
        # I,MDC,RDC,SETVL,VSCHD,VCMOD,RCOMP,DELTI,METER,DCVMIN,CCCITMX,CCCACC
        # IPR,NBR,ALFMX,ALFMN,RCR,XCR,EBASR,TRR,TAPR,TMXR,TMNR,STPR,ICR,IFR,ITR,IDR,XCAPR
        # IPI,NBI,GAMMX,GAMMN,RCI,XCI,EBASI,TRI,TAPI,TMXI,TMNI,STPI,ICI,IFI,ITI,IDI,XCAPI
        trx_data = file.next().split(",")
        while trx_data[0].strip()[0] != "0":
            logger.warning("Ignoring two-terminal DC line data.")
            trx_data = file.next().split(",")

        # VSC DC line data.
        # 'NAME', MDC, RDC, O1, F1, ... O4, F4
        # IBUS,TYPE,MODE,DOCET,ACSET,ALOSS,BLOSS,MINOSS,SMAX,IMAX,PWF,MAXQ,MINQ,
        # REMOT,RMPCT
        trx_data = file.next().split(",")
        while trx_data[0].strip()[0] != "0":
            logger.warning("Ignoring VSC DC line data.")
            trx_data = file.next().split(",")

        # Switched shunt data.
        # I,MODSW,VSWHI,VSWLO,SWREM,RMPCT,'RMIDNT',BINIT,N1,B1,N2,B2,...N8,B8
        trx_data = file.next().split(",")
        while trx_data[0].strip()[0] != "0":
            bus = self.bus_map[abs(int(trx_data[0]))]
            bus.b_shunt += float(trx_data[7])
            trx_data = file.next().split(",")

        # Transformer impedance correction table.
        # I, T1, F1, T2, F2, T3, F3, ... T11, F11
        trx_data = file.next().split(",")
        while trx_data[0].strip()[0] != "0":
            logger.warning("Ignoring transformer X correction table data.")
            trx_data = file.next().split(",")

        # Multi-terminal dc line data.
        # I, NCONV, NDCBS, NDCLN, MDC, VCONV, VCMOD, VCONVN
        # IB,N,ANGMX,ANGMN,RC,XC,EBAS,TR,TAP,TPMX,TPMN,TSTP,SETVL,DCPF,MARG,CNVCOD
        # IDC, IB, IA, ZONE, 'NAME', IDC2, RGRND, OWNER
        # IDC, JDC, DCCKT, RDC, LDC
        trx_data = file.next().split(",")
        while trx_data[0].strip()[0] != "0":
            logger.warning("Ignoring multi-terminal dc line data.")
            trx_data = file.next().split(",")

        # Multisection line data.
        # I,J,ID,DUM1,DUM2,...DUM9
        trx_data = file.next().split(",")
        while trx_data[0].strip()[0] != "0":
            logger.warning("Ignoring multisection line data.")
            trx_data = file.next().split(",")

        # Zone data.
        # I,'ZONAME'
        trx_data = file.next().split(",")
        while trx_data[0].strip()[0] != "0":
            logger.warning("Ignoring zone data.")
            trx_data = file.next().split(",")

        # Interarea transfer data.
        # ARFROM, ARTO, TRID, PTRAN
        trx_data = file.next().split(",")
        while trx_data[0].strip()[0] != "0":
            logger.warning("Ignoring interarea transfer data.")
            trx_data = file.next().split(",")

        # Owner data.
        # I,'OWNAME'
        trx_data = file.next().split(",")
        while trx_data[0].strip()[0] != "0":
            logger.warning("Ignoring owner data.")
            trx_data = file.next().split(",")

        # FACTS device data.
        # N,I,J,MODE,PDES,QDES,VSET,SHMX,TRMX,VTMN,VTMX,VSMX,IMX,LINX,RMPCT,OWNER,SET1,SET2,VSREF
        trx_data = file.next().split(",")
        while trx_data[0].strip()[0] != "0":
            logger.warning("Ignoring FACTS device data.")
            trx_data = file.next().split(",")

        return case

#------------------------------------------------------------------------------
#  "PSSEWriter" class:
#------------------------------------------------------------------------------

class PSSEWriter(_CaseWriter):
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
        timestr = time.strftime("%Y%m%d%H%M", time.gmtime())
        file.write("%d, %8.2f, 30 / PSS(tm)E-30 RAW created by Pylon (%s).\n" %
                   (change_code, s_base, timestr))
        file.write(" %s\n" % self.case.name)
        file.write(" %d BUSES, %d BRANCHES\n" %
                   (len(self.case.buses), len(self.case.branches)))


    def write_bus_data(self, file):
        """ Writes bus data in MATPOWER format.
        """
        # I, 'NAME', BASKV, IDE, GL, BL, AREA, ZONE, VM, VA, OWNER
        bus_attrs = ["_i", "name", "v_base", "type", "g_shunt", "b_shunt",
                     "area", "zone",
                     "v_magnitude", "v_angle"]

        for bus in self.case.buses:
            vals = [getattr(bus, a) for a in bus_attrs]
            d = {PQ: 1, PV: 2, REFERENCE: 3, ISOLATED: 4}
            vals[3] = d[vals[3]]
            vals.append(1)

#            print len(vals), vals

            file.write("%6d,'%-10s',%10.4f,%d,%10.3f,%10.3f,%4d,%4d,%10.3f,"
                       "%10.3f%4d\n" % tuple(vals))
        file.write(" 0 / END OF BUS DATA, BEGIN LOAD DATA\n")


        # I, ID, STATUS, AREA, ZONE, PL, QL, IP, IQ, YP, YQ, OWNER
        load_attrs = ["_i", "area", "zone", "p_demand", "q_demand"]

        for bus in self.case.buses:
            if bus.p_demand > 0.0 or bus.q_demand > 0.0:
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

            file.write("%6d,'%s',%10.3f,%10.3f,%10.3f,%10.3f,%10.5f,%6d,%10.3f,"
                       "%10.5f,%10.5f,%10.5f,%10.5f,%7.5f,%d,%7.1f,%10.3f,"
                       "%10.3f,%4d,%6.4f\n" % tuple(vals))
        file.write(" 0 / END OF GENERATOR DATA, BEGIN NON-TRANSFORMER BRANCH DATA\n")


    def write_branch_data(self, file):
        """ Writes branch data to file.
        """
        # I,J,CKT,R,X,B,RATEA,RATEB,RATEC,GI,BI,GJ,BJ,ST,LEN,O1,F1,...,O4,F4
        branch_attr = ["r", "x", "b", "rate_a", "rate_b", "rate_c"]

        for branch in self.case.branches:
            if feq(branch.ratio, 0.0):
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
            if not feq(branch.ratio, 0.0):
                vals = []
                vals.append(branch.from_bus._i)
                vals.append(branch.to_bus._i)
                # K,CKT,CW,CZ,CM,MAG1,MAG2,NMETR
                vals.extend([0, "1 ", 1, 1, 1, 0.0, 0.0, 2])
                vals.append(branch.name)
                vals.append(branch.online)
                vals.extend([1, 1.0]) # O1,F1

                file.write("%6d,%6d,%6d,'%2s',%d,%d,%d,%10.3f,%10.3f,%d,"
                           "'%-12s',%d,%4d,%6.4f\n" % tuple(vals))
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
