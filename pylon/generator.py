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

""" Defines a generator as a complex power bus injection.
"""

#------------------------------------------------------------------------------
#  Imports:
#------------------------------------------------------------------------------

import logging

from util import Named

#------------------------------------------------------------------------------
#  Constants:
#------------------------------------------------------------------------------

GENERATOR = "generator"
DISPATCHABLE_LOAD = "vload"
POLYNOMIAL = "poly"
PW_LINEAR = "pwl"

#------------------------------------------------------------------------------
#  Logging:
#------------------------------------------------------------------------------

logger = logging.getLogger(__name__)

#------------------------------------------------------------------------------
#  "Generator" class:
#------------------------------------------------------------------------------

class Generator(Named):
    """ Defines a power system generator component. Fixes voltage magnitude
        and active power injected at parent bus. Or when at it's reactive
        power limit fixes active and reactive power injected at parent bus.
    """

    def __init__(self, bus, name=None, online=True, base_mva=100.0,
                 p=100.0, p_max=200.0, p_min=0.0, v_magnitude=1.0,
                 q=0.0, q_max=30.0, q_min=-30.0, c_startup=0.0, c_shutdown=0.0,
                 p_cost=None, pcost_model=POLYNOMIAL,
                 q_cost=None, qcost_model=None):
        """ Initialises a new Generator instance.
        """
        # Busbar to which the generator is connected.
        self.bus = bus

        # Unique name.
        self.name = name

        # Is the generator in service?
        self.online = online

        # Machine MVA base.
        self.base_mva = base_mva

        # Active power output (MW).
        self.p = p
        # Maximum active power output (MW).
        self.p_max = p_max
        # Minimum active power output (MW).
        self.p_min = p_min

        # Voltage magnitude setpoint (pu).
        self.v_magnitude = v_magnitude

        # Reactive power output (MVAr).
        self.q = q
        # Maximum reactive power (MVAr).
        self.q_max = q_max
        # Minimum reactive power (MVAr).
        self.q_min = q_min

        # Start up cost.
        self.c_startup = c_startup
        # Shut down cost.
        self.c_shutdown = c_shutdown

        # Active power cost model: 'poly' or 'pwl' (default: 'poly')
        if isinstance(p_cost, tuple):
            self.pcost_model = POLYNOMIAL
        elif isinstance(p_cost, list):
            self.pcost_model = PW_LINEAR
        else:
            self.pcost_model = pcost_model

        # Reactive power cost model: 'poly', 'pwl' or None (default: 'poly')
        if isinstance(q_cost, tuple):
            self.qcost_model = POLYNOMIAL
        elif isinstance(q_cost, list):
            self.qcost_model = PW_LINEAR
        else:
            self.qcost_model = qcost_model

        # Active power cost represented either by a tuple of quadratic
        # polynomial coefficients or a list of piece-wise linear coordinates
        # according to the value of the 'pcost_model' attribute.
        if p_cost is not None:
            self.p_cost = p_cost
        else:
            if self.pcost_model == POLYNOMIAL:
                self.p_cost = (0.01, 0.1, 10.0)
            elif self.pcost_model == PW_LINEAR:
                self.p_cost = [(0.0, 0.0), (p_max, 10.0)]
            else:
                raise ValueError

        # Reactive power cost.
        self.q_cost = q_cost

        self.mu_pmin = 0.0
        self.mu_pmax = 0.0

        self.mu_qmin = 0.0
        self.mu_qmax = 0.0

        # Unit Commitment -----------------------------------------------------

        # Ramp up rate (p.u./h).
#        self.rate_up = rate_up
        # Ramp down rate (p.u./h).
#        self.rate_down = rate_down

        # Minimum running time (h).
#        self.min_up = min_up
        # Minimum shut down time (h).
#        self.min_down = min_down

        # Initial number of periods up.
#        self.initial_up = initial_up
        # Initial number of periods down.
#        self.initial_down = initial_down

    @property
    def q_limited(self):
        """ Is the machine at it's limit of reactive power?
        """
        if (self.q >= self.q_max) or (self.q <= self.q_min):
            return True
        else:
            return False

    @property
    def is_load(self):
        """ Returns true if the generator if a dispatchable load. This may
            need to be revised to allow sensible specification of both elastic
            demand and pumped storage units.
        """
        return (self.p_min < 0.0) and (self.p_max == 0.0)


    def reset(self):
        """ Resets the result variables.
        """
        self.mu_pmin = 0.0
        self.mu_pmax = 0.0


    def total_cost(self, p=None, p_cost=None, pcost_model=None):
        """ Computes total cost for the generator at the given output level.
        """
        p = self.p if p is None else p
        p_cost = self.p_cost if p_cost is None else p_cost
        pcost_model = self.pcost_model if pcost_model is None else pcost_model

        if pcost_model == PW_LINEAR:
            n_segments = len(p_cost) - 1
            # Iterate over the piece-wise linear segments.
            for i in range(n_segments):
                x1, y1 = p_cost[i]
                x2, y2 = p_cost[i + 1]
                if x1 <= p <= x2:
                    m = (y2 - y1) / (x2 - x1)
                    c = y1 - m * x1
                    result = m*p + c
                    break
            else:
                raise ValueError, "Value [%f] outwith pwl cost curve." % p
                # Use the last segment for values outwith the cost curve.
#                result = m*p + c
        elif pcost_model == POLYNOMIAL:
            result = p_cost[-1]
            for i in range(1, len(p_cost)):
                result += p_cost[-(i + 1)] * p**i
        else:
            raise ValueError

        if self.is_load:
            return -result
        else:
            return result


#    def poly_cost(self, val=None, der=0, reactive=False):
#        """ Evaluates polynomial generator cost and derivatives.
#        """
#        cost_model = self.qcost_model if reactive else self.pcost_model
#        cost = self.q_cost if reactive else self.p_cost
#        if val is None: val = self.q if reactive else self.p
#
#        if cost_model == PW_LINEAR:
#            logger.error("Cost must be polynomial.")
#            return
#
#        # 1st column is constant term, 2nd linear, etc.
#        c = list(reversed(cost))
#
#        print c
#
#        # Do derivatives.
#        for d in range(der):
#            if len(c) >= 2:
#                c = c[1:len(c) - d + 1]
#            else:
#                c = 0.0
#                break
#            for k in range(1, len(c) - d):
#                c[k] *= k
#
#        # Evaluate polynomial.
#        if len(c) == 0:
#            f = 0.0
#        else:
#            f = c[0] # constant term
#            for k in range(1, len(c)):
#                f += c[k] * val**(k-1)
#
#        return f


    def pwl_to_poly(self):
        """ Converts the first segment of the pwl cost to linear quadratic.
            FIXME: Curve-fit for all segments.
        """
        if self.pcost_model == PW_LINEAR:
            x0 = self.p_cost[0][0]
            y0 = self.p_cost[0][1]
            x1 = self.p_cost[1][0]
            y1 = self.p_cost[1][1]
            m = (y1 - y0) / (x1 - x0)
            c = y0 - m * x0

            self.pcost_model = POLYNOMIAL
            self.p_cost = (m, c)
        else:
            return


    def poly_to_pwl(self, n_points=10):
        """ Sets the piece-wise linear cost attribute, converting the
            polynomial cost variable by evaluating at zero and then at
            n_points evenly spaced points between p_min and p_max.
        """
        assert self.pcost_model == POLYNOMIAL
        p_min = self.p_min
        p_max = self.p_max
        p_cost = []

        if p_min > 0.0:
            # Make the first segment go from the origin to p_min.
            step = (p_max - p_min) / (n_points - 2)

            y0 = self.total_cost(0.0)
            p_cost.append((0.0, y0))

            x = p_min
            n_points -= 1
        else:
            step = (p_max - p_min) / (n_points - 1)
            x = 0.0

        for _ in range(n_points):
            y = self.total_cost(x)
            p_cost.append((x, y))
            x += step

        # Change the cost model and set the new cost.
        self.pcost_model = PW_LINEAR
        self.p_cost = p_cost


    def get_offers(self, n_points=6):
        """ Returns quantity and price offers created from the cost function.
        """
        from pyreto.smart_market import Offer

        qtyprc = self._get_qtyprc(n_points)
        return [Offer(self, qty, prc) for qty, prc in qtyprc]


    def get_bids(self, n_points=6):
        """ Returns quantity and price bids created from the cost function.
        """
        from pyreto.smart_market import Bid

        qtyprc = self._get_qtyprc(n_points)
        return [Bid(self, qty, prc) for qty, prc in qtyprc]


    def _get_qtyprc(self, n_points=6):
        """ Returns a list of tuples of the form (qty, prc) created from the
            cost function.  If the cost function is polynomial it will be
            converted to piece-wise linear using poly_to_pwl(n_points).
        """
        if self.pcost_model == POLYNOMIAL:
            # Convert polynomial cost function to piece-wise linear.
            self.poly_to_pwl(n_points)

        n_segments = len(self.p_cost) - 1

        qtyprc = []

        for i in range(n_segments):
            x1, y1 = self.p_cost[i]
            x2, y2 = self.p_cost[(i + 1)]

            quantity = x2 - x1
            price = (y2 - y1) / quantity

            qtyprc.append((quantity, price))

        return qtyprc


#    def offers_bids_to_pwl(self, offers, bids):
#        """ Updates the piece-wise linear total cost function using the given
#            offer/bid blocks.
#
#            @see: matpower4.0b1/extras/smartmarket/off2case.m
#        """
##        offbids = offers + bids
#        valid_offers = [offer for offer in offers if
#                        offer.generator == self and
#                        not offer.withheld and
#                        round(offer.quantity, 4) > 0.0]
#
#        valid_bids = [bid for bid in bids if
#                      bid.vload == self and
#                      not bid.withheld and
#                      round(offer.quantity, 4) > 0.0]
#
#        p_offers = [v for v in valid_offers if not v.reactive]
#        q_offers = [v for v in valid_offers if v.reactive]
#        p_bids = [v for v in valid_bids if not bid.reactive]
#        q_bids = [v for v in valid_bids if bid.reactive]
#
#        if p_offers and not self.is_load:
#            logger.warning("Offer no allowed for vload [%s]." % self.name)
#            p_offers = []
#        if q_offers and self.q_max <= 0.0:
#            logger.warning("Q offer not allowed for gen [%s]." % self.name)
#            q_offers = []
#        if p_bids and self.is_load:
#            logger.warning("Bid not allowed for generator [%s]." % self.name)
#            p_bids = []
#        if q_bids and self.q_min >= 0.0:
#            logger.warning("Q bid not allowed for gen [%s]." % self.name)
#            q_bids = []
#
#        if p_offers:
#            self.p_cost = self._offbids_to_points(p_offers)
#            self.pcost_model = PW_LINEAR
#            self.online = True
#        else:
#            self.p_cost = [(0.0, 0.0), (self.p_max, 0.0)]
#            self.pcost_model = PW_LINEAR
#            if q_offers:
#                # Dispatch at zero real power without shutting down
#                # if capacity offered for reactive power.
#                self.p_min = 0.0
#                self.p_max = 0.0
#                self.online = True
#
#        if q_offers or q_bids:
#            offer_points = self._offbids_to_points(q_offers)
#            bid_points = self._offbids_to_points(q_bids, True)
#
#            self.qcost_model = PW_LINEAR
#            self.online = True
#            if not p_offers:
#                # Dispatch at zero real power without shutting down
#                # if capacity offered for reactive power.
#                self.p_min = 0.0
#                self.p_max = 0.0
#                self.online = True
#        else:
#            self.q_cost = [(0.0, 0.0), (self.q_max, 0.0)]
#            self.qcost_model = PW_LINEAR


    def offers_to_pwl(self, offers):
        """ Updates the piece-wise linear total cost function using the given
            offer blocks.

            @see: matpower3.2/extras/smartmarket/off2case.m
        """
        assert not self.is_load
        # Only apply offers associated with this generator.
        g_offers = [offer for offer in offers if offer.generator == self]
        # Fliter out zero quantity offers.
        gt_zero = [offr for offr in g_offers if round(offr.quantity, 4) > 0.0]
        # Ignore withheld offers.
        valid = [offer for offer in gt_zero if not offer.withheld]

        p_offers = [v for v in valid if not v.reactive]
        q_offers = [v for v in valid if v.reactive]

        if p_offers:
            self.p_cost = self._offbids_to_points(p_offers)
            self.pcost_model = PW_LINEAR
            self.online = True
        else:
            self.p_cost = [(0.0, 0.0), (self.p_max, 0.0)]
            self.pcost_model = PW_LINEAR
            if q_offers:
                # Dispatch at zero real power without shutting down
                # if capacity offered for reactive power.
                self.p_min = 0.0
                self.p_max = 0.0
                self.online = True
            else:
                self.online = False

        if q_offers:
            self.q_cost = self._offbids_to_points(q_offers)
            self.qcost_model = PW_LINEAR
        else:
            self.q_cost = None#[(0.0, 0.0), (self.q_max, 0.0)]
            self.qcost_model = PW_LINEAR

        if not len(p_offers) and not len(q_offers):
            logger.info("No valid offers for generator, shutting down.")
            self.online = False

        self._adjust_limits()


    def bids_to_pwl(self, bids):
        """ Updates the piece-wise linear total cost function using the given
            bid blocks.

            @see: matpower3.2/extras/smartmarket/off2case.m
        """
        assert self.is_load
        # Apply only those bids associated with this dispatchable load.
        vl_bids = [bid for bid in bids if bid.vLoad == self]
        # Filter out zero quantity bids.
        gt_zero = [bid for bid in vl_bids if round(bid.quantity, 4) > 0.0]
        # Ignore withheld offers.
        valid_bids = [bid for bid in gt_zero if not bid.withheld]

        p_bids = [v for v in valid_bids if not v.reactive]
        q_bids = [v for v in valid_bids if v.reactive]

        if p_bids:
            self.p_cost = self._offbids_to_points(p_bids, True)
            self.pcost_model = PW_LINEAR
            self.online = True
        else:
            self.p_cost = [(0.0, 0.0), (self.p_max, 0.0)]
            self.pcost_model = PW_LINEAR
            logger.info("No valid active power bids for dispatchable load "
                        "[%s], shutting down." % self.name)
            self.online = False

        if q_bids:
            self.q_cost = self._offbids_to_points(q_bids, True)
            self.qcost_model = PW_LINEAR
            self.online = True
        else:
            self.q_cost = [(self.q_min, 0.0), (0.0, 0.0), (self.q_max, 0.0)]
            self.qcost_model = PW_LINEAR
#            logger.info("No valid bids for dispatchable load, shutting down.")
#            self.online = False

        self._adjust_limits()


    def _offbids_to_points(self, offbids, arebids=False):
        """ Returns a list of points for a piece-wise linear function from the
            given offer/bid blocks.
        """
        # Sort offers/bids by price in ascending order.
        offbids.sort(key=lambda x: x.price, reverse=arebids)

        points = [(0.0, offbids[0].noLoadCost)]
        # Form piece-wise linear total cost function.
        for i, offbid in enumerate(offbids):
            x1, y1 = points[i]
            x2 = x1 + offbid.quantity # MW.
            m = offbid.price # $/MWh
            y2 = m * (x2 - x1) + y1
            points.append((x2, y2))

        if arebids:
            points = [(-x, -y) for x, y in points]
            points.reverse()

        n_segs = len(points) - 1
        logger.info("%d segment pwl cost function: %s" % (n_segs, points))

        return points


    def _adjust_limits(self):
        """ Sets the active power limits, 'p_max' and 'p_min', according to
            the pwl cost function points.
        """
        if not self.is_load:
#            self.p_min = min([point[0] for point in self.p_cost])
            self.p_max = max([point[0] for point in self.p_cost])
        else:
            p_min = min([point[0] for point in self.p_cost])
            self.p_max = 0.0
            self.q_min = self.q_min * p_min / self.p_min
            self.q_max = self.q_max * p_min / self.p_min
            self.p_min = p_min

# EOF -------------------------------------------------------------------------
