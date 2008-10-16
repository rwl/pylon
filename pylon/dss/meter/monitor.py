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

""" Defines the monitor circuit element """

#------------------------------------------------------------------------------
#  Imports:
#------------------------------------------------------------------------------

from enthought.traits.api import Instance, Int, Enum, Bool

from pylon.dss.common.circuit_element import CircuitElement

from meter_element import MeterElement

#------------------------------------------------------------------------------
#  "MonitorObject" class:
#------------------------------------------------------------------------------

class Monitor(MeterElement):
    """ A monitor is a circuit element that is connected to a terminal of
    another circuit element.  It records the voltages and currents at that
    terminal as a function of time and can report those values upon demand.

    A Monitor is defined by a New commands:

    New Type=Monitor Name=myname Element=elemname Terminal=[1,2,...]
    Buffer=clear|save

    Upon creation, the monitor buffer is established.  There is a file
    associated with the buffer.  It is named "Mon_elemnameN.mon"  where N is
    the terminal no. The file is truncated to zero at creation or buffer
    clearing.

    The Monitor keeps results in the in-memory buffer until it is filled.  Then
    it appends the buffer to the associated file and resets the in-memory
    buffer.

    For buffer=save, the present in-memory buffer is appended to the disk file
    so that it is saved for later reference.

    The Monitor is a passive device that takes a sample whenever its
    "TakeSample" method is invoked.  The SampleAll method of the Monitor ckt
    element class will force all monitors elements to take a sample.  If the
    present time (for the most recent solution is greater than the last time
    entered in to the monitor buffer, the sample is appended to the buffer.
    Otherwise, it replaces the last entry.

    Monitor Files are simple binary files of doubles.  The first record
    contains the number of conductors per terminal (NCond). (always use 'round'
    function when converting this to an integer). Then subsequent records
    consist of time and voltage and current samples for each terminal (all
    complex doubles) in the order shown below:

    The time values will not necessarily be in a uniform time step;  they will
    be at times samples or solutions were taken.  This could vary from several
    hours down to a few milliseconds.

    The monitor ID can be determined from the file name.  Thus, these values
    can be post-processed at any later time, provided that the monitors are not
    reset.

    Modes are:
        0: Standard mode - V and I,each phase, Mag and Angle
        1: Power each phase, complex (kw and kvars)
        2: Transformer Tap
        3: State Variables
        +16: Sequence components: V012, I012
        +32: Magnitude Only
        +64: Pos Seq only or Average of phases


    A monitor is a benign circuit element that is associated with a terminal of
    another circuit element.  It takes a sample when instructed, recording the
    time and the complex values of voltage and current, or power, at all
    phases.

    The data are saved in a file (separate one for each monitor) at the
    conclusion of a multistep solution or each solution in a Monte Carlo
    calculation.  In essence, it works like a real power monitor.  The data in
    the file may be converted to csv form and, for example, brought into
    (EPRI provides VBA routines to read the monitor files directly and import
    either complex voltages and currents or their magnitudes.)  The binary form
    of the monitor file is
        Signature (4-byte Integer) signifies that this is a
        DSS monitor file = 43756
        Version (4-byte integer)    version number of the file
        Sample Size (4-byte integer)    No. of quantities saved per sample
        Mode (4-byte integer)         Monitor mode

    Records follow
    <--- All voltages first ---------------->|<--- All currents ----->|
    <hour 1> <sec 1> <V1.re>  <V1.im>  <V2.re>  <V2.im>  .... <I1.re>  <I1.im>
    <hour 2> <sec 1> <V1.re>  <V1.im>  <V2.re>  <V2.im>  .... <I1.re>  <I1.im>
    <hour 3> <sec 1> <V1.re>  <V1.im>  <V2.re>  <V2.im>  .... <I1.re>  <I1.im>

    If powers are saved then the record has only the power for each phase.

    All values are Singles (32-bit). Hours and Seconds values are not included
    in Sample Size. Recorded values are not necessarily saved as illustrated,
    depending on Mode (see below).  However, the file is always packed singles
    with each record beginning with the hour and seconds past the hour.

    For Monte Carlo runs, the hour is set to the number of the solution and
    seconds is set to zero.

    Monitors may be connected to both power delivery elements and power
    conversion elements.

    """

    # Name (Full Object name) of element to which the monitor is connected.
    element = Instance(CircuitElement)

    # Number of the terminal of the circuit element to which the monitor is
    # connected.  1 or 2, typically. For monitoring states, attach monitor to
    # terminal 1.
    terminal = Int(1)

    # Bitmask integer designating the values the monitor is to capture:
    #    0 = Voltages and currents
    #    1 = Powers
    #    2 = Tap Position (Transformers only)
    #    3 = State Variables (PCElements only)
    # Normally, these would be actual phasor quantities from solution.
    # Combine with adders below to achieve other results for terminal
    # quantities:
    #     +16 = Sequence quantities
    #     +32 = Magnitude only
    #     +64 = Positive sequence only or avg of all phases
    #
    # Mix adder to obtain desired results. For example:
    # Mode=112 will save positive sequence voltage and current magnitudes only
    # Mode=48 will save all sequence voltages and currents, but magnitude only.
    mode = Enum("V & I", "P & Q", "Tap Position", "State Variables")

    # {Clear | Save | Take}
    # (C)lears or (S)aves current buffer.
    # (T)ake action takes a sample.
    # Note that monitors are automatically reset (cleared) when the
    # Set Mode= command is issued.
    # Otherwise, the user must explicitly reset all monitors (reset monitors
    # command) or individual monitors with the Clear action.
    action = Enum("Clear", "Save", "Take")

    # Include Residual channel (sum of all phases) for voltage and current.
    # Does not apply to sequence quantity modes or power modes.
    residual = Bool(
        False, desc="Include Residual channel (sum of all phases) for voltage "
        "and current"
    )

    # Report voltage and current in polar form (Mag/Angle). Otherwise, it will
    # be real and imaginary.
    v_i_polar = Bool(True, desc="Report voltage and current in polar form")

    # Report power in Apparent power, S, in polar form (Mag/Angle). Otherwise,
    # is P and Q
    p_polar = Bool(False, desc="Report apparent power, in polar form")

# EOF -------------------------------------------------------------------------
