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

""" Defines a class for reading MATPOWER data files.
"""

#------------------------------------------------------------------------------
#  Imports:
#------------------------------------------------------------------------------

import os.path
import logging

from parsing_util import \
    integer, boolean, real, scolon, matlab_comment, make_unique_name, \
    ToInteger, lbrack, rbrack

from pyparsing import \
    Literal, Word, ZeroOrMore, Optional, OneOrMore, alphanums, delimitedList, \
    alphas, Combine, printables

from pylon.case import Case, Bus, Branch, Generator, Load

#------------------------------------------------------------------------------
#  Logging:
#------------------------------------------------------------------------------

logger = logging.getLogger(__name__)
#logger.setLevel(logging.INFO)

#------------------------------------------------------------------------------
#  "MATPOWERReader" class:
#------------------------------------------------------------------------------

class MATPOWERReader(object):
    """ Defines a method class for reading MATPOWER data files and
        returning a Case object.
    """

    def __init__(self):
        """ Initialises a new PSSEReader instance.
        """
        # Path to the data file or file object.
        self.file_or_filename = None

        # The resulting case.
        self.case = None

        # The system MVA base to which machines default
        self.base_mva = 100.0

        # Index of the slack bus. Bus objects can not be made slack until
        # at least one generator is attached so the attribute is set at the end
        # of the parsing operation.
        self.slack_idx = -1

        # Maintain an ordered list of instantiated generators that may be
        # used in processing generator cost data since the structure gives
        # no reference to the generator to which the cost data applies.
        # These are added when the generator is instantiated and removed
        # when the cost data is processed. The presence of any left overs
        # is checked at the end of the parsing operation.
        self.generators = []


    def __call__(self, file_or_filename):
        """ Call the reader with something like reader(fd)
        """
        return self.read(file_or_filename)

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
        self.case = case = Case()
        self.slack_idx = -1
        self.generators = []

        # Form array constructs
        header = self._get_header_construct()
        base_mva = self._get_base_mva_construct()
        bus_array = self._get_bus_array_construct()
        gen_array = self._get_generator_array_construct()
        branch_array = self._get_branch_array_construct()
        area_array = self._get_area_array_construct()
        generator_cost_array = self._get_generator_cost_array_construct()

        # Assemble pyparsing case:
        parsing_case = header + \
            ZeroOrMore(matlab_comment) + base_mva + \
            ZeroOrMore(matlab_comment) + bus_array + \
            ZeroOrMore(matlab_comment) + gen_array + \
            ZeroOrMore(matlab_comment) + branch_array + \
            ZeroOrMore(matlab_comment) + Optional(area_array) + \
            ZeroOrMore(matlab_comment) + Optional(generator_cost_array)

        # Parse the data file
        data = parsing_case.parseFile(file_or_filename)

        # Set the slack bus.
        case.buses[self.slack_idx].slack = True

        # Reset the list of instantiated generators if necessary
        if len(self.generators):
            logger.warning("No cost data for %d generators" %
                len(self.generators))

        self.generators = []

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
        header = Literal("function") + \
            lbrack + delimitedList(Word(alphas)) + rbrack + \
            "=" + title

        return header


    def _get_base_mva_construct(self):
        """ Returns a construct for the base MVA expression.
        """
        base_mva = real.setResultsName("baseMVA")
        base_mva.setParseAction(self._push_base_mva)
        base_mva_expr = Literal("baseMVA") + Literal("=") + base_mva + scolon

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

        bus_array = Combine(Optional("mpc.") + Literal('bus')) + '=' + '[' + \
            ZeroOrMore(bus_data) + Optional(']' + scolon)

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
            min_active + scolon

        gen_data.setParseAction(self._push_generator)

        gen_array = Literal('gen') + '=' + '[' + \
            ZeroOrMore(gen_data) + Optional(']' + scolon)

        return gen_array


    def _get_branch_array_construct(self):
        """ Returns a construct for an array of branch data.
        """
        source_bus = integer.setResultsName("fbus")
        target_bus = integer.setResultsName("tbus")
        resistance = real.setResultsName("r")
        reactance = real.setResultsName("x")
        susceptance = real.setResultsName("b")
        long_mva = real.setResultsName("rateA")
        short_mva = real.setResultsName("rateB")
        emerg_mva = real.setResultsName("rateC")
        ratio = real.setResultsName("ratio")
        angle = real.setResultsName("angle")
        status = boolean.setResultsName("status")

        branch_data = source_bus + target_bus + resistance + reactance + \
            susceptance + long_mva + short_mva + emerg_mva + ratio + angle + \
            status + scolon

        branch_data.setParseAction(self._push_branch)

        branch_array = Literal('branch') + '=' + '[' + \
            ZeroOrMore(branch_data) + Optional(']' + scolon)

        return branch_array


    def _get_area_array_construct(self):
        """ Returns a construct for an array of area data.
        """
        area = integer.setResultsName("area_id")
        price_ref_bus = integer.setResultsName("price_ref_bus")

        area_data = area + price_ref_bus + scolon

        area_array = Literal('areas') + '=' + '[' + \
            ZeroOrMore(area_data) + Optional(']' + scolon)

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
        x0 = real.setResultsName("x0")
        y0 = real.setResultsName("y0")
        x1 = real.setResultsName("x1")
        y1 = real.setResultsName("y1")

        linear_cost_data = model + startup + shutdown + n + \
            OneOrMore(real) + scolon

        linear_cost_data.setParseAction(self._push_generator_cost)

#        piecewise_cost_data = model + startup + shutdown + n + OneOrMore(tuple)
#        piecewise_cost_data.setParseAction(self.push_piecewise_cost)

#        polynomial_cost_data = model + startup + shutdown + n + OneOrMore(real)
#        polynomial_cost_data.setParseAction(self.push_polynomial_cost)

        generator_cost_array = Literal('gencost') + '=' + '[' + \
            ZeroOrMore(linear_cost_data) + Optional(']' + scolon)

        return generator_cost_array

    #--------------------------------------------------------------------------
    #  Parse actions:
    #--------------------------------------------------------------------------

    def _push_title(self, tokens):
        """ Sets the case's name.
        """
        self.case.name = tokens["title"]


    def _push_base_mva(self, tokens):
        """ Set the MVA base for the case.
        """
        self.base_mva = base_mva = tokens["baseMVA"]
        self.case.base_mva = base_mva


    def _push_bus(self, tokens):
        """ Adds a bus to the case and a load (if any).
        """
        logger.debug("Parsing bus data: %s" % tokens)

        name = str(tokens["bus_id"])
        bus  = Bus(name=name)

        # Assign a private id attribute for use when pushing generators and
        # branches.
        bus._bus_id = tokens["bus_id"]

        base_kv = tokens["baseKV"]

        bus.v_base      = base_kv
        bus.g_shunt     = tokens["Gs"]
        bus.b_shunt     = tokens["Bs"]
        bus.v_magnitude_guess = tokens["Vm"]
        bus.v_angle_guess = tokens["Va"]
        bus.v_magnitude = tokens["Vm"]
        bus.v_angle     = tokens["Va"]

        # Bus type 3 denotes a slack bus in MATPOWER
        if tokens["bus_type"] == 3:
            self.slack_idx = tokens["bus_id"]-1

        # Loads are included in bus data with MATPOWER
        if (tokens["Pd"] > 0) or (tokens["Qd"] > 0):
            l   = Load()
            l.p = tokens["Pd"]
            l.q = tokens["Qd"]
            bus.loads.append(l)

        bus.zone = tokens["zone"]

        bus.v_max = tokens["Vmax"]
        bus.v_min = tokens["Vmin"]

        self.case.buses.append(bus)


    def _push_generator(self, tokens):
        """ Adds a generator to the respective bus.
        """
        logger.debug("Parsing generator data: %s" % tokens)

        base_mva = tokens["mBase"]
        # Default to system base
        if base_mva == 0.0:
            base_mva = self.base_mva

        # Locate the generator's bus.
        for i, bus in enumerate(self.case.buses):
            if bus._bus_id == tokens["bus_id"]:
                break
        else:
            logger.error("Bus [%d] not found." % tokens["bus_id"])
            return

        # Set unique name to ease identification.
        g_names = [g.name for g in self.generators]

        generator = Generator(name=make_unique_name("g", g_names))

        generator.p           = tokens["Pg"]
        generator.q_max       = tokens["Qmax"]
        generator.q_min       = tokens["Qmin"]
        generator.v_magnitude = tokens["Vg"]
        generator.base_mva    = tokens["mBase"]
        generator.online      = tokens["status"]
        generator.p_max       = tokens["Pmax"]
        generator.p_min       = tokens["Pmin"]

#        generator.p_max_bid   = tokens["Pmax"]
#        generator.p_min_bid   = tokens["Pmin"]

#        bus.generators.append(generator)
        self.case.buses[i].generators.append(generator)

        # Maintain the list of instantiated generators for
        # gen cost evaluation
        self.generators.append(generator)


    def _push_branch(self, tokens):
        """ Adds a branch to the case.
        """
        logger.debug("Parsing branch data: %s" % tokens)

        buses = self.case.buses

        bus_names      = [ v.name for v in buses ]
        source_bus_idx = bus_names.index( str( tokens["fbus"] ) )
        target_bus_idx = bus_names.index( str( tokens["tbus"] ) )
        source_bus     = buses[ source_bus_idx ]
        target_bus     = buses[ target_bus_idx ]

#        source_bus = self.case.buses[tokens["fbus"]-1]
#        target_bus = self.case.buses[tokens["tbus"]-1]

        branch_names = [e.name for e in self.case.branches]
        e = Branch(source_bus=source_bus, target_bus=target_bus)

        e.name        = make_unique_name("e", branch_names)
        e.r           = tokens["r"]
        e.x           = tokens["x"]
        e.b           = tokens["b"]
        e.s_max       = tokens["rateA"]
        e.ratio       = tokens["ratio"]
        e.phase_shift = tokens["angle"]
        e.online      = tokens["status"]

        self.case.branches.append(e)


    def _push_generator_cost(self, string, location, tokens):
        """ Adds cost data to generators.
        """
        logger.debug("Parsing generator cost data: %s" % tokens)

        # There should be one or more generators in our list
        if not len(self.generators):
            logger.error("More cost data than there are generators")
            return

        # Apply cost data to first generator in list and then remove it
        g = self.generators[0]

        g.c_startup = float( tokens["startup"] )
        g.c_shutdown = float( tokens["shutdown"] )

        # Piecewise linear cost data
        if tokens["model"] == 1:
            coords = tokens[4:]
#            print "Piecewise linear coordinates:", coords

            # Check that there is an even number of coordinates
            if len(coords) % 2 != 0:
                print "Uneven number of coordinates for pw linear cost"

            # Check that there are twice as many coordinates as 'n'
            if len(coords) != 2 * float( tokens["n"] ):
                print "No. coords specified and no. supplied do not match"

            points = []
            # Form as list of tuples
            for i, coord in enumerate( coords ):
                if i % 2 == 0:
                    # FIXME: This should really use the machine MVA base
                    x = float( coord )
                    y = float( coords[i+1] )
                    points.append( (x, y) )
#            print "Points:", points

            g.pwl_points = points
            g.cost_model = "pwl"

        # Polynomial cost data
        elif tokens["model"] == 2:
            coeffs = [ float(c) for c in tokens[4:] ]
#            print "Coefficients:", coeffs

            n_coeffs = len(coeffs)

            # Check the number of coefficients supplied
            if n_coeffs != float(tokens["n"]):
                print "No. of coeffs specified and no. supplied do not match"

            if n_coeffs > 3:
                print "Only quadratic polynomial cost curves supported"
                coeffs = coeffs[:3]

            if n_coeffs < 3:
                for i in 3-n_coeffs:
                    coeffs.append(0)

            g.cost_coeffs = tuple(coeffs)
            g.cost_model  = "poly"

        else:
            raise ValueError, "Invalid cost model number"

        # TODO: Parse possible reactive power cost data (rows ng+1)

        # Remove the processed generator
        self.generators.pop(0)

# EOF -------------------------------------------------------------------------
