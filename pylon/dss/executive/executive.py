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

""" Defines commands for the executive """

#------------------------------------------------------------------------------
#  Imports:
#------------------------------------------------------------------------------

from enthought.traits.api import Instance

from enthought.traits.ui.api import ModelView, View, Item, Group

from enthought.traits.ui.menu import NoButtons

#from enthought.enable.tools.api import MoveTool


from pylon.dss.common.circuit import Circuit
from executive_options import ExecutiveOptions
from executive_menu import menu_bar, tool_bar

from pylon.dss.common.bus import Bus
from pylon.dss.delivery.api import Fault, Transformer, Line, Capacitor
from pylon.dss.control.api import CapacitorControl
from pylon.dss.control.api import RegulatorControl

from pylon.dss.conversion.api import \
    VoltageSource, CurrentSource, Generator, Load

from pyramid.mapping import Mapping, CanvasMapping, NodeMapping
from pyramid.element_tool import ElementTool
from pyramid.context_menu_tool import ContextMenuTool

from godot.node import Node as GodotNode

#------------------------------------------------------------------------------
#  "ExecCommand" class:
#------------------------------------------------------------------------------

class Executive(ModelView):
    """ Defines commands for the executive """

    #--------------------------------------------------------------------------
    #  Trait Definitions:
    #--------------------------------------------------------------------------

    # The model this handler defines a view and controller for
#    model = Instance(Circuit)

    # Options for DSS
    options = Instance(ExecutiveOptions, ())

    diagram = Instance(Mapping)

    #--------------------------------------------------------------------------
    #  Views:
    #--------------------------------------------------------------------------

    traits_view = View(
#        Item(
#            name="model", show_label=False, id=".table_editor", style="custom"
#        ),
        Item(
            name="diagram", show_label=False, id=".diagram_editor",
            style="custom"
        ),
        id="circuit_vm.view", title="Pylon", resizable=True,
        width=.81, height=.81, kind="live",
        buttons=NoButtons, menubar=menu_bar, toolbar=tool_bar
    )

    def _diagram_default(self):
        """ Trait initialiser """

        mapping = Mapping(
            diagram = CanvasMapping(
                domain_model=self.model,
#                diagram_canvas=Canvas(bgcolor="lightslategrey", draw_axes=True),
                tools=[ContextMenuTool]
            ),
            node_mappings = [
                NodeMapping(
                    containment_trait="buses", element=Bus,
                    dot_node=GodotNode(
                        shape="rectangle", fixed_size=True,
                        width=1.5, height=0.5,
                        fill_color="white", color="orange",
                        style=["filled"]
                    ),
                    tools=[ElementTool] #, MoveTool]
                ),
                NodeMapping(
                    containment_trait="generators", element=Generator,
                    dot_node=GodotNode(
                        shape="circle", color="red", style=["filled"],
                        fill_color="blue"
                    ),
                    tools=[ElementTool] #, MoveTool]
                ),
                NodeMapping(
                    containment_trait="loads", element=Load,
                    dot_node=GodotNode(shape="invtriangle"),
                    tools=[ElementTool] #, MoveTool]
                ),
                NodeMapping(
                    containment_trait="voltage_sources", element=VoltageSource,
                    dot_node=GodotNode(shape="doublecircle"),
                    tools=[ElementTool] #, MoveTool]
                ),
                NodeMapping(
                    containment_trait="current_sources", element=CurrentSource,
                    dot_node=GodotNode(shape="pentagon"),
                    tools=[ElementTool] #, MoveTool]
                ),
                NodeMapping(
                    containment_trait="cap_controls", element=CapacitorControl,
                    dot_node=GodotNode(shape="invhouse"),
                    tools=[ElementTool] #, MoveTool]
                ),
                NodeMapping(
                    containment_trait="reg_controls", element=RegulatorControl,
                    dot_node=GodotNode(shape="egg"),
                    tools=[ElementTool] #, MoveTool]
                )
            ],
            program="dot"
        )
        mapping.refresh_diagram()

        return mapping


    def _model_changed(self, new):
        """ Handles the model changing """

        self.diagram.diagram.domain_model = new


    #--------------------------------------------------------------------------
    #  Action handlers:
    #--------------------------------------------------------------------------

    def preferences(self, info):
        """ Handles display of the preferences dialog """

        options = self.options

        if info.initialized and (options is not None):
            options.edit_traits(parent=info.ui.control, kind="livemodal")


    def new_bus(self, info):
        """ Handles adding a new bus to the circuit """

        circuit = self.model

        if info.initialized and (circuit is not None):
            e = Bus()
            retval = e.edit_traits(parent=info.ui.control, kind="livemodal")
            if retval.result:
                circuit.buses.append(e)


    def new_line(self, info):
        """ Handles adding a new line to the circuit """

        circuit = self.model

        if info.initialized and (circuit is not None):
            e = Line()
            retval = e.edit_traits(parent=info.ui.control, kind="livemodal")
            if retval.result:
                circuit.lines.append(e)


    def new_transformer(self, info):
        """ Handles adding a new transformer to the circuit """

        circuit = self.model

        if info.initialized and (circuit is not None):
            e = Transformer()
            retval = e.edit_traits(parent=info.ui.control, kind="livemodal")
            if retval.result:
                circuit.transformers.append(e)


    def new_generator(self, info):
        """ Handles adding a new generator to the circuit """

        circuit = self.model

        if info.initialized and (circuit is not None):
            e = Generator()
            retval = e.edit_traits(parent=info.ui.control, kind="livemodal")
            if retval.result:
                circuit.generators.append(e)


    def new_load(self, info):
        """ Handles adding a new load to the circuit """

        circuit = self.model

        if info.initialized and (circuit is not None):
            e = Load()
            retval = e.edit_traits(parent=info.ui.control, kind="livemodal")
            if retval.result:
                circuit.loads.append(e)


    def new_voltage_source(self, info):
        """ Handles adding a new voltage source to the circuit """

        circuit = self.model

        if info.initialized and (circuit is not None):
            e = VoltageSource()
            retval = e.edit_traits(parent=info.ui.control, kind="livemodal")
            if retval.result:
                circuit.voltage_sources.append(e)


    def new_current_source(self, info):
        """ Handles adding a new current source to the circuit """

        circuit = self.model

        if info.initialized and (circuit is not None):
            e = VoltageSource()
            retval = e.edit_traits(parent=info.ui.control, kind="livemodal")
            if retval.result:
                circuit.voltage_sources.append(e)


    def new_fault(self, info):
        """ Handles adding a new line to the circuit """

        circuit = self.model

        if info.initialized and (circuit is not None):
            e = Fault()
            retval = e.edit_traits(parent=info.ui.control, kind="livemodal")
            if retval.result:
                circuit.faults.append(e)


    def new_capacitor(self, info):
        """ Handles adding a new capacitor to the circuit """

        circuit = self.model

        if info.initialized and (circuit is not None):
            e = Capacitor()
            retval = e.edit_traits(parent=info.ui.control, kind="livemodal")
            if retval.result:
                circuit.shunt_capacitors.append(e)


    def new_capacitor_control(self, info):
        """ Handles adding a new capacitor control to the circuit """

        circuit = self.model

        if info.initialized and (circuit is not None):
            e = CapacitorControl()
            retval = e.edit_traits(parent=info.ui.control, kind="livemodal")
            if retval.result:
                circuit.cap_controls.append(e)


    def new_regulator_control(self, info):
        """ Handles adding a new regulator control to the circuit """

        circuit = self.model

        if info.initialized and (circuit is not None):
            e = RegulatorControl()
            retval = e.edit_traits(parent=info.ui.control, kind="livemodal")
            if retval.result:
                circuit.reg_controls.append(e)



    def new(self, info):
        """ Create a new object within the DSS. Object becomes the active
        object.

        """

        pass


    def edit(self, info):
        """ Edit an object. The object is selected and it then becomes the
        active object.

        Note that Edit is the default command.  You many change a property
        value simply by giving the full property name and the new value.

        """

        pass


    def more(self, info):
        """ Continuation of editing on the active object. """

        pass


    def select(self, info):
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


    def save(self, info, klass, dir):
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


    def show(self, info):
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


    def solve(self, info):
        """ Perform the solution of the present solution mode. You can set any
        option that you can set with the Set command (see Set). The Solve
        command is virtually synonymous with the Set command except that
        a solution is performed after the options are processed.

        """

        pass


    def enable(self, info):
        """ Enables a circuit element or entire class """

        pass


    def disable(self, info):
        """ Disables a circuit element or entire class. The item remains
        defined, but is not included in the solution.

        """

        pass


    def plot(self, info, type, quantity, max, dots, labels, object, show_loops,
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


    def reset(self, info):
        """ {MOnitors | MEters | Faults | Controls | Eventlog | Keeplist |
        (no argument) }

        Resets all Monitors, Energymeters, etc.

        If no argument specified, resets all options listed.

        """

        pass


    def compile(self, info):
        """ Reads the designated file name containing DSS commands and
        processes them as if they were entered directly into the command line.
        The file is said to be "compiled."

        Similar to "redirect" except changes the default directory to the path
        of the specified file.

        Syntax:
            Compile filename

        """

        pass


    def set_value(self, info):
        """ Used to set various DSS solution modes and options.  You may also
        set the options with the Solve command.

        See "Options" for help.

        """


        pass


    def dump(self, info):
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


    def open(self, info):
        """ Opens the specified terminal and conductor of the specified circuit
        element. If the conductor is not specified, all phase conductors of the
        terminal are opened.

        Examples:
            Open line.line1 2 (opens all phases of terminal 2)
            Open line.line1 2 3 (opens the 3rd conductor of terminal 2)

        """

        pass


#    def close(self, info):
#        """ Opposite of the Open command """
#
#        pass


    def redirect(self, info):
        """ Reads the designated file name containing DSS commands and
        processes them as if they were entered directly into the command line.
        Similar to "Compile", but leaves current directory where it was when
        Redirect command is invoked. Can temporarily change to subdirectories
        if nested Redirect commands require.

        """

        pass


    def help(self, info):
        """ Handles display of help """

        pass


    def quit(self, info):
        """ Handles closing the application """

        pass


    def what(self, info):
        """ Inquiry for property value.  Result is put into GlobalReault and
        can be seen in the Result Window. Specify the full property name.

        Example: ? Line.Line1.R1

        Note you can set this property merely by saying:
            Line.line1.r1=.058

        """

        pass


    def next(self, info):
        """ {Year | Hour | t}  Increments year, hour, or time as specified.  If
        "t" is specified, then increments time by current step size.

        """

        pass


    def panel(self, info):
        """ Displays main control panel window. """

        pass


    def sample(self, info):
        """ Force all monitors and meters to take a sample now """

        pass


    def clear(self, info):
        """ Clear all circuits currently in memory """

        pass


    def about(self, info):
        """ Handles display of the 'About' dialog box """

        pass


    def calc_voltage_bases(self, info):
        """ Calculates voltagebase for buses based on voltage bases defined
        with Set voltagebases=... command.

        """

        pass


    def set_kv_base(self, info):
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


    def build_y(self, info):
        """ Forces rebuild of Y matrix upon next Solve command regardless of
        need. The usual reason for doing this would be to reset the matrix for
        another load level when using LoadModel=PowerFlow (the default) when
        the system is difficult to solve when the load is far from its base
        value.  Works by invalidating the Y primitive matrices for all the
        Power Conversion elements.

        """

        pass


    def get_value(self, info):
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


    def initialise(self, info):
        """ This command forces reinitialization of the solution for the next
        Solve command. To minimize iterations, most solutions start with the
        previous solution unless there has been a circuit change.  However, if
        the previous solution is bad, it may be necessary to re-initialize. In
        most cases, a re-initiallization results in a zero-load power flow
        solution with only the series power delivery elements considered.

        """

        pass


    def export(self, info):
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


    def file_edit(self, info):
        """ Edit specified file in default text file editor (see set_editor=
        option). Fileedit EXP_METERS.CSV (brings up the meters export file)
        "FileEdit" may be abbreviated to a unique character string.

        """

        pass


    def voltages(self, info):
        """ Returns the voltages for the ACTIVE BUS in the Result string.
        For setting the active Bus, use the Select command or the
        set_bus= option.

        Returned as magnitude and angle quantities, comma separated, one set
        per conductor of the terminal.

        """

        pass


    def currents(self, info):
        """ Returns the currents for each conductor of ALL terminals of the
        active circuit element in the Result string/ (See select command.)
        Returned as comma-separated magnitude and angle.

        """

        pass


    def powers(self, info):
        """ Returns the powers (complex) going into each conductors of ALL
        terminals of the active circuit element in the Result string.
        (See select command.)

        Returned as comma-separated kW and kvar.

        """

        pass


    def seq_voltages(self, info):
        """ Returns the sequence voltages at all terminals of the active
        circuit element (see Select command) in Result string.  Returned as
        comma-separated magnitude only values.

        Order of returned values: 0, 1, 2  (for each terminal).

        """

        pass


    def seq_currents(self, info):
        """ Returns the sequence currents into all terminals of the active
        circuit element (see Select command) in Result string.  Returned as
        comma-separated magnitude only values.

        Order of returned values: 0, 1, 2  (for each terminal).

        """

        pass


    def seq_power(self, info):
        """ Returns the sequence powers into all terminals of the active
        circuit element (see Select command) in Result string.  Returned as
        comma-separated kw, kvar pairs.

        Order of returned values: 0, 1, 2  (for each terminal).

        """

        pass


    def losses(self, info):
        """ Returns the total losses for the active circuit element in the
        Result string in kW, kvar.

        """

        pass


    def phase_losses(self, info):
        """ Returns the losses for the active circuit element for each PHASE in
        the Result string in comma-separated kW, kvar pairs.

        """

        pass


    def ckt_losses(self, info):
        """ Returns the total losses for the active circuit in the Result
        string in kW, kvar.

        """

        pass


    def allocate_loads(self, info):
        """ Estimates the allocation factors for loads that are defined using
        the XFKVA property. Requires that energymeter objects be defined with
        the PEAKCURRENT property set. Loads that are not in the zone of an
        energymeter cannot be allocated.

        """

        pass


    def form_edit(self, info):
        """ FormEdit [class.object].  Brings up form editor on active DSS
        object.

        """

        pass


    def totals(self, info):
        """ Totals all EnergyMeter objects in the circuit and reports register
        totals in the result string.

        """

        pass


    def capacity(self, info):
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


    def classes(self, info):
        """ List of intrinsic DSS Classes. Returns comma-separated list in
        Result variable.

        """

        pass


    def user_classes(self, info):
        """ List of user-defined DSS Classes. Returns comma-separated list in
        Result variable.

        """

        pass


    def z_sc(self, info):
        """ Returns full Zsc matrix for the ACTIVE BUS in comma-separated
        complex number form.

        """

        pass


    def z_sc10(self, info):
        """ Returns symmetrical component impedances, Z1, Z0 for the ACTIVE BUS
        in comma-separated R+jX form.

        """

        pass


    def z_sc_refresh(self, info):
        """ Refreshes Zsc matrix for the ACTIVE BUS. """

        pass


    def y_sc(self, info):
        """ Returns full Ysc matrix for the ACTIVE BUS in comma-separated
        complex number form G + jB.

        """

        pass


    def pu_voltages(self, info):
        """ Just like the Voltages command, except the voltages are in per unit
        if the kVbase at the bus is defined.

        """

        pass


    def var_values(self, info):
        """ Returns variable values for active element if PC element.
        Otherwise, returns null.

        """

        pass


    def var_names(self, info):
        """ Returns variable names for active element if PC element. Otherwise,
        returns null.

        """

        pass


    def bus_coords(self, info):
        """ Define x,y coordinates for buses.  Execute after Solve command
        performed so that bus lists are defined. Reads coordinates from a CSV
        file with records of the form: busname, x, y.

        Example: BusCoords [file=]xxxx.csv

        """

        pass


    def make_bus_list(self, info):
        """ Updates the buslist using the currently enabled circuit elements.
        (This happens automatically for Solve command.)

        """

        pass


    def make_pos_sequence(self, info):
        """ Attempts to convert present circuit model to a positive sequence
        equivalent. It is recommended to Save the circuit after this and edit
        the saved version to correct possible misinterpretations.

        """

        pass


    def reduce(self, info):
        """ {All | MeterName}  Default is "All".  Reduce the circuit according
        to reduction options. See "Set ReduceOptions" and "Set Keeplist"
        options.

        Energymeter objects actually perform the reduction.  "All" causes all
        meters to reduce their zones.

        """

        pass


    def interpolate(self, info):
        """ {All | MeterName}  Default is "All". Interpolates coordinates for
        missing bus coordinates in meter zone'

        """

        pass


    def align_file(self, info):
        """ Alignfile [file=]filename.  Aligns DSS script files in columns for
        easier reading.

        """

        pass


    def top(self, info):
        """ [class=]{Loadshape | Monitor  } [object=]{ALL (Loadshapes only) |
        objectname}.

        Send specified object to TOP.  Loadshapes must be hourly fixed
        interval.

        """

        pass


    def rotate(self, info):
        """ Rotate circuit plotting coordinates by specified angle """

        pass


    def v_diff(self, info):
        """ Displays the difference between the present solution and the last
        on saved using the SAVE VOLTAGES command.

        """

        pass


    def summary(self, info):
        """ Displays a power flow summary of the most recent solution. """

        pass


    def distribute(self, info):
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


    def di_plot(self, info):
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


    def compare_cases(self, info):
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


    def yearly_curves(self, info):
        """ [cases=](case1, case2, ...) [registers=](reg1, reg2, ...)
        [meter=]{Totals* | SystemMeter | metername}

        Plots yearly curves for specified cases and registers.

        Default: meter=Totals.
        Example: yearlycurves cases=(basecase, pvgens) registers=9

        """

        pass


    def cd(self, info):
        """ Change default directory to specified directory """

        pass


    def visualise(self, info):
        """ [What=] {Currents* | Voltages | Powers} [element=]full_element_name
        (class.name). Shows the currents for selected element on a drawing in
        polar coordinates.

        """

        pass


    def close_di(self, info):
        """ Close all DI files ... useful at end of yearly solution where DI
        files are left open.

        (Reset and Set Year=nnn will also close the DI files)

        """

        pass


    def estimate(self, info):
        """ Execute state estimator on present circuit given present sensor
        values.

        """

        pass

#------------------------------------------------------------------------------
#  Standalone call:
#------------------------------------------------------------------------------

if __name__ == "__main__":
    circuit = Circuit()
    executive = Executive(model=circuit)
    executive.configure_traits(filename="/tmp/circuit.pkl")

# EOF -------------------------------------------------------------------------
