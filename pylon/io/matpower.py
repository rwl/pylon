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

""" Defines a class for reading MATPOWER data files.
"""

#------------------------------------------------------------------------------
#  Imports:
#------------------------------------------------------------------------------

import time
import logging
from os.path import basename, splitext

#from parsing_util import \
#    integer, boolean, real, scolon, matlab_comment, make_unique_name, \
#    ToInteger, lbrack, rbrack, equals

#from pyparsing import \
#    Literal, Word, ZeroOrMore, Optional, OneOrMore, delimitedList, \
#    alphas, Combine, printables, quotedString

from pylon.case import Case, Bus, Branch, PQ, PV, REFERENCE, ISOLATED
from pylon.generator import Generator, PW_LINEAR, POLYNOMIAL
from pylon.io.common import _CaseReader, _CaseWriter

#------------------------------------------------------------------------------
#  Logging:
#------------------------------------------------------------------------------

logger = logging.getLogger(__name__)

#------------------------------------------------------------------------------
#  "MATPOWERReader" class:
#------------------------------------------------------------------------------

class MATPOWERReader(_CaseReader):
    """ Defines a reader for MATPOWER case files.
    """

    def __init__(self, version=2):
        # MATPOWER case format version.
        self.version = version

        # Map of bus indcies to Bus objects.
        self._bus_map = {}

        # Does the case define a MATLAB struct.
        self._is_struct = True


    def read(self, file_or_filename):
        """ Returns a Case given a MATPOWER file or file name.
        """
        t0 = time.time()
        self._bus_map = {}
        if isinstance(file_or_filename, basestring):
            fname = basename(file_or_filename)
            logger.info("Loading MATPOWER file [%s]." % fname)

            file = None
            try:
                file = open(file_or_filename, "rb")
            except:
                logger.error("Error opening: %s" % fname)
                return None
            finally:
                if file is not None:
                    case = self._parse_file(file)
                    file.close()
        else:
            file = file_or_filename
            case = self._parse_file(file)

        case.index_buses()

        logger.info("MATPOWER file parsed in %.2fs." % (time.time() - t0))

        return case


    def _parse_file(self, file):
        """ Parses the given file-like object.
        """
        case = Case()
        file.seek(0)

        line = file.readline().split()
        if line[0] != "function":
            logger.error("Invalid data file header.")
            return case
        if line[1] != "mpc":
            self._is_struct = False
            base = ""
        else:
            base = "mpc."
        case.name = line[-1]

        for line in file:
            if line.startswith("%sbaseMVA" % base):
                case_data = line.rstrip(";\n").split()
                case.base_mva = float(case_data[-1])
            elif line.startswith("%sbus" % base):
                self._parse_buses(case, file)
            elif line.startswith("%sgencost" % base):
                self._parse_gencost(case, file)
            elif line.startswith("%sgen" % base):
                self._parse_generators(case, file)
            elif line.startswith("%sbranch" % base):
                self._parse_branches(case, file)

        return case


    def _parse_buses(self, case, file):
        bustype_map = {1: "PQ", 2: "PV", 3: "ref", 4: "isolated"}

        for line in file:
            if line.startswith("]"):
                break
            bus_data = line.rstrip(";\n").split()
            bus = Bus()
            i = int(bus_data[0])
            self._bus_map[i] = bus
            bus._i = i

            bus.type = bustype_map[int(bus_data[1])]
            bus.p_demand = float(bus_data[2])
            bus.q_demand = float(bus_data[3])
            bus.g_shunt = float(bus_data[4])
            bus.b_shunt = float(bus_data[5])
            bus.area = int(bus_data[6])
            bus.v_magnitude = float(bus_data[7])
            bus.v_angle = float(bus_data[8])
            bus.v_base = float(bus_data[9])
            bus.zone = int(bus_data[10])
            bus.v_max = float(bus_data[11])
            bus.v_min = float(bus_data[12])

            case.buses.append(bus)
        return


    def _parse_generators(self, case, file):

        for line in file:
            if line.startswith("]"):
                break
            gen_data = line.strip(";\n").split()
            bus = self._bus_map[int(gen_data[0])]
            g = Generator(bus)

            g.p = float(gen_data[1])
            g.q = float(gen_data[2])
            g.q_max = float(gen_data[3])
            g.q_min = float(gen_data[4])
            g.v_magnitude = float(gen_data[5])
            g.base_mva = float(gen_data[6])
            g.online = bool(gen_data[7])
            g.p_max = float(gen_data[8])
            g.p_min = float(gen_data[9])

            case.generators.append(g)
        return


    def _parse_branches(self, case, file):
        for line in file:
            if line.startswith("]"):
                break
            branch_data = line.strip(";\n").split()
            from_bus = self._bus_map[int(branch_data[0])]
            to_bus = self._bus_map[int(branch_data[1])]
            l = Branch(from_bus, to_bus)

            l.r = float(branch_data[2])
            l.x = float(branch_data[3])
            l.b = float(branch_data[4])
            l.rate_a = float(branch_data[5])
            l.rate_b = float(branch_data[6])
            l.rate_c = float(branch_data[7])
            l.ratio = float(branch_data[8])
            l.phase_shift = float(branch_data[9])
            l.online = bool(branch_data[10])

            case.branches.append(l)
        return


    def _parse_gencost(self, case, file):
#        line = file.readline()
#        for g in case.generators:

        for i, line in enumerate(file):
            if line.startswith("]"):
#                logger.warning("Missing cost data [%d]." % i)
                break

            g = case.generators[i]

            model, c_startup, c_shutdown, cost = self._parse_gencost_line(line)

            g.pcost_model = model
            g.c_startup = c_startup
            g.c_shutdown = c_shutdown
            g.p_cost = cost

#            line = file.readline()

        if line.startswith("]"):
            logger.info("No reactive power cost data.")
            return

#        for g in case.generators:

        for i, line in enumerate(file):
            g = case.generators[i]

            if line.startswith("]"):
                logger.warning("No Q cost data for %s" % g.name)
                continue

            model, _, _, cost = self._parse_gencost_line(line)

            g.qcost_model = model
            g.q_cost = cost

#            line = file.readline()

        for line in file:
            if not line.startswith("]"):
                logger.info("Superfluous Q cost data [%s]." % line)
            else:
                return


    def _parse_gencost_line(self, line):
        gencost_map = {1: PW_LINEAR, 2: POLYNOMIAL}

        gencost_data = line.replace(";", "").strip("\n").split()

        model = gencost_map[int(gencost_data[0])]
        c_startup = float(gencost_data[1])
        c_shutdown = float(gencost_data[2])
        n = int(gencost_data[3])
        if model == PW_LINEAR:
            d = gencost_data[4:4 + (2 * n)]
            cost = []
            for j in range(n):
                cost.append((float(d[2 * j]), float(d[2 * j + 1])))
        else:
            d = gencost_data[4:4 + n]
            cost = tuple([float(a) for a in d])

        return model, c_startup, c_shutdown, cost

#------------------------------------------------------------------------------
#  "MATPOWERReader" class:
#------------------------------------------------------------------------------

#class MATPOWERReader(_CaseReader):
#    """ Defines a method class for reading MATPOWER data files and
#        returning a Case object.
#    """
#
#    def __init__(self, case_format=2):
#        """ Initialises a new MATPOWERReader instance.
#        """
#        #: MATPOWER case format.  Version 2 introduced in MATPOWER 4.0b1.
#        self.case_format = case_format
#
#        #: Path to the data file or file object.
#        self.file_or_filename = None
#
#        #: The resulting case.
#        self.case = None
#
#        #: Count of generators to which cost data has been applied.
#        self.costed = 0
#
#    #--------------------------------------------------------------------------
#    #  Parse a MATPOWER data file and return a case object
#    #--------------------------------------------------------------------------
#
#    def read(self, file_or_filename):
#        """ Parse a MATPOWER data file and return a case object
#
#            file_or_filename: File name of file object with MATPOWER data
#            return: Case object
#        """
#        self.file_or_filename = file_or_filename
#
#        if isinstance(file_or_filename, basestring):
#            fname = basename(file_or_filename)
#            logger.info("Parsing MATPOWER case file [%s]." % fname)
#        else:
#            logger.info("Parsing MATPOWER case file.")
#
#        # Initialise:
#        case = self.case = Case()
#        self.costed = 0
#
#        # Form array constructs
#        header = self._get_header_construct()
#        version = self._get_case_format_construct()
#        base_mva = self._get_base_mva_construct()
#        bus_array = self._get_bus_array_construct()
#        gen_array = self._get_generator_array_construct()
#        branch_array = self._get_branch_array_construct()
#        area_array = self._get_area_array_construct()
#        generator_cost_array = self._get_generator_cost_array_construct()
#
#        # Assemble pyparsing case:
#        parsing_case = header + \
#            ZeroOrMore(matlab_comment) + version + \
#            ZeroOrMore(matlab_comment) + base_mva + \
#            ZeroOrMore(matlab_comment) + bus_array + \
#            ZeroOrMore(matlab_comment) + gen_array + \
#            ZeroOrMore(matlab_comment) + branch_array + \
#            ZeroOrMore(matlab_comment) + Optional(area_array) + \
#            ZeroOrMore(matlab_comment) + Optional(generator_cost_array)
#
#        # Parse the data file
#        parsing_case.parseFile(file_or_filename)
#
#        # Update internal indices.
#        case.index_buses()
#        case.index_branches()
#
#        return case
#
#    #--------------------------------------------------------------------------
#    #  Construct getters:
#    #--------------------------------------------------------------------------
#
#    def _get_header_construct(self):
#        """ Returns a construct for the header of a MATPOWER data file.
#        """
#        # Use the function name for the Case title
#        title = Word(printables).setResultsName("title")
#        title.setParseAction(self._push_title)
#        if self.case_format == 1:
#            header = Literal("function") + \
#                lbrack + delimitedList(Word(alphas)) + rbrack + \
#                "=" + title
#        elif self.case_format == 2:
#            header = Literal("function") + Literal("mpc") + equals + title
#
#        return header
#
#
#    def _get_case_format_construct(self):
#        """ Returns a construct for the case formet expression introduced in
#            MATPOWER 4.0.
#        """
#        if self.case_format == 1:
#            version_expr = Optional(matlab_comment)
#        else:
#            version = quotedString.setResultsName("version")
#            version_expr = Literal("mpc.version") + equals + version + scolon
#
#        return version_expr
#
#
#    def _get_base_mva_construct(self):
#        """ Returns a construct for the base MVA expression.
#        """
#        base_mva = real.setResultsName("baseMVA")
#        base_mva.setParseAction(self._push_base_mva)
#        base_mva_expr = Combine(Optional("mpc.") + Literal("baseMVA")) + \
#            Literal("=") + base_mva + scolon
#
#        return base_mva_expr
#
#
#    def _get_bus_array_construct(self):
#        """ Returns a construct for an array of bus data.
#        """
#        bus_id = integer.setResultsName("bus_id")
#        bus_type = ToInteger(Word('123', exact=1)).setResultsName("bus_type")
#        appr_demand = real.setResultsName("Pd") + real.setResultsName("Qd")
#        shunt_addm = real.setResultsName("Gs") + real.setResultsName("Bs")
#        area = integer.setResultsName("area")
#        Vm = real.setResultsName("Vm")
#        Va = real.setResultsName("Va")
#        kV_base = real.setResultsName("baseKV")
#        zone = integer.setResultsName("zone")
#        Vmax = real.setResultsName("Vmax")
#        Vmin = real.setResultsName("Vmin")
#
#        bus_data = bus_id + bus_type + appr_demand + shunt_addm + \
#            area + Vm + Va + kV_base + zone + Vmax + Vmin + scolon
#
#        bus_data.setParseAction(self._push_bus)
#
#        bus_array = Combine(Optional("mpc.") + Literal('bus')) + equals + \
#            lbrack + ZeroOrMore(bus_data) + Optional(rbrack + scolon)
#
#        return bus_array
#
#
#    def _get_generator_array_construct(self):
#        """ Returns an construct for an array of generator data.
#        """
#        bus_id = integer.setResultsName("bus_id")
#        active = real.setResultsName("Pg")
#        reactive = real.setResultsName("Qg")
#        max_reactive = real.setResultsName("Qmax")
#        min_reactive = real.setResultsName("Qmin")
#        voltage = real.setResultsName("Vg")
#        base_mva = real.setResultsName("mBase")
#        status = boolean.setResultsName("status")
#        max_active = real.setResultsName("Pmax")
#        min_active = real.setResultsName("Pmin")
#
#        gen_data = bus_id + active + reactive + max_reactive + \
#            min_reactive + voltage + base_mva + status + max_active + \
#            min_active + ZeroOrMore(real) + scolon
#
#        gen_data.setParseAction(self._push_generator)
#
#        gen_array = Combine(Optional("mpc.") + Literal('gen')) + equals + \
#            lbrack + ZeroOrMore(gen_data) + Optional(rbrack + scolon)
#
#        return gen_array
#
#
#    def _get_branch_array_construct(self):
#        """ Returns a construct for an array of branch data.
#        """
#        from_bus = integer.setResultsName("fbus")
#        to_bus = integer.setResultsName("tbus")
#        resistance = real.setResultsName("r")
#        reactance = real.setResultsName("x")
#        susceptance = real.setResultsName("b")
#        long_mva = real.setResultsName("rateA")
#        short_mva = real.setResultsName("rateB")
#        emerg_mva = real.setResultsName("rateC")
#        ratio = real.setResultsName("ratio")
#        angle = real.setResultsName("angle")
#        status = boolean.setResultsName("status")
#        ang_min = real.setResultsName("ang_min")
#        ang_max = real.setResultsName("ang_max")
#
#        branch_data = from_bus + to_bus + resistance + reactance + \
#            susceptance + long_mva + short_mva + emerg_mva + ratio + angle + \
#            status + Optional(ang_min + ang_max) + scolon
#
#        branch_data.setParseAction(self._push_branch)
#
#        branch_array = Combine(Optional("mpc.") + Literal('branch')) + \
#            equals + lbrack + ZeroOrMore(branch_data) + \
#            Optional(rbrack + scolon)
#
#        return branch_array
#
#
#    def _get_area_array_construct(self):
#        """ Returns a construct for an array of area data.
#        """
#        area = integer.setResultsName("area_id")
#        price_ref_bus = integer.setResultsName("price_ref_bus")
#
#        area_data = area + price_ref_bus + scolon
#
#        if self.case_format == 1:
#            area_array = Literal('areas') + equals + lbrack + \
#                ZeroOrMore(area_data) + Optional(rbrack + scolon)
#        elif self.case_format == 2:
#            area_array = Optional(Combine(Literal('mpc.areas')) + \
#                equals + lbrack + \
#                ZeroOrMore(area_data) + Optional(rbrack + scolon))
#
#        return area_array
#
#
#    def _get_generator_cost_array_construct(self):
#        """ Returns a construct for an array of generator cost data.
#        """
#        # [model, startup, shutdown, n, x0, y0, x1, y1]
#        # 1 - piecewise linear, 2 - polynomial
#        model = integer.setResultsName("model")
#        # start up cost
#        startup = real.setResultsName("startup")
#        # shut down cost
#        shutdown = real.setResultsName("shutdown")
#        # number of cost coefficients to follow for polynomial
#        # cost function, or number of data points for pw linear
#        n  = integer.setResultsName("n")
##        x0 = real.setResultsName("x0")
##        y0 = real.setResultsName("y0")
##        x1 = real.setResultsName("x1")
##        y1 = real.setResultsName("y1")
#
#        linear_cost_data = model + startup + shutdown + n + \
#            OneOrMore(real) + scolon
#
#        linear_cost_data.setParseAction(self._push_generator_cost)
#
##        piecewise_cost_data = model + startup + shutdown + n + OneOrMore(tuple)
##        piecewise_cost_data.setParseAction(self.push_piecewise_cost)
#
##        polynomial_cost_data = model + startup + shutdown + n + OneOrMore(real)
##        polynomial_cost_data.setParseAction(self.push_polynomial_cost)
#
#        gen_cost_array = Combine(Optional("mpc.") + Literal('gencost')) + \
#            equals + lbrack + ZeroOrMore(linear_cost_data) + \
#            Optional(rbrack + scolon)
#
#        return gen_cost_array
#
#    #--------------------------------------------------------------------------
#    #  Parse actions:
#    #--------------------------------------------------------------------------
#
#    def _push_title(self, tokens):
#        """ Sets the case's name.
#        """
#        logger.debug("Parsing system name: %s" % tokens["title"])
#
#        self.case.name = tokens["title"]
#
#
#    def _push_base_mva(self, tokens):
#        """ Set the MVA base for the case.
#        """
#        logger.debug("Parsing system base: %.1f" % tokens["baseMVA"])
#
#        self.case.base_mva = tokens["baseMVA"]
#
#
#    def _push_bus(self, tokens):
#        """ Adds a bus to the case.
#        """
#        logger.debug("Parsing bus data: %s" % tokens)
#
#        name = "Bus-" + str(tokens["bus_id"])
#        bus = Bus(name=name)
#
#        # Assign a private id attribute for use when pushing generators
#        # and branches.
#        bus._bus_id = tokens["bus_id"]
#
#        base_kv = tokens["baseKV"]
#
#        bus.v_base = base_kv
#        bus.g_shunt = tokens["Gs"]
#        bus.b_shunt = tokens["Bs"]
#        bus.v_magnitude = tokens["Vm"]
#        bus.v_angle = tokens["Va"]
#        bus.v_magnitude = tokens["Vm"]
#        bus.v_angle = tokens["Va"]
#
#        # Bus type 3 denotes a slack bus in MATPOWER
#        bustype_map = {1: "PQ", 2: "PV", 3: "ref", 4: "isolated"}
#        bus.type = bustype_map[tokens["bus_type"]]
#
#        bus.p_demand = tokens["Pd"]
#        bus.q_demand = tokens["Qd"]
#
#        bus.area = tokens["area"]
#        bus.zone = tokens["zone"]
#
#        bus.v_max = tokens["Vmax"]
#        bus.v_min = tokens["Vmin"]
#
#        self.case.buses.append(bus)
#
#
#    def _push_generator(self, tokens):
#        """ Adds a generator to the respective bus.
#        """
#        logger.debug("Parsing generator data: %s" % tokens)
#
##        base_mva = tokens["mBase"]
##        if base_mva == 0.0:
##            base_mva = self.base_mva # Default to system base.
#
#        # Locate the generator bus.
#        for bus in self.case.buses:
#            if bus._bus_id == tokens["bus_id"]:
#                break
#        else:
#            logger.error("Bus [%d] not found." % tokens["bus_id"])
#            return
#
#        generator = Generator(bus)
#
#        # Set an unique name to ease identification.
#        g_names = [g.name for g in self.case.generators]
#
#        generator.name = make_unique_name("Generator", g_names)
#        generator.p = tokens["Pg"]
#        generator.q_max = tokens["Qmax"]
#        generator.q_min = tokens["Qmin"]
#        generator.v_magnitude = tokens["Vg"]
#        generator.base_mva = tokens["mBase"]
#        generator.online = tokens["status"]
#        generator.p_max = tokens["Pmax"]
#        generator.p_min = tokens["Pmin"]
#
#        self.case.generators.append(generator)
#
#
#    def _push_branch(self, tokens):
#        """ Adds a branch to the case.
#        """
#        logger.debug("Parsing branch data: %s" % tokens)
#
#        buses = self.case.buses
#
#        bus_ids = [bus._bus_id for bus in buses]
#
#        from_bus_idx = bus_ids.index(tokens["fbus"])
#        to_bus_idx = bus_ids.index(tokens["tbus"])
#        from_bus = buses[from_bus_idx]
#        to_bus = buses[to_bus_idx]
#
##        from_bus = self.case.buses[tokens["fbus"]-1]
##        to_bus = self.case.buses[tokens["tbus"]-1]
#
#        branch_names = [e.name for e in self.case.branches]
#        e = Branch(from_bus=from_bus, to_bus=to_bus)
#
#        e.name        = make_unique_name("e", branch_names)
#        e.r           = tokens["r"]
#        e.x           = tokens["x"]
#        e.b           = tokens["b"]
#        e.rate_a      = tokens["rateA"]
#        e.rate_b      = tokens["rateB"]
#        e.rate_c      = tokens["rateC"]
#        e.ratio       = tokens["ratio"]
#        e.phase_shift = tokens["angle"]
#        e.online      = tokens["status"]
#
#        if self.case_format == 2:
#            e.ang_min = tokens["ang_min"]
#            e.ang_max = tokens["ang_max"]
#
#        self.case.branches.append(e)
#
#
#    def _push_generator_cost(self, string, location, tokens):
#        """ Adds cost data to generators.
#        """
#        logger.debug("Parsing generator cost data: %s" % tokens)
#
#        # Assume gen cost data provided in order of generators.
#        g = self.case.generators[self.costed]
#
#        g.c_startup = tokens["startup"]
#        g.c_shutdown = tokens["shutdown"]
#
#        # Piecewise linear cost data
#        if tokens["model"] == 1:
#            coords = tokens[4:]
#
#            # Check that there is an even number of coordinates
#            if len(coords) % 2 != 0:
#                logger.error("Uneven number of coordinates for pwl cost")
#
#            # Check that there are twice as many coordinates as 'n'
#            if len(coords) != 2 * tokens["n"]:
#                logger.error("Number of cost values specified [%d] and no. " \
#                    "given [%d] do not match." % (2*tokens["n"], len(coords)))
#
#            points = []
#            # Form a list of tuples.
#            for i, coord in enumerate(coords):
#                if i % 2 == 0:
#                    x = float(coord)
#                    y = float(coords[i + 1])
#                    points.append((x, y))
#
#            g.p_cost = points
#            g.pcost_model = "pwl"
#
#        # Polynomial cost data
#        elif tokens["model"] == 2:
#            coeffs = tokens[4:]
#
#            if len(coeffs) != float(tokens["n"]):
#                logger.error("Number of cost values specified [%d] and no. " \
#                    "supplied [%d] do not match." % (tokens["n"], len(coeffs)))
#
#            if len(coeffs) > 3:
#                logger.warning("Only quadratic polynomial cost functions " \
#                               "currently supported")
#                coeffs = coeffs[:3]
#
#            if len(coeffs) < 3:
#                for i in 3 - len(coeffs):
#                    coeffs.append(0.0)
#
#            g.p_cost = tuple(coeffs)
#            g.pcost_model = "poly"
#
#        else:
#            raise ValueError, "Invalid cost model number"
#
#        # TODO: Parse possible reactive power cost data (rows ng+1)
#
#        self.costed += 1

#------------------------------------------------------------------------------
#  "MATPOWERWriter" class:
#------------------------------------------------------------------------------

class MATPOWERWriter(_CaseWriter):
    """ Write case data to a file in MATPOWER format.

    Based on savecase.m from MATPOWER by Ray Zimmerman, developed at PSERC
    Cornell. See U{http://www.pserc.cornell.edu/matpower/} for more info.
    """

    #--------------------------------------------------------------------------
    #  "object" interface:
    #--------------------------------------------------------------------------

    def __init__(self, case):
        """ Initialises a new MATPOWERWriter instance.
        """
        super(MATPOWERWriter, self).__init__(case)

        #: Function name must match the file name in MATLAB.
        self._fcn_name = case.name

        self._prefix = "mpc."

    #--------------------------------------------------------------------------
    #  "_CaseWriter" interface:
    #--------------------------------------------------------------------------

    def write(self, file_or_filename):
        """ Writes case data to file in MATPOWER format.
        """
        if isinstance(file_or_filename, basestring):
            self._fcn_name, _ = splitext(basename(file_or_filename))
        else:
            self._fcn_name = self.case.name

        self._fcn_name = self._fcn_name.replace(",", "").replace(" ", "_")

        super(MATPOWERWriter, self).write(file_or_filename)


#    def _write_data(self, file):
#        super(MATPOWERWriter, self)._write_data(file)
#        self.write_area_data(file)
#        file.write("return;\n")


    def write_case_data(self, file):
        """ Writes the case data in MATPOWER format.
        """
        file.write("function mpc = %s\n" % self._fcn_name)
        file.write('\n%%%% MATPOWER Case Format : Version %d\n' % 2)
        file.write("mpc.version = '%d';\n" % 2)

        file.write("\n%%%%-----  Power Flow Data  -----%%%%\n")
        file.write("%%%% system MVA base\n")
        file.write("%sbaseMVA = %g;\n" % (self._prefix, self.case.base_mva))


    def write_bus_data(self, file):
        """ Writes bus data in MATPOWER format.
        """
#        labels = ["bus_id", "type", "Pd", "Qd", "Gs", "Bs", "area", "Vm", "Va",
#            "baseKV", "Vmax", "Vmin"]

        bus_attrs = ["_i", "type", "p_demand", "q_demand", "g_shunt","b_shunt",
            "area", "v_magnitude", "v_angle", "v_base", "zone",
            "v_max", "v_min", "p_lmbda", "q_lmbda", "mu_vmin", "mu_vmax"]

        file.write("\n%%%% bus data\n")
        file.write("%%\tbus_i\ttype\tPd\tQd\tGs\tBs\tarea\tVm\tVa\tbaseKV"
                   "\tzone\tVmax\tVmin\tlam_P\tlam_Q\tmu_Vmax\tmu_Vmin")
        file.write("\n%sbus = [\n" % self._prefix)


        for bus in self.case.buses:
            vals = [getattr(bus, a) for a in bus_attrs]
            d = {PQ: 1, PV: 2, REFERENCE: 3, ISOLATED: 4}
            vals[1] = d[vals[1]]

            assert len(vals) == 17

            file.write("\t%d\t%d\t%g\t%g\t%g\t%g\t%d\t%.8g\t%.8g\t%g\t%d\t%g"
                       "\t%g\t%.4f\t%.4f\t%.4f\t%.4f;\n" % tuple(vals[:]))
        file.write("];\n")



    def write_generator_data(self, file):
        """ Writes generator data in MATPOWER format.
        """
        gen_attr = ["p", "q", "q_max", "q_min", "v_magnitude",
            "base_mva", "online", "p_max", "p_min", "mu_pmax", "mu_pmin",
            "mu_qmax", "mu_qmin"]

        file.write("\n%%%% generator data\n")
        file.write("%%\tbus\tPg\tQg\tQmax\tQmin\tVg\tmBase\tstatus\tPmax\tPmin")
        file.write("\tmu_Pmax\tmu_Pmin\tmu_Qmax\tmu_Qmin")
        file.write("\n%sgen = [\n" % self._prefix)

        for generator in self.case.generators:
            vals = [getattr(generator, a) for a in gen_attr]
            vals.insert(0, generator.bus._i)
            assert len(vals) == 14
            file.write("\t%d\t%g\t%g\t%g\t%g\t%.8g\t%g\t%d\t%g\t%g\t%g\t%g"
                       "\t%g\t%g;\n" % tuple(vals))
        file.write("];\n")


    def write_branch_data(self, file):
        """ Writes branch data to file.
        """
        branch_attr = ["r", "x", "b", "rate_a", "rate_b", "rate_c",
            "ratio", "phase_shift", "online", "ang_min", "ang_max", "p_from",
            "q_from", "p_to", "q_to", "mu_s_from", "mu_s_to", "mu_angmin",
            "mu_angmax"]

        file.write("\n%%%% branch data\n")
        file.write("%%\tfbus\ttbus\tr\tx\tb\trateA\trateB\trateC\tratio"
                   "\tangle\tstatus")
        file.write("\tangmin\tangmax")
        file.write("\tPf\tQf\tPt\tQt")
        file.write("\tmu_Sf\tmu_St")
        file.write("\tmu_angmin\tmu_angmax")
        file.write("\n%sbranch = [\n" % self._prefix)

        for branch in self.case.branches:
            vals = [getattr(branch, a) for a in branch_attr]

            vals.insert(0, branch.to_bus._i)
            vals.insert(0, branch.from_bus._i)

            file.write("\t%d\t%d\t%g\t%g\t%g\t%g\t%g\t%g\t%g\t%g\t%d\t%g\t%g"
                       "\t%.4f\t%.4f\t%.4f\t%.4f\t%.4f\t%.4f\t%.4f\t%.4f;\n" %
                       tuple(vals))
        file.write("];\n")


    def write_generator_cost_data(self, file):
        """ Writes generator cost data to file.
        """
        file.write("\n%%%% generator cost data\n")
        file.write("%%\t1\tstartup\tshutdown\tn\tx1\ty1\t...\txn\tyn\n")
        file.write("%%\t2\tstartup\tshutdown\tn\tc(n-1)\t...\tc0\n")
        file.write("%sgencost = [\n" % self._prefix)

        for generator in self.case.generators:
            n = len(generator.p_cost)
            template = '\t%d\t%g\t%g\t%d'
            for _ in range(n):
                template = '%s\t%%g' % template
            template = '%s;\n' % template

            if generator.pcost_model == PW_LINEAR:
                t = 2
#                cp = [p for p, q in generator.p_cost]
#                cq = [q for p, q in generator.p_cost]
#                c = zip(cp, cq)
                c = [v for pc in generator.p_cost for v in pc]
            elif generator.pcost_model == POLYNOMIAL:
                t = 1
                c = list(generator.p_cost)
            else:
                raise

            vals = [t, generator.c_startup, generator.c_shutdown, n] + c

            file.write(template % tuple(vals))
        file.write("];\n")


#        file.write("%% generator cost data" + "\n")
#        file.write("%\n")
#        file.write("% Piecewise linear:" + "\n")
#        file.write("%\t1\tstartup\tshutdwn\tn_point\tx1\ty1\t...\txn\tyn\n")
#        file.write("%\n")
#        file.write("% Polynomial:" + "\n")
#        file.write("%\t2\tstartup\tshutdwn\tn_coeff\tc(n-1)\t...\tc0\n")
#
#        file.write("gencost = [" + "\n")
#        file.write("];" + "\n")

    #--------------------------------------------------------------------------
    #  "MatpowerWriter" interface:
    #--------------------------------------------------------------------------

    def write_area_data(self, file):
        """ Writes area data to file.
        """
        file.write("%% area data" + "\n")
        file.write("%\tno.\tprice_ref_bus" + "\n")
        file.write("areas = [" + "\n")
        # TODO: Implement areas
        file.write("\t1\t1;" + "\n")

        file.write("];" + "\n")

# EOF -------------------------------------------------------------------------
