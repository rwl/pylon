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

""" Defines a class for importing PSS/E data files """

#------------------------------------------------------------------------------
#  Imports:
#------------------------------------------------------------------------------

from parsing_util import integer, boolean, real, scolon, psse_comment

from pyparsing import \
    Literal, Word, restOfLine, alphanums, printables, quotedString, White, \
    OneOrMore, ZeroOrMore

from pylon.network import Network
from pylon.bus import Bus
from pylon.branch import Branch
from pylon.generator import Generator
from pylon.load import Load

#from pylon.pypylon import Network, Bus, Branch, Generator, Load

#-------------------------------------------------------------------------------
#  "PSSEImporter" class:
#-------------------------------------------------------------------------------

class PSSEImporter:

    def parse_file(self, file_or_filename):
        """ Defines a method class for importing PSS/E data files and
        returning a Network object.

        file_or_filename: File name of file object with PSS/E data
        return: Network object

        """

        self.network = Network()

        header = self._get_header_construct()
        title = self._get_title_construct()
        bus_data = self._get_bus_data_construct()
        separator = self._get_separator_construct()
        load_data = self._get_load_data_construct()
        generator_data = self._get_generator_data_construct()
        branch_data = self._get_branch_data_construct()
        transformer_data = self._get_transformer_data_construct()

        # Parse case
        case = ZeroOrMore(psse_comment) + header + \
               ZeroOrMore(psse_comment) + title + \
               ZeroOrMore(psse_comment) + ZeroOrMore(bus_data) + \
               ZeroOrMore(psse_comment) + separator + \
               ZeroOrMore(psse_comment) + ZeroOrMore(load_data) + \
               ZeroOrMore(psse_comment) + separator + \
               ZeroOrMore(psse_comment) + ZeroOrMore(generator_data) + \
               ZeroOrMore(psse_comment) + separator + \
               ZeroOrMore(psse_comment) + ZeroOrMore(branch_data) + \
               ZeroOrMore(psse_comment) + separator + \
               ZeroOrMore(psse_comment) + ZeroOrMore(transformer_data) + \
               ZeroOrMore(psse_comment)

        data = case.parseFile(file_or_filename)

        return self.network

    #--------------------------------------------------------------------------
    #  Construct getters:
    #--------------------------------------------------------------------------

    def _get_separator_construct(self):
        """ Returns a construct for a PSS/E separator """

        # Tables are separated by a single 0
        separator = Literal('0') + White('\n')# + LineEnd()
        separator.setParseAction(self._push_separator)

        return separator


    def _get_header_construct(self):
        """ Returns a construct for the header of a PSS/E file """

        first_line = Word('0', exact=1).suppress() + real + \
                     restOfLine.suppress()
        first_line.setParseAction(self._push_system_base)

        return first_line


    def _get_title_construct(self):
        """ Returns a construct for the subtitle of a PSS/E file """

        title = Word(alphanums).suppress() + restOfLine.suppress()
        sub_title = Word(printables) + restOfLine.suppress()
#        sub_title = Combine(Word(alphanums) + restOfLine)
        sub_title.setParseAction(self._push_sub_title)
        sub_title.setResultsName("sub_title")

        return title + sub_title


    def _get_bus_data_construct(self):
        """ Returns a construct for a line of bus data """

        # [I, IDE, PL, QL, GL, BL, IA, VM, VA, 'NAME', BASKL, ZONE]
#        i = integer
#        ide = Word('1234', exact=1)
#        load_mw = real
#        load_mvar = real
#        sh_conductance = real
#        sh_susceptance = real
#        area = integer
#        volt_magnitude = real
#        volt_angle = real
#        bus_name = quotedString
#        base_kv = real
#        loss_zone = integer
#
#        bus_data = i + ide + load_mw + load_mvar + sh_conductance + \
#                   sh_susceptance + area + volt_magnitude + volt_angle + \
#                   bus_name + base_kv + loss_zone

        # Bus, Name, Base_kV, Type, Y_re, Y_im, Area, Zone, PU_Volt, Angle
        i = integer.setResultsName("Bus")
        bus_name = quotedString.setResultsName("Name")
        base_kv = real.setResultsName("Base_kV")
        ide = Word("1234", exact=1).setResultsName("Type")
        sh_conductance = real.setResultsName("Y_re")
        sh_susceptance = real.setResultsName("Y_im")
        area = integer.setResultsName("Area")
        zone = integer.setResultsName("Zone")
        v_magnitude = real.setResultsName("PU_Volt")
        v_angle = real.setResultsName("Angle")

        bus_data = i + bus_name + base_kv + ide + sh_conductance + \
                   sh_susceptance + area + zone + v_magnitude + v_angle

        bus_data.setParseAction(self._push_bus_data)

        return bus_data


    def _get_load_data_construct(self):
        """ Returns a construct of a line of load data """

        # [Bus, LoadID, Status, Area, Zone, LP, LQ]
        bus_id = integer.setResultsName("Bus")
        load_id = integer.setResultsName("LoadID")
        status = boolean.setResultsName("Status")
        area = integer.setResultsName("Area")
        zone = integer.setResultsName("Zone")
        p_load = real.setResultsName("LP")
        q_load = real.setResultsName("LQ")

        load_data = bus_id + load_id + status + area + zone + p_load + q_load

        load_data.setParseAction(self._push_load_data)

        return load_data


    def _get_generator_data_construct(self):
        """ Returns a construct for a line of generator data """

        # [I,ID,PG,QG,QT,QB,VS,IREG,MBASE,ZR,ZX,RT,XT,GTAP,STAT,RMPCT,PT,PB]
#        bus_idx = integer
#        machine_id = Word(alphanums, exact=1)
#        mw_out = real
#        mvar_out = real
#        mvar_max = real
#        mvar_min = real
#        v_setpoint = real
#        reg_idx = integer
#        mva_base = real
#        z_r = real
#        z_x = real
#        r_t = real
#        x_t = real
#        g_tap = real
#        status = boolean
#        rmpct = real
#        mw_max = real
#        mw_min = real
#
#        generator_data = bus_idx + machine_id + mw_out + mvar_out + mvar_max + \
#                         mvar_min + v_setpoint + reg_idx + mva_base + z_r + \
#                         z_x + r_t + x_t + g_tap + status + rmpct + mw_max + \
#                         mw_min

        # Bus, ID, P, Q, Qmax, Qmin, SchedV, RegBs, MVAbase, ZR, ZX, RTr,
        # XTr, GTAP, Stat, Percent, Pmax, Pmin

        bus_id = integer.setResultsName("Bus")
        generator_id = integer.setResultsName("ID")
        p = real.setResultsName("P")
        q = real.setResultsName("Q")
        q_max = real.setResultsName("Qmax")
        q_min = real.setResultsName("Qmin")
        v_sched = real.setResultsName("SchedV")
        reg_bus = integer.setResultsName("RegBs")
        mva_base = real.setResultsName("MVAbase")
        r_zero = real.setResultsName("ZR")
        x_zero = real.setResultsName("ZX")
        r_tr = real.setResultsName("RTr")
        x_tr = real.setResultsName("XTr")
        gtap = integer.setResultsName("GTAP")
        status = boolean.setResultsName("Stat")
        percent = integer.setResultsName("Percent")
        p_max = real.setResultsName("Pmax")
        p_min = real.setResultsName("Pmin")

        generator_data = bus_id + generator_id + p + q + q_max + q_min + \
            v_sched + reg_bus + mva_base + r_zero + x_zero + r_tr + x_tr + \
            gtap + status + percent + p_max + p_min

        generator_data.setParseAction(self._push_generator)

        return generator_data


    def _get_branch_data_construct(self):
        """ Returns a construct for a line of branch data """

        # From, To, ID, R, X, B, RateA, RateB, RateC, G_busI, B_busI,
        # G_busJ, B_busJ, Stat, Len
        from_bus_id = integer.setResultsName("From")
        to_bus_id = integer.setResultsName("To")
        id = integer.setResultsName("ID")
        r = real.setResultsName("R")
        x = real.setResultsName("X")
        b = real.setResultsName("B")
        rate_a = real.setResultsName("RateA")
        rate_b = real.setResultsName("RateB")
        rate_c = real.setResultsName("RateC")
        g_bus_i = real.setResultsName("G_busI")
        b_bus_i = real.setResultsName("B_busI")
        g_bus_j = real.setResultsName("G_busJ")
        b_bus_j = real.setResultsName("B_busJ")
        status = boolean.setResultsName("Stat")
        length = real.setResultsName("Len")

        branch_data = from_bus_id + to_bus_id + id + r + x + b + \
            rate_a + rate_b + rate_c + g_bus_i + b_bus_i + g_bus_j + \
            b_bus_j + status + length

        branch_data.setParseAction(self._push_branch)

        return branch_data


    def _get_transformer_data_construct(self):
        """ Returns a construct for a line of transformer data """

        # From, To, K, ID, CW, CZ, CM, MAG1, MAG2, NMETR, NAME, STAT, O1, F1
        # R1-2, X1-2, SBASE1-2
        # WINDV1, NOMV1, ANG1, RATA1, RATB1, RATC1, COD, CONT, RMA, RMI, VMA, VMI, NTP, TAB, CR, CX
        # WINDV2, NOMV2

        # Unused column of data
        unused = Literal("/").suppress()

        from_bus_id = integer.setResultsName("From")
        to_bus_id = integer.setResultsName("To")
        k = integer.setResultsName("K")
        id = integer.setResultsName("ID")
        cw = integer.setResultsName("CW")
        cz = integer.setResultsName("CZ")
        cm = integer.setResultsName("CM")
        mag1 = real.setResultsName("MAG1")
        mag2 = real.setResultsName("MAG2")
        nmetr = integer.setResultsName("NMETR")
        name = quotedString.setResultsName("NAME")
        status = boolean.setResultsName("STAT")
        o1 = integer.setResultsName("o1")
        f1 = integer.setResultsName("f1")

        transformer_general = from_bus_id + to_bus_id + k + id + \
            cw + cz + cm + mag1 + mag2 + nmetr + name + status + \
            o1 + f1 + OneOrMore(unused)

        r12 = real.setResultsName("R1-2")
        x12 = real.setResultsName("X1-2")
        s_base12 = real.setResultsName("SBASE1-2")

        transformer_impedance = r12 + x12 + s_base12 + OneOrMore(unused)

        v1_wind = real.setResultsName("WINDV1")
        v1_nom = real.setResultsName("NOMV1")
        angle1 = real.setResultsName("ANG1")
        rate_a1 = real.setResultsName("RATA1")
        rate_b1 = real.setResultsName("RATB1")
        rate_c1 = real.setResultsName("RATC1")
        cod = integer.setResultsName("COD")
        cont = real.setResultsName("CONT")
        rma = real.setResultsName("RMA")
        rmi = real.setResultsName("RMI")
        vma = real.setResultsName("VMA")
        vmi = real.setResultsName("VMI")
        ntp = real.setResultsName("NTP")
        tab = real.setResultsName("TAB")
        cr = real.setResultsName("CR")
        cx = real.setResultsName("CX")

        transformer_winding_1 = v1_wind + v1_nom + angle1 + rate_a1 + \
            rate_b1 + rate_c1 + cod + cont + rma + rmi + vma + vmi + \
            ntp + tab + cr + cx

        v2_wind = real.setResultsName("WINDV2")
        v2_nom = real.setResultsName("NOMV2")

        transformer_winding_2 = v2_wind + v2_nom + OneOrMore(unused)

        transformer_data = transformer_general + transformer_impedance + \
            transformer_winding_1 + transformer_winding_2

        transformer_data.setParseAction(self._push_transformer_data)

        return transformer_data

    #--------------------------------------------------------------------------
    #  Parse actions:
    #--------------------------------------------------------------------------

    def _push_system_base(self, tokens):
        """ Set the system base """

        print 'System base:', tokens
        self.network.mva_base = float(tokens[0])


    def _push_title(self, tokens):
        """ Handles the network title """

        print "Title:", tokens


    def _push_sub_title(self, tokens):
        """ Sets the entwork name """

        print 'Subtitle:', tokens
        self.network.name = tokens[0]


    def _push_separator(self):
        """ Handles separators """

        print 'parsed separator'


    def _push_bus_data(self, tokens):
        """ Adds a bus to the network """

        # [I, IDE, PL, QL, GL, BL, IA, VM, VA, 'NAME', BASKL, ZONE]
        # Bus, Name, Base_kV, Type, Y_re, Y_im, Area, Zone, PU_Volt, Angle
        print 'Bus:', tokens

        bus = Bus(network=self.network)

        bus.name = tokens["Name"].strip("'")
        bus.id = tokens["Bus"]

        bus.v_amplitude_default=tokens["PU_Volt"]
        bus.v_phase_default=tokens["Angle"]

        # Bus type 3 denotes a slack bus in MATPOWER
#        if int(tokens[1]) == 3: v.slack = True

        self.network.buses.append(bus)


    def _push_load_data(self, tokens):
        """ Adds a load to a bus """

        #[Bus, Load, ID, Status, Area, Zone, LP, LQ]
        print "Load:", tokens

        buses = [bus for bus in self.network.buses if
                 bus.id == str(tokens["Bus"])]

        if len(buses) == 0:
            print "Parent bus [%s] for load not found" % tokens["Bus"]
            return
        elif len(buses) == 1:
            bus = buses[0]
        else:
            print "More than on parent bus for load found", buses
            return

        load = Load()

        load.p = tokens["LP"]
        load.q = tokens["LQ"]

        bus.loads.append(load)


    def _push_generator(self, tokens):
        """ Adds a generator to a bus """

        # [I,ID,PG,QG,QT,QB,VS,IREG,MBASE,ZR,ZX,RT,XT,GTAP,STAT,RMPCT,PT,PB]
        # Bus, ID, P, Q, Qmax, Qmin, SchedV, RegBs, MVAbase, ZR, ZX, RTr, XTr,
        # GTAP, Stat, Percent, Pmax, Pmin

        print 'Generator:', tokens

        buses = [bus for bus in self.network.buses if
                 bus.id == str(tokens["Bus"])]

        if len(buses) == 0:
            print "Parent bus [%s] for generator not found" % tokens["Bus"]
            return
        elif len(buses) == 1:
            bus = buses[0]
        else:
            print "More than one parent bus for generator found", buses
            return

        g = Generator()

        g.p = tokens["P"]
        g.q_max = tokens["Qmax"]
        g.q_min = tokens["Qmin"]

        bus.generators.append(g)


    def _push_branch(self, tokens):
        """ Adds a branch to the network """

        # From, To, ID, R, X, B, RateA, RateB, RateC, G_busI, B_busI,
        # G_busJ, B_busJ, Stat, Len

        print "Branch:", tokens

        fr_bus = None
        to_bus = None
        for v in self.network.buses:
            if v.id == str(tokens["From"]):
                fr_bus = v
            if v.id == str(tokens["To"]):
                to_bus = v
            if fr_bus is not None and to_bus is not None:
                break

        if (fr_bus is None) or (to_bus is None):
            print "A bus for branch from %s to %s not found" % \
            (tokens["From"], tokens["To"])

#        fr_buses = [
#            bus for bus in self.network.buses if bus.id == tokens["From"]
#        ]
#
#        if len(fr_buses) == 0:
#            print "From bus [%s] for branch not found" % tokens["From"]
#            return
#        elif len(fr_buses) == 1:
#            fr_bus = fr_buses[0]
#        else:
#            print "More than on from bus for branch found", buses
#            return
#
#        to_buses = [
#            bus for bus in self.network.buses if bus.id == tokens["To"]
#        ]
#
#        if len(to_buses) == 0:
#            print "To bus [%s] for branch not found" % tokens["To"]
#            return
#        elif len(to_buses) == 1:
#            to_bus = to_buses[0]
#        else:
#            print "More than on to bus for branch found", buses
#            return

        branch = Branch(
            network=self.network,
            source_bus=fr_bus,
            target_bus=to_bus
        )

        branch.r = tokens["R"]
        branch.x = tokens["X"]
        branch.b = tokens["B"]
        branch.s_max = tokens["RateA"]
        branch.s_max_winter = tokens["RateB"]
        branch.s_max_summer = tokens["RateC"]
        branch.in_service = tokens["Stat"]

        self.network.add_branch(branch)


    def _push_transformer_data(self, tokens):
        """ Adds a branch to the network with transformer data """

        print "Transformer:", tokens

        fr_buses = [
            bus for bus in self.network.buses if bus.id == tokens["From"]
        ]

        if len(fr_buses) == 0:
            print "From bus [%s] for transformer not found" % tokens["From"]
            return
        elif len(fr_buses) == 1:
            fr_bus = fr_buses[0]
        else:
            print "More than on from bus for transformer found", buses
            return

        to_buses = [
            bus for bus in self.network.buses if bus.id == tokens["To"]
        ]

        if len(to_buses) == 0:
            print "To bus [%s] for transformer not found" % tokens["To"]
            return
        elif len(to_buses) == 1:
            to_bus = to_buses[0]
        else:
            print "More than on to bus for transformer found", buses
            return

        branch = Branch(
            network=self.network,
            source_bus=fr_bus,
            target_bus=to_bus
        )

        branch.in_service = tokens["STAT"]

        self.network.add_branch(branch)

#------------------------------------------------------------------------------
#  Convenience function for PSS/E import
#------------------------------------------------------------------------------

def import_psse(file_or_filename):
    """ Convenience function for import of a PSS/E data file given a
    file name or object.

    """

    return PSSEImporter().parse_file(file_or_filename)

#------------------------------------------------------------------------------
#  Standalone call:
#------------------------------------------------------------------------------

if __name__ == "__main__":
    import sys
    import logging
    logger = logging.getLogger()
    handler = logging.StreamHandler(sys.stdout)
#    handler = logging.StreamHandler(file("/tmp/psse.log", "w"))
    logger.addHandler(handler)
    logger.setLevel(logging.DEBUG)

    DATA_FILE = "/home/rwl/python/aes/model/psse/ukgds/HV_OHb.raw"

    n = PSSEImporter().parse_file(DATA_FILE)

# EOF -------------------------------------------------------------------------
