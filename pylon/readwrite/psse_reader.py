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

""" Defines a reader for PSS/E data files.
"""

#------------------------------------------------------------------------------
#  Imports:
#------------------------------------------------------------------------------

import time
import logging

from parsing_util \
    import integer, boolean, real, scolon, psse_comment, comma_sep

from pyparsing \
    import Literal, Word, restOfLine, alphanums, printables, quotedString, \
    White, OneOrMore, ZeroOrMore, Optional, alphas

from pylon import Case, Bus, Branch, Generator, Load

#------------------------------------------------------------------------------
#  Logging:
#------------------------------------------------------------------------------

logger = logging.getLogger(__name__)

#-------------------------------------------------------------------------------
#  "PSSEReader" class:
#-------------------------------------------------------------------------------

class PSSEReader(object):
    """ Defines a reader of PSS/E data files that returns a case object.
    """

    def __init__(self):
        """ Initialises a new PSSEReader instance.
        """
        # Path to the data file or file object.
        self.file_or_filename = None
        # The resulting case.
        self.case = None


    def __call__(self, file_or_filename):
        """ Calls the reader with the given file or file name.
        """
        self.read(file_or_filename)


    def read(self, file_or_filename):
        """ Parses a PSS/E data file and returns a case object.
        """
        self.file_or_filename = file_or_filename

        logger.info("Parsing PSS/E case file [%s]." % file_or_filename)

        t0 = time.time()

        self.case = Case()

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
               ZeroOrMore(psse_comment) + Optional(title) + \
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

        elapsed = time.time() - t0
        logger.info("PSS/E case file parsed in %.3fs." % elapsed)

        return self.case

    #--------------------------------------------------------------------------
    #  Construct getters:
    #--------------------------------------------------------------------------

    def _get_separator_construct(self):
        """ Returns a construct for a PSS/E separator.
        """
        # Tables are separated by a single 0
        separator = Literal('0') + Optional(restOfLine)#White('\n')
        separator.setParseAction(self._push_separator)

        return separator


    def _get_header_construct(self):
        """ Returns a construct for the header of a PSS/E file.
        """
        first_line = Word('0', exact=1).suppress() + comma_sep + real + \
            restOfLine.suppress()
        first_line.setParseAction(self._push_system_base)
        return first_line


    def _get_title_construct(self):
        """ Returns a construct for the subtitle of a PSS/E file.
        """
        title = Word(alphas).suppress() + restOfLine.suppress()
        sub_title = Word(printables) + restOfLine.suppress()
#        sub_title = Combine(Word(alphanums) + restOfLine)
        sub_title.setParseAction(self._push_sub_title)
        sub_title.setResultsName("sub_title")

        return title + sub_title


    def _get_bus_data_construct(self):
        """ Returns a construct for a line of bus data.
        """
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
        i = integer.setResultsName("Bus") + comma_sep
        bus_name = quotedString.setResultsName("Name") + comma_sep
        base_kv = real.setResultsName("Base_kV") + comma_sep
        ide = Word("1234", exact=1).setResultsName("Type") + comma_sep
        sh_conductance = real.setResultsName("Y_re") + comma_sep
        sh_susceptance = real.setResultsName("Y_im") + comma_sep
        area = integer.setResultsName("Area") + comma_sep
        zone = integer.setResultsName("Zone") + comma_sep
        v_magnitude = real.setResultsName("PU_Volt") + comma_sep
        v_angle = real.setResultsName("Angle")

        bus_data = i + bus_name + base_kv + ide + sh_conductance + \
            sh_susceptance + area + zone + v_magnitude + v_angle + \
            restOfLine.suppress()

        bus_data.setParseAction(self._push_bus_data)
        return bus_data


    def _get_load_data_construct(self):
        """ Returns a construct for a line of load data.
        """
        # [Bus, LoadID, Status, Area, Zone, LP, LQ]
        bus_id = integer.setResultsName("Bus") + comma_sep
        load_id = integer.setResultsName("LoadID") + comma_sep
        status = boolean.setResultsName("Status") + comma_sep
        area = integer.setResultsName("Area") + comma_sep
        zone = integer.setResultsName("Zone") + comma_sep
        p_load = real.setResultsName("LP") + comma_sep
        q_load = real.setResultsName("LQ")

        load_data = bus_id + load_id + status + area + zone + p_load + \
                    q_load + restOfLine.suppress()

        load_data.setParseAction(self._push_load_data)
        return load_data


    def _get_generator_data_construct(self):
        """ Returns a construct for a line of generator data.
        """
        # [I,ID,PG,QG,QT,QB,VS,IREG,MBASE,ZR,ZX,RT,XT,GTAP,STAT,RMPCT,PT,PB]
#        bus_idx = integer
#        machine_id = Word(alphanums, exact=1)
#        mw_out = real
#        mvar_out = real
#        mvar_max = real
#        mvar_min = real
#        v_setpoint = real
#        reg_idx = integer
#        base_mva = real
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
#                         mvar_min + v_setpoint + reg_idx + base_mva + z_r + \
#                         z_x + r_t + x_t + g_tap + status + rmpct + mw_max + \
#                         mw_min

        # Bus, ID, P, Q, Qmax, Qmin, SchedV, RegBs, MVAbase, ZR, ZX, RTr,
        # XTr, GTAP, Stat, Percent, Pmax, Pmin

        bus_id = integer.setResultsName("Bus") + comma_sep
        generator_id = integer.setResultsName("ID") + comma_sep
        p = real.setResultsName("P") + comma_sep
        q = real.setResultsName("Q") + comma_sep
        q_max = real.setResultsName("Qmax") + comma_sep
        q_min = real.setResultsName("Qmin") + comma_sep
        v_sched = real.setResultsName("SchedV") + comma_sep
        reg_bus = integer.setResultsName("RegBs") + comma_sep
        base_mva = real.setResultsName("MVAbase") + comma_sep
        r_zero = real.setResultsName("ZR") + comma_sep
        x_zero = real.setResultsName("ZX") + comma_sep
        r_tr = real.setResultsName("RTr") + comma_sep
        x_tr = real.setResultsName("XTr") + comma_sep
        gtap = integer.setResultsName("GTAP") + comma_sep
        status = boolean.setResultsName("Stat") + comma_sep
        percent = integer.setResultsName("Percent") + comma_sep
        p_max = real.setResultsName("Pmax") + comma_sep
        p_min = real.setResultsName("Pmin")

        generator_data = bus_id + generator_id + p + q + q_max + q_min + \
            v_sched + reg_bus + base_mva + r_zero + x_zero + r_tr + x_tr + \
            gtap + status + percent + p_max + p_min + restOfLine.suppress()

        generator_data.setParseAction(self._push_generator)
        return generator_data


    def _get_branch_data_construct(self):
        """ Returns a construct for a line of branch data.
        """
        # From, To, ID, R, X, B, RateA, RateB, RateC, G_busI, B_busI,
        # G_busJ, B_busJ, Stat, Len
        from_bus_id = integer.setResultsName("From") + comma_sep
        to_bus_id = integer.setResultsName("To") + comma_sep
        id = integer.setResultsName("ID") + comma_sep
        r = real.setResultsName("R") + comma_sep
        x = real.setResultsName("X") + comma_sep
        b = real.setResultsName("B") + comma_sep
        rate_a = real.setResultsName("RateA") + comma_sep
        rate_b = real.setResultsName("RateB") + comma_sep
        rate_c = real.setResultsName("RateC") + comma_sep
        g_bus_i = real.setResultsName("G_busI") + comma_sep
        b_bus_i = real.setResultsName("B_busI") + comma_sep
        g_bus_j = real.setResultsName("G_busJ") + comma_sep
        b_bus_j = real.setResultsName("B_busJ") + comma_sep
        status = boolean.setResultsName("Stat") + comma_sep
        length = real.setResultsName("Len")

        branch_data = from_bus_id + to_bus_id + id + r + x + b + \
            rate_a + rate_b + rate_c + g_bus_i + b_bus_i + g_bus_j + \
            b_bus_j + status + length + restOfLine.suppress()

        branch_data.setParseAction(self._push_branch)
        return branch_data


    def _get_transformer_data_construct(self):
        """ Returns a construct for a line of transformer data.
        """
        # From, To, K, ID, CW, CZ, CM, MAG1, MAG2, NMETR, NAME, STAT, O1, F1
        # R1-2, X1-2, SBASE1-2
        # WINDV1, NOMV1, ANG1, RATA1, RATB1, RATC1, COD, CONT, RMA, RMI, VMA, VMI, NTP, TAB, CR, CX
        # WINDV2, NOMV2

        # Unused column of data
        unused = Literal("/").suppress()

        from_bus_id = integer.setResultsName("From") + comma_sep
        to_bus_id = integer.setResultsName("To") + comma_sep
        k = integer.setResultsName("K") + comma_sep
        id = integer.setResultsName("ID") + comma_sep
        cw = integer.setResultsName("CW") + comma_sep
        cz = integer.setResultsName("CZ") + comma_sep
        cm = integer.setResultsName("CM") + comma_sep
        mag1 = real.setResultsName("MAG1") + comma_sep
        mag2 = real.setResultsName("MAG2") + comma_sep
        nmetr = integer.setResultsName("NMETR") + comma_sep
        name = quotedString.setResultsName("NAME") + comma_sep
        status = boolean.setResultsName("STAT") + comma_sep
        o1 = integer.setResultsName("o1") + comma_sep
        f1 = integer.setResultsName("f1") + comma_sep

        transformer_general = from_bus_id + to_bus_id + k + id + \
            cw + cz + cm + mag1 + mag2 + nmetr + name + status + \
            o1 + f1 + OneOrMore(unused)

        r12 = real.setResultsName("R1-2") + comma_sep
        x12 = real.setResultsName("X1-2") + comma_sep
        s_base12 = real.setResultsName("SBASE1-2") + comma_sep

        transformer_impedance = r12 + x12 + s_base12 + OneOrMore(unused)

        v1_wind = real.setResultsName("WINDV1") + comma_sep
        v1_nom = real.setResultsName("NOMV1") + comma_sep
        angle1 = real.setResultsName("ANG1") + comma_sep
        rate_a1 = real.setResultsName("RATA1") + comma_sep
        rate_b1 = real.setResultsName("RATB1") + comma_sep
        rate_c1 = real.setResultsName("RATC1") + comma_sep
        cod = integer.setResultsName("COD") + comma_sep
        cont = real.setResultsName("CONT") + comma_sep
        rma = real.setResultsName("RMA") + comma_sep
        rmi = real.setResultsName("RMI") + comma_sep
        vma = real.setResultsName("VMA") + comma_sep
        vmi = real.setResultsName("VMI") + comma_sep
        ntp = real.setResultsName("NTP") + comma_sep
        tab = real.setResultsName("TAB") + comma_sep
        cr = real.setResultsName("CR") + comma_sep
        cx = real.setResultsName("CX") + comma_sep

        transformer_winding_1 = v1_wind + v1_nom + angle1 + rate_a1 + \
            rate_b1 + rate_c1 + cod + cont + rma + rmi + vma + vmi + \
            ntp + tab + cr + cx

        v2_wind = real.setResultsName("WINDV2") + comma_sep
        v2_nom = real.setResultsName("NOMV2") + comma_sep

        transformer_winding_2 = v2_wind + v2_nom + OneOrMore(unused)

        transformer_data = transformer_general + transformer_impedance + \
            transformer_winding_1 + transformer_winding_2

        transformer_data.setParseAction(self._push_transformer_data)

        return transformer_data

    #--------------------------------------------------------------------------
    #  Parse actions:
    #--------------------------------------------------------------------------

    def _push_system_base(self, tokens):
        """ Set the system base.
        """
        logger.debug("MVA Base: %.3f" % tokens[0])
        self.case.base_mva = tokens[0]


    def _push_title(self, tokens):
        """ Handles the case title.
        """
        logger.debug("Title: %s" % tokens[0])


    def _push_sub_title(self, tokens):
        """ Sets the case name.
        """
        logger.debug("Sub-Title: %s" % tokens[0])
        self.case.name = tokens[0]


    def _push_separator(self):
        """ Handles separators.
        """
        logger.debug("Parsed separator.")


    def _push_bus_data(self, tokens):
        """ Adds a bus to the case.
        """
        # [I, IDE, PL, QL, GL, BL, IA, VM, VA, 'NAME', BASKL, ZONE]
        # Bus, Name, Base_kV, Type, Y_re, Y_im, Area, Zone, PU_Volt, Angle
        logger.debug("Parsing bus data: %s" % tokens)

        bus = Bus()
        bus.name = tokens["Name"].strip("'")
        bus._bus_id = tokens["Bus"]

        bus.v_magnitude_guess = tokens["PU_Volt"]
        bus.v_magnitude = tokens["PU_Volt"]

        bus.v_angle_guess = tokens["Angle"]
        bus.v_angle = tokens["Angle"]

        self.case.buses.append(bus)


    def _push_load_data(self, tokens):
        """ Adds a load to a bus.
        """
        #[Bus, Load, ID, Status, Area, Zone, LP, LQ]
        logger.debug("Parsing load data: %s" % tokens)

        for bus in self.case.buses:
            if bus._bus_id == tokens["Bus"]:
                break
        else:
            pass
            logger.error("Bus [%d] for load not found." % tokens["Bus"])

        load = Load(p=tokens["LP"], q=tokens["LQ"])
        bus.loads.append(load)


    def _push_generator(self, tokens):
        """ Adds a generator to a bus.
        """
        # [I,ID,PG,QG,QT,QB,VS,IREG,MBASE,ZR,ZX,RT,XT,GTAP,STAT,RMPCT,PT,PB]
        # Bus, ID, P, Q, Qmax, Qmin, SchedV, RegBs, MVAbase, ZR, ZX, RTr, XTr,
        # GTAP, Stat, Percent, Pmax, Pmin

        logger.debug("Parsing generator data: %s" % tokens)

        for bus in self.case.buses:
            if bus._bus_id == tokens["Bus"]:
                break
        else:
            logger.error("Bus [%d] for generator not found." % tokens["Bus"])
            return

        base = tokens["MVAbase"]

        g = Generator()
        g.base_mva = base
        g.p_max = tokens["Pmax"]
        g.p_min = tokens["Pmin"]
        g.p     = tokens["P"]

        g.q_max = tokens["Qmax"]
        g.q_min = tokens["Qmin"]
        g.q     = tokens["Q"]

        g.status = tokens["Stat"]

        bus.generators.append(g)


    def _push_branch(self, tokens):
        """ Adds a branch to the case.
        """
        # From, To, ID, R, X, B, RateA, RateB, RateC, G_busI, B_busI,
        # G_busJ, B_busJ, Stat, Len
        logger.debug("Parsing branch data: %s", tokens)

        from_bus = None
        to_bus = None
        for v in self.case.buses:
            if from_bus is None:
                if v._bus_id == tokens["From"]:
                    from_bus = v
            if to_bus is None:
                if v._bus_id == tokens["To"]:
                    to_bus = v
            if (from_bus is not None) and (to_bus is not None):
                break
        else:
            logger.error("A bus for branch from %d to %d not found" %
            (tokens["From"], tokens["To"]))
            return

#        from_buses = [
#            bus for bus in self.case.buses if bus.id == tokens["From"]
#        ]
#
#        if len(from_buses) == 0:
#            print "From bus [%s] for branch not found" % tokens["From"]
#            return
#        elif len(from_buses) == 1:
#            from_bus = from_buses[0]
#        else:
#            print "More than on from bus for branch found", buses
#            return
#
#        to_buses = [
#            bus for bus in self.case.buses if bus.id == tokens["To"]
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

        branch = Branch(source_bus=from_bus, target_bus=to_bus)

        branch.r = tokens["R"]
        branch.x = tokens["X"]
        branch.b = tokens["B"]
        branch.s_max = tokens["RateA"]
        branch.s_max_winter = tokens["RateB"]
        branch.s_max_summer = tokens["RateC"]
        branch.online = tokens["Stat"]

        self.case.branches.append(branch)


    def _push_transformer_data(self, tokens):
        """ Adds a branch to the case with transformer data.
        """
        logger.debug("Parsing transformer data: %s" % tokens)

        from_bus = None
        to_bus = None
        for v in self.case.buses:
            if from_bus is None:
                if v._bus_id == tokens["From"]:
                    from_bus_id = v
            if to_bus is None:
                if v._bus_id == tokens["To"]:
                    to_bus = v
            if (from_bus is not None) and (to_bus is not None):
                break
        else:
            logger.error("A bus for branch from %d to %d not found" %
            (tokens["From"], tokens["To"]))
            return

        branch = Branch(source_bus=from_bus, target_bus=to_bus)
        branch.online = tokens["STAT"]

        self.case.branches.append(branch)

# EOF -------------------------------------------------------------------------
