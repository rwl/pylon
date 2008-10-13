#------------------------------------------------------------------------------
# Copyright (C) 2008 Richard W. Lincoln
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

""" Defines a transformer """

#------------------------------------------------------------------------------
#  "Transformer" class:
#------------------------------------------------------------------------------

class Transformer:
    """ The Transfomer model is implemented as a multi-terminal (two or more)
    power delivery element.

    A transfomer consists of two or more Windings, connected in somewhat
    arbitray fashion (with the standard Wye-Delta defaults, of course).  You
    can specify the parameters of a winding one winding at a time or use arrays
    to set all the values.  Use the "wdg=..." parameter to select a winding.

    Transformers have one or more phases.  The number of conductors per
    terminal is always one more than the number of phases.  For wye- or
    star-connected windings, the extra conductor is the neutral point.  For
    delta-connected windings, the extra terminal is open internally (you
    normally leave this connected to node 0).

    """

    # Number of phases this transformer.
    phases = 3

    # Number of windings, this transformers. (Also is the number of terminals)
    windings = 2

    # Winding Defintion -------------------------------------------------------

    # Set this = to the number of the winding you wish to define.  Then set
    # the values for this winding.  Repeat for each winding.  Alternatively,
    # use the array collections (buses, kvas, etc.) to define the windings.
    # Note: impedances are BETWEEN pairs of windings; they are not the property
    # of a single winding.
    wdg = 1

    # Bus to which this winding is connected.
    bus = None

    # Connection of this winding. Default is "wye" with the neutral solidly
    # grounded.
    conn = "wye"

    # For 2-or 3-phase, enter phase-phase kV rating.  Otherwise, kV rating of
    # the actual winding
    kv = 12.47

    # Base kVA rating of the winding. Side effect: forces change of max normal
    # and emerg kva ratings.
    kva = 1000

    # Per unit tap that this winding is on.
    tap = 1.0

    # Percent resistance this winding.  (half of total for a 2-winding).
    pct_r = 0.2

    # Neutral resistance of wye (star)-connected winding in actual ohms. If
    # entered as a negative value, the neutral is assumed to be open, or
    # floating.
    r_neut = -1

    # Neutral reactance of wye(star)-connected winding in actual ohms. May
    # be + or -.
    x_neut = 0

    # General Data ------------------------------------------------------------

    # Use the following parameters to set the winding values using arrays
    # (setting of wdg=... is ignored).

    # Use this to specify all the bus connections at once using an array.
    # Example:
    #     New Transformer.T1 buses="Hibus, lowbus"
    buses = ""

    # Use this to specify all the Winding connections at once using an array.
    # Example:
    #    New Transformer.T1 buses="Hibus, lowbus" ~ conns=(delta, wye)
    conns = ""

    # Use this to specify the kV ratings of all windings at once using an
    # array. Example:
    # New Transformer.T1 buses="Hibus, lowbus"
    # ~ conns=(delta, wye)
    # ~ kvs=(115, 12.47)
    # See kV= property for voltage rules.
    kv_s = ""

    # Use this to specify the kVA ratings of all windings at once using an
    # array.
    kva_s = ""

    # Use this to specify the p.u. tap of all windings at once using an array.
    taps = ""

    # Use this to specify the percent reactance, H-L (winding 1 to winding 2).
    # Use for 2- or 3-winding transformers. On the kva base of winding 1.
    x_hl = 7

    # Use this to specify the percent reactance, H-T (winding 1 to winding 3).
    # Use for 3-winding transformers only. On the kVA base of winding 1.
    x_ht = 35

    # Use this to specify the percent reactance, L-T (winding 2 to winding 3).
    # Use for 3-winding transformers only. On the kVA base of winding 1.
    x_lt = 30

    # Use this to specify the percent reactance between all pairs of windings
    # as an array.
    # All values are on the kVA base of winding 1.  The order of the values is
    # as follows:
    #    (x12 13 14... 23 24.. 34 ..)
    # There will be n(n-1)/2 values, where n=number of windings.
    x_sc_array = ""

    # Thermal time constant of the transformer in hours.  Typically about 2.
    thermal = 2

    # n Exponent for thermal properties in IEEE C57.  Typically 0.8.
    n = 0.8

    # m Exponent for thermal properties in IEEE C57.  Typically 0.9 - 1.0
    m = 0.8

    # Temperature rise, deg C, for full load.
    fl_rise = 65

    # Hot spot temperature rise, deg C.
    hs_rise = 15

    # Percent load loss at full load. The %R of the High and Low windings (1
    # and 2) are adjusted to agree at rated kVA loading.
    pct_load_loss = 0

    # Percent no load losses at rated excitatation voltage. Converts to a
    # resistance in parallel with the magnetizing impedance in each winding.
    pct_no_load_loss = 0

    # Normal maximum kVA rating of H winding (winding 1).  Usually 100% - 110%
    # of maximum nameplate rating, depending on load shape. Defaults to 110% of
    # kVA rating of Winding 1.
    norm_h_kva = ""

    # Emergency (contingency)  kVA rating of H winding (winding 1).  Usually
    # 140% - 150% of
    # maximum nameplate rating, depending on load shape. Defaults to 150% of
    # kVA rating of Winding 1.
    emerg_h_kva = ""

    # {Yes|No}  Designates whether this transformer is to be considered a
    # substation.
    sub = "No"

    # Max per unit tap for the active winding.
    max_tap = 1.10

    # Min per unit tap for the active winding.
    min_tap = 0.90

    # Total number of taps between min and max tap.
    num_taps = 32

    # Substation Name. Optional. If specified, printed on plots
    subname = ""

    # Percent magnetizing current. Default=0.0. Magnetizing branch is in
    # parallel with windings in each phase. Also, see "ppm_antifloat".
    pct_image = 0

    # Default=1 ppm.  Parts per million by which the reactive term is increased
    # to protect against accidentally floating a winding.
    # If positive then the effect is adding a small reactor to ground. If
    # negative, then a capacitor.
    ppm_antifloat = 1

# EOF -------------------------------------------------------------------------
