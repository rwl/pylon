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

""" Defines a class for reading MATPOWER data files.
"""

#------------------------------------------------------------------------------
#  Imports:
#------------------------------------------------------------------------------

import os.path
import logging

from parsing_util import \
    integer, boolean, real, scolon, matlab_comment, make_unique_name, \
    ToInteger, lbrack, rbrack, equals

from pyparsing import \
    Literal, Word, ZeroOrMore, Optional, OneOrMore, delimitedList, \
    alphas, Combine, printables, quotedString

from pylon.case import Case, Bus, Branch
from pylon.generator import Generator
from pylon.readwrite.common import CaseReader

#------------------------------------------------------------------------------
#  Logging:
#------------------------------------------------------------------------------

logger = logging.getLogger(__name__)

#------------------------------------------------------------------------------
#  "MATPOWERReader" class:
#------------------------------------------------------------------------------

class MATPOWERReader(CaseReader):
    """ Defines a method class for reading MATPOWER data files and
        returning a Case object.
    """

    def __init__(self, case_format=2):
        """ Initialises a new MATPOWERReader instance.
        """
        # MATPOWER case format.  Version 2 introduced in MATPOWER 4.0b1.
        self.case_format = case_format

        # Path to the data file or file object.
        self.file_or_filename = None

        # The resulting case.
        self.case = None

        # Count of generators to which cost data has been applied.
        self.costed = 0

    #--------------------------------------------------------------------------
    #  Parse a MATPOWER data file and return a case object
    #--------------------------------------------------------------------------

    def read(self, file_or_filename):
        """ Parse a MATPOWER data file and return a case object

            file_or_filename: File name of file object with MATPOWER data
            return: Case object
        """
        self.file_or_filename = file_or_filename

        if isinstance(file_or_filename, basestring):
            fname = os.path.basename(file_or_filename)
            logger.info("Parsing MATPOWER case file [%s]." % fname)
        else:
            logger.info("Parsing MATPOWER case file.")

        # Initialise:
        case = self.case = Case()
        self.costed = 0

        # Form array constructs
        header = self._get_header_construct()
        version = self._get_case_format_construct()
        base_mva = self._get_base_mva_construct()
        bus_array = self._get_bus_array_construct()
        gen_array = self._get_generator_array_construct()
        branch_array = self._get_branch_array_construct()
        area_array = self._get_area_array_construct()
        generator_cost_array = self._get_generator_cost_array_construct()

        # Assemble pyparsing case:
        parsing_case = header + \
            ZeroOrMore(matlab_comment) + version + \
            ZeroOrMore(matlab_comment) + base_mva + \
            ZeroOrMore(matlab_comment) + bus_array + \
            ZeroOrMore(matlab_comment) + gen_array + \
            ZeroOrMore(matlab_comment) + branch_array + \
            ZeroOrMore(matlab_comment) + Optional(area_array) + \
            ZeroOrMore(matlab_comment) + Optional(generator_cost_array)

        # Parse the data file
        parsing_case.parseFile(file_or_filename)

        # Update internal indices.
        case.index_buses()
        case.index_branches()

        return case

    #--------------------------------------------------------------------------
    #  Construct getters:
    #--------------------------------------------------------------------------

    def _get_header_construct(self):
        """ Returns a construct for the header of a MATPOWER data file.
        """
        # Use the function name for the Case title
        title = Word(printables).setResultsName("title")
        title.setParseAction(self._push_title)
        if self.case_format == 1:
            header = Literal("function") + \
                lbrack + delimitedList(Word(alphas)) + rbrack + \
                "=" + title
        elif self.case_format == 2:
            header = Literal("function") + Literal("mpc") + equals + title

        return header


    def _get_case_format_construct(self):
        """ Returns a construct for the case formet expression introduced in
            MATPOWER 4.0.
        """
        if self.case_format == 1:
            version_expr = Optional(matlab_comment)
        else:
            version = quotedString.setResultsName("version")
            version_expr = Literal("mpc.version") + equals + version + scolon

        return version_expr


    def _get_base_mva_construct(self):
        """ Returns a construct for the base MVA expression.
        """
        base_mva = real.setResultsName("baseMVA")
        base_mva.setParseAction(self._push_base_mva)
        base_mva_expr = Combine(Optional("mpc.") + Literal("baseMVA")) + \
            Literal("=") + base_mva + scolon

        return base_mva_expr


    def _get_bus_array_construct(self):
        """ Returns a construct for an array of bus data.
        """
        bus_id = integer.setResultsName("bus_id")
        bus_type = ToInteger(Word('123', exact=1)).setResultsName("bus_type")
        appr_demand = real.setResultsName("Pd") + real.setResultsName("Qd")
        shunt_addm = real.setResultsName("Gs") + real.setResultsName("Bs")
        area = integer.setResultsName("area")
        Vm = real.setResultsName("Vm")
        Va = real.setResultsName("Va")
        kV_base = real.setResultsName("baseKV")
        zone = integer.setResultsName("zone")
        Vmax = real.setResultsName("Vmax")
        Vmin = real.setResultsName("Vmin")

        bus_data = bus_id + bus_type + appr_demand + shunt_addm + \
            area + Vm + Va + kV_base + zone + Vmax + Vmin + scolon

        bus_data.setParseAction(self._push_bus)

        bus_array = Combine(Optional("mpc.") + Literal('bus')) + equals + \
            lbrack + ZeroOrMore(bus_data) + Optional(rbrack + scolon)

        return bus_array


    def _get_generator_array_construct(self):
        """ Returns an construct for an array of generator data.
        """
        bus_id = integer.setResultsName("bus_id")
        active = real.setResultsName("Pg")
        reactive = real.setResultsName("Qg")
        max_reactive = real.setResultsName("Qmax")
        min_reactive = real.setResultsName("Qmin")
        voltage = real.setResultsName("Vg")
        base_mva = real.setResultsName("mBase")
        status = boolean.setResultsName("status")
        max_active = real.setResultsName("Pmax")
        min_active = real.setResultsName("Pmin")

        gen_data = bus_id + active + reactive + max_reactive + \
            min_reactive + voltage + base_mva + status + max_active + \
            min_active + ZeroOrMore(real) + scolon

        gen_data.setParseAction(self._push_generator)

        gen_array = Combine(Optional("mpc.") + Literal('gen')) + equals + \
            lbrack + ZeroOrMore(gen_data) + Optional(rbrack + scolon)

        return gen_array


    def _get_branch_array_construct(self):
        """ Returns a construct for an array of branch data.
        """
        from_bus = integer.setResultsName("fbus")
        to_bus = integer.setResultsName("tbus")
        resistance = real.setResultsName("r")
        reactance = real.setResultsName("x")
        susceptance = real.setResultsName("b")
        long_mva = real.setResultsName("rateA")
        short_mva = real.setResultsName("rateB")
        emerg_mva = real.setResultsName("rateC")
        ratio = real.setResultsName("ratio")
        angle = real.setResultsName("angle")
        status = boolean.setResultsName("status")
        ang_min = real.setResultsName("ang_min")
        ang_max = real.setResultsName("ang_max")

        branch_data = from_bus + to_bus + resistance + reactance + \
            susceptance + long_mva + short_mva + emerg_mva + ratio + angle + \
            status + Optional(ang_min + ang_max) + scolon

        branch_data.setParseAction(self._push_branch)

        branch_array = Combine(Optional("mpc.") + Literal('branch')) + \
            equals + lbrack + ZeroOrMore(branch_data) + \
            Optional(rbrack + scolon)

        return branch_array


    def _get_area_array_construct(self):
        """ Returns a construct for an array of area data.
        """
        area = integer.setResultsName("area_id")
        price_ref_bus = integer.setResultsName("price_ref_bus")

        area_data = area + price_ref_bus + scolon

        if self.case_format == 1:
            area_array = Literal('areas') + equals + lbrack + \
                ZeroOrMore(area_data) + Optional(rbrack + scolon)
        elif self.case_format == 2:
            area_array = Optional(Combine(Literal('mpc.areas')) + \
                equals + lbrack + \
                ZeroOrMore(area_data) + Optional(rbrack + scolon))

        return area_array


    def _get_generator_cost_array_construct(self):
        """ Returns a construct for an array of generator cost data.
        """
        # [model, startup, shutdown, n, x0, y0, x1, y1]
        # 1 - piecewise linear, 2 - polynomial
        model = integer.setResultsName("model")
        # start up cost
        startup = real.setResultsName("startup")
        # shut down cost
        shutdown = real.setResultsName("shutdown")
        # number of cost coefficients to follow for polynomial
        # cost function, or number of data points for pw linear
        n  = integer.setResultsName("n")
#        x0 = real.setResultsName("x0")
#        y0 = real.setResultsName("y0")
#        x1 = real.setResultsName("x1")
#        y1 = real.setResultsName("y1")

        linear_cost_data = model + startup + shutdown + n + \
            OneOrMore(real) + scolon

        linear_cost_data.setParseAction(self._push_generator_cost)

#        piecewise_cost_data = model + startup + shutdown + n + OneOrMore(tuple)
#        piecewise_cost_data.setParseAction(self.push_piecewise_cost)

#        polynomial_cost_data = model + startup + shutdown + n + OneOrMore(real)
#        polynomial_cost_data.setParseAction(self.push_polynomial_cost)

        gen_cost_array = Combine(Optional("mpc.") + Literal('gencost')) + \
            equals + lbrack + ZeroOrMore(linear_cost_data) + \
            Optional(rbrack + scolon)

        return gen_cost_array

    #--------------------------------------------------------------------------
    #  Parse actions:
    #--------------------------------------------------------------------------

    def _push_title(self, tokens):
        """ Sets the case's name.
        """
        logger.debug("Parsing system name: %s" % tokens["title"])

        self.case.name = tokens["title"]


    def _push_base_mva(self, tokens):
        """ Set the MVA base for the case.
        """
        logger.debug("Parsing system base: %.1f" % tokens["baseMVA"])

        self.case.base_mva = tokens["baseMVA"]


    def _push_bus(self, tokens):
        """ Adds a bus to the case.
        """
        logger.debug("Parsing bus data: %s" % tokens)

        name = "Bus-" + str(tokens["bus_id"])
        bus = Bus(name=name)

        # Assign a private id attribute for use when pushing generators
        # and branches.
        bus._bus_id = tokens["bus_id"]

        base_kv = tokens["baseKV"]

        bus.v_base = base_kv
        bus.g_shunt = tokens["Gs"]
        bus.b_shunt = tokens["Bs"]
        bus.v_magnitude_guess = tokens["Vm"]
        bus.v_angle_guess = tokens["Va"]
        bus.v_magnitude = tokens["Vm"]
        bus.v_angle = tokens["Va"]

        # Bus type 3 denotes a slack bus in MATPOWER
        bustype_map = {1: "PQ", 2: "PV", 3: "ref", 4: "isolated"}
        bus.type = bustype_map[tokens["bus_type"]]

        bus.p_demand = tokens["Pd"]
        bus.q_demand = tokens["Qd"]

        bus.area = tokens["area"]
        bus.zone = tokens["zone"]

        bus.v_max = tokens["Vmax"]
        bus.v_min = tokens["Vmin"]

        self.case.buses.append(bus)


    def _push_generator(self, tokens):
        """ Adds a generator to the respective bus.
        """
        logger.debug("Parsing generator data: %s" % tokens)

#        base_mva = tokens["mBase"]
#        if base_mva == 0.0:
#            base_mva = self.base_mva # Default to system base.

        # Locate the generator bus.
        for bus in self.case.buses:
            if bus._bus_id == tokens["bus_id"]:
                break
        else:
            logger.error("Bus [%d] not found." % tokens["bus_id"])
            return

        generator = Generator(bus)

        # Set an unique name to ease identification.
        g_names = [g.name for g in self.case.generators]

        generator.name = make_unique_name("Generator", g_names)
        generator.p = tokens["Pg"]
        generator.q_max = tokens["Qmax"]
        generator.q_min = tokens["Qmin"]
        generator.v_magnitude = tokens["Vg"]
        generator.base_mva = tokens["mBase"]
        generator.online = tokens["status"]
        generator.p_max = tokens["Pmax"]
        generator.p_min = tokens["Pmin"]

        self.case.generators.append(generator)


    def _push_branch(self, tokens):
        """ Adds a branch to the case.
        """
        logger.debug("Parsing branch data: %s" % tokens)

        buses = self.case.buses

        bus_ids = [bus._bus_id for bus in buses]

        from_bus_idx = bus_ids.index(tokens["fbus"])
        to_bus_idx = bus_ids.index(tokens["tbus"])
        from_bus = buses[from_bus_idx]
        to_bus = buses[to_bus_idx]

#        from_bus = self.case.buses[tokens["fbus"]-1]
#        to_bus = self.case.buses[tokens["tbus"]-1]

        branch_names = [e.name for e in self.case.branches]
        e = Branch(from_bus=from_bus, to_bus=to_bus)

        e.name        = make_unique_name("e", branch_names)
        e.r           = tokens["r"]
        e.x           = tokens["x"]
        e.b           = tokens["b"]
        e.rate_a      = tokens["rateA"]
        e.rate_b      = tokens["rateB"]
        e.rate_c      = tokens["rateC"]
        e.ratio       = tokens["ratio"]
        e.phase_shift = tokens["angle"]
        e.online      = tokens["status"]

        if self.case_format == 2:
            e.ang_min = tokens["ang_min"]
            e.ang_max = tokens["ang_max"]

        self.case.branches.append(e)


    def _push_generator_cost(self, string, location, tokens):
        """ Adds cost data to generators.
        """
        logger.debug("Parsing generator cost data: %s" % tokens)

        # Assume gen cost data provided in order of generators.
        g = self.case.generators[self.costed]

        g.c_startup = tokens["startup"]
        g.c_shutdown = tokens["shutdown"]

        # Piecewise linear cost data
        if tokens["model"] == 1:
            coords = tokens[4:]

            # Check that there is an even number of coordinates
            if len(coords) % 2 != 0:
                logger.error("Uneven number of coordinates for pwl cost")

            # Check that there are twice as many coordinates as 'n'
            if len(coords) != 2 * tokens["n"]:
                logger.error("Number of cost values specified [%d] and no. " \
                    "given [%d] do not match." % (2*tokens["n"], len(coords)))

            points = []
            # Form a list of tuples.
            for i, coord in enumerate(coords):
                if i % 2 == 0:
                    x = float(coord)
                    y = float(coords[i + 1])
                    points.append((x, y))

            g.p_cost = points
            g.pcost_model = "pwl"

        # Polynomial cost data
        elif tokens["model"] == 2:
            coeffs = tokens[4:]

            if len(coeffs) != float(tokens["n"]):
                logger.error("Number of cost values specified [%d] and no. " \
                    "supplied [%d] do not match." % (tokens["n"], len(coeffs)))

            if len(coeffs) > 3:
                logger.warning("Only quadratic polynomial cost functions " \
                               "currently supported")
                coeffs = coeffs[:3]

            if len(coeffs) < 3:
                for i in 3 - len(coeffs):
                    coeffs.append(0.0)

            g.p_cost = tuple(coeffs)
            g.pcost_model = "poly"

        else:
            raise ValueError, "Invalid cost model number"

        # TODO: Parse possible reactive power cost data (rows ng+1)

        self.costed += 1

# EOF -------------------------------------------------------------------------
