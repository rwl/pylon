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

""" Defines a test case for the Pyreto market experiment.
"""

#------------------------------------------------------------------------------
#  Imports:
#------------------------------------------------------------------------------

import unittest
from os.path import dirname, join

from pylon import Network, Bus, Generator, Load
from pylon.readwrite import MATPOWERReader

from pylon.pyreto.main import one_for_one

#------------------------------------------------------------------------------
#  Constants:
#------------------------------------------------------------------------------

DATA_FILE = join(dirname(__file__), "..", "test", "data", "case6ww.m")

#------------------------------------------------------------------------------
#  Returns a test power system:
#------------------------------------------------------------------------------

def get_test_network():
    """ Returns a test power system network.
    """
    # Read network from data file.
#    reader = MATPOWERReader()
#    power_sys = reader(DATA_FILE)

    # Build one bus test network.
    bus1 = Bus(name="Bus 1")

    generator = Generator(name        = "G1",
                          p_max       = 2.0,
                          p_min       = 0.0,
                          cost_model  = "polynomial",
                          cost_coeffs = (0.0, 6.0, 0.0))

    generator2 = Generator(name        = "G2",
                           p_max       = 6.0,
                           p_min       = 0.0,
                           cost_model  = "polynomial",
                           cost_coeffs = (0.0, 10.0, 0.0))

    load = Load(name="L1", p=1.0, q=0.0)

    bus1.generators.append(generator)
    bus1.generators.append(generator2)
    bus1.loads.append(load)

    power_sys = Network(name="1bus")
    power_sys.buses.append(bus1)

    return power_sys

#------------------------------------------------------------------------------
#  "MarketExperimentTest" class:
#------------------------------------------------------------------------------

class MarketExperimentTest(unittest.TestCase):
    """ Defines a test case for the Pyreto market experiment.
    """

    def setUp(self):
        """ The test runner will execute this method prior to each test.
        """
        self.power_sys = get_test_network()


    def test_contracts_market(self):
        """ Test trading through a bilateral contracts market.
        """
        market = ContractsMarket()
        buyer = Agent()
        market.add_buyer(buyer)
        seller = Agent()
        market.add_seller(seller)

        bids = market.get_bids(seller)
        offers = market.get_quotes(buyer)

        market.submit_bid(buyer, (100.0, 12.6, 48))
        market.request_quote(buyer, (80.0, 9.0, 24))

        market.submit_quote(seller, (80.0, 9.0, 24))


    def test_over_the_counter_trading(self):
        """ Test trading through shorter-term bilateral contracts.
        """
        otc = OTCMarket()


    def test_power_exchange(self):
        """ Test trading through exchange facilities constructed for the
            purpose of trading.
        """
        px = PowerExchange()


    def test_balancing_mechanism(self):
        """ Test system balancing using a reserve market.
        """
        bm = BalancingMechanism()


#    def test_opf(self):
#        """ Examine the DC OPF routine output.
#        """
#        routine = DCOPFRoutine()
#        routine(power_sys)
#        writer = ReSTWriter()
#        writer.write_generator_data(power_sys, sys.stdout)


    def test_experiment(self):
        """ Test a market experiment.
        """
        experiment = one_for_one(self.power_sys)
        experiment.doInteractions()


if __name__ == "__main__":
    unittest.main()

# EOF -------------------------------------------------------------------------
