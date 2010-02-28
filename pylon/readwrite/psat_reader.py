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

""" Defines a class for reading PSAT data files.
"""

#------------------------------------------------------------------------------
#  Imports:
#------------------------------------------------------------------------------

import time
import logging
from os.path import basename, splitext

from parsing_util import integer, boolean, real, scolon, matlab_comment
from pyparsing import Optional, Literal, ZeroOrMore

from pylon import Case, Bus, Branch, Generator

from pylon.readwrite.common import CaseReader

#------------------------------------------------------------------------------
#  Logging:
#------------------------------------------------------------------------------

logger = logging.getLogger(__name__)

#------------------------------------------------------------------------------
#  "PSATReader" class:
#------------------------------------------------------------------------------

class PSATReader(CaseReader):
    """ Defines a method class for reading PSAT data files and
        returning a Case object.
    """

    #--------------------------------------------------------------------------
    #  "CaseReader" interface:
    #--------------------------------------------------------------------------

    def read(self, file_or_filename):
        """ Parses a PSAT data file and returns a case object

            file_or_filename: File object or path to PSAT data file
            return: Case object
        """
        self.file_or_filename = file_or_filename

        logger.info("Parsing PSAT case file [%s]." % file_or_filename)

        t0 = time.time()

        self.case = Case()

        # Name the case
        if isinstance(file_or_filename, basestring):
            name, _ = splitext(basename(file_or_filename))
        else:
            name, _ = splitext(file_or_filename.name)

        self.case.name = name

        bus_array = self._get_bus_array_construct()
        line_array = self._get_line_array_construct()
        # TODO: Lines.con - Alternative line data format
        slack_array = self._get_slack_array_construct()
        pv_array = self._get_pv_array_construct()
        pq_array = self._get_pq_array_construct()
        demand_array = self._get_demand_array_construct()
        supply_array = self._get_supply_array_construct()
        # TODO: Varname.bus (Bus names)

        # Pyparsing case:
        case = \
            ZeroOrMore(matlab_comment) + bus_array + \
            ZeroOrMore(matlab_comment) + line_array + \
            ZeroOrMore(matlab_comment) + slack_array + \
            ZeroOrMore(matlab_comment) + pv_array + \
            ZeroOrMore(matlab_comment) + pq_array + \
            ZeroOrMore(matlab_comment) + demand_array + \
            ZeroOrMore(matlab_comment) + supply_array

        case.parseFile(file_or_filename)

        elapsed = time.time() - t0
        logger.info("PSAT case file parsed in %.3fs." % elapsed)

        return self.case

    #--------------------------------------------------------------------------
    #  "PSATReader" interface:
    #--------------------------------------------------------------------------

    def _get_bus_array_construct(self):
        """ Returns a construct for an array of bus data.
        """
        bus_no = integer.setResultsName("bus_no")
        v_base = real.setResultsName("v_base") # kV
        v_magnitude_guess = Optional(real).setResultsName("v_magnitude_guess")
        v_angle_guess = Optional(real).setResultsName("v_angle_guess") # radians
        area = Optional(integer).setResultsName("area") # not used yet
        region = Optional(integer).setResultsName("region") # not used yet

        bus_data = bus_no + v_base + v_magnitude_guess + v_angle_guess + \
            area + region + scolon

        bus_data.setParseAction(self.push_bus)

        bus_array = Literal("Bus.con") + "=" + "[" + "..." + \
            ZeroOrMore(bus_data + Optional("]" + scolon))

        # Sort buses according to their name (bus_no)
        bus_array.setParseAction(self.sort_buses)

        return bus_array


    def _get_line_array_construct(self):
        """ Returns a construct for an array of line data.
        """
        from_bus = integer.setResultsName("fbus")
        to_bus = integer.setResultsName("tbus")
        s_rating = real.setResultsName("s_rating") # MVA
        v_rating = real.setResultsName("v_rating") # kV
        f_rating = real.setResultsName("f_rating") # Hz
        length = real.setResultsName("length") # km (Line only)
        v_ratio = real.setResultsName("v_ratio") # kV/kV (Transformer only)
        r = real.setResultsName("r") # p.u. or Ohms/km
        x = real.setResultsName("x") # p.u. or Henrys/km
        b = real.setResultsName("b") # p.u. or Farads/km (Line only)
        tap_ratio = real.setResultsName("tap") # p.u./p.u. (Transformer only)
        phase_shift = real.setResultsName("shift") # degrees (Transformer only)
        i_limit = Optional(real).setResultsName("i_limit") # p.u.
        p_limit = Optional(real).setResultsName("p_limit") # p.u.
        s_limit = Optional(real).setResultsName("s_limit") # p.u.
        status = Optional(boolean).setResultsName("status")

        line_data = from_bus + to_bus + s_rating + v_rating + \
            f_rating + length + v_ratio + r + x + b + tap_ratio + \
            phase_shift + i_limit + p_limit + s_limit + status + scolon

        line_data.setParseAction(self.push_line)

        line_array = Literal("Line.con") + "=" + "[" + "..." + \
            ZeroOrMore(line_data + Optional("]" + scolon))

        return line_array


    def _get_slack_array_construct(self):
        """ Returns a construct for an array of slack bus data.
        """
        bus_no = integer.setResultsName("bus_no")
        s_rating = real.setResultsName("s_rating") # MVA
        v_rating = real.setResultsName("v_rating") # kV
        v_magnitude = real.setResultsName("v_magnitude") # p.u.
        ref_angle = real.setResultsName("ref_angle") # p.u.
        q_max = Optional(real).setResultsName("q_max") # p.u.
        q_min = Optional(real).setResultsName("q_min") # p.u.
        v_max = Optional(real).setResultsName("v_max") # p.u.
        v_min = Optional(real).setResultsName("v_min") # p.u.
        p_guess = Optional(real).setResultsName("p_guess") # p.u.
         # Loss participation coefficient
        lp_coeff = Optional(real).setResultsName("lp_coeff")
        ref_bus = Optional(boolean).setResultsName("ref_bus")
        status = Optional(boolean).setResultsName("status")

        slack_data = bus_no + s_rating + v_rating + v_magnitude + \
            ref_angle + q_max + q_min + v_max + v_min + p_guess + \
            lp_coeff + ref_bus + status + scolon

        slack_data.setParseAction(self.push_slack)

        slack_array = Literal("SW.con") + "=" + "[" + "..." + \
            ZeroOrMore(slack_data + Optional("]" + scolon))

        return slack_array


    def _get_pv_array_construct(self):
        """ Returns a construct for an array of PV generator data.
        """
        bus_no = integer.setResultsName("bus_no")
        s_rating = real.setResultsName("s_rating") # MVA
        v_rating = real.setResultsName("v_rating") # kV
        p = real.setResultsName("p") # p.u.
        v = real.setResultsName("v") # p.u.
        q_max = Optional(real).setResultsName("q_max") # p.u.
        q_min = Optional(real).setResultsName("q_min") # p.u.
        v_max = Optional(real).setResultsName("v_max") # p.u.
        v_min = Optional(real).setResultsName("v_min") # p.u.
         # Loss participation coefficient
        lp_coeff = Optional(real).setResultsName("lp_coeff")
        status = Optional(boolean).setResultsName("status")

        pv_data = bus_no + s_rating + v_rating + p + v + q_max + \
            q_min + v_max + v_min + lp_coeff + status + scolon

        pv_data.setParseAction(self.push_pv)

        pv_array = Literal("PV.con") + "=" + "[" + "..." + \
            ZeroOrMore(pv_data + Optional("]" + scolon))

        return pv_array


    def _get_pq_array_construct(self):
        """ Returns a construct for an array of PQ load data.
        """
        bus_no = integer.setResultsName("bus_no")
        s_rating = real.setResultsName("s_rating") # MVA
        v_rating = real.setResultsName("v_rating") # kV
        p = real.setResultsName("p") # p.u.
        q = real.setResultsName("q") # p.u.
        v_max = Optional(real).setResultsName("v_max") # p.u.
        v_min = Optional(real).setResultsName("v_min") # p.u.
        # Allow conversion to impedance
        z_conv = Optional(boolean).setResultsName("z_conv")
        status = Optional(boolean).setResultsName("status")

        pq_data = bus_no + s_rating + v_rating + p + q + v_max + \
            v_min + z_conv + status + scolon

        pq_data.setParseAction(self.push_pq)

        pq_array = Literal("PQ.con") + "=" + "[" + "..." + \
            ZeroOrMore(pq_data + Optional("]" + scolon))

        return pq_array


    def _get_demand_array_construct(self):
        """ Returns a construct for an array of power demand data.
        """
        bus_no = integer.setResultsName("bus_no")
        s_rating = real.setResultsName("s_rating") # MVA
        p_direction = real.setResultsName("p_direction") # p.u.
        q_direction = real.setResultsName("q_direction") # p.u.
        p_bid_max = real.setResultsName("p_bid_max") # p.u.
        p_bid_min = real.setResultsName("p_bid_min") # p.u.
        p_optimal_bid = Optional(real).setResultsName("p_optimal_bid")
        p_fixed = real.setResultsName("p_fixed") # $/hr
        p_proportional = real.setResultsName("p_proportional") # $/MWh
        p_quadratic = real.setResultsName("p_quadratic") # $/MW^2h
        q_fixed = real.setResultsName("q_fixed") # $/hr
        q_proportional = real.setResultsName("q_proportional") # $/MVArh
        q_quadratic = real.setResultsName("q_quadratic") # $/MVAr^2h
        commitment = boolean.setResultsName("commitment")
        cost_tie_break = real.setResultsName("cost_tie_break") # $/MWh
        cost_cong_up = real.setResultsName("cost_cong_up") # $/h
        cost_cong_down = real.setResultsName("cost_cong_down") # $/h
        status = Optional(boolean).setResultsName("status")

        demand_data = bus_no + s_rating + p_direction + q_direction + \
            p_bid_max + p_bid_min + p_optimal_bid + p_fixed + \
            p_proportional + p_quadratic + q_fixed + q_proportional + \
            q_quadratic + commitment + cost_tie_break + cost_cong_up + \
            cost_cong_down + status + scolon

        demand_data.setParseAction(self.push_demand)

        demand_array = Literal("Demand.con") + "=" + "[" + "..." + \
            ZeroOrMore(demand_data + Optional("]" + scolon))

        return demand_array


    def _get_supply_array_construct(self):
        """ Returns a construct for an array of power supply data.
        """
        bus_no = integer.setResultsName("bus_no")
        s_rating = real.setResultsName("s_rating") # MVA
        p_direction = real.setResultsName("p_direction") # CPF
        p_bid_max = real.setResultsName("p_bid_max") # p.u.
        p_bid_min = real.setResultsName("p_bid_min") # p.u.
        p_bid_actual = real.setResultsName("p_bid_actual") # p.u.
        p_fixed = real.setResultsName("p_fixed") # $/hr
        p_proportional = real.setResultsName("p_proportional") # $/MWh
        p_quadratic = real.setResultsName("p_quadratic") # $/MW^2h
        q_fixed = real.setResultsName("q_fixed") # $/hr
        q_proportional = real.setResultsName("q_proportional") # $/MVArh
        q_quadratic = real.setResultsName("q_quadratic") # $/MVAr^2h
        commitment = boolean.setResultsName("commitment")
        cost_tie_break = real.setResultsName("cost_tie_break") # $/MWh
        lp_factor = real.setResultsName("lp_factor")# Loss participation factor
        q_max = real.setResultsName("q_max") # p.u.
        q_min = real.setResultsName("q_min") # p.u.
        cost_cong_up = real.setResultsName("cost_cong_up") # $/h
        cost_cong_down = real.setResultsName("cost_cong_down") # $/h
        status = Optional(boolean).setResultsName("status")

        supply_data = bus_no + s_rating + p_direction + p_bid_max + \
            p_bid_min + p_bid_actual + p_fixed + p_proportional + \
            p_quadratic + q_fixed + q_proportional + q_quadratic + \
            commitment + cost_tie_break + lp_factor + q_max + q_min + \
            cost_cong_up + cost_cong_down + status + scolon

        supply_data.setParseAction(self.push_supply)

        supply_array = Literal("Supply.con") + "=" + "[" + "..." + \
            ZeroOrMore(supply_data + Optional("]" + scolon))

        return supply_array


    def _get_generator_ramping_construct(self):
        """ Returns a construct for an array of generator ramping data.
        """
        supply_no = integer.setResultsName("supply_no")
        s_rating = real.setResultsName("s_rating") # MVA
        up_rate = real.setResultsName("up_rate") # p.u./h
        down_rate = real.setResultsName("down_rate") # p.u./h
        min_period_up = real.setResultsName("min_period_up") # h
        min_period_down = real.setResultsName("min_period_down") # h
        initial_period_up = integer.setResultsName("initial_period_up")
        initial_period_down = integer.setResultsName("initial_period_down")
        c_startup = real.setResultsName("c_startup") # $
        status = boolean.setResultsName("status")

        g_ramp_data = supply_no + s_rating + up_rate + down_rate + \
            min_period_up + min_period_down + initial_period_up + \
            initial_period_down + c_startup + status + scolon

        g_ramp_array = Literal("Rmpg.con") + "=" + "[" + \
            ZeroOrMore(g_ramp_data + Optional("]" + scolon))

        return g_ramp_array


    def _get_load_ramping_construct(self):
        """ Returns a construct for an array of load ramping data.
        """
        bus_no = integer.setResultsName("bus_no")
        s_rating = real.setResultsName("s_rating") # MVA
        up_rate = real.setResultsName("up_rate") # p.u./h
        down_rate = real.setResultsName("down_rate") # p.u./h
        min_up_time = real.setResultsName("min_up_time") # min
        min_down_time = real.setResultsName("min_down_time") # min
        n_period_up = integer.setResultsName("n_period_up")
        n_period_down = integer.setResultsName("n_period_down")
        status = boolean.setResultsName("status")

        l_ramp_data = bus_no + s_rating + up_rate + down_rate + \
            min_up_time + min_down_time + n_period_up + \
            n_period_down + status + scolon

        l_ramp_array = Literal("Rmpl.con") + "=" + "[" + \
            ZeroOrMore(l_ramp_data + Optional("]" + scolon))

        return l_ramp_array

    #--------------------------------------------------------------------------
    #  Parse actions:
    #--------------------------------------------------------------------------

    def push_bus(self, tokens):
        """ Adds a Bus object to the case.
        """
        logger.debug("Pushing bus data: %s" % tokens)

        bus = Bus()
        bus.name = tokens["bus_no"]
        bus.v_magnitude_guess = tokens["v_magnitude_guess"]
        bus.v_angle_guess = tokens["v_angle_guess"]
        bus.v_magnitude = tokens["v_magnitude_guess"]
        bus.v_angle = tokens["v_angle_guess"]

        self.case.buses.append(bus)


    def sort_buses(self, tokens):
        """ Sorts bus list according to name (bus_no).
        """
        self.case.buses.sort(key=lambda obj: obj.name)


    def push_line(self, tokens):
        """ Adds a Branch object to the case.
        """
        logger.debug("Pushing line data: %s" % tokens)

        from_bus = self.case.buses[tokens["fbus"]-1]
        to_bus = self.case.buses[tokens["tbus"]-1]

        e = Branch(from_bus=from_bus, to_bus=to_bus)
        e.r = tokens["r"]
        e.x = tokens["x"]
        e.b = tokens["b"]
        e.rate_a = tokens["s_limit"]
        e.rate_b = tokens["p_limit"]
        e.rate_c = tokens["i_limit"]
        # Optional parameter
        if tokens["tap"] == 0: #Transmission line
            e.ratio = 1.0
        else: # Transformer
            e.ratio = tokens["tap"]
        e.phase_shift = tokens["shift"]
        # Optional parameter
#        if "status" in tokens.keys:
#        e.online = tokens["status"]

        self.case.branches.append(e)


    def push_slack(self, tokens):
        """ Finds the slack bus, adds a Generator with the appropriate data
            and sets the bus type to slack.
        """
        logger.debug("Pushing slack data: %s" % tokens)

        bus = self.case.buses[tokens["bus_no"] - 1]

        g = Generator(bus)
        g.q_max = tokens["q_max"]
        g.q_min = tokens["q_min"]
        # Optional parameter
#        if tokens.has_key("status"):
#        g.online = tokens["status"]

        self.case.generators.append(g)

        bus.type = "ref"


    def push_pv(self, tokens):
        """ Creates and Generator object, populates it with data,
            finds its Bus and adds it.
        """
        logger.debug("Pushing PV data: %s" % tokens)

        bus = self.case.buses[tokens["bus_no"]-1]

        g = Generator(bus)
        g.p = tokens["p"]
        g.q_max = tokens["q_max"]
        g.q_min = tokens["q_min"]
        # Optional parameter
#        if tokens.has_key("status"):
#        g.online = tokens["status"]

        self.case.generators.append(g)


    def push_pq(self, tokens):
        """ Creates and Load object, populates it with data,
            finds its Bus and adds it.
        """
        logger.debug("Pushing PQ data: %s" % tokens)

        bus = self.case.buses[tokens["bus_no"] - 1]
        bus.p_demand = tokens["p"]
        bus.q_demand = tokens["q"]


    def push_demand(self, tokens):
        """ Added OPF and CPF data to an appropriate Load.
        """
        logger.debug("Pushing demand data: %s" % tokens)

#        bus = self.case.buses[tokens["bus_no"] - 1]
#        n_loads = len(bus.loads)
#
#        if n_loads == 0:
#            logger.error("No load at bus [%s] for matching demand" % bus)
#            return
#        elif n_loads > 1:
#            l = bus.loads[0]
#            logger.warning(
#                "More than one load at bus [%s] for demand. Using the "
#                "first one [%s]." % (bus, l)
#            )
#        else:
#            l = bus.loads[0]

        # Optional parameter
#        if tokens.has_key("status"):
#            l.in_service = tokens["status"]


    def push_supply(self, tokens):
        """ Adds OPF and CPF data to a Generator.
        """
        logger.debug("Pushing supply data: %s" % tokens)

        bus = self.case.buses[tokens["bus_no"] - 1]
        n_generators = len([g for g in self.case.generators if g.bus == bus])

        if n_generators == 0:
            logger.error("No generator at bus [%s] for matching supply" % bus)
            return
        elif n_generators > 1:
            g = [g for g in self.case.generators if g.bus == bus][0]
            logger.warning(
                "More than one generator at bus [%s] for demand. Using the "
                "first one [%s]." % (bus, g)
            )
        else:
            g = [g for g in self.case.generators if g.bus == bus][0]

        g.pcost_model = "poly"
        g.poly_coeffs = (
            tokens["p_fixed"],
            tokens["p_proportional"],
            tokens["p_quadratic"]
        )
        # Optional parameter
#        if tokens.has_key("status"):
#            g.online = tokens["status"]

# EOF -------------------------------------------------------------------------
