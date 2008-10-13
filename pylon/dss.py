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

""" Defines objects common to all circuits in the DSS """

#------------------------------------------------------------------------------
#  "ExecOptions" class:
#------------------------------------------------------------------------------

class ExecOptions:
    """ Defines options for an executive """

    # Sets the active DSS class type.
    type

    # Sets the active DSS element by name. You can use the complete object spec
    # (class.name) or just the name.  if full name is specifed, class becomes
    # the active class, also.
    element

    # Sets the hour used for the start time of the solution.
    hour

    # Sets the seconds from the hour for the start time of the solution.
    sec

    # Sets the Year (integer number) to be used for the solution. For certain
    # solution types, this determines the growth multiplier.
    year

    # Sets the frequency for the solution of the active circuit.
    frequency

    # Sets the time step in sec for the active circuit.  Nominally for dynamics
    # solution.
    step_size

    # Set the solution Mode: One of
    #    Snapshot,
    #    Daily,
    #    DIrect,
    #    DUtycycle,
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
    mode = ""

    # One of [Uniform | Gaussian | Lognormal | None ] for Monte Carlo
    # Variables.
    random = ""

    # Number of solutions to perform for Monte Carlo or dutycycle solutions.
    number = 2

    # Specify the solution start time as an array: time=(hour, secs)
    time = (12, 60)

    # Synonym for type
    klass

    # Synonym for element
    object

    # Set the active circuit by name.
    circuit

    # Set the command string required to start up the editor preferred by the
    # user. Does not require a circuit defined.
    editor

    # Sets the solution tolerance.
    tolerance = 0.0001

    # = Sets the maximum allowable iterations for power flow solutions.
    max_iter = 15

    # Alternate name for time step size.
    h

    # {Powerflow | Admittance} depending on the type of solution you wish to
    # perform. If admittance, a non-iterative, direct solution is done with all
    # loads and generators modeled by their equivalent admittance.
    load_model = "PowerFlow"

    # Global load multiplier for this circuit.  Does not affect loads
    # designated to be "fixed".  All other base kW values are multiplied by
    # this number. Defaults to 1.0 when the circuit is created. As with other
    # values, it always stays at the last value to which it was set until
    # changed again.
    load_mult = 1.0

    # Minimum permissible per unit voltage for normal conditions.
    norm_vmin_pu = 0.95

    # Maximum permissible per unit voltage for normal conditions.
    norm_vmax_pu = 1.05

    # Minimum permissible per unit voltage for emergency (contingency)
    # conditions.
    emerg_vmin_pu = 0.90

    # Maximum permissible per unit voltage for emergency (contingency)
    # conditions.
    emerg_vmax_pu = 1.08

    # Percent mean to use for global load multiplier.
    pct_mean = 65

    # Percent Standard deviation to use for global load multiplier.
    pct_std_dev = 9

    # Set Load-Duration Curve. Global load multiplier is defined by this curve
    # for LD1 and LD2 solution modes.
    ld_curve = 0

    # Set default annual growth rate, percent, for loads with no growth curve
    # specified.
    pct_growth = 2.5

    # Size of generator, kW, to automatically add to system.
    gen_kw = 1000.0

    # Power factor of generator to assume for automatic addition.
    gen_pf = 1.0

    # Size of capacitor, kVAR, to automatically add to system.
    cap_kvar = 600.0

    # {Generator | Capacitor} Type of device for AutoAdd Mode.
    add_type = "Generator"

    # {YES/TRUE | NO/FALSE}   Default is No. Flag to indicate if it is OK to
    # have devices of same name in the same class. If No, then a New command is
    # treated as an Edit command.
    # If Yes, then a New command will always result in a device being added.
    allow_duplicates

    # {YES/TRUE | NO/FALSE}  Default is No. if No, then meter zones are
    # recomputed each time there is a change in the circuit. If Yes, then meter
    # zones are not recomputed unless they have not yet been computed. Meter
    # zones are normally recomputed on Solve command following a circuit
    # change.
    zone_lock

    # Weighting factor for UE/EEN in AutoAdd functions.
    # Autoadd mode minimizes (Lossweight * Losses + UEweight * UE).
    # If you wish to ignore UE, set to 0.
    # This applies only when there are EnergyMeter objects. Otherwise, AutoAdd
    # mode minimizes total system losses.
    ue_weight = 1.0

    # Weighting factor for Losses in AutoAdd functions. Autoadd mode minimizes
    # (Lossweight * Losses + UEweight * UE).
    # If you wish to ignore Losses, set to 0. This applies only when there are
    # EnergyMeter objects. Otherwise, AutoAdd mode minimizes total system
    # losses.
    loss_weight = 1.0

    # Which EnergyMeter register(s) to use for UE in AutoAdd Mode. May be one
    # or more registers.  if more than one, register values are summed
    # together. Array of integer values > 0.  Defaults to 11 (for Load EEN).
    # For a list of EnergyMeter register numbers, do the "Show Meters" command
    # after defining a circuit.
    ue_regs = 11

    # Which EnergyMeter register(s) to use for Losses in AutoAdd Mode. May be
    # one or more registers.  If more than one, register values are summed
    # together. Array of integer values > 0.  Defaults to 13 (for Zone kWh
    # Losses). For a list of EnergyMeter register numbers, do the "Show Meters"
    # command after defining a circuit.
    loss_regs = 13

    # Define legal bus voltage bases for this circuit.  Enter an array
    # of the legal voltage bases, in phase-to-phase voltages, for example:
    # set voltagebases=".208, .480, 12.47, 24.9, 34.5, 115.0, 230.0"
    # When the CalcVoltageBases command is issued, a snapshot solution is
    # performed with no load injections and the bus base voltage is set to the
    # nearest legal voltage base. The defaults are as shown in the example
    # above.
    voltage_bases

    # {Normal | Newton}  Solution algorithm type.  Normal is a fixed point
    # iteration that is a little quicker than the Newton iteration.  Normal is
    # adequate for most radial distribution circuits.  Newton is more robust
    # for circuits that are difficult to solve.
    algorithm = "Normal"

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
    trapezoidal = False

    # Array of bus names to include in AutoAdd searches. Or, you can specify a
    # text file holding the names, one to a line, by using the syntax
    # (file=filename) instead of the actual array elements. Default is null,
    # which results in the program using either the buses in the EnergyMeter
    # object zones or, if no EnergyMeters, all the buses, which can make for
    # lengthy solution times. Examples:
    #    Set autobuslist=(bus1, bus2, bus3, ... )
    #    Set autobuslist=(file=buslist.txt)
    auto_bus_list

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
    control_mode = "Static"

    # Set to YES to trace the actions taken in the control queue. Creates a
    # file named TRACE_CONTROLQUEUE.CSV in the default directory. The names of
    # all circuit elements taking an action are logged.
    trace_mode = False

    # Global multiplier for the kW output of every generator in the circuit.
    # Applies to all but Autoadd solution modes. Ignored for generators
    # designated as Status=Fixed.
    gen_mult = 1.0

    # Default daily load shape name. Default value is "default", which is a
    # 24-hour curve defined when the DSS is started.
    default_daily = "default"

    # Default yearly load shape name. Default value is "default", which is a
    # 24-hour curve defined when the DSS is started.
    default_yearly = "default"

    # Sets all allocation factors for all loads in the active circuit to the
    # value given.
    allocation_factors

    # {Multiphase | Positive}  Default = Multiphase.  Designates whether
    # circuit model is to interpreted as a normal multi-phase model or a
    #positive-sequence only model
    ckt_model = "Multiphase"

    # Sets the price signal ($/MWh) for the circuit.
    price_signal = 25

    # Sets the curve to use to obtain for price signal. Default is none
    # (null string). If none, price signal either remains constant or is set by
    # an external process. Curve is defined as a loadshape (not normalized) and
    # should correspond to the type of analysis being performed (daily, yearly,
    # load-duration, etc.).
    price_curve = None

    # Set the active terminal of the active circuit element. May also be done
    # with select command.
    terminal

    # Set the fundamental frequency for harmonic solution and the default base
    # frequency for all impedance quantities. Side effect: also changes the
    # value of the solution frequency.
    base_frequency = 60

    # Array of harmonics for which to perform a solution in Harmonics mode. If
    # ALL, then solution is performed for all harmonics defined in spectra
    # currently being used. Otherwise, specify a more limited list such as:
    #    set_harmonics=(1, 5, 7, 11, 13,)
    harmonics = "All"

    # Max control iterations per solution.
    max_controller = 10

    # Set Active Bus by name.  Can also be done with Select and SetkVBase
    # commands and the "Set Terminal="  option. The bus connected to the active
    # terminal becomes the active bus. See z_sc and z_sc012 commands.
    bus = ""

    # Set the data path for files written or read by the DSS.  Defaults to the
    # startup path. May be Null.  Executes a CHDIR to this path if non-null.
    # Does not require a circuit defined.
    data_path

    # Array of bus names to keep when performing circuit reductions. You can
    # specify a text file holding the names, one to a line, by using the syntax
    # (file=filename) instead of the actual array elements. Command is
    # cumulative (reset keeplist first). Reduction algorithm may keep other
    # buses automatically. Examples:
    #    Reset Keeplist (sets all buses to FALSE (no keep))
    #    Set KeepList=(bus1, bus2, bus3, ... )
    #    Set KeepList=(file=buslist.txt)
    keep_list

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
    reduce_option

    # Set for keeping demand interval data for daily, yearly, etc, simulations.
    # Side Effect:  Resets all meters!!!
    demand_interval = False

    # Sets the Normal rating of all lines to a specified percent of the
    # emergency rating.  Note: This action takes place immediately. Only the
    # in-memory value is changed for the duration of the run.
    pct_normal

    # Set to Yes/True if you wish a separate demand interval (DI) file written
    # for each meter.  Otherwise, only the totalizing meters are written.
    di_verbose = False

    # Name of case for yearly simulations with demand interval data.
    # Becomes the name of the subdirectory under which all the year data are
    # stored. Default = circuit name. Side Effect: Sets the prefix for output
    # files
    case_name = ""

    # Number code for node marker on circuit plots (SDL MarkAt options).
    marker_code = ""

    # Width of node marker.
    node_width = 1

    # Significant solution events are added to the Event Log, primarily for
    # debugging.
    log = False

    # Opens DSSRecorder.DSS in DSS install folder and enables recording of all
    # commands that come through the text command interface. Closed by either
    # setting to NO/FALSE or exiting the program. When closed by this command,
    # the file name can be found in the Result. Does not require a circuit
    # defined.
    recorder = False

    # For yearly solution mode, sets overload reporting on/off. DemandInterval
    # must be set to true for this to have effect.
    overload_report = False

    # For yearly solution mode, sets voltage exception reporting on/off.
    # DemandInterval must be set to true for this to have effect.
    voltage_exception_report = False

#------------------------------------------------------------------------------
#  "ExecCommand" class:
#------------------------------------------------------------------------------

class ExecCommand:
    """ Defines commands for the executive """

    def new(self):
        """ Create a new object within the DSS. Object becomes the active
        object.

        """

        pass


    def edit(self):
        """ Edit an object. The object is selected and it then becomes the
        active object.

        Note that Edit is the default command.  You many change a property
        value simply by giving the full property name and the new value.

        """

        pass


    def more(self):
        """ Continuation of editing on the active object. """

        pass


    def select(self):
        """ Selects an element and makes it the active element.  You can also
        specify the active terminal (default = 1).

        Syntax:
            Select [element=]elementname  [terminal=]terminalnumber

        Example:
            Select Line.Line1
            ~ R1=.1'+CRLF+'(continue editing)
            Select Line.Line1 2
            Voltages  (returns voltages at terminal 2 in Result)

        """

        pass


    def save(self, klass, dir):
        """ Default class = Meters, which saves the present values in both
        monitors and energy meters in the active circuit.
        "Save Circuit" saves the present enabled circuit elements to the
        specified subdirectory in standard DSS form with a Master.txt file and
        separate files for each class of data. If Dir= not specified a unique
        name based on the circuit name is created automatically.  If dir= is
        specified, any existing files are overwritten.
        "Save Voltages" saves the present solution in a simple CSV format in a
        file called DSS_SavedVoltages.
        Used for VDIFF command.
        Any class can be saved to a file.  If no filename specified, the
        classname is used.

        """

        pass


    def show(self):
        """ Writes selected results to a text file and brings up the editor
        (see Set Editor=....) with the file for you to browse.

        Valid Options (*=default):
            Show Buses
            Show Currents  [[residual=]yes|no*] [Seq* | Elements]
            Show COnvergence  (convergence report)
            Show ELements [Classname] (shows names of all elements in circuit
            or all elements of a class)
            Show Faults (after Fault Study)
            Show Generators
            Show Losses
            Show Meters
            Show Monitor Monitorname
            Show Panel (control panel)
            Show Powers [MVA|kVA*] [Seq* | Elements]
            Show Voltages [LL |LN*]  [Seq* | Nodes | Elements]
            Show Zone  EnergyMeterName [Treeview]
            Show AutoAdded  (see AutoAdd solution mode)
            Show Taps  (regulated transformers)
            Show Overloads (overloaded PD elements)
            Show Unserved [UEonly] (unserved loads)
            Show EVentlog
            Show VAriables
            Show Isolated
            Show Ratings
            Show Loops
            Show Yprim  (shows Yprim for active ckt element)
            Show Y      (shows system Y)
            Show BusFlow busname [MVA|kVA*] [Seq* | Elements]
            Show LineConstants [frequency] [none|mi|km|kft|m|me|ft|in|cm]

        Default is "show voltages LN Seq".

        """

        pass


    def solve(self):
        """ Perform the solution of the present solution mode. You can set any
        option that you can set with the Set command (see Set). The Solve
        command is virtually synonymous with the Set command except that
        a solution is performed after the options are processed.

        """

        pass


    def enable(self):
        """ Enables a circuit element or entire class """

        pass


    def disable(self):
        """ Disables a circuit element or entire class. The item remains
        defined, but is not included in the solution.

        """

        pass


    def plot(self, type, quantity, max, dots, labels, object, show_loops,
             c1, c2, c3, r3=0.85, r2=0.50, channels=[], bases=[], subs=False,
             thinkness=7):
        """ Plots results in a variety of manners.

        Implemented options (in order):

            Type = {Circuit | Monitor | Daisy | Zones | AutoAdd | General}

            Quantity = {Voltage | Current | Power | Losses | Capacity |
            (Value Index for General, AutoAdd, or Circuit[w/ file]) }

            Max = {0 | value corresponding to max scale or line thickness}

            Dots = {Y | N}

            Labels = {Y | N}

            Object = [metername for Zone plot | Monitor name | File Name for
            General bus data or Circuit branch data]

            ShowLoops = {Y | N} (default=N)

            R3 = pu value for tri-color plot max range [.85] (Color C3)

            R2 = pu value for tri-color plot mid range [.50] (Color C2)

            C1, C2, C3 = {RGB color number}

            Channels=(array of channel numbers for monitor plot)

            Bases=(array of base values for each channel for monitor plot).
            Default is 1.0 for each.  Set Base= after defining channels.

            Subs={Y | N} (default=N) (show substations)

            Thickness=max thickness allowed for lines in circuit plots
            (default=7)

        """

        pass


    def reset(self):
        """ {MOnitors | MEters | Faults | Controls | Eventlog | Keeplist |
        (no argument) }

        Resets all Monitors, Energymeters, etc.

        If no argument specified, resets all options listed.

        """

        pass


    def compile(self):
        """ Reads the designated file name containing DSS commands and
        processes them as if they were entered directly into the command line.
        The file is said to be "compiled."

        Similar to "redirect" except changes the default directory to the path
        of the specified file.

        Syntax:
            Compile filename

        """

        pass


    def set_value(self):
        """ Used to set various DSS solution modes and options.  You may also
        set the options with the Solve command.

        See "Options" for help.

        """


        pass


    def dump(self):
        """ Display the properties of either a specific DSS object or a
        complete dump on all variables in the problem (Warning! Could be very
        large!).

        Brings up the default text editor with the text file written by this
        command.

        Syntax: dump [class.obj] [debug]

        Examples:
            Dump line.line1
            Dump solution  (dumps all solution vars)
            Dump commands  (dumps all commands to a text file)
            Dump transformer.*  (dumps all transformers)
            Dump ALLOCationfactors  (load allocation factors)
            Dump (dumps all objects in circuit)

        """

        pass


    def open(self):
        """ Opens the specified terminal and conductor of the specified circuit
        element. If the conductor is not specified, all phase conductors of the
        terminal are opened.

        Examples:
            Open line.line1 2 (opens all phases of terminal 2)
            Open line.line1 2 3 (opens the 3rd conductor of terminal 2)

        """

        pass


    def close(self):
        """ Opposite of the Open command """

        pass


    def redirect(self):
        """ Reads the designated file name containing DSS commands and
        processes them as if they were entered directly into the command line.
        Similar to "Compile", but leaves current directory where it was when
        Redirect command is invoked. Can temporarily change to subdirectories
        if nested Redirect commands require.

        """

        pass


    def help(self):
        """ Handles display of help """

        pass


    def quit(self):
        """ Handles closing the application """

        pass


    def what(self):
        """ Inquiry for property value.  Result is put into GlobalReault and
        can be seen in the Result Window. Specify the full property name.

        Example: ? Line.Line1.R1

        Note you can set this property merely by saying:
            Line.line1.r1=.058

        """

        pass


    def next(self):
        """ {Year | Hour | t}  Increments year, hour, or time as specified.  If
        "t" is specified, then increments time by current step size.

        """

        pass


    def panel(self):
        """ Displays main control panel window. """

        pass


    def sample(self):
        """ Force all monitors and meters to take a sample now """

        pass


    def clear(self):
        """ Clear all circuits currently in memory """

        pass


    def about(self):
        """ Handles display of the 'About' dialog box """

        pass


    def calc_voltage_bases(self):
        """ Calculates voltagebase for buses based on voltage bases defined
        with Set voltagebases=... command.

        """

        pass


    def set_kv_base(self):
        """ Command to explicitly set the base voltage for a bus.

        Bus must be previously defined. Parameters in order are:

            Bus = {bus name}
            kVLL = (line-to-line base kV)
            kVLN = (line-to-neutral base kV)

        kV base is normally given in line-to-line kV (phase-phase). However,
        it may also be specified by line-to-neutral kV.

        The following exampes are equivalent:

            setkvbase Bus=B9654 kVLL=13.2
            setkvbase B9654 13.2
            setkvbase B9654 kvln=7.62

        """

        pass


    def build_y(self):
        """ Forces rebuild of Y matrix upon next Solve command regardless of
        need. The usual reason for doing this would be to reset the matrix for
        another load level when using LoadModel=PowerFlow (the default) when
        the system is difficult to solve when the load is far from its base
        value.  Works by invalidating the Y primitive matrices for all the
        Power Conversion elements.

        """

        pass


    def get_value(self):
        """ Returns DSS property values set using the Set command. Result is
        return in Result property of the Text interface.

        VBA Example:
            DSSText.Command = "Get mode"
            Answer = DSSText.Result
            Multiple properties may be requested on one get.  The results are
            appended and the individual values separated by commas.

        See help on set_value() command for property names.

        """

        pass


    def initialise(self):
        """ This command forces reinitialization of the solution for the next
        Solve command. To minimize iterations, most solutions start with the
        previous solution unless there has been a circuit change.  However, if
        the previous solution is bad, it may be necessary to re-initialize. In
        most cases, a re-initiallization results in a zero-load power flow
        solution with only the series power delivery elements considered.

        """

        pass


    def export(self):
        """ Export various solution values to CSV files for import into other
        programs.

        Creates a new CSV file except for Energymeter and Generator objects,
        for which the results for each device of this class are APPENDED to the
        CSV File. You may export to a specific file by specifying the file name
        as the LAST parameter on the line. Otherwise, the default file names
        shown below are used. For Energymeter and Generator, specifying the
        switch "/multiple" (or /m) for the file name will cause a separate file
        to be written for each meter or generator. The default is for a single
        file containing all elements.

        Syntax for Implemented Exports:

            Export Voltages  [Filename]   (EXP_VOLTAGES.CSV)
            Export SeqVoltages [Filename] (EXP_SEQVOLTAGES.CSV)
            Export Currents [Filename]    (EXP_CURRENTS.CSV)
            Export Overloads [Filename]    EXP_OVERLOADS.CSV)
            Export Unserved  [UEonly] [Filename]   EXP_UNSERVED.CSV)
            Export SeqCurrents [Filename] (EXP_SEQCURRENTS.CSV)
            Export Powers [MVA] [Filename](EXP_POWERS.CSV)
            Export Faultstudy [Filename]  (EXP_FAULTS.CSV)
            Export Generators [Filename | /m ]  (EXP_GENMETERS.CSV)
            Export Loads [Filename]       (EXP_LOADS.CSV)
            Export Meters [Filename |/m ] (EXP_METERS.CSV)
            Export Monitors monitorname   (file name is assigned)
            Export Yprims  [Filename]     (EXP_Yprims.CSV) (all YPrim matrices)
            Export Y  [Filename]          (EXP_Y.CSV)   (system Y matrix)

        May be abreviated Export V, Export C, etc.  Default is "V".

        """

        pass


    def file_edit(self):
        """ Edit specified file in default text file editor (see set_editor=
        option). Fileedit EXP_METERS.CSV (brings up the meters export file)
        "FileEdit" may be abbreviated to a unique character string.

        """

        pass


    def voltages(self):
        """ Returns the voltages for the ACTIVE BUS in the Result string.
        For setting the active Bus, use the Select command or the
        set_bus= option.

        Returned as magnitude and angle quantities, comma separated, one set
        per conductor of the terminal.

        """

        pass


    def currents(self):
        """ Returns the currents for each conductor of ALL terminals of the
        active circuit element in the Result string/ (See select command.)
        Returned as comma-separated magnitude and angle.

        """

        pass


    def powers(self):
        """ Returns the powers (complex) going into each conductors of ALL
        terminals of the active circuit element in the Result string.
        (See select command.)

        Returned as comma-separated kW and kvar.

        """

        pass


    def seq_voltages(self):
        """ Returns the sequence voltages at all terminals of the active
        circuit element (see Select command) in Result string.  Returned as
        comma-separated magnitude only values.

        Order of returned values: 0, 1, 2  (for each terminal).

        """

        pass


    def seq_currents(self):
        """ Returns the sequence currents into all terminals of the active
        circuit element (see Select command) in Result string.  Returned as
        comma-separated magnitude only values.

        Order of returned values: 0, 1, 2  (for each terminal).

        """

        pass


    def seq_power(self):
        """ Returns the sequence powers into all terminals of the active
        circuit element (see Select command) in Result string.  Returned as
        comma-separated kw, kvar pairs.

        Order of returned values: 0, 1, 2  (for each terminal).

        """

        pass


    def losses(self):
        """ Returns the total losses for the active circuit element in the
        Result string in kW, kvar.

        """

        pass


    def phase_losses(self):
        """ Returns the losses for the active circuit element for each PHASE in
        the Result string in comma-separated kW, kvar pairs.

        """

        pass


    def ckt_losses(self):
        """ Returns the total losses for the active circuit in the Result
        string in kW, kvar.

        """

        pass


    def allocate_loads(self):
        """ Estimates the allocation factors for loads that are defined using
        the XFKVA property. Requires that energymeter objects be defined with
        the PEAKCURRENT property set. Loads that are not in the zone of an
        energymeter cannot be allocated.

        """

        pass


    def form_edit(self):
        """ FormEdit [class.object].  Brings up form editor on active DSS
        object.

        """

        pass


    def totals(self):
        """ Totals all EnergyMeter objects in the circuit and reports register
        totals in the result string.

        """

        pass


    def capacity(self):
        """ Find the maximum load the active circuit can serve in the PRESENT
        YEAR. Uses the EnergyMeter objects with the registers set with the
        SET UEREGS= (..) command for the AutoAdd functions.

        Syntax (defaults shown):
            capacity [start=]0.9 [increment=]0.005

        Returns the metered kW (load + losses - generation) and per unit load
        multiplier for the loading level at which something in the system
        reports an overload or undervoltage. If no violations, then it returns
        the metered kW for peak load for the year (1.0 multiplier). Aborts and
        returns 0 if no energymeters.

        """

        pass


    def classes(self):
        """ List of intrinsic DSS Classes. Returns comma-separated list in
        Result variable.

        """

        pass


    def user_classes(self):
        """ List of user-defined DSS Classes. Returns comma-separated list in
        Result variable.

        """

        pass


    def z_sc(self):
        """ Returns full Zsc matrix for the ACTIVE BUS in comma-separated
        complex number form.

        """

        pass


    def z_sc10(self):
        """ Returns symmetrical component impedances, Z1, Z0 for the ACTIVE BUS
        in comma-separated R+jX form.

        """

        pass


    def z_sc_refresh(self):
        """ Refreshes Zsc matrix for the ACTIVE BUS. """

        pass


    def y_sc(self):
        """ Returns full Ysc matrix for the ACTIVE BUS in comma-separated
        complex number form G + jB.

        """

        pass


    def pu_voltages(self):
        """ Just like the Voltages command, except the voltages are in per unit
        if the kVbase at the bus is defined.

        """

        pass


    def var_values(self):
        """ Returns variable values for active element if PC element.
        Otherwise, returns null.

        """

        pass


    def var_names(self):
        """ Returns variable names for active element if PC element. Otherwise,
        returns null.

        """

        pass


    def bus_coords(self):
        """ Define x,y coordinates for buses.  Execute after Solve command
        performed so that bus lists are defined. Reads coordinates from a CSV
        file with records of the form: busname, x, y.

        Example: BusCoords [file=]xxxx.csv

        """

        pass


    def make_bus_list(self):
        """ Updates the buslist using the currently enabled circuit elements.
        (This happens automatically for Solve command.)

        """

        pass


    def make_pos_sequence(self):
        """ Attempts to convert present circuit model to a positive sequence
        equivalent. It is recommended to Save the circuit after this and edit
        the saved version to correct possible misinterpretations.

        """

        pass


    def reduce(self):
        """ {All | MeterName}  Default is "All".  Reduce the circuit according
        to reduction options. See "Set ReduceOptions" and "Set Keeplist"
        options.

        Energymeter objects actually perform the reduction.  "All" causes all
        meters to reduce their zones.

        """

        pass


    def interpolate(self):
        """ {All | MeterName}  Default is "All". Interpolates coordinates for
        missing bus coordinates in meter zone'

        """

        pass


    def align_file(self):
        """ Alignfile [file=]filename.  Aligns DSS script files in columns for
        easier reading.

        """

        pass


    def top(self):
        """ [class=]{Loadshape | Monitor  } [object=]{ALL (Loadshapes only) |
        objectname}.

        Send specified object to TOP.  Loadshapes must be hourly fixed
        interval.

        """

        pass


    def rotate(self):
        """ Rotate circuit plotting coordinates by specified angle """

        pass


    def v_diff(self):
        """ Displays the difference between the present solution and the last
        on saved using the SAVE VOLTAGES command.

        """

        pass


    def summary(self):
        """ Displays a power flow summary of the most recent solution. """

        pass


    def distribute(self):
        """ {Proportional | Uniform |Random | Skip} skip=nn PF=nn file=filename
        MW=nn

        Distributes generators on the system in the manner specified by "how".

            kW = total generation to be distributed (default=1000)
            how= process name as indicated (default=proportional to load)
            skip = no. of buses to skip for "How=Skip" (default=1)
            PF = power factor for new generators (default=1.0)
            file = name of file to save (default=distgenerators.txt)
            MW = alternate way to specify kW (default = 1)

        """

        pass


    def di_plot(self):
        """ [case=]casename [year=]yr [registers=](reg1, reg2,...)  [peak=]y/n
        [meter=]metername

        Plots demand interval (DI) results from yearly simulation cases.
        Plots selected registers from selected meter file (default =
        DI_Totals.CSV).
        Peak defaults to NO.  If YES, only daily peak of specified registers
        is plotted. Example:

        DI_Plot basecase year=5 registers=(9,11) no

        """

        pass


    def compare_cases(self):
        """ [Case1=]casename [case2=]casename [register=](register number)
        [meter=]{Totals* | SystemMeter | metername}.

        Compares yearly simulations of two specified cases with respect to the
        quantity in the designated register from the designated meter file.

        Defaults:
            Register=9 meter=Totals.

        Example:
            Comparecases base pvgens 10

        """

        pass


    def yearly_curves(self):
        """ [cases=](case1, case2, ...) [registers=](reg1, reg2, ...)
        [meter=]{Totals* | SystemMeter | metername}

        Plots yearly curves for specified cases and registers.

        Default: meter=Totals.
        Example: yearlycurves cases=(basecase, pvgens) registers=9

        """

        pass


    def cd(self):
        """ Change default directory to specified directory """

        pass


    def visualise(self):
        """ [What=] {Currents* | Voltages | Powers} [element=]full_element_name
        (class.name). Shows the currents for selected element on a drawing in
        polar coordinates.

        """

        pass


    def close_di(self):
        """ Close all DI files ... useful at end of yearly solution where DI
        files are left open.

        (Reset and Set Year=nnn will also close the DI files)

        """

        pass


    def estimate(self):
        """ Execute state estimator on present circuit given present sensor
        values.

        """

        pass

#------------------------------------------------------------------------------
#  "Circuit" class:
#------------------------------------------------------------------------------

class Circuit:
    """ Defines a container of circuit elements """

    case_name = ""

    active_bus_idx = 1

    # Fundamental and default base frequency
    fundamental = 60.0

    auto_add_buses = []

    devices = []

    faults = []

    ckt_elements = []

    pde_elements = []

    pce_elements = []

    dss_controls = []

    sources = []

    meter_elements = []

    generators = []

    # Not yet used
    substations = []

    transformers = []

    cap_controls = []

    reg_controls = []

    lines = []

    loads = []

    shunt_capacitors = []

    feeders = []

    control_queue = []

    solution = None

    auto_add_obj = None

    # AutoAdd -----------------------------------------------------------------

    ue_weight = 1.0

    loss_weight = 1.0

    ue_regs = [10]

    n_ue_regs = 0

    loss_regs = [13]

    n_loss_regs = 0

    capacity_start = 0.9

    capacity_increment = 0.005

    # Default to Euler method
    trapezoidal_integration = False

    log_events = True

    load_dur_curve = ""

    load_dur_curve_obj = None

    price_curve = ""

    price_curve_obj = None

    n_devices = property

    n_buses = property

    n_nodes = property

    max_devices = 1000

    max_buses = 1000

    max_nodes = 3000

    inc_devices = 1000

    inc_buses = 1000

    inc_nodes = 3000

    # Bus and Node ------------------------------------------------------------

    buses = []

    node_bus_map = {}

    # Flags -------------------------------------------------------------------

    is_solved = False

    allow_duplicates = False

    # Meter zones recomputed after each change
    zones_locked = False

    meter_zones_computed = False

    # Model is to be interpreted as Pos seq
    positive_sequence = False

    # Voltage limits ----------------------------------------------------------

    normal_min_volts = 0.95

    normal_max_volts = 1.05

    # per unit voltage restraints for this circuit
    emerg_min_volts = 0.90

    emerg_max_volts = 1.08

    legal_voltage_bases = [0.208, 0.480, 12.47, 24.9, 35.4, 115.0, 230.0]

    # Global circuit multipliers ----------------------------------------------

    generator_dispatch_ref = 0.0

    default_growth_rate = 1.025

    default_growth_factor = 1.0

    # global multiplier for every generator
    gen_multiplier = 1.0

    harm_mult = 1.0

    default_hour_mult

    # price signal for entire circuit
    price_signal = 25.0

    # Energy meter totals -----------------------------------------------------

    register_totals = []

    default_daily_shape_obj = None

    default_yearly_shape_obj = None

    current_directory = ""

    reduction_strategy = None

    reduction_max_angle = 15.0

    reduction_z_mag = 0.02

    reduction_strategy_string = ""

    pct_normal_factor



#------------------------------------------------------------------------------
#  "LineCode" class:
#------------------------------------------------------------------------------

class LineCode:
    """ The Linecode object is a general DSS object used by all circuits
    as a reference for obtaining line impedances.

    Linecodes are objects that contain impedance characteristics for lines and
    cables.  The term "line code" is an old term that simply refers to a code
    that was made up by programmers to describe a line construction.  In most
    distribution analysis programs, one can describe a line by its linecode
    and its length.  Linecodes were defined in a separate file.  This
    collection of objects emulates the old linecode files, except that the
    concept is slightly more powerful.

    Ultimately, the impedance of a line is described by its series impedance
    matrix and nodal capacitive admittance matrix.  These matrices may be
    specified directly or they can be generated by specifying the symmetrical
    component data.  Note that the impedances of lines may be specified
    directly and one does not need to use a line code, although the linecode
    will be more convenient most of the time.  There may be hundreds of lines,
    but only a few different kinds of line constructions.

    LineCode also performs a Kron reduction, reducing out the last conductor
    in the impedance matrices, which is assumed to be a neutral conductor.
    This applies only if the impedance is specified as a matrix. If the
    impedance is defined as symmetrical components, this function does not
    apply because symmetrical component values already assume the reduction.

    By specifying the values of Rg, Xg, and rho, the DSS will take the base
    frequency impedance matrix values and adjust the earth return component
    for frequency. Skin effect in the conductors is not modified. To represent
    skin effect, you have to define the geometry.

    This assumes the impedance matrix is constructed as follows:

                 Z_{11} + Z_{g} Z_{12} + Z_{g} Z_{13} + Z_{g}

    Z = R + jX = Z_{21} + Z_{g} Z_{22} + Z_{g} Z_{23} + Z_{g}

                 Z_{31} + Z_{g} Z_{32} + Z_{g} Z_{33} + Z_{g}

    """

    # Number of phases in the line this line code data represents.  Setting
    # this property reinitializes the line code.  Impedance matrix is reset
    # for default symmetrical component.
    n_phases = 3

    # Positive-sequence Resistance, ohms per unit length.  See also r_matrix.
    r1 = 0.058

    # Positive-sequence Reactance, ohms per unit length.  See also x_matrix.
    x1 = 0.1206

    # Zero-sequence Resistance, ohms per unit length.
    r0 = 0.1784

    # Zero-sequence Reactance, ohms per unit length.
    x0 = 0.4047

    # Positive-sequence capacitance, nF per unit length. See also c_matrix.
    c1 = 3.4

    # Zero-sequence capacitance, nF per unit length.
    c0 = 1.6

    # One of (ohms per ...) {none|mi|km|kft|m|me|ft|in|cm}.  Default is none;
    # assumes units agree with length units given in Line object.
    units = None


    # Resistance matrix, lower triangle, ohms per unit length. Order of the
    # matrix is the number of phases.  May be used to specify the impedance of
    # any line configuration.  For balanced line models, you may use the
    # standard symmetrical component data definition instead.
    r_matrix = ""

    # Reactance matrix, lower triangle, ohms per unit length. Order of the
    # matrix is the number of phases.  May be used to specify the impedance of
    # any line configuration.  For balanced line models, you may use the
    # standard symmetrical component data definition instead.
    x_matrix = ""

    # Nodal Capacitance matrix, lower triangle, nf per unit length.Order of the
    # matrix is the number of phases.  May be used to specify the shunt
    # capacitance of any line configuration.  For balanced line models, you may
    # use the standard symmetrical component data definition instead.
    c_matrix = ""

    # Frequency (Hz) at which impedances are specified.
    base_freq = 60

    # Normal ampere limit on line.  This is the so-called Planning Limit. It
    # may also be the value above which load will have to be dropped in a
    # contingency.  Usually about 75% - 80% of the emergency (one-hour) rating.
    norm_amps = 400

    # Emergency ampere limit on line (usually one-hour rating).
    emerg_amps = 600

    # Number of faults per unit length per year.
    fault_rate = 0.1

    # Percentage of the faults that become permanent (requiring a line crew to
    # repair and a sustained interruption).
    pct_perm = 20

    # Hours to repair.
    repair = 3

    # Kron = Y/N. Default=N.  Perform Kron reduction on the impedance matrix
    # after it is formed, reducing order by 1.  Do this only on initial
    # definition after matrices are defined. Ignored for symmetrical
    # components.
    kron = "N"

    # Carson earth return resistance per unit length used to compute impedance
    # values at base frequency.  For making better frequency adjustments.
    rg = 0

    # Carson earth return reactance per unit length used to compute impedance
    # values at base frequency.  For making better frequency adjustments.
    xg = 0

    # Earth resitivity (meter ohmsused to compute earth correction factor.
    rho = 100

#------------------------------------------------------------------------------
#  "WireData" class:
#------------------------------------------------------------------------------

class WireData:
    """ The WireData object is a general DSS object used by all circuits
    as a reference for obtaining line impedances.

    This class of data defines the raw conductor data that is used to compute
    the impedance for a line geometry.

    Note that you can use whatever units you want for any of the dimensional
    data - be sure to declare the units. Otherwise, the units are all assumed
    to match, which would be very rare for conductor data.  Conductor data is
    usually supplied in a hodge-podge of units. Everything is converted to
    meters internally to the DSS.

    """

    # DC resistance, ohms per unit length (see r_units). Defaults to r_ac if
    # not specified.
    r_dc = -1

    # Resistance at 60 Hz per unit length. Defaults to r_dc if not specified.
    r_ac = -1

    # Length units for resistance: ohms per {mi|kft|km|m|Ft|in|cm}
    r_units = None

    # GMR at 60 Hz. Defaults to .7788*radius if not specified.
    gmr_ac = -1

    # Units for GMR: {mi|kft|km|m|Ft|in|cm}
    gmr_units = None

    # Outside radius of conductor. Defaults to GMR/0.7788 if not specified.
    radius = -1

    # Units for outside radius: {mi|kft|km|m|Ft|in|cm}
    rad_units = None

    # Normal ampacity, amperes. Defaults to Emergency amps/1.5 if not
    # specified.
    norm_amps = -1

    # Emergency ampacity, amperes. Defaults to 1.5 * Normal Amps if not
    # specified.
    emer_gamps = -1

    # Diameter; Alternative method for entering radius.
    diam = -1

#------------------------------------------------------------------------------
#  "LineGeometry" class:
#------------------------------------------------------------------------------

class LineGeometry:
    """ The LineGeometry object is a general DSS object used by all circuits
    as a reference for obtaining line impedances.

    Defines the positions of the conductors.

    """

    # Number of conductors in this geometry.
    n_conds = 3

    # Number of phases.  All other conductors are considered neutrals and might
    # be reduced out.
    n_phases = 3

    # Set this = number of the conductor you wish to define.
    cond = 1

    # Code from WireData. MUST BE PREVIOUSLY DEFINED. no default.
    wire = ""

    # x coordinate.
    x = 0

    # Height of conductor.
    h = 32

    # Units for x and h: {mi|kft|km|m|Ft|in|cm } Initial default is "ft", but
    # defaults to last unit defined
    units = "ft"

    # Normal ampacity, amperes for the line. Defaults to first conductor if not
    # specified.
    norm_amps = 0

    # Emergency ampacity, amperes. Defaults to first conductor if not
    # specified.
    emerg_amps = 0

    # {Yes | No} Default = no. Reduce to n_phases (Kron Reduction). Reduce out
    # neutrals.
    reduce = "No"

#------------------------------------------------------------------------------
#  "LoadShape" class:
#------------------------------------------------------------------------------

class LoadShape:
    """ The LoadShape object is a general DSS object used by all circuits
    as a reference for obtaining yearly, daily, and other load shapes.

    Loadshapes default to fixed interval data.  If the Interval is specified to
    be 0.0, then both time and multiplier data are expected.  If the Interval
    is  greater than 0.0, the user specifies only the multipliers.  The Hour
    command is ignored and the files are assumed to contain only the multiplier
    data.

    The user may place the data in CSV or binary files as well as passing
    through the command interface. Obviously, for large amounts of data such as
    8760 load curves, the command interface is cumbersome.  CSV files are text
    separated by commas, one interval to a line. There are two binary formats
    permitted: 1) a file of Singles; 2) a file of Doubles.

    For fixed interval data, only the multiplier is expected.  Therefore, the
    CSV format would contain only one number per line.  The two binary formats
    are packed.

    For variable interval data, (hour, multiplier) pairs are expected in both
    formats.

    The Mean and Std Deviation are automatically computed when a new series of
    points is entered.

    The data may also be entered in unnormalized form.  The normalize=Yes
    command will force normalization.  That is, the multipliers are scaled so
    that the maximum value is 1.0.


    A LoadShape object consists of a series of multipliers, nominally ranging
    from 0.0 to 1.0 that are applied to the base kW values of the load to
    represent variation of the load over some time period.

    Load shapes are generally fixed interval, but may also be variable
    interval.  For the latter, both the time, hr, and the multiplier must be
    specified.

    All loadshapes, whether they be daily, yearly, or some arbitrary duty
    cycle, are maintained in this class.  Each load simply refers to the
    appropriate shape by name.

    The loadshape arrays may be entered directly in command line, or the load
    shapes may be stored in one of three different types of files from which
    the shapes are loaded into memory.

    """

    # Max number of points to expect in load shape vectors. This gets reset to
    # the number of multiplier values found (in files only) if less than
    # specified.
    n_pts = 0

    # Time interval (hrs) for fixed interval data.  If set = 0 then time data
    # (in hours) is expected using either the Hour property or input files.
    interval = 1

    # Array of multiplier values for active power (P).  Can also use the
    # syntax: mult = (file=filename) where the file contains one value per
    # line. In "file=" syntax, the number of points may be altered.
    mult = ""

    # Array of hour values. Only necessary to define for variable interval
    # data.  If the data are fixed interval, do not use this property.  Can
    # also use the syntax: mult = (file=filename) where the file contains one
    # value per line.
    hour = ""

    # Mean of the active power multipliers.  Automatically computed when a
    # curve is defined.  However, you may set it independently.  Used for Monte
    # Carlo load simulations.
    #
    # The mean and standard deviation are always computed after an array of
    # points are entered or normalized (see below).  However, if you are doing
    # only parametric load studies using the Monte Carlo solution mode, only
    # the Mean and Std Deviation are required to define a loadshape.  These two
    # values may be defined directly rather than by supplying the curve.  Of
    # course, the multiplier points are not generated.
    mean = 0

    # Standard deviation of active power multipliers.  This is automatically
    # computed when a vector or file of multipliers is entered.  However, you
    # may set it to another value indepently.  Is overwritten if you
    # subsequently read in a curve.  Used for Monte Carlo load simulations.
    std_dev = 0

    # The next three parameters instruct the LoadShape object to get its data
    # from a file.  Three different formats are allowed. If Interval>0 then
    # only the multiplier is entered.  For variable interval data, set
    # Interval=0.0 and enter both the time (in hours) and multiplier, in that
    # order for each interval.

    # Switch input of active power load curve data to a csv file containing
    # (hour, mult) points, or simply (mult) values for fixed time interval
    # data, one per line.
    #
    # NOTE: This action may reset the number of points to a lower value.
    csv_file = ""

    # Switch input of active power load curve data to a binary file of singles
    # containing (hour, mult) points, or simply (mult) values for fixed time
    # interval data, packed one after another.
    #
    # NOTE: This action may reset the number of points to a lower value.
    sng_file = ""

    # Switch input of active power load curve data to a binary file of doubles
    # containing (hour, mult) points, or simply (mult) values for fixed time
    # interval data, packed one after another.
    #
    # NOTE: This action may reset the number of points to a lower value.
    dbl_file = ""

    # NORMALIZE is only defined action. After defining load curve data, setting
    # action=normalize will modify the multipliers so that the peak is 1.0.
    # The mean and std deviation are recomputed.
    #
    # Many times the raw load shape data is in actual kW or some other unit.
    # The load shapes normally will have a maximum value of 1.0.  Specifying
    # this parameter as "Action=N" after the load shape multiplier data are
    # imported will force the normalization of the data in memory and
    # recalculation of the mean and standard deviation.
    action = "normalise"

    # Array of multiplier values for reactive power (Q).  Can also use the
    # syntax: qmult = (file=filename) where the file contains one value per
    # line.
    q_mult = ""

#------------------------------------------------------------------------------
#  "GrowthShape" class:
#------------------------------------------------------------------------------

class GrowthShape:
    """ The GrowthShape object is a general DSS object used by all circuits
    as a reference for obtaining yearly growth curves.

    A GrowthShape object is similar to a Loadshape object.  However, it is
    intended to represent the growth in load year-by-year and the way the curve
    is specified is entirely different.  You must enter the growth for the
    first year.  Thereafter, only the years where there is a change must be
    entered.  Otherwise it is assumed the growth stays the same.

    Growth shapes are entered as multipliers for the previous year's load.  If
    the load grows by 2.5% in a year, the multiplier is entered as 1.025.  You
    do not need to enter subsequent years if the multiplier remains the same.
    You need only enter the years in which the growth rate is assumed to have
    changed.

    The user may place the data in CSV or binary files as well as passing
    through the command interface. The rules are the same as for LoadShapes
    except that the year is always entered.  CSV files are text separated by
    commas, one interval to a line. There are two binary formats permitted:
    1) a file of Singles; 2) a file of Doubles.

    """

    # Number of points to expect in subsequent vector.
    n_pts = 0

    # Array of year values, or a text file spec, corresponding to the
    # multipliers.  Enter only those years where the growth changes.  May be
    # any integer sequence -- just so it is consistent. See help on mult.
    # Setting the global solution variable Year=0 causes the growth factor to
    # default to 1.0, effectively neglecting growth.  This is what you would do
    # for all base year analyses.  You may also use the syntax:
    # year=(file=filename.ext) in which the array values are entered one per
    # line in the text file referenced.
    year = ""

    # Array of growth multiplier values, or a text file spec, corresponding to
    # the year values.  Enter the multiplier by which you would multiply the
    # previous year''s load to get the present year''s.  Examples:
    #    Year = "1, 2, 5"   Mult="1.05, 1.025, 1.02".
    #    Year= (File=years.txt) Mult= (file=mults.txt).
    # Text files contain one value per line.
    #
    # Normally, only a few points need be entered and the above parameters will
    # be quite sufficient.  However, provision has been made to enter the
    # (year, multiplier) points from files just like the LoadShape objects.
    # You may also use the syntax: mult=(file=filename.ext) in which the array
    # values are entered one per line in the text file referenced.
    mult = ""

    # Switch input of growth curve data to a csv file containing (year, mult)
    # points, one per line.
    csv_file = ""

    # Switch input of growth curve data to a binary file of singles containing
    # (year, mult) points, packed one after another.
    sng_file = ""

    # Switch input of growth curve data to a binary file of doubles containing
    # (year, mult) points, packed one after another.
    dbl_file = ""

#------------------------------------------------------------------------------
#  "TimeCurrentCurve" class:
#------------------------------------------------------------------------------

class TimeCurrentCurve:
    """ Nominally, a time-current curve, but also used for volt-time curves.

    Collections of time points.  Return values can be interpolated either
    Log-Log as traditional TCC or as over- or under-voltage definite time.

    A TCC_Curve object is defined similarly to Loadshape and Growthshape
    objects in that they all are defined by curves consisting of arrays of
    points.  Intended to model time-current characteristics for overcurrent
    relays, TCC_Curve objects are also used for other relay types requiring
    time curves.  Both the time array and the C array must be entered.

    """

    # Number of points to expect in time-current arrays.
    n_pts = 0

    # Array of current (or voltage) values corresponding to time values.
    c_array = ""

    # Array of time values in sec. Typical array syntax:
    #     t_array = (1, 2, 3, 4, ...)
    # Can also substitute a file designation:
    #     t_array =  (file=filename)
    # The specified file has one value per line.
    t_array = ""

#------------------------------------------------------------------------------
#  Circuit Elements:
#------------------------------------------------------------------------------

""" The following DSS objects are circuit elements.  The DSS contains
collections of each class that are treated as libraries of objects of each
class.  However, individual dircuit element objects are owned by a Circuit
object.

"""

#------------------------------------------------------------------------------
#  "VSource" class:
#------------------------------------------------------------------------------

class VSource:
    """ This is a special power conversion element.  It is special because
    voltage sources must be identified to initialize the solution with all
    other injection sources set to zero.

    A Vsource object is simply a multi-phase Thevenin equivalent with data
    specified as it would commonly be for a power system source equivalent:
    Line-line voltage (kV) and short circuit MVA.

    """

    # Name of bus to which the source's one terminal is connected.  Remember
    # to specify the node order if the terminals are connected in some unusual
    # manner.
    bus_1 = None

    # Base Source kV, usually L-L unless you are making a positive-sequence
    # model in which case, it will be L-N.
    base_kv = 115

    # Per unit of the base voltage that the source is actually operating at.
    # Assumed balanced for all phases.
    pu = 1

    # Phase angle in degrees of first phase.
    angle = 0

    # Source frequency.
    frequency = 60

    # Number of phases.
    phases = 3

    # MVA Short circuit, 3-phase fault.  Z1 is determined by squaring the base
    # kv and dividing by this value.  For single-phase source, this value is
    # not used.
    mva_sc3 = 2000

    # MVA Short Circuit, 1-phase fault.  The "single-phase impedance", Zs, is
    # determined by squaring the base kV and dividing by this value.  Then Z0
    # is determined by Z0 = 3Zs - 2Z1.  For 1-phase sources, Zs is used
    # directly. Use x0_r0 to define X/R ratio for 1-phase source.
    mva_sc1 = 2100

    # Positive-sequence X/R ratio.
    x1_r1 = 4

    # Zero-sequence X/R ratio.
    x0_r0 = 3

    # Alternate method of defining the source impedance. 3-phase short circuit
    # current, amps.
    i_sc3 = 10000

    # Alternate method of defining the source impedance. Single-phase short
    # circuit current, amps.
    i_sc1 = 10500

    # Alternate method of defining the source impedance. Positive-sequence
    # resistance, ohms.
    r1 = 1.65

    # Alternate method of defining the source impedance. Positive-sequence
    # reactance, ohms.
    x1 = 6.6

    # Alternate method of defining the source impedance. Zero-sequence
    # resistance, ohms.
    r0 = 1.9

    # Alternate method of defining the source impedance. Zero-sequence
    # reactance, ohms.
    x0 = 5.7

    # Base Frequency for impedance specifications.
    base_freq = 60

    # {pos*| zero | none} Maintain specified sequence for harmonic solution.
    # Default is positive sequence. Otherwise, angle between phases rotates
    # with harmonic.
    scan_type = "Pos"

#------------------------------------------------------------------------------
#  "Line" class:
#------------------------------------------------------------------------------

class Line:
    """ Line impedances are specified in per unit length and are multiplied by
    the length when the primitive Y matrix is computed.

    You may specify the impedances of the line either by symmetrical components
    or by R, X, and nodal C matrices  (also per unit length).

    All C's is entered in nano farads.

    The ultimate values are in the matrices.  If you specify matrices, then the
    symmetrical component values are ignored.  However, if you change any of
    the symmetrical component values the matrices will be recomputed.  It is
    assumed you want to use symmetrical component values.  Don't mix data entry
    by matrix and by symmetrical components.

    Note that if you change the number of phases, the matrices are reallocated
    and reinitialized with whatever is currently in the symmetrical component
    data.


    Multi-phase, two-port line or cable.  Pi model.  Power delivery element
    described by its impedance.  Impedances may be specified by symmetrical
    component values or by matrix values.  Alternatively, you may simply refer
    to an existing LineCode object from which the impedance values will be
    copied.  Then you need only specify the length.

    You can define the line impedance at a base frequency directly in a Line
    object definition or you can import the impedance definition from a
    LineCode object. Both of these definitions of impedance are quite similar
    except that the LineCode object can perform Kron reduction.

    If the geometry property is specified all previous definitions are ignored.
    The DSS will compute the impedance matrices from the specified geometry
    each time the frequency changes.

    Whichever definition is the most recent applies, as with nearly all DSS
    functions.

    Note the units property; you can declare any length measurement in whatever
    units you please.  Internally, everything is converted to meters. Just be
    sure to declare the units. Otherwise, they are assumed to be compatible
    with other data or irrelevant.

    """

    # Name of bus for terminal 1. Node order definitions optional.
    bus_1 = None

    # Name of bus for terminal 2.
    bus_2 = None

    # Name of linecode object describing line impedances.
    # If you use a line code, you do not need to specify the impedances here.
    # The line code must have been PREVIOUSLY defined.  The values specified
    # last will prevail over those specified earlier (left-to-right sequence
    # of properties).  If no line code or impedance data are specified, line
    # object defaults to 336 MCM ACSR on 4 ft spacing.
    line_code = ""

    # Length of line. If units do not match the impedance data, specify "units"
    # property.
    length = 1.0

    # No. of phases.  A line has the same number of conductors per terminal as
    # phases.  Neutrals are not explicitly modeled unless declared as a phase
    # and the impedance matrices adjusted accordingly.
    phases = 3

    # Positive-sequence Resistance, ohms per unit length.
    r1 = 0.058

    # Positive-sequence Reactance, ohms per unit length.
    x1 = 0.1206

    # Zero-sequence Resistance, ohms per unit length.
    r0 = 0.1784

    # Zero-sequence Reactance, ohms per unit length.
    x0 = 0.4047

    # Positive-sequence capacitance, nF per unit length.
    c1 = 3.4

    # Zero-sequence capacitance, nF per unit length.
    c0 = 1.6

    # Resistance matrix, lower triangle, ohms per unit length. Order of the
    # matrix is the number of phases. May be used to specify the impedance of
    # any line configuration.  For balanced line models, you may use the
    # standard symmetrical component data definition instead.
    r_matrix = ""

    # Reactance matrix, lower triangle, ohms per unit length. Order of the
    # matrix is the number of phases. May be used to specify the impedance of
    # any line configuration.  For balanced line models, you may use the
    # standard symmetrical component data definition instead.
    x_matrix = ""

    # Nodal Capacitance matrix, lower triangle, nf per unit length.Order of the
    # matrix is the number of phases.  May be used to specify the shunt
    # capacitance of any line configuration.  For balanced line models, you may
    # use the standard symmetrical component data definition instead.
    c_matrix = ""

    # {Y/N | T/F}  Default= No/False.  Designates this line as a switch for
    # graphics and algorithmic purposes.
    # SIDE EFFECT: Sets R1=0.001 X1=0.0. You must reset if you want something
    # different.
    switch = False

    # Carson earth return resistance per unit length used to compute impedance
    # values at base frequency.  For making better frequency adjustments.
    rg = 0.0

    # Carson earth return reactance per unit length used to compute impedance
    # values at base frequency.  For making better frequency adjustments.
    xg = 0.0

    # Earth resitivity used to compute earth correction factor. Overrides Line
    # geometry definition if specified.
    rho = 100

    # Geometry code for LineGeometry Object. Supercedes any previous definition
    # of line impedance. Line constants are computed for each frequency change
    # or rho change. CAUTION: may alter number of phases.
    geometry = ""

    # Length Units = {none | mi|kft|km|m|Ft|in|cm } Default is None - assumes
    # length units match impedance units.
    units = None

#------------------------------------------------------------------------------
#  "Load" class:
#------------------------------------------------------------------------------

class Load:
    """ The load is assumed balanced over the no. of phases defined.  To model
    unbalanced loads, define separate single-phase loads.

    If you do not specify load shapes defaults are:
        Yearly:  Defaults to No variation or Daily when Daily is defined
        Daily:   Defaults to No variation  (i.e. multiplier = 1.0 always)
        Dutycycle: Defaults to Daily shape
        Growth: Circuit default growth factor


    A Load is a complicated Power Conversion element that is at the heart of
    many analyses.  It is basically defined by its nominal kW and PF or its kW
    and kvar.  Then it may be modified by a number of multipliers, including
    the global circuit load multiplier, yearly load shape, daily load shape,
    and a dutycycle load shape.

    The default is for the load to be a current injection source.  Thus, its
    primitive Y matrix contains only the impedance that might exist from the
    neutral of a wye-connected load to ground.  However, if the load model is
    switched to Admittance from PowerFlow (see Set LoadModel command), the load
    is converted to an admittance and included in the system Y matrix.  This
    would be the model used for fault studies where convergence might not be
    achieved because of low voltages.

    Loads are assumed balanced for the number of phases specified.  If you
    would like unbalanced loads, enter separate single-phase loads.

    There are three legal ways to specify the base load:
        1.kW, PF
        2.kw, kvar
        3.kVA, PF

    If you sent these properties in the order shown, the definition should
    work. If you deviate from these procedures, the result may or may not be
    what you want.  (To determine if it has accomplished the desired effect,
    execute the Dump command for the desired load(s) and observe the settings.)

    """

    # Name of bus to which the load is connected.  Include node definitions if
    # the terminal conductors are connected abnormally.  3-phase Wye-connected
    # loads have 4 conductors; Delta-connected have 3.  Wye-connected loads, in
    # general, have one more conductor than phases.  1-phase Delta has 2
    # conductors; 2-phase has 3.  The remaining Delta, or line-line,
    # connections have the same number of conductors as phases.
    bus_1 = None

    # Number of Phases, this load.  Load is evenly divided among phases.
    n_phases = 3

    # Nominal rated (1.0 per unit) voltage, kV, for load. For 2- and 3-phase
    # loads, specify phase-phase kV.  Otherwise, specify actual kV across each
    # branch of the load.  If wye (star), specify phase-neutral kV.  If delta
    # or phase-phase connected, specify phase-phase kV.
    kv = 12.47

    # Total base kW for the load.  Normally, you would enter the maximum kW for
    # the load for the first year and allow it to be adjusted by the load
    # shapes, growth shapes, and global load multiplier.
    # Legal ways to define base load:
    #    kW, PF
    #    kW, kvar
    #    kVA, PF
    kw = 10

    # Load power factor.  Enter negative for leading powerfactor (when kW and
    # kvar have opposite signs.)
    pf = 0.88

    # Integer code for the model to use for load variation with voltage.
    # Valid values are:
    # 1:Standard constant P+jQ load. (Default)
    # 2:Constant impedance load.
    # 3:Const P, Quadratic Q (like a motor).
    # 4:Nominal Linear P, Quadratic Q (feeder mix). Use this with CVRfactor.
    # 5:Constant Current Magnitude
    # 6:Const P, Fixed Q
    # 7:Const P, Fixed Impedance Q
    # For Types 6 and 7, only the P is modified by load multipliers.
    model = 1

    # Load shape to use for yearly simulations.  Must be previously defined
    # as a Loadshape object. Defaults to Daily load shape when Daily is
    # defined.  The daily load shape is repeated in this case. Otherwise, the
    # default is no variation.
    yearly = ""

    # Load shape to use for daily simulations.  Must be previously defined
    # as a Loadshape object of 24 hrs, typically. Default is no variation
    # (constant) if not defined. Side effect: Sets Yearly load shape if not
    # already defined.
    daily = ""

    # Load shape to use for duty cycle simulations.  Must be previously defined
    # as a Loadshape object.  Typically would have time intervals less than
    # 1 hr. Designate the number of points to solve using the Set Number=xxxx
    # command. If there are fewer points in the actual shape, the shape is
    # assumed to repeat. Defaults to Daily curve If not specified.
    duty = ""

    # Characteristic  to use for growth factors by years.  Must be previously
    # defined as a Growthshape object. Defaults to circuit default growth
    # factor
    growth = ""

    # {wye or LN | delta or LL}.
    conn = "wye"

    # Specify the base kvar for specifying load as kW & kvar.  Assumes kW has
    # been already defined.  Alternative to specifying the power factor.  Side
    # effect: the power factor and kVA is altered to agree.
    kvar = 5

    # Neutral resistance of wye (star)-connected load in actual ohms. If
    # entered as a negative value, the neutral is assumed to be open, or
    # floating.
    r_neut = -1

    # Neutral reactance of wye(star)-connected load in actual ohms.  May be
    # + or -.
    x_neut = 0

    # {Variable | Fixed | Exempt}.  Default is variable. If Fixed, no load
    # multipliers apply;  however, growth multipliers do apply.  All
    # multipliers apply to Variable loads.  Exempt loads are not modified by
    # the global load multiplier, such as in load duration curves, etc.  Daily
    # multipliers do apply, so this is a good way to represent industrial load
    # that stays the same for the period study.
    status = "variable"

    # An arbitrary integer number representing the class of load so that load
    # values may be segregated by load value. Default is 1; not used
    # internally.
    klass = 1

    # Minimum per unit voltage for which the MODEL is assumed to apply.
    # Below this value, the load model reverts to a constant impedance model.
    v_min_pu = 0.95

    # Maximum per unit voltage for which the MODEL is assumed to apply.
    # Above this value, the load model reverts to a constant impedance model.
    v_max_pu = 1.05

    # Minimum per unit voltage for load EEN evaluations, Normal limit.
    # Default = 0, which defaults to system "vminnorm" property (see Set
    # Command under Executive).  If this property is specified, it ALWAYS
    # overrides the system specification. This allows you to have different
    # criteria for different loads. Set to zero to revert to the default system
    # value.
    v_min_norm = 0.0

    # Minimum per unit voltage for load UE evaluations, Emergency limit.
    # Default = 0, which defaults to system "vminemerg" property (see Set
    # Command under Executive).  If this property is specified, it ALWAYS
    # overrides the system specification. This allows you to have different
    # criteria for different loads.  Set to zero to revert to the default
    # system value.
    v_min_emerg = 0.0

    # Rated kVA of service transformer for allocating loads based on connected
    # kVA at a bus. Side effect:  kW, PF, and kvar are modified.
    xf_kva = 0.0

    # Allocation factor for allocating loads based on connected kVA at a bus.
    # Side effect:  kW, PF, and kvar are modified by multiplying this factor
    # times the XFKVA (if > 0).
    allocation_factor = 0.5

    # Specify base Load in kVA (and power factor).  This is intended to be used
    # in combination with the power factor (PF) to determine the actual load.
    kva = 11.3636

    # Percent mean value for load to use for monte carlo studies if no
    # loadshape is assigned to this load.
    pct_mean = 50

    # Percent Std deviation value for load to use for monte carlo studies if no
    # loadshape is assigned to this load.
    pct_std_dev = 10

    # Percent reduction in active power (watts) per 1% reduction in voltage
    # from 100% rated. Typical values range from 0.4 to 0.8. Applies to Model=4
    # only. Intended to represent conservation voltage reduction or voltage
    # optimization measures.
    cvr_watts = 1

    # Percent reduction in reactive power (vars) per 1% reduction in voltage
    # from 100% rated. Typical values range from 2 to 3. Applies to Model=4
    # only. Intended to represent conservation voltage reduction or voltage
    # optimization measures.
    cvr_vars = 2

#------------------------------------------------------------------------------
#  "Generator" class:
#------------------------------------------------------------------------------

class Generator:
    """ The generator is essentially a negative load that can be dispatched.

    If the dispatch value (DispValue) is 0, the generator always follows the
    appropriate dispatch curve, which are simply load curves. If DispValue>0
    then the generator only comes on when the global circuit load multiplier
    exceeds DispValue.  When the generator is on, it always follows the
    dispatch curve appropriate for the type of solution being performed.

    If you want to model a generator that is fully on whenever it is dispatched
    on, simply designate "Status=Fixed".  The default is "Status=Variable"
    (i.e., it follows a dispatch curve.  You could also define a dispatch curve
    that is always 1.0.

    Generators have their own energy meters that record:
        1. Total kwh
        2. Total kvarh
        3. Max kW
        4. Max kVA
        5. Hours in operation
        6. Price * kwH

    Generator meters reset with the circuit energy meters and take a sample
    with the circuit energy meters as well. The Energy meters also used
    trapezoidal integration so that they are compatible with Load-Duration
    simulations.

    Generator models are:
        1. Constant P, Q  (* dispatch curve, if appropriate).
        2. Constant Z  (For simple solution)
        3. Constant P, |V|  like a standard power flow  [not implemented]
        4. Constant P, Fixed Q  (vars)
        5. Constant P, Fixed Q  (reactance)

    Most of the time you will use #1 for planning studies.

    The default is for the generator to be a current injection source.  Thus,
    its primitive Y matrix contains only the impedance that might exist from
    the neutral of a wye-connected generator to ground.  However, if the
    generator model is switched to Admittance from PowerFlow (see Set Mode
    command), the generator is converted to an admittance and included in the
    system Y matrix.

    Generators are assumed balanced for the number of phases specified.  If you
    would like unbalanced generators, enter separate single-phase generators.

    """

    # Number of Phases, this Generator.  Power is evenly divided among phases.
    n_phases = 3

    # Bus to which the Generator is connected.  May include specific node
    # specification.
    bus_1 = None

    # Nominal rated (1.0 per unit) voltage, kV, for Generator. For 2- and
    # 3-phase Generators, specify phase-phase kV. Otherwise, specify actual kV
    # across each branch of the Generator. If wye (star), specify phase-neutral
    # kV.  If delta or phase-phase connected, specify phase-phase kV.
    kv = 12.47

    # Total base kW for the Generator.  A positive value denotes power coming
    # OUT of the element, which is the opposite of a load. This value is
    # modified depending on the dispatch mode.  Unaffected by the global load
    # multiplier and growth curves.  If you want there to be more generation,
    # you must add more generators or change this value.
    kw = 100

    # Generator power factor. Default is 0.80. Enter negative for leading
    # powerfactor (when kW and kvar have opposite signs.) A positive power
    # factor for a generator signifies that the generator produces vars as is
    # typical for a synchronous generator.  Induction machines would be
    # specified with a negative power factor.
    pf = 0.80

    # Specify the base kvar.  Alternative to specifying the power factor.  Side
    # effect: the power factor value is altered to agree based on present value
    # of kW.
    kvar = 5

    # Integer code for the model to use for generation variation with voltage.
    # Valid values are:
    #    1:Generator injects a constant kW at specified power factor.
    #    2:Generator is modeled as a constant admittance.
    #    3:Const kW, constant kV.  Somewhat like a conventional transmission
    #    power flow P-V generator.
    #    4:Const kW, Fixed Q (Q never varies)
    #    5:Const kW, Fixed Q(as a constant reactance)
    #    6:Compute load injection from User-written Model.(see usage of Xd,Xdp)
    #    7:Constant kW, kvar, but current limited below Vminpu
    model = 1

    # Minimum per unit voltage for which the Model is assumed to apply. Below
    # this value, the load model reverts to a constant impedance model.
    v_min_pu = 0.95

    # Maximum per unit voltage for which the Model is assumed to apply. Above
    # this value, the load model reverts to a constant impedance model.
    v_max_pu = 1.05

    # Dispatch shape to use for yearly simulations.  Must be previously defined
    # as a Loadshape object. If this is not specified, the daily dispatch shape
    # is repeated. If the generator is assumed to be ON continuously, specify
    # this value as FIXED, or designate a curve that is 1.0 per unit at all
    # times. Nominally for 8760 simulations.  If there are fewer points in the
    # designated shape than the number of points in the solution, the curve is
    # repeated.
    yearly = ""

    # Dispatch shape to use for daily simulations.  Must be previously defined
    # as a Loadshape object of 24 hrs, typically.  If generator is assumed to
    # be ON continuously, specify this value as FIXED, or designate a Loadshape
    # object that is 1.0 perunit for all hours.
    daily = ""

    # Load shape to use for duty cycle dispatch simulations such as for wind
    # generation. Must be previously defined as a Loadshape object. Typically
    # would have time intervals less than 1 hr -- perhaps, in seconds.
    # Designate the number of points to solve using the Set Number=xxxx
    # command.  If there are fewer points in the actual shape, the shape is
    # assumed to repeat.
    duty = ""

    # In default mode, gen is either always on or follows dispatch curve as
    # specified.  Otherwise, the gen comes on when either the global default
    # load level or the price level exceeds the dispatch value.
    disp_mode

    # If = 0.0 Then Generator follow dispatch curves, if any.  If > 0  Then
    # Generator is ON only when either the price signal exceeds this value or
    # the load multiplier (set loadmult=) times the default yearly growth
    # factor exceeds this value.  Then the generator follows dispatch curves,
    # if any (see also Status).
    disp_value

    # ={wye|LN|delta|LL}
    conn = "wye"

    # Removed due to causing confusion - Add neutral impedance externally.
    r_neut = -1

    # Removed due to causing confusion - Add neutral impedance externally.
    x_neut = 0

    # {Fixed|Variable}.  If Fixed, then dispatch multipliers do not apply. The
    #  generator is alway at full power when it is ON. Default is Variable
    # (follows curves).
    status = "variable"

    # An arbitrary integer number representing the class of Generator so that
    # Generator values may be segregated by class.
    klass = 1

    # Per Unit voltage set point for Model = 3  (typical power flow model).
    v_pu = 1.0

    # Maximum kvar limit for Model = 3.  Defaults to twice the specified load
    # kvar. Always reset this if you change PF or kvar properties.
    max_kvar

    # Minimum kvar limit for Model = 3. Enter a negative number if generator
    # can absorb vars.  Defaults to negative of Maxkvar.  Always reset this if
    # you change PF or kvar properties.
    min_kvar

    # Deceleration factor for P-V generator model (Model=3).  Default is 0.1.
    # If the circuit converges easily, you may want to use a higher number such
    # as 1.0. Use a lower number if solution diverges. Use Debugtrace=yes to
    # create a file that will trace the convergence of a generator model.
    pv_factor = 0.1

    # {Yes | No}  Forces generator ON despite requirements of other dispatch
    # modes.  Stays ON until this property is set to NO, or an internal
    # algorithm cancels the forced ON state.
    force_on = "no"

    # kVA rating of electrical machine. Defaults to 1.2* kW if not specified.
    # Applied to machine or inverter definition for Dynamics mode solutions.
    kva

    # MVA rating of electrical machine.  Alternative to using kVA=.
    mva

    # Per unit synchronous reactance of machine. Presently used only for
    # Thevinen impedance for power flow calcs of user models (model=6).
    # Typically use a value 0.4 to 1.0. Default is 1.0
    x_d

    # Per unit transient reactance of the machine.  Used for Dynamics mode and
    # Fault studies.  Default is 0.27.  For user models, this value is used for
    # the Thevinen/Norton impedance for Dynamics Mode.
    x_dp

    # Per unit subtransient reactance of the machine.  Used for Harmonics.
    # Default is 0.20.
    x_dpp

    # Per unit mass constant of the machine.  MW-sec/MVA.
    h

    # Damping constant.  Usual range is 0 to 4. Default is 1.0.  Adjust to get
    # damping
    d

    # Name of DLL containing user-written model, which computes the terminal
    # currents for Dynamics studies, overriding the default model.  Set to
    # "none" to negate previous setting.
    user_model

    # String (in quotes or parentheses) that gets passed to user-written model
    # for defining the data required for that model.
    user_data

    # Name of user-written DLL containing a Shaft model, which models the prime
    # mover and determines the power on the shaft for Dynamics studies.
    # Models additional mass elements other than the single-mass model in the
    # DSS default model. Set to "none" to negate previous setting.
    shaft_model

    # String (in quotes or parentheses) that gets passed to user-written shaft
    # dynamic model for defining the data for that model.
    shaft_data

    # {Yes | No }  Default is no.  Turn this on to capture the progress of the
    # generator model for each iteration.  Creates a separate file for each
    # generator named "GEN_name.CSV".
    debug_trace

#------------------------------------------------------------------------------
#  "EnergyMeter" class:
#------------------------------------------------------------------------------

class EnergyMeter:
    """ This class of device accumulates the energy of the voltage and current
    in the terminal of the device to which it is connected.

    It is an intelligent energy meter capable of measuring losses of all
    devices within its "zone".

    The Zone is determined automatically after a circuit change.  The Zone
    starts on the opposite side of the branch on which the meter is located and
    continues in the same direction through the network until
        a) an open point is encountered
        b) an open terminal or switch is encountered
        c) another energy meter is encountered
        d) a branch that is already included in a zone is encountered

    It keeps track of kwh, kvarh, UE,  EEN, Losses, etc., having registers FOR
    each of these quantities.

    In EEN/UE calculations, line overload takes precedence.

    If the Max Zone kW limits are specified, then these replace the line
    overload UE/EEN numbers. These limits were added so that the user can
    override line limits in cases such as networks where it is difficult to
    judge the UE from the individual line limits.

    Only the maximum |kVA| overload is accumulated, not all.  Loads downline
    from an overload are marked WITH a factor representing the degree of
    overload.  This is used to compute EEN/UE FOR loads.

    FOR low voltages, the full kW FOR loads below the emergency min voltage are
    counted. The EEN is proportioned based on how low the voltage is.

    Emergency min voltage must be less than normal min voltage.


    An EnergyMeter object is an intelligent meter connected to a terminal of a
    circuit element.  It simulates the behavior of an actual energy meter.
    However, it has more capability because it can access values at other
    places in the circuit rather than simply at the location at which it is
    installed.  It measures not only power and energy values at its location,
    but losses and overload values within a defined region of the circuit.
    The operation of the object is simple.  It has several registers that
    accumulate certain values.  At the beginning of a study, the registers are
    cleared (reset) to zero.  At the end of each subsequent solution, the meter
    is instructed to take a sample.  Energy values are then integrated using
    the interval of time that has passed since the previous solution.

    Registers

    There are two types of registers:
        1.Energy Accumulators (for energy values)
        2.Maximum power values ("drag hand" registers).

    The energy registers use trapezoidal integration, which allows to use
    somewhat arbitrary time step sizes between solutions with less integration
    error. This is important for using load duration curves approximated with
    straight lines, for example.

    The present definitions of the registers are:
        1.KWh at the meter location.
        2.Kvarh at the meter location.
        3.Maximum kW at the meter location.
        4.Maximum kVA at the meter location.
        5.KWh in the meter zone.
        6.Kvarh in the meter zone.
        7.Maximum kW in the meter zone.
        8.Maximum kVA in the meter zone.
        9.Overload kWh in the meter zone, normal ratings.
        10.Overload kWh in the meter zone, emergency ratings.
        11.Energy Exceeding Normal (EEN) in the loads in the meter zone.
        12.Unserved Energy (UE) in the loads in the meter zone.
        13.Losses (kWh) in power delivery elements in the meter zone.
        14.Reactive losses (kvarh) in power delivery elements in the meter
        zone.
        15.Maximum losses (kW) in  power delivery elements in the meter zone.
        16.Maximum reactive losses (kvar) in power delivery elements in the
        meter zone.

    Zones

    The EnergyMeter object uses the concept of a zone.  This is an area of the
    circuit for which the meter is responsible.  It can compute energies,
    losses, etc for any power delivery object and Load object in its zone
    (Generator objects have their own intrinsic meters).


    A zone is a collection of circuit elements "downline" from the meter.  This
    concept is nominally applicable to radial circuits, but also has some
    applicability to meshed circuits.  The zones are automatically determined
    according to the following rules:
        1.Start with the circuit element in which the meter is located.  Ignore
        the terminal on which the meter is connected.  This terminal is the
        start of the zone. Begin tracing with the other terminal(s).
        2.Trace out the circuit, finding all other circuit elements (loads and
        power delivery elements) connected to the zone.  Continue tracing out
        every branch of the circuit. Stop tracing a branch when:
        The end of the circuit branch is reached
    A circuit element containing another EnergyMeter object is encountered
    A OPEN terminal is encountered.  (all phases in the terminal are open.)
    A disabled device is encountered.
    A circuit element already included in another zone is encountered.
    There are no more circuit elements to consider.
    Zones are automatically updated after a change in the circuit unless
    the ZONELOCK option (Set command) is set to true (Yes).  Then zones
    remain fixed after initial determination.

    """

    # Name (Full Object name) of element to which the monitor is connected.
    element

    # Number of the terminal of the circuit element to which the monitor is
    # connected.  1 or 2, typically.
    terminal

    # {Clear (reset) | Save | Take | Zonedump | Allocate | Reduce}
    # (A)llocate = Allocate loads on the meter zone to match PeakCurrent.
    # (C)lear = reset all registers to zero
    # (R)educe = reduces zone by merging lines (see Set Keeplist &
    # ReduceOption)
    # (S)ave = saves the current register values to a file. File name is
    # "MTR_metername.CSV". (T)ake = Takes a sample at present solution
    # (Z)onedump = Dump names of elements in meter zone to a file
    # File name is "Zone_metername.CSV".
    action

    # Enter a string ARRAY of any combination of the following. Options
    # processed left-to-right:
    #     (E)xcess : (default) UE/EEN is estimate of energy over capacity
    #     (T)otal : UE/EEN is total energy after capacity exceeded
    #     (R)adial : (default) Treats zone as a radial circuit
    #     (M)esh : Treats zone as meshed network (not radial).
    #     (C)ombined : (default) Load UE/EEN computed from combination of
    #     overload and undervoltage.
    #     (V)oltage : Load UE/EEN computed based on voltage only.
    # Example: option=(E, R)
    option

    # Upper limit on kVA load in the zone, Normal configuration. Default is 0.0
    # (ignored).  Overrides limits on individual lines for overload EEN. With
    # "LocalOnly=Yes" option, uses only load in metered branch.
    kva_norm

    # Upper limit on kVA load in the zone, Emergency configuration. Default is
    # 0.0 (ignored). Overrides limits on individual lines for overload UE.
    # With "LocalOnly=Yes" option, uses only load in metered branch.
    kva_emerg

    # ARRAY of current magnitudes representing the peak currents measured at
    # this location for the load allocation function.  Default is (400, 400,
    # 400). Enter one current for each phase
    peak_current

    # ARRAY of full element names for this meter''s zone.  Default is for meter
    # to find it''s own zone. If specified, DSS uses this list instead.  Can
    # access the names in a single-column text file.  Examples:
    # zonelist=[line.L1, transformer.T1, Line.L3]
    # zonelist=(file=branchlist.txt)
    zone_list

    # {Yes | No}  Default is NO.  If Yes, meter considers only the monitored
    # element for EEN and UE calcs.  Uses whole zone for losses.
    local_only

    # Mask for adding registers whenever all meters are totalized.  Array of
    # floating point numbers representing the multiplier to be used for summing
    # each register from this meter.  Default = (1, 1, 1, 1, ... ).  You only
    # have to enter as many as are changed (positional). Useful when two meters
    # monitor same energy, etc.
    mask

    # {Yes | No}  Default is YES. Compute Zone losses. If NO, then no losses at
    # all are computed.
    losses

    # {Yes | No}  Default is YES. Compute Line losses. If NO, then none of the
    # losses are computed.
    line_losses

    # {Yes | No}  Default is YES. Compute Transformer losses. If NO,
    # transformers are ignored in loss calculations.
    xfmr_losses

    # {Yes | No}  Default is YES. Compute Sequence losses in lines and
    # segregate by line mode losses and zero mode losses.
    seq_losses

    # {Yes | No}  Default is YES. Compute losses and segregate by voltage base.
    # If NO, then voltage-based tabulation is not reported.
    v_base_losses

    # {Yes | No}  Default is YES. When YES, write Overload exception report
    # when Demand Intervals are written.
    overload_report

#------------------------------------------------------------------------------
#  "MonitorObject" class:
#------------------------------------------------------------------------------

class Monitor:
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
    element = ""

    # Number of the terminal of the circuit element to which the monitor is
    # connected.  1 or 2, typically. For monitoring states, attach monitor to
    # terminal 1.
    terminal = 1

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

    # Mix adder to obtain desired results. For example:
    # Mode=112 will save positive sequence voltage and current magnitudes only
    # Mode=48 will save all sequence voltages and currents, but magnitude only.
    mode = 0

    # {Clear | Save | Take}
    # (C)lears or (S)aves current buffer.
    # (T)ake action takes a sample.
    # Note that monitors are automatically reset (cleared) when the
    # Set Mode= command is issued.
    # Otherwise, the user must explicitly reset all monitors (reset monitors
    # command) or individual monitors with the Clear action.
    action = ""

    # {Yes/True | No/False} Default = No.  Include Residual cbannel (sum of all
    # phases) for voltage and current.
    # Does not apply to sequence quantity modes or power modes.
    residual = False

    # {Yes/True | No/False} Default = YES. Report voltage and current in polar
    # form (Mag/Angle). (default)  Otherwise, it will be real and imaginary.
    v_i_polar = True

    # {Yes/True | No/False} Default = YES. Report power in Apparent power, S,
    # in polar form (Mag/Angle).(default)  Otherwise, is P and Q
    p_polar = False

#------------------------------------------------------------------------------
#  "Capacitor" class:
#------------------------------------------------------------------------------

class Capacitor:
    """ Basic  capacitor

    Implemented as a two-terminal constant impedance (Power Delivery Element)

    Bus2 connection defaults to 0 node of Bus1 (if Bus2 has the default bus
    connection at the time Bus1 is defined.  Therefore, if only Bus1 is
    specified, a shunt capacitor results.
    If delta connected, Bus2 is set to node zero of Bus1 and nothing is
    returned in the lower half of YPrim - all zeroes.

    If an ungrounded wye is desired, explicitly set Bus2= and set all nodes the
    same, e.g. Bus1.4.4.4   (uses 4th node of Bus1 as neutral point)
    or BusNew.1.1.1  (makes a new bus for the neutral point)
    You must specify the nodes or you will get a series capacitor!

    A series capacitor is specified simply by setting bus2 and declaring the
    connection to be Wye.  If the connection is specified as delta, nothing
    will be connected to Bus2. In fact the number of terminals is set to 1.

    Capacitance may be specified as:

     1.  kvar and kv ratings at base frequency.  impedance.  Specify kvar as total for
         all phases (all cans assumed equal). For 1-phase, kV = capacitor can kV rating.
         For 2 or 3-phase, kV is line-line three phase. For more than 3 phases, specify
         kV as actual can voltage.
     2.  Capacitance in uF to be used in each phase.  If specified in this manner,
         the given value is always used whether wye or delta.
     3.  A nodal C matrix (like a nodal admittance matrix).
         If conn=wye then 2-terminal through device
         If conn=delta then 1-terminal.
         Microfarads.

    """

    # Name of first bus. Examples:
    #     bus1=busname bus1=busname.1.2.3
    bus_1 = None

    # Name of 2nd bus. Defaults to all phases connected to first bus, node 0.
    # (Shunt Wye Connection) Not necessary to specify for delta (LL) connection
    bus_2 = None

    # Number of phases.
    phases = 3

    # Total kvar, if one step, or ARRAY of kvar ratings for each step.  Evenly
    # divided among phases. See rules for NUMSTEPS.
    kvar = 1200

    # For 2, 3-phase, kV phase-phase. Otherwise specify actual can rating.
    kv = 12.47

    # {wye | delta |LN |LL}  Default is wye, which is equivalent to LN
    conn = "wye"

    # Nodal cap. matrix, lower triangle, microfarads, of the following form:
    #     cmatrix="c11 | -c21 c22 | -c31 -c32 c33"
    # All steps are assumed the same if this property is used.
    cmatrix = ""

    # ARRAY of Capacitance, each phase, for each step, microfarads.
    # See Rules for NumSteps.
    cuf = ""

    # ARRAY of series resistance in each phase (line), ohms.
    r = 0

    # ARRAY of series inductive reactance(s) in each phase (line) for filter,
    # ohms at base frequency. Use this OR "h" property to define filter.
    xl = 0

    # ARRAY of harmonics to which each step is tuned. Zero is interpreted as
    # meaning zero reactance (no filter).
    harm = 0

    # Number of steps in this capacitor bank. Default = 1. Forces reallocation
    # of the capacitance, reactor, and states array.  Rules:
    # If this property was previously =1, the value in the kvar property is
    # divided equally among the steps. The kvar property does not need to be
    # reset if that is accurate.  If the Cuf or Cmatrix property was used
    # previously, all steps are set to the value of the first step.
    # The states property is set to all steps on. All filter steps are set to
    # the same harmonic.
    # If this property was previously >1, the arrays are reallocated, but no
    # values are altered. You must SUBSEQUENTLY assign all array properties.
    n_steps = 1

    # ARRAY of integers {1|0} states representing the state of each step
    # (on|off). Defaults to 1 when reallocated (on).
    # Capcontrol will modify this array as it turns steps on or off.
    states = 1

#------------------------------------------------------------------------------
#  "CapacitorControl" class:
#------------------------------------------------------------------------------

class CapacitorControl:
    """ A CapControl is a control element that is connected to a terminal of
    another circuit element and controls a capacitor.  The control is usually
    placed in the terminal of a line or transformer, although a voltage control
    device could be placed in the terminal of the capacitor it controls.

    Capacitor to be controlled must already exist.

    """

    # Full object name of the circuit element, typically a line or transformer,
    # to which the capacitor control's PT and/or CT are connected. There is no
    # default; must be specified.
    element = None

    # Number of the terminal of the circuit element to which the CapControl is
    # connected. 1 or 2, typically.  Default is 1.
    terminal = 1

    # Name of Capacitor element which the CapControl controls. No Default; Must
    # be specified.Do not specify the full object name; "Capacitor" is assumed
    # for the object class.
    capacitor = None

    # {Current | voltage | kvar |time } Control type.  Specify the ONsetting
    # and OFFsetting appropriately with the type of control. (See help for
    # ONsetting)
    type = "Current"

    # Ratio of the PT that converts the monitored voltage to the control
    # voltage. Default is 60.  If the capacitor is Wye, the 1st phase
    # line-to-neutral voltage is monitored.  Else, the line-to-line voltage
    # (1st - 2nd phase) is monitored.
    pt_ratio = 60

    # Ratio of the CT from line amps to control ampere setting for current and
    # kvar control types.
    ct_ratio = 60.0

    # Value at which the control arms to switch the capacitor ON (or ratchet up
    # a step).  Type of Control:
    #    Current: Line Amps / CTratio
    #    Voltage: Line-Neutral (or Line-Line for delta) Volts / PTratio
    #    kvar:    Total kvar, all phases (3-phase for pos seq model). This is
    #    directional.
    #    Time:    Hrs from Midnight as a floating point number (decimal).
    #    7:30am would be entered as 7.5.
    on_setting = 300

    # Value at which the control arms to switch the capacitor OFF. (See help
    # for ONsetting)
    off_setting = 200

    # Time delay, in seconds, from when the control is armed before it sends
    # out the switching command to turn ON.  The control may reset before the
    # action actually occurs. This is used to determine which capacity control
    # will act first. Default is 15.  You may specify any floating point number
    # to achieve a model of whatever condition is necessary.
    delay = 15.0

    # Switch to indicate whether VOLTAGE OVERRIDE is to be considered. Vmax and
    # Vmin must be set to reasonable values if this property is Yes.
    volt_override = False

    # Maximum voltage, in volts.  If the voltage across the capacitor divided
    # by the PTRATIO is greater than this voltage, the capacitor will switch
    # OFF regardless of other control settings. Default is 126 (goes with a PT
    # ratio of 60 for 12.47 kV system).
    v_max = 126

    # Minimum voltage, in volts.  If the voltage across the capacitor divided
    # by the PTRATIO is less than this voltage, the capacitor will switch ON
    # regardless of other control settings. Default is 115 (goes with a PT
    # ratio of 60 for 12.47 kV system).
    v_min = 115

    # Time delay, in seconds, for control to turn OFF when present state is ON.
    delay_off = 15.0

    # Dead time after capacitor is turned OFF before it can be turned back ON.
    dead_time = 300.0

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

#------------------------------------------------------------------------------
#  "Fault" class:
#------------------------------------------------------------------------------

class Fault:
    """ One or more faults can be placed across any two buses in the circuit.
    Like the capacitor, the second bus defaults to the ground node of the
    same bus that bus1 is connected to.

    The fault is basically an uncoupled, multiphase resistance branch. however,
    you may also specify it as NODAL CONDUCTANCE (G) matrix, which will give
    you complete control of a complex fault situation.

    To eliminate a fault from the system after it has been defined, disable it.

    In Monte Carlo Fault mode, the fault resistance is varied by the % std dev
    specified If %Stddev is specified as zero (default), the resistance is
    varied uniformly.

    Fault may have its "ON" time specified (defaults to 0). When Time (t)
    exceeds this value, the fault will be enabled.  Else it is disabled.

    Fault may be designated as Temporary.  That is, after it is enabled, it
    will disable itself if the fault current drops below the MinAmps value.

    """

    # Name of first bus.
    bus_1 = None

    # Name of 2nd bus.
    bus_2 = None

    # Number of phases.
    phases = 1

    # Resistance, each phase, ohms. Default is 0.0001. Assumed to be Mean value
    # if gaussian random mode.Max value if uniform mode.  A Fault is actually a
    # series resistance that defaults to a wye connection to ground on the
    # second terminal.  You may reconnect the 2nd terminal to achieve whatever
    # connection.  Use the Gmatrix property to specify an arbitrary conductance
    # matrix.
    r = 0.0001

    # Percent standard deviation in resistance to assume for Monte Carlo fault
    # (MF) solution mode for GAUSSIAN distribution. Default is 0 (no variation
    # from mean).
    pct_std_dev = 0

    # Use this to specify a nodal conductance (G) matrix to represent some
    # arbitrary resistance network. Specify in lower triangle form as usual for
    # DSS matrices.
    g_matrix

    # Time (sec) at which the fault is established for time varying
    # simulations. Default is 0.0 (on at the beginning of the simulation)
    on_time = 0.0

    # Designate whether the fault is temporary.  For Time-varying simulations,
    # the fault will be removed if the current through the fault drops below
    # the MINAMPS criteria.
    temporary = False

    # Minimum amps that can sustain a temporary fault.
    min_amps = 5

#------------------------------------------------------------------------------
#  "Feeder" class:
#------------------------------------------------------------------------------

class Feeder:
    """ User cannot instantiate this object.  Feeders are created on the fly
    when a radial system is specified.  Feeders are created from Energymeters
    and are given the same name.

    Feeders get created from energy meters if Radial is set to yes and meter
    zones are already computed.  If Radial=Yes and the meterzones are reset,
    then the feeders are redefined.  If Radial is subsequently set to NO or a
    solution mode is used that doesn't utilize feeders, the get currents
    routines will not do anything.

    Feeders cannot be re-enabled unless the energymeter object allows them to
    be.

    Feeders are not saved.  This is implicit with the Energymeter saving.

    """

    # Name of harmonic spectrum for this device.
    spectrum = ""

    # Base Frequency for ratings.
    base_freq = 60

    # Indicates whether this element is enabled.
    enabled = True

#------------------------------------------------------------------------------
#  "GeneratorDispatcher" class:
#------------------------------------------------------------------------------

class GeneratorDispatcher:
    """ A GenDispatcher is a control element that is connected to a terminal of
    another circuit element and sends dispatch kW signals to a set of
    generators it controls.

    """

    # Full object name of the circuit element, typically a line or transformer,
    # which the control is monitoring. There is no default; must be specified.
    element = None

    # Number of the terminal of the circuit element to which the GenDispatcher
    # control is connected. 1 or 2, typically.  Default is 1. Make sure you
    # have the direction on the power matching the sign of kWLimit.
    terminal = 1

    # kW Limit for the monitored element. The generators are dispatched to hold
    # the power in band.the object class.
    kw_limit = 8000

    # Bandwidth (kW) of the dead band around the target limit. No dispatch
    # changes are attempted if the power in the monitored terminal stays within
    # this band.
    kw_band = 100

    # Max kvar to be delivered through the element.  Uses same dead band as kW.
    kvar_limit = 0

    # Array list of generators to be dispatched.  If not specified, all
    # generators in the circuit are assumed dispatchable.
    gen_list = []

    # Array of proportional weights corresponding to each generator in the
    # gen_list. The needed kW to get back to center band is dispatched to each
    # generator according to these weights. Default is to set all weights to
    # 1.0.
    weights = [1.0]

#------------------------------------------------------------------------------
#  "CurrentSource" class:
#------------------------------------------------------------------------------

class CurrentSource:
    """ Ideal current source

    Stick'em on wherever you want as many as you want

    ISource maintains a positive sequence for harmonic scans.  If you want zero
    sequence, use three single-phase ISource.

    """

    # Name of bus to which source is connected.
    bus_1 = None

    # Magnitude of current source, each phase, in Amps.
    amps = 0

    # Phase angle in degrees of first phase. Phase shift between phases is
    # assumed 120 degrees when number of phases <= 3
    angle = 0

    # Source frequency.  Defaults to  circuit fundamental frequency.
    frequency = 60

    # Number of phases. For 3 or less, phase shift is 120 degrees.
    phases = 3

    # {pos*| zero | none} Maintain specified sequence for harmonic solution.
    # Otherwise, angle between phases rotates with harmonic.
    scantype = "pos"

#------------------------------------------------------------------------------
#  "Reactor" class:
#------------------------------------------------------------------------------

class Reactor:
    """ Uses same rules as Capacitor and Fault for connections

    Implemented as a two-terminal constant impedance (Power Delivery Element)
    Defaults to a Shunt Reactor but can be connected as a two-terminal series
    reactor

    If Parallel=Yes, then the R and X components are treated as being in
    parallel.

    Bus2 connection defaults to 0 node of Bus1 (if Bus2 has the default bus
    connection at the time Bus1 is defined.  Therefore, if only Bus1 is
    specified, a shunt Reactor results. If delta connected, Bus2 is set to node
    zero of Bus1 and nothing is returned in the lower half of YPrim - all
    zeroes.

    If an ungrounded wye is desired, explicitly set Bus2= and set all nodes the
    same, e.g.
        Bus1.4.4.4   (uses 4th node of Bus1 as neutral point)
        or BusNew.1.1.1  (makes a new bus for the neutral point)
    You must specify the nodes or you will get a series Reactor!

    A series Reactor is specified simply by setting bus2 and declaring the
    connection to be Wye.  If the connection is specified as delta, nothing
    will be connected to Bus2. In fact the number of terminals is set to 1.

    Reactance may be specified as:

     1.  kvar and kv ratings at base frequency.  impedance.  Specify kvar as
         total for all phases. For 1-phase, kV = Reactor coil kV rating.
         For 2 or 3-phase, kV is line-line three phase. For more than 3 phases,
         specify kV as actual coil voltage.
     2.  Series Resistance and Reactance in ohns at base frequency to be used
         in each phase.  If specified in this manner, the given value is always
         used whether wye or delta.
     3.  A R and X  matrices. If conn=wye then 2-terminal through device
         If conn=delta then 1-terminal. Ohms at base frequency
         Note that Rmatix may be in parallel with Xmatric (set parallel = Yes)

    """

    # Name of first bus.
    bus_1 = None

    # Name of 2nd bus. Defaults to all phases connected to first bus, node 0.
    # (Shunt Wye Connection)Not necessary to specify for delta (LL)
    # connection
    bus_2 = None

    # Number of phases.
    phases = 3

    # Total kvar, all phases.  Evenly divided among phases. Only determines X.
    # Specify R separately
    k_var = 1200

    # For 2, 3-phase, kV phase-phase. Otherwise specify actual coil rating.
    kv = 12.47

    # {wye | delta |LN |LL}  Default is wye, which is equivalent to LN. If
    # Delta, then only one terminal.
    conn = "wye"

    # Resistance matrix, lower triangle, ohms at base frequency. Order of the
    # matrix is the number of phases.
    r_matrix = []

    # Reactance matrix, lower triangle, ohms at base frequency. Order of the
    # matrix is the number of phases.
    x_matrix = []

    # Signifies R and X are to be interpreted as being in parallel.
    parallel = False

    # Resistance, each phase, ohms.
    r = 0

    # Reactance, each phase, ohms at base frequency.
    x = 0

    # Resistance in parallel with R and X (the entire branch). Assumed infinite
    # if not specified.
    rp = 0

#------------------------------------------------------------------------------
#  "Recloser" class:
#------------------------------------------------------------------------------

class Recloser:
    """ A Recloser is a control element that is connected to a terminal of a
    circuit element and controls the switches in the same or another terminal.

    The control is usually placed in the terminal of a line or transformer, but
    it could be any element

    CktElement to be controlled must already exist.

    """

    # Full object name of the circuit element, typically a line, transformer,
    # load, or generator, to which the Recloser's PT and/or CT are connected.
    # This is the "monitored" element. There is no default; must be specified.
    monitored_obj = None

    # Number of the terminal of the circuit element to which the Recloser is
    # connected. 1 or 2, typically.
    monitored_term = 1

    # Name of circuit element switch that the Recloser controls. Specify the
    # full object name.Defaults to the same as the Monitored element. This is
    # the "controlled" element.
    switched_obj = None

    # Number of the terminal of the controlled element in which the switch is
    # controlled by the Recloser. 1 or 2, typically.
    switched_term = 1

    # Number of Fast (fuse saving) operations. (See "Shots")
    n_fast = 1

    # Name of the TCC Curve object that determines the Phase Fast trip. Must
    # have been previously defined as a TCC_Curve object. Default is "A".
    # Multiplying the current values in the curve by the "phasetrip" value
    # gives the actual current.
    phase_fast = "A"

    # Name of the TCC Curve object that determines the Phase Delayed trip. Must
    # have been previously defined as a TCC_Curve object. Default is "D".
    # Multiplying the current values in the curve by the "phasetrip" value
    # gives the actual current.
    phase_delayed = "D"

    # Name of the TCC Curve object that determines the Ground Fast trip.  Must
    # have been previously defined as a TCC_Curve object. Multiplying the
    # current values in the curve by the "groundtrip" value gives the actual
    # current.
    ground_fast = None

    # Name of the TCC Curve object that determines the Ground Delayed trip.
    # Must have been previously defined as a TCC_Curve object. Multiplying the
    # current values in the curve by the "groundtrip" value gives the actual
    # current.
    ground_delayed = None

    phase_trip = 1.0

    # Multiplier or actual ground amps (3I0) for the ground TCC curve.
    ground_trip = 1.0

    # Multiplier or actual phase amps for the phase TCC curve.
    phase_inst = 1.0

    # Actual amps for instantaneous ground trip which is assumed to happen in
    # 0.01 sec + Delay Time.Default is 0.0, which signifies no inst trip.
    ground_inst = 0

    # Reset time in sec for Recloser.
    reset = 15

    # Total Number of fast and delayed shots to lockout. This is one more than
    # the number of reclose intervals.
    shots = 4

    # Array of reclose intervals.  Default for Recloser is (0.5, 2.0, 2.0)
    # seconds. A locked out Recloser must be closed manually (action=close).
    reclose_intervals = (0.5, 2.0, 2.0)

    # Fixed delay time (sec) added to Recloser trip time. Used to represent
    # breaker time or any other delay.
    delay = 0.0

    # {Trip/Open | Close}  Action that overrides the Recloser control.
    # Simulates manual control on recloser "Trip" or "Open" causes the
    # controlled element to open and lock out. "Close" causes the controlled
    # element to close and the Recloser to reset to its first operation.
    action = "Trip/Open"

    # Time dial for Phase Fast trip curve. Multiplier on time axis of specified
    # curve.
    td_ph_fast = 1.0

    # Time dial for Ground Fast trip curve. Multiplier on time axis of
    # specified curve.
    td_gr_fast = 1.0

    # Time dial for Phase Delayed trip curve. Multiplier on time axis of
    # specified curve.
    td_ph_delayed = 1.0

    # Time dial for Ground Delayed trip curve. Multiplier on time axis of
    # specified curve.
    td_gr_delayed = 1.0

#------------------------------------------------------------------------------
#  "RegControl" class:
#------------------------------------------------------------------------------

class RegControl:
    """ A RegControl is a control element that is connected to a terminal of
    another circuit element that must be a transformer.

    """

    # Name of Transformer element to which the RegControl is connected. Do not
    # specify the full object name; "Transformer" is assumed for the object
    # class.
    transformer = None

    # Number of the winding of the transformer element that the RegControl is
    # monitoring. 1 or 2, typically.  Side Effect: Sets TAPWINDING property to
    # the same winding.
    winding = 1

    # Voltage regulator setting, in VOLTS, for the winding being controlled.
    # Multiplying this value times the ptratio should yield the voltage across
    # the WINDING of the controlled transformer.
    v_reg = 120.0

    # Bandwidth in VOLTS for the controlled bus (see help for ptratio property)
    band = 3.0

    # Ratio of the PT that converts the controlled winding voltage to the
    # regulator voltage. If the winding is Wye, the line-to-neutral voltage is
    # used.  Else, the line-to-line voltage is used.
    pt_ratio = 60.0

    # Rating, in Amperes, of the primary CT rating for converting the line amps
    # to control amps.The typical default secondary ampere rating is 5 Amps.
    ct_prim = 300

    # R setting on the line drop compensator in the regulator, expressed in
    # VOLTS.
    r = 0.0

    # X setting on the line drop compensator in the regulator, expressed in
    # VOLTS.
    x = 0.0

    # Name of a bus in the system to use as the controlled bus instead of the
    # bus to which the winding is connected or the R and X line drop
    # compensator settings.  Do not specify this value if you wish to use the
    # line drop compensator settings.  Default is null string. Assumes the base
    # voltage for this bus is the same as the transformer winding base
    # specified above. Note: This bus WILL BE CREATED by the regulator control
    # upon SOLVE if not defined by some other device.
    bus = None

    # Time delay, in seconds, from when the voltage goes out of band to when
    # the tap changing begins. This is used to determine which regulator
    # control will act first. You may specify any floating point number to
    # achieve a model of whatever condition is necessary.
    delay = 15

    # Indicates whether or not the regulator can be switched to regulate in the
    # reverse direction. Default is No.Typically applies only to line
    # regulators and not to LTC on a substation transformer.
    reversible = False

    # Voltage setting in volts for operation in the reverse direction.
    rev_v_reg = 120

    # Bandwidth for operating in the reverse direction.
    rev_band = 3

    # R line drop compensator setting for reverse direction.
    rev_r = 0.0

    # X line drop compensator setting for reverse direction.
    rev_x = 0.0

    # Delay in sec between tap changes. This is how long it takes between
    # changes after the first change.
    tap_delay = 2

    # Turn this on to capture the progress of the regulator model for each
    # control iteration.  Creates a separate file for each RegControl named
    # "REG_name.CSV".
    debug_trace = False

    # Maximum allowable tap change per control iteration in STATIC control
    # mode. Set this to 1 to better approximate actual control action. Set this
    # to 0 to fix the tap in the current position.
    max_tap_change = 16

    # The time delay is adjusted inversely proportional to the amount the
    # voltage is outside the band down to 10%.
    inverse_time = False

    # Winding containing the actual taps, if different than the WINDING
    # property. Defaults to the same winding as specified by the WINDING
    # property.
    tap_winding = 1

#------------------------------------------------------------------------------
#  "Relay" class:
#------------------------------------------------------------------------------

class Relay:
    """ A Relay is a control element that is connected to a terminal of a
    circuit element and controls the switches in the same or another terminal.

    The control is usually placed in the terminal of a line or transformer, but
    it could be any element.

    Voltage relay is a definite time relay that operates after the voltage
    stays out of bounds for a fixed time interval.  It will then reclose a set
    time after the voltage comes back in the normal range.

    """

    # Full object name of the circuit element, typically a line, transformer,
    # load, or generator, to which the relay's PT and/or CT are connected. This
    # is the "monitored" element. There is no default; must be specified.
    monitored_obj = None

    # Number of the terminal of the circuit element to which the Relay is
    # connected. 1 or 2, typically.
    monitored_term = 1

    # Name of circuit element switch that the Relay controls. Specify the full
    # object name. Defaults to the same as the Monitored element. This is the
    # "controlled" element.
    switched_obj = None

    # Number of the terminal of the controlled element in which the switch is
    # controlled by the Relay. 1 or 2, typically.
    switched_term = 1

    # One of a legal relay type:
    #    Current Voltage Reversepower 46 (neg seq current)
    #    47 (neg seq voltage)
    #    Generic (generic over/under relay) Default is overcurrent relay
    #    (Current) Specify the curve and pickup settings appropriate for each
    #    type. Generic relays monitor PC Element Control variables and trip on
    #    out of over/under range in definite time.
    type = "current"

    # Name of the TCC Curve object that determines the phase trip.  Must have
    # been previously defined as a TCC_Curve object. Default is none (ignored).
    # For overcurrent relay, multiplying the current values in the curve by the
    # "phasetrip" value gives the actual current.
    phase_curve = None

    # Name of the TCC Curve object that determines the ground trip. Must have
    # been previously defined as a TCC_Curve object. For overcurrent relay,
    # multiplying the current values in the curve by the "groundtrip" value
    # gives the actual current.
    ground_curve = None

    # Multiplier or actual phase amps for the phase TCC curve.
    phase_trip = 1.0

    # Multiplier or actual ground amps (3I0) for the ground TCC curve.
    ground_trip = 1.0

    # Time dial for Phase trip curve. Multiplier on time axis of specified
    # curve.
    td_phase

    # Time dial for Ground trip curve. Multiplier on time axis of specified
    # curve.
    td_ground

    # Actual  amps (Current relay) or kW (reverse power relay) for
    # instantaneous phase trip which is assumed to happen in 0.01 sec + Delay
    # Time. Default is 0.0, which signifies no inst trip. Use this value for
    # specifying the Reverse Power threshold (kW) for reverse power relays.
    phase_inst = 0.0

    # Actual  amps for instantaneous ground trip which is assumed to happen in
    # 0.01 sec + Delay Time.Default is 0.0, which signifies no inst trip.
    ground_inst

    # Reset time in sec for relay.
    reset = 15

    # Number of shots to lockout. This is one more than the number of reclose
    # intervals.
    shots = 4

    # Array of reclose intervals. If none, specify "NONE". Default for
    # overcurrent relay is (0.5, 2.0, 2.0) seconds. Default for a voltage relay
    # is (5.0). In a voltage relay, this is  seconds after restoration of
    # voltage that the reclose occurs. Reverse power relay is one shot to
    # lockout, so this is ignored.  A locked out relay must be closed manually
    # (set action=close).
    reclose_intervals = (0.5, 2.0, 2.0)

    # Trip time delay (sec) for definite time relays. Default is 0.0 for
    # current and voltage relays.  If >0 then this value is used instead of
    # curves.  Used exclusively by RevPower, 46 and 47 relays at this release.
    # Defaults to 0.1 s for these relays.
    delay = 0.0

    # TCC Curve object to use for overvoltage relay.  Curve is assumed to be
    # defined with per unit voltage values. Voltage base should be defined for
    # the relay.
    overvolt_curve = None

    # TCC Curve object to use for undervoltage relay.  Curve is assumed to be
    # defined with per unit voltage values. Voltage base should be defined for
    # the relay.
    undervolt_curve = None

    # Voltage base (kV) for the relay. Specify line-line for 3 phase devices);
    # line-neutral for 1-phase devices.  Relay assumes the number of phases of
    # the monitored element.  Default is 0.0, which results in assuming the
    # voltage values in the "TCC" curve are specified in actual line-to-neutral
    # volts.
    kv_base = 0.0

    # Percent voltage pickup for 47 relay (Neg seq voltage). Specify also base
    # voltage (kvbase) and delay time value.
    pct_pickup_47 = 2

    # Base current, Amps, for 46 relay (neg seq current). Used for establishing
    # pickup and per unit I-squared-t.
    base_amps_46

    # Percent pickup current for 46 relay (neg seq current). When current
    # exceeds this value * BaseAmps, I-squared-t calc starts.
    pct_pickup_46 = 20.0

    # Negative Sequence I-squared-t trip value for 46 relay (neg seq current).
    # Default is 1 (trips in 1 sec for 1 per unit neg seq current).
    # Should be 1 to 99.
    isqt_46 = 1

    # Name of variable in PC Elements being monitored.  Only applies to Generic
    # relay.
    variable

    # Trip setting (high value) for Generic relay variable. Relay trips in
    # definite time if value of variable exceeds this value.
    overtrip

    # Trip setting (low value) for Generic relay variable.  Relay trips in
    # definite time if value of variable is less than this value.
    undertrip

    # Fixed delay time (sec) added to relay time. Designed to represent breaker
    # time or some other delay after a trip decision is made.Use Delay_Time
    # property for setting a fixed trip time delay.Added to trip time of
    # current and voltage relays. Could use in combination with inst trip value
    # to obtain a definite time overcurrent relay.
    breaker_time = 0.0

    # {Trip/Open | Close} Action that overrides the relay control. Simulates
    # manual control on breaker. "Trip" or "Open" causes the controlled element
    # to open and lock out. "Close" causes the controlled element to close and
    # the relay to reset to its first operation.
    action = "Trip/Open"

#------------------------------------------------------------------------------
#  "Sensor" class:
#------------------------------------------------------------------------------

class Sensor:
    """ """

    # Name (Full Object name) of element to which the Sensor is connected.
    element = None

    # Number of the terminal of the circuit element to which the Sensor is
    # connected. 1 or 2, typically. For Sensoring states, attach Sensor to
    # terminal 1.
    terminal = 1

    # Array of any of { Voltage | Current | kW | kvar } in any order.
    # Quantities being sensed. Scalar magnitudes only.
    modes = ["v"]

    # Array of Voltages (kV) measured by the voltage sensor.
    v = 7.2

    # Array of Currents (amps) measured by the current sensor.
    i = 0.0

    # Array of Active power (kW) measurements at the sensor.
    p = 0.0

    # Array of Reactive power (kvar) measurements at the sensor.
    q = 0.0

    # Array of phases being monitored by this sensor. [1, 2, 3] or [2 3 1] or
    # [1], etc.  Corresponds to the order that the measurement arrays will be
    # supplied. Defaults to same number of quantities as phases in the
    # monitored element.
    phases = [1, 2, 3]

    # Connection: { wye | delta | LN | LL }. Applies to voltage measurement. If
    # wye or LN, voltage is assumed measured line-neutral; otherwise,
    # line-line.
    conn = "wye"

    # Assumed percent error in the measurement.
    pct_error = 1

    # Action options: SQERROR: Show square error of the present value of the
    # monitored terminal quantity vs the sensor value. Actual values - convert
    # to per unit in calling program.  Value reported in result window/result
    # variable.
    action = None

#------------------------------------------------------------------------------
#  "Spectrum" class:
#------------------------------------------------------------------------------

class Spectrum:
    """ Spectrum specified as Harmonic, pct magnitude and angle

    Spectrum is shifted by the fundamental angle and stored in MultArray
    so that the fundamental is at zero degrees phase shift.

    """

    # Number of frequencies in this spectrum. (See CSVFile)
    n_harm = 0

    # Array of harmonic values.
    harmonic = []

    # Array of magnitude values, assumed to be in PERCENT.
    pct_mag = []

    # Array of phase angle values, degrees.
    angle = []

    # File of spectrum points with (harmonic, magnitude-percent, angle-degrees)
    # values, one set of 3 per line, in CSV format. If fewer than NUMHARM
    # frequencies found in the file, NUMHARM is set to the smaller value.
    csv_file = ""

# EOF -------------------------------------------------------------------------
