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

""" Defines options for an executive """

#------------------------------------------------------------------------------
#  Imports:
#------------------------------------------------------------------------------

from enthought.traits.api import \
    HasTraits, Instance, Int, Float, Enum, Tuple, Str, Range, Bool, \
    Directory, List

from enthought.traits.ui.api import View, Item, Group, HGroup

from pylon.dss.common.circuit_element import CircuitElement

from pylon.dss.common.circuit import Circuit

#------------------------------------------------------------------------------
#  "ExecutiveOptions" class:
#------------------------------------------------------------------------------

class ExecutiveOptions(HasTraits):
    """ Defines options for an executive """

    # Sets the active DSS class type.
    type = Instance(HasTraits)

    # Sets the active DSS element by name. You can use the complete object spec
    # (class.name) or just the name.  if full name is specifed, class becomes
    # the active class, also.
    element = Instance(CircuitElement)

    # Sets the hour used for the start time of the solution.
    hour = Int(12)

    # Sets the seconds from the hour for the start time of the solution.
    sec = Int(0)

    # Sets the Year (integer number) to be used for the solution. For certain
    # solution types, this determines the growth multiplier.
    year = Int(2008)

    # Sets the frequency for the solution of the active circuit.
    frequency = Float(60.0)

    # Sets the time step in sec for the active circuit. Nominally for dynamics
    # solution.
    step_size = Float(0.1)

    # Set the solution Mode: One of
    #    Snapshot,
    #    Daily,
    #    Direct,
    #    Dutycycle,
    #    Dynamic,
    #    Harmonic,
    #    M1 (Monte Carlo 1),
    #    M2 (Monte Carlo 2),
    #    M3 (Monte Carlo 3),
    #    Faultstudy,
    #    Yearly (follow Yearly curve),
    #    MF (monte carlo fault study)
    #    Peakday,
    #    LD1 (load-duration 1)
    #    LD2 (load-duration 2)
    #    AutoAdd (see AddType)
    #
    # Side effect: setting the Mode propergy resets all monitors and energy
    # meters. It also resets the time step, etc. to defaults for each mode.
    # After the initial reset, the user must explicitly reset the monitors
    # and/or meters until another Set Mode= command.
    mode = Enum(
        "Snapshot", "Daily", "Direct", "Duty Cycle", "Dynamic", "Harmonic",
        "Monte Carlo 1", "Monte Carlo 2", "Monte Carlo 3", "Fault Study",
        "Yearly", "Monte Carlo Fault Study", "Peak-Day", "Load Duration 1",
        "Load Duration 2", "Auto Add", desc="Solution mode"
    )

    # One of [Uniform | Gaussian | Lognormal | None ] for Monte Carlo
    # Variables.
    random = Enum("Uniform", "Gaussian", "Log-Normal", "None")

    # Number of solutions to perform for Monte Carlo or dutycycle solutions.
    number = Int(
        2, desc="Number of solutions to perform for Monte Carlo or dutycycle "
        "solutions"
    )

    # Specify the solution start time as a tuple: time=(hour, secs)
    time = Tuple(Float(12), Float(00), desc="Solution start time")

    # Synonym for type
#    klass

    # Synonym for element
#    object

    # Set the active circuit by name.
    circuit = Instance(Circuit)

    # Set the command string required to start up the editor preferred by the
    # user. Does not require a circuit defined.
#    editor

    # Sets the solution tolerance.
    tolerance = Float(0.0001, desc="Solution tolerance")

    # Sets the maximum allowable iterations for power flow solutions.
    max_iter = Int(
        15, desc="maximum allowable iterations for power flow solutions"
    )

    # Alternate name for time step size.
#    h

    # {Powerflow | Admittance} depending on the type of solution you wish to
    # perform. If admittance, a non-iterative, direct solution is done with all
    # loads and generators modeled by their equivalent admittance.
    load_model = Enum("PowerFlow", "Admittance")

    # Global load multiplier for this circuit.  Does not affect loads
    # designated to be "fixed".  All other base kW values are multiplied by
    # this number. Defaults to 1.0 when the circuit is created. As with other
    # values, it always stays at the last value to which it was set until
    # changed again.
    load_mult = Float(1.0, desc="Global load multiplier")

    # Minimum permissible per unit voltage for normal conditions.
    norm_vmin_pu = Float(
        0.95, desc="Minimum permissible per unit voltage for normal conditions"
    )

    # Maximum permissible per unit voltage for normal conditions.
    norm_vmax_pu = Float(
        1.05, desc="Maximum permissible per unit voltage for normal conditions"
    )

    # Minimum permissible per unit voltage for emergency (contingency)
    # conditions.
    emerg_vmin_pu = Float(
        0.90, desc="Minimum permissible per unit voltage for emergency "
        "(contingency) conditions"
    )

    # Maximum permissible per unit voltage for emergency (contingency)
    # conditions.
    emerg_vmax_pu = Float(
        1.08, desc="Maximum permissible per unit voltage for emergency "
        "(contingency) conditions"
    )

    # Percent mean to use for global load multiplier.
    pct_mean = Range(
        0, 100, 65, desc="Percentage mean to use for global load multiplier"
    )

    # Percent Standard deviation to use for global load multiplier.
    pct_std_dev = Range(
        0, 100, 9, desc="Percent standard deviation to use for global "
        "load multiplier"
    )

    # Set Load-Duration Curve. Global load multiplier is defined by this curve
    # for LD1 and LD2 solution modes.
    ld_curve = Float(0.0, desc="Load-duration curve")

    # Set default annual growth rate, percent, for loads with no growth curve
    # specified.
    pct_growth = Range(0.0, 100.0, 2.5, desc="Annual growth rate")

    # Size of generator, kW, to automatically add to system.
    gen_kw = Float(1000.0)

    # Power factor of generator to assume for automatic addition.
    gen_pf = Float(1.0)

    # Size of capacitor, kVAR, to automatically add to system.
    cap_kvar = Float(600.0)

    # Type of device for AutoAdd Mode.
    add_type = Enum("Generator", "Capacitor")

    # Flag to indicate if it is OK to have devices of same name in the same
    # class. If No, then a New command is treated as an Edit command.
    # If Yes, then a New command will always result in a device being added.
    allow_duplicates = Bool(False)

    # If false, then meter zones are recomputed each time there is a change in
    # the circuit. If Yes, then meter zones are not recomputed unless they have
    # not yet been computed. Meter zones are normally recomputed on Solve
    # command following a circuit change.
    zone_lock = Bool(False)

    # Weighting factor for UE/EEN in AutoAdd functions.
    # Autoadd mode minimizes (Lossweight * Losses + UEweight * UE).
    # If you wish to ignore UE, set to 0.
    # This applies only when there are EnergyMeter objects. Otherwise, AutoAdd
    # mode minimizes total system losses.
    ue_weight = Float(1.0)

    # Weighting factor for Losses in AutoAdd functions. Autoadd mode minimizes
    # (Lossweight * Losses + UEweight * UE).
    # If you wish to ignore Losses, set to 0. This applies only when there are
    # EnergyMeter objects. Otherwise, AutoAdd mode minimizes total system
    # losses.
    loss_weight = Float(1.0)

    # Which EnergyMeter register(s) to use for UE in AutoAdd Mode. May be one
    # or more registers.  if more than one, register values are summed
    # together. Array of integer values > 0.  Defaults to 11 (for Load EEN).
    # For a list of EnergyMeter register numbers, do the "Show Meters" command
    # after defining a circuit.
    ue_regs = Int(11)

    # Which EnergyMeter register(s) to use for Losses in AutoAdd Mode. May be
    # one or more registers.  If more than one, register values are summed
    # together. Array of integer values > 0.  Defaults to 13 (for Zone kWh
    # Losses). For a list of EnergyMeter register numbers, do the "Show Meters"
    # command after defining a circuit.
    loss_regs = Int(13)

    # Define legal bus voltage bases for this circuit.  Enter an array
    # of the legal voltage bases, in phase-to-phase voltages, for example:
    # set voltagebases=".208, .480, 12.47, 24.9, 34.5, 115.0, 230.0"
    # When the CalcVoltageBases command is issued, a snapshot solution is
    # performed with no load injections and the bus base voltage is set to the
    # nearest legal voltage base. The defaults are as shown in the example
    # above.
    voltage_bases = List(Float, [.208, .480, 12.47, 24.9, 34.5, 115.0, 230.0])

    # Solution algorithm type.  Normal is a fixed point iteration that is a
    # little quicker than the Newton iteration.  Normal is adequate for most
    # radial distribution circuits.  Newton is more robust for circuits that
    # are difficult to solve.
    algorithm = Enum("Normal", "Newton")

    # Specifies whether to use trapezoidal integration for accumulating energy
    # meter registers. Applies to EnergyMeter and Generator objects.  Default
    # method simply multiplies the present value of the registers times the
    # width of the interval. Trapezoidal is more accurate when there are sharp
    # changes in a load shape or unequal intervals. Trapezoidal is
    # automatically used for some load-duration curve simulations where the
    # interval size varies considerably. Keep in mind that for Trapezoidal, you
    # have to solve one more point than the number of intervals. That is, to do
    # a Daily simulation on a 24-hr load shape, you would set Number=25 to
    # force a solution at the first point again to establish the last (24th)
    # interval.
    trapezoidal = Bool(
        False, desc="whether to use trapezoidal integration for accumulating "
        "energy meter registers"
    )

    # Array of bus names to include in AutoAdd searches. Or, you can specify a
    # text file holding the names, one to a line, by using the syntax
    # (file=filename) instead of the actual array elements. Default is null,
    # which results in the program using either the buses in the EnergyMeter
    # object zones or, if no EnergyMeters, all the buses, which can make for
    # lengthy solution times. Examples:
    #    Set autobuslist=(bus1, bus2, bus3, ... )
    #    Set autobuslist=(file=buslist.txt)
    auto_bus_list = List(Str)

    # Control mode for the solution.
    # Set to OFF to prevent controls from changing.
    #
    #    STATIC = Time does not advance.  Control actions are executed in order
    #    of shortest time to act until all actions are cleared from the control
    #    queue.  Use this mode for power flow solutions which may require
    #    several regulator tap changes per solution.
    #
    #    EVENT = solution is event driven.  Only the control actions nearest in
    #    time are executed and the time is advanced automatically to the time
    #    of the event.
    #
    #    TIME = solution is time driven.  Control actions are executed when the
    #    time for the pending action is reached or surpassed. Controls may
    #    reset and may choose not to act when it comes their time.
    #    Use TIME mode when modeling a control externally to the DSS and a
    #    solution mode such as DAILY or DUTYCYCLE that advances time, or set
    #    the time (hour and sec) explicitly from the external program.
    control_mode = Enum("Static", "Event", "Time")

    # Set to YES to trace the actions taken in the control queue. Creates a
    # file named TRACE_CONTROLQUEUE.CSV in the default directory. The names of
    # all circuit elements taking an action are logged.
    trace_mode = Bool(
        False, desc="Trace the actions taken in the control queue"
    )

    # Global multiplier for the kW output of every generator in the circuit.
    # Applies to all but Autoadd solution modes. Ignored for generators
    # designated as Status=Fixed.
    gen_mult = Float(
        1.0, desc="Global multiplier for the kW output of every generator"
    )

    # Default daily load shape name. Default value is "default", which is a
    # 24-hour curve defined when the DSS is started.
    default_daily = Str("default")

    # Default yearly load shape name. Default value is "default", which is a
    # 24-hour curve defined when the DSS is started.
    default_yearly = Str("default")

    # Sets all allocation factors for all loads in the active circuit to the
    # value given.
    allocation_factors = Float

    # Designates whether circuit model is to interpreted as a normal
    # multi-phase model or a positive-sequence only model
    ckt_model = Enum("Multiphase", "Positive")

    # Sets the price signal ($/MWh) for the circuit.
    price_signal = Float(25.0)

    # Sets the curve to use to obtain for price signal. Default is none
    # (null string). If none, price signal either remains constant or is set by
    # an external process. Curve is defined as a loadshape (not normalized) and
    # should correspond to the type of analysis being performed (daily, yearly,
    # load-duration, etc.).
    price_curve = Str

    # Set the active terminal of the active circuit element. May also be done
    # with select command.
    terminal = Int(1)

    # Set the fundamental frequency for harmonic solution and the default base
    # frequency for all impedance quantities. Side effect: also changes the
    # value of the solution frequency.
    base_frequency = Float(60.0)

    # Array of harmonics for which to perform a solution in Harmonics mode. If
    # ALL, then solution is performed for all harmonics defined in spectra
    # currently being used. Otherwise, specify a more limited list such as:
    #    set_harmonics=(1, 5, 7, 11, 13,)
    harmonics = List(Int, [1, 5, 7, 13])

    # Max control iterations per solution.
    max_controller = Int(10, desc="Max control iterations")

    # Set Active Bus by name.  Can also be done with Select and SetkVBase
    # commands and the "Set Terminal="  option. The bus connected to the active
    # terminal becomes the active bus. See z_sc and z_sc012 commands.
    bus = Str

    # Set the data path for files written or read by the DSS.  Defaults to the
    # startup path. May be Null.  Executes a CHDIR to this path if non-null.
    # Does not require a circuit defined.
    data_path = Directory

    # Array of bus names to keep when performing circuit reductions. You can
    # specify a text file holding the names, one to a line, by using the syntax
    # (file=filename) instead of the actual array elements. Command is
    # cumulative (reset keeplist first). Reduction algorithm may keep other
    # buses automatically. Examples:
    #    Reset Keeplist (sets all buses to FALSE (no keep))
    #    Set KeepList=(bus1, bus2, bus3, ... )
    #    Set KeepList=(file=buslist.txt)
    keep_list = List(
        Str, desc="bus names to keep when performing circuit reductions"
    )

    # Strategy for reducing feeders.
    # Default is to eliminate all dangling end buses and buses without load,
    # caps, or taps.
    #    "Stubs [Zmag=0.02]" merges short branches with impedance less than
    #    Zmag (default = 0.02 ohms)
    #
    #    "MergeParallel" merges lines that have been found to be in parallel
    #
    #    "Breakloops" disables one of the lines at the head of a loop.
    #
    #    "Tapends [maxangle=15]" eliminates all buses except those at the
    #    feeder ends, at tap points and where the feeder turns by greater than
    #    maxangle degrees.
    #
    #    "Ends" eliminates dangling ends only.
    #
    #    "Switches" merges switches with downline lines and eliminates dangling
    #    switches.
    #
    #    Marking buses with "Keeplist" will prevent their elimination.
    reduce_option = Enum(
        "Stubs", "Merge Parallel", "Break Loops", "Tap Ends", "Ends",
        "Switches", desc="Strategy for reducing feeders"
    )

    # Set for keeping demand interval data for daily, yearly, etc, simulations.
    # Side Effect:  Resets all meters!!!
    demand_interval = Bool(False, desc="Caution: Resets all meters!")

    # Sets the Normal rating of all lines to a specified percent of the
    # emergency rating.  Note: This action takes place immediately. Only the
    # in-memory value is changed for the duration of the run.
    pct_normal = Range(0, 100, desc="Percentage of the emergency rating")

    # Set to Yes/True if you wish a separate demand interval (DI) file written
    # for each meter.  Otherwise, only the totalizing meters are written.
    di_verbose = Bool(False)

    # Name of case for yearly simulations with demand interval data.
    # Becomes the name of the subdirectory under which all the year data are
    # stored. Default = circuit name. Side Effect: Sets the prefix for output
    # files
    case_name = Str

    # Number code for node marker on circuit plots (SDL MarkAt options).
    marker_code = Str

    # Width of node marker.
    node_width = Float(1.0)

    # Significant solution events are added to the Event Log, primarily for
    # debugging.
    log = Bool(False)

    # Opens DSSRecorder.DSS in DSS install folder and enables recording of all
    # commands that come through the text command interface. Closed by either
    # setting to NO/FALSE or exiting the program. When closed by this command,
    # the file name can be found in the Result. Does not require a circuit
    # defined.
    recorder = Bool(False)

    # For yearly solution mode, sets overload reporting on/off. DemandInterval
    # must be set to true for this to have effect.
    overload_report = Bool(False)

    # For yearly solution mode, sets voltage exception reporting on/off.
    # DemandInterval must be set to true for this to have effect.
    voltage_exception_report = Bool(False)

    #--------------------------------------------------------------------------
    #  Views:
    #--------------------------------------------------------------------------

    traits_view = View(HGroup(
        Group(
            [
                "marker_code", "random", "ld_curve", "number", "load_mult",
                "pct_mean", "load_model", "log", "trace_mode", "ue_regs",
                "add_type", "gen_pf", "terminal", "harmonics", "type",
                "default_yearly", "max_controller", "pct_growth",
                "demand_interval", "bus", "case_name", "hour", "loss_regs",
                "auto_bus_list", "keep_list", "norm_vmax_pu", "pct_normal",
                "price_signal", "trait_modified", "node_width", "data_path",
                "norm_vmin_pu", "frequency", "sec", "cap_kvar", "year"
            ]
        ),
        Group(
            [
                "price_curve", "pct_std_dev", "ckt_model", "trait_added",
                "allow_duplicates", "emerg_vmin_pu", "step_size",
                "reduce_option", "voltage_bases", "recorder", "loss_weight",
                "tolerance", "gen_mult", "zone_lock", "default_daily",
                "ue_weight", "allocation_factors", "di_verbose", "gen_kw",
                "base_frequency", "algorithm", "overload_report",
                "voltage_exception_report", "element", "circuit", "time",
                "control_mode", "emerg_vmax_pu", "mode", "trapezoidal",
                "max_iter"
            ]
        )),
        id="pylon.executive.executive_options",
        resizable=True, title="Preferences"
    )

#------------------------------------------------------------------------------
#  Standalone call:
#------------------------------------------------------------------------------

if __name__ == "__main__":
    ExecutiveOptions().configure_traits()

# EOF -------------------------------------------------------------------------
