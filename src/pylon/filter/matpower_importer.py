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

""" Defines a class for importing MATPOWER data files """

#------------------------------------------------------------------------------
#  Imports:
#------------------------------------------------------------------------------

from parsing_util import \
    integer, boolean, real, scolon, matlab_comment, make_unique_name, ToInteger

from pyparsing import \
    Literal, Word, ZeroOrMore, Optional, OneOrMore, alphanums, delimitedList, \
    alphas

from pylon.network import Network
from pylon.bus import Bus
from pylon.branch import Branch
from pylon.generator import Generator
from pylon.load import Load

#from pylon.pypylon import Network, Bus, Branch, Generator, Load

#------------------------------------------------------------------------------
#  "MATPOWERImporter" class:
#------------------------------------------------------------------------------

class MATPOWERImporter:
    """ Defines a method class for importing MATPOWER data files and
    returning a Network object.

    """

    # The resulting network object
    network = Network

    # The system MVA base to which machines default
    base_mva = 100.0

    # Index of the slack bus. Bus objects can not be made slack until
    # at least one generator is attached.
    slack_idx = -1

    # Maintain an ordered list of instantiated generators that may be
    # used in processing generator cost data since the structure gives
    # no reference to the generator to which the cost data applies.
    # These are added when the generator is instantiated and removed
    # when the cost data is processed. The presence of any left overs
    # is checked at the end of the parsing operation.
    generators = []

    #--------------------------------------------------------------------------
    #  Parse a MATPOWER data file and return a network object
    #--------------------------------------------------------------------------

    def parse_file(self, file_or_filename):
        """ Parse a MATPOWER data file and return a network object

        file_or_filename: File name of file object with MATPOWER data
        return: Network object

        """

        # Initialise:
        self.network = Network()
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
        case = header + \
            ZeroOrMore(matlab_comment) + base_mva + \
            ZeroOrMore(matlab_comment) + bus_array + \
            ZeroOrMore(matlab_comment) + gen_array + \
            ZeroOrMore(matlab_comment) + branch_array + \
            ZeroOrMore(matlab_comment) + area_array + \
            ZeroOrMore(matlab_comment) + generator_cost_array

        # Parse the data file
        data = case.parseFile(file_or_filename)

        # Set the slack bus.
        # FIXME: This is a bit smelly
        self.network.buses[self.slack_idx].slack = True

        # Reset the list of instantiated generators if necessary
        if len(self.generators):
            print "No cost data for %d generators" % len(self.generators)
            self.generators = []

        return self.network

    #--------------------------------------------------------------------------
    #  Construct getters:
    #--------------------------------------------------------------------------

    def _get_header_construct(self):
        """ Returns a construct for the header of a MATPOWER data file """

        # Use the function name for the Network title
        title = Word(alphanums).setResultsName("title")
        title.setParseAction(self._push_title)
        header = Literal("function") + "[" + delimitedList(Word(alphas)) + \
            "]" + "=" + title

        return header


    def _get_base_mva_construct(self):
        """ Returns a construct for the base MVA expression """

        mva_base = integer.setResultsName("baseMVA")
        mva_base.setParseAction(self._push_mva_base)
        mva_base_expr = Literal("baseMVA") + Literal("=") + mva_base + scolon

        return mva_base_expr


    def _get_bus_array_construct(self):
        """ Returns a construct for an array of bus data """

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

        bus_array = Literal('bus') + '=' + '[' + \
            ZeroOrMore(bus_data + Optional(']' + scolon))

        return bus_array


    def _get_generator_array_construct(self):
        """ Returns an construct for an array of generator data """

        bus_id = integer.setResultsName("bus_id")
        active = real.setResultsName("Pg")
        reactive = real.setResultsName("Qg")
        max_reactive = real.setResultsName("Qmax")
        min_reactive = real.setResultsName("Qmin")
        voltage = real.setResultsName("Vg")
        mva_base = real.setResultsName("mBase")
        status = boolean.setResultsName("status")
        max_active = real.setResultsName("Pmax")
        min_active = real.setResultsName("Pmin")

        gen_data = bus_id + active + reactive + max_reactive + \
            min_reactive + voltage + mva_base + status + max_active + \
            min_active + scolon

        gen_data.setParseAction(self._push_generator)

        gen_array = Literal('gen') + '=' + '[' + \
            ZeroOrMore(gen_data + Optional(']' + scolon))

        return gen_array


    def _get_branch_array_construct(self):
        """ Returns a construct for an array of branch data """

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
            ZeroOrMore(branch_data + Optional(']' + scolon))

        return branch_array


    def _get_area_array_construct(self):
        """ Returns a construct for an array of area data """

        area = integer.setResultsName("area_id")
        price_ref_bus = integer.setResultsName("price_ref_bus")

        area_data = area + price_ref_bus + scolon

        area_array = Literal('areas') + '=' + '[' + \
            ZeroOrMore(area_data + Optional(']' + scolon))

        return area_array


    def _get_generator_cost_array_construct(self):
        """ Returns a construct for an array of generator cost data """

        # [model, startup, shutdown, n, x0, y0, x1, y1]
        # 1 - piecewise linear, 2 - polynomial
        model = integer.setResultsName("model")
        # start up cost
        startup = real.setResultsName("startup")
        # shut down cost
        shutdown = real.setResultsName("shutdown")
        # number of cost coefficients to follow for polynomial
        # cost function, or number of data points for pw linear
        n = integer.setResultsName("n")
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
            ZeroOrMore(linear_cost_data + Optional(']' + scolon))

        return generator_cost_array

    #--------------------------------------------------------------------------
    #  Parse actions:
    #--------------------------------------------------------------------------

    def _push_title(self, tokens):
        """ Sets the network's name """

        self.network.name = tokens["title"]


    def _push_mva_base(self, tokens):
        """ Set the MVA base for the network """

        self.base_mva = base_mva = tokens["baseMVA"]
        self.network.mva_base = base_mva


    def _push_bus(self, tokens):
        """ Adds a bus to the network and a load (if any) """

        bus = Bus(name=make_unique_name("v", self.network.bus_names))

        base_kv = tokens["baseKV"]
        bus.v_base = base_kv

        bus.g_shunt=tokens["Gs"]/self.base_mva
        bus.b_shunt=tokens["Bs"]/self.base_mva
        bus.v_amplitude_guess=tokens["Vm"]
        bus.v_phase_guess=tokens["Va"]

        # Bus type 3 denotes a slack bus in MATPOWER
        if tokens["bus_type"] == 3:
            self.slack_idx = tokens["bus_id"]-1

        self.network.buses.append(bus)

        # Loads are included in bus data with MATPOWER
        if tokens["Pd"] > 0 or tokens["Qd"] > 0:
            l = Load()
            l.p = tokens["Pd"]/self.base_mva
            l.q = tokens["Qd"]/self.base_mva
            bus.loads.append(l)

        bus.zone = tokens["zone"]

        bus.v_max = tokens["Vmax"]
        bus.v_min = tokens["Vmin"]


    def _push_generator(self, tokens):
        """ Adds a generator to the respective bus """

        base_mva = tokens["mBase"]
        # Default to system base
        if base_mva == 0.0:
            base_mva = self.base_mva

        # Locate the associated bus in the network
        bus = self.network.buses[tokens["bus_id"]-1]

        g = Generator()

        g.p = tokens["Pg"]/base_mva
        g.q_max = tokens["Qmax"]/base_mva
        g.q_min = tokens["Qmin"]/base_mva
        g.v_amplitude = tokens["Vg"]
        g.base_mva = tokens["mBase"]
        g.in_service = tokens["status"]
        g.p_max = tokens["Pmax"]/base_mva
        g.p_min = tokens["Pmin"]/base_mva

        bus.generators.append(g)

        # Maintain the list of instantiated generators for
        # gen cost evaluation
        self.generators.append(g)


    def _push_branch(self, tokens):
        """ Adds a branch to the network """

        source_bus = self.network.buses[tokens["fbus"]-1]
        target_bus = self.network.buses[tokens["tbus"]-1]

        e = Branch(
            source_bus=source_bus, target_bus=target_bus,
            name=make_unique_name("e", self.network.branch_names),
            network=self.network
        )
        e.r = tokens["r"]
        e.x = tokens["x"]
        e.b = tokens["b"]
        e.s_max = tokens["rateA"] / self.base_mva
        e.ratio = tokens["ratio"]
        e.phase_shift = tokens["angle"]
        e.in_service = tokens["status"]

        self.network.add_branch(e)


    def _push_generator_cost(self, string, location, tokens):
        """ Adds cost data to generators """

        # There should be one or more generators in our list
        if not len(self.generators):
            print "More cost data than there are generators"
            return

        # Apply cost data to first generator in list and then remove it
        g = self.generators[0]

        g.cost_startup = float(tokens["startup"])
        g.cost_shutdown = float(tokens["shutdown"])

        # Piecewise linear cost data
        if tokens["model"] == 1:
            coords = tokens[4:]
#            print "Piecewise linear coordinates:", coords

            # Check that there is an even number of coordinates
            if len(coords) % 2 != 0:
                print "Uneven number of coordinates for pw linear cost"

            # Check that there are twice as many coordinates as 'n'
            if len(coords) != 2 * float(tokens["n"]):
                print "No. coords specified and no. supplied do not match"

            points = []
            # Form as list of tuples
            for i in range(len(coords)):
                if i % 2 == 0:
                    # FIXME: This should really use the machine MVA base
                    x = float(coords[i])/self.base_mva
                    y = float(coords[i+1])
                    points.append((x, y))
#            print "Points:", points

            g.pwl_points = points
            g.cost_model = "Piecewise Linear"

        # Polynomial cost data
        elif tokens["model"] == 2:
            coeffs = [float(c) for c in tokens[4:]]
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
            g.cost_model = "Polynomial"

        else:
            raise ValueError, "Invalid cost model number"

        # TODO: Parse possible reactive power cost data (rows ng+1)

        # Remove the processed generator
        self.generators.pop(0)

#------------------------------------------------------------------------------
#  Convenience function for MATPOWER import
#------------------------------------------------------------------------------

def import_matpower(file_or_filename):
    """ Convenience function for import of a MATPOWER data file given a
    file name or object.

    """

    return MATPOWERImporter().parse_file(file_or_filename)

#------------------------------------------------------------------------------
#  Standalone call:
#------------------------------------------------------------------------------

if __name__ == "__main__":
    import sys
    import logging
    logger = logging.getLogger()
    logger.addHandler(logging.StreamHandler(sys.stdout))
    logger.setLevel(logging.DEBUG)

    data_file = "/home/rwl/python/aes/matpower_3.2/rwl_003.m"
    #data_file = "/home/rwl/python/aes/model/matpower/case30.m"
    filter = MATPOWERImporter()
    print filter.parse_file(data_file)

# EOF -------------------------------------------------------------------------
