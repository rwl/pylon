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

""" Defines the generator element """

#------------------------------------------------------------------------------
#  Imports:
#------------------------------------------------------------------------------

from enthought.traits.api import \
    Instance, List, Int, Float, Str, Trait, Enum, Bool

from enthought.traits.ui.api import View, Item, Group

from enthought.traits.ui.api import TableEditor, InstanceEditor
from enthought.traits.ui.extras.checkbox_column import CheckboxColumn

from enthought.traits.ui.table_filter import \
    EvalFilterTemplate, MenuFilterTemplate, RuleFilterTemplate, RuleTableFilter

from pylon.dss.common.circuit_element import CircuitElementColumn

from pylon.dss.common.bus import Bus

from power_conversion_element import PowerConversionElement

#------------------------------------------------------------------------------
#  "Generator" class:
#------------------------------------------------------------------------------

class Generator(PowerConversionElement):
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
    n_phases = Int(3)

    # Bus to which the Generator is connected.  May include specific node
    # specification.
    bus_1 = Instance(Bus)

    # Nominal rated (1.0 per unit) voltage, kV, for Generator. For 2- and
    # 3-phase Generators, specify phase-phase kV. Otherwise, specify actual kV
    # across each branch of the Generator. If wye (star), specify phase-neutral
    # kV.  If delta or phase-phase connected, specify phase-phase kV.
    kv = Float(12.47, desc="Nominal rated voltage")

    # Total base kW for the Generator.  A positive value denotes power coming
    # OUT of the element, which is the opposite of a load. This value is
    # modified depending on the dispatch mode.  Unaffected by the global load
    # multiplier and growth curves.  If you want there to be more generation,
    # you must add more generators or change this value.
    kw = Float(100.0, desc="Total base kW for the Generator")

    # Generator power factor. Default is 0.80. Enter negative for leading
    # powerfactor (when kW and kvar have opposite signs.) A positive power
    # factor for a generator signifies that the generator produces vars as is
    # typical for a synchronous generator.  Induction machines would be
    # specified with a negative power factor.
    pf = Float(0.80, desc="Generator power factor")

    # Specify the base kvar.  Alternative to specifying the power factor.  Side
    # effect: the power factor value is altered to agree based on present value
    # of kW.
    kvar = Float(5.0)

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
    model = Trait(
        "Constant kW", {
            "Constant kW": 1, "Constant Y": 2, "Constant kW & kV": 3,
            "Const kW, Fixed Q": 4, "Const kW, Fixed Q (Const X)": 5,
            "User model": 6, "Constant kW, kVar. Limited I": 7
        },
        desc="Model to use for generation variation with voltage"
    )

    # Minimum per unit voltage for which the Model is assumed to apply. Below
    # this value, the load model reverts to a constant impedance model.
    v_min_pu = Float(0.95, desc="Minimum per unit voltage")

    # Maximum per unit voltage for which the Model is assumed to apply. Above
    # this value, the load model reverts to a constant impedance model.
    v_max_pu = Float(1.05, desc="Maximum per unit voltage")

    # Dispatch shape to use for yearly simulations.  Must be previously defined
    # as a Loadshape object. If this is not specified, the daily dispatch shape
    # is repeated. If the generator is assumed to be ON continuously, specify
    # this value as FIXED, or designate a curve that is 1.0 per unit at all
    # times. Nominally for 8760 simulations.  If there are fewer points in the
    # designated shape than the number of points in the solution, the curve is
    # repeated.
    yearly = Str(desc="Dispatch shape to use for yearly simulations")

    # Dispatch shape to use for daily simulations.  Must be previously defined
    # as a Loadshape object of 24 hrs, typically.  If generator is assumed to
    # be ON continuously, specify this value as FIXED, or designate a Loadshape
    # object that is 1.0 perunit for all hours.
    daily = Str(desc="Dispatch shape to use for daily simulations")

    # Load shape to use for duty cycle dispatch simulations such as for wind
    # generation. Must be previously defined as a Loadshape object. Typically
    # would have time intervals less than 1 hr -- perhaps, in seconds.
    # Designate the number of points to solve using the Set Number=xxxx
    # command.  If there are fewer points in the actual shape, the shape is
    # assumed to repeat.
    duty = Str(desc="Load shape to use for duty cycle dispatch simulations")

    # In default mode, gen is either always on or follows dispatch curve as
    # specified.  Otherwise, the gen comes on when either the global default
    # load level or the price level exceeds the dispatch value.
    disp_mode = Enum("Always On", "Follow Curve")

    # If = 0.0 Then Generator follow dispatch curves, if any.  If > 0  Then
    # Generator is ON only when either the price signal exceeds this value or
    # the load multiplier (set loadmult=) times the default yearly growth
    # factor exceeds this value.  Then the generator follows dispatch curves,
    # if any (see also Status).
    disp_value = Float

    # Connection type
    conn = Enum("Wye", "LN", "Delta", "LL", desc="Connection type")

    # Removed due to causing confusion - Add neutral impedance externally.
    r_neut = Float(-1.0, desc="Neutral resistance")

    # Removed due to causing confusion - Add neutral impedance externally.
    x_neut = Float(0.0, desc="Neutral reactance")

    # {Fixed|Variable}.  If Fixed, then dispatch multipliers do not apply. The
    #  generator is alway at full power when it is ON. Default is Variable
    # (follows curves).
    status = Enum("Variable", "Fixed")

    # An arbitrary integer number representing the class of Generator so that
    # Generator values may be segregated by class.
    klass = Int(1)

    # Per Unit voltage set point for Model = 3  (typical power flow model).
    v_pu = Float(1.0, desc="Per unit voltage set point for model = 3")

    # Maximum kvar limit for Model = 3.  Defaults to twice the specified load
    # kvar. Always reset this if you change PF or kvar properties.
    max_kvar = Float(desc="Maximum kVar limit for model = 3")

    # Minimum kvar limit for Model = 3. Enter a negative number if generator
    # can absorb vars.  Defaults to negative of Maxkvar.  Always reset this if
    # you change PF or kvar properties.
    min_kvar = Float(desc="Minimum kVar limit for model = 3")

    # Deceleration factor for P-V generator model (Model=3).  Default is 0.1.
    # If the circuit converges easily, you may want to use a higher number such
    # as 1.0. Use a lower number if solution diverges. Use Debugtrace=yes to
    # create a file that will trace the convergence of a generator model.
    pv_factor = Float(0.1, desc="Deceleration factor for P-V generator model")

    # {Yes | No}  Forces generator ON despite requirements of other dispatch
    # modes.  Stays ON until this property is set to NO, or an internal
    # algorithm cancels the forced ON state.
    force_on = Bool(False, desc="Forces generator on")

    # kVA rating of electrical machine. Defaults to 1.2* kW if not specified.
    # Applied to machine or inverter definition for Dynamics mode solutions.
    kva = Float(1.2, desc="kVA rating of electrical machine")

    # MVA rating of electrical machine.  Alternative to using kVA=.
    mva = Float(desc="Alternative to kVA")

    # Per unit synchronous reactance of machine. Presently used only for
    # Thevinen impedance for power flow calcs of user models (model=6).
    # Typically use a value 0.4 to 1.0. Default is 1.0
    x_d = Float(1.0, desc="Per unit synchronous reactance of machine")

    # Per unit transient reactance of the machine.  Used for Dynamics mode and
    # Fault studies.  Default is 0.27.  For user models, this value is used for
    # the Thevinen/Norton impedance for Dynamics Mode.
    x_dp = Float(0.27, desc="Per unit transient reactance of the machine")

    # Per unit subtransient reactance of the machine.  Used for Harmonics.
    # Default is 0.20.
    x_dpp = Float(0.2, desc="Per unit subtransient reactance of the machine")

    # Per unit mass constant of the machine.  MW-sec/MVA.
    h = Float(desc="Per unit mass constant of the machine (MW-sec/MVA)")

    # Damping constant.  Usual range is 0 to 4. Default is 1.0.  Adjust to get
    # damping
    d = Float(1.0, desc="Damping constant")

    # Name of DLL containing user-written model, which computes the terminal
    # currents for Dynamics studies, overriding the default model.  Set to
    # "none" to negate previous setting.
    user_model = Str

    # String (in quotes or parentheses) that gets passed to user-written model
    # for defining the data required for that model.
    user_data = Str

    # Name of user-written DLL containing a Shaft model, which models the prime
    # mover and determines the power on the shaft for Dynamics studies.
    # Models additional mass elements other than the single-mass model in the
    # DSS default model. Set to "none" to negate previous setting.
    shaft_model = Str

    # String (in quotes or parentheses) that gets passed to user-written shaft
    # dynamic model for defining the data for that model.
    shaft_data = Str

    # {Yes | No }  Default is no.  Turn this on to capture the progress of the
    # generator model for each iteration.  Creates a separate file for each
    # generator named "GEN_name.CSV".
    debug_trace = Bool(False)

    #--------------------------------------------------------------------------
    #  Views:
    #--------------------------------------------------------------------------

    traits_view = View(
        [
            # CircuitElement traits
            "enabled", "base_freq",
            # PowerConversionElement traits
            "spectrum", "inj_current",
            # Generator traits
            "bus_1", "kv", "kw", "pf", "kvar", "model", "v_min_pu", "v_max_pu",
            "yearly", "daily", "duty", "disp_mode", "disp_value", "conn",
            "r_neut", "x_neut", "status", "klass", "v_pu", "max_kvar",
            "min_kvar", "pv_factor", "force_on", "kva", "mva", "x_d", "x_dp",
            "x_dpp", "h", "d", "user_model", "user_data", "shaft_model",
            "shaft_data", "debug_trace"
        ],
        id="pylon.conversion.generator",
        resizable=True, title="Generator",
        buttons=["OK", "Cancel", "Help"],
        close_result=False
    )

#------------------------------------------------------------------------------
#  Generator table editor:
#------------------------------------------------------------------------------

generators_table_editor = TableEditor(
    columns=[
        # CircuitElement traits
        CheckboxColumn(name="enabled"),
        CircuitElementColumn(name="base_freq"),
        # PowerConversionElement traits
        CircuitElementColumn(name="spectrum"),
        CircuitElementColumn(name="inj_current"),
        # Generator traits
        CircuitElementColumn(name="bus_1"),
        CircuitElementColumn(name="kv"),
        CircuitElementColumn(name="kw"),
        CircuitElementColumn(name="pf"),
        CircuitElementColumn(name="kvar"),
    ],
    other_columns = [  # not initially displayed
        CircuitElementColumn(name="model"),
        CircuitElementColumn(name="v_min_pu"),
        CircuitElementColumn(name="v_max_pu"),
        CircuitElementColumn(name="yearly"),
        CircuitElementColumn(name="daily"),
        CircuitElementColumn(name="duty"),
        CircuitElementColumn(name="disp_mode"),
        CircuitElementColumn(name="disp_value"),
        CircuitElementColumn(name="conn"),
        CircuitElementColumn(name="r_neut"),
        CircuitElementColumn(name="x_neut"),
        CircuitElementColumn(name="status"),
        CircuitElementColumn(name="klass"),
        CircuitElementColumn(name="v_pu"),
        CircuitElementColumn(name="max_kvar"),
        CircuitElementColumn(name="min_kvar"),
        CircuitElementColumn(name="pv_factor"),
        CircuitElementColumn(name="force_on"),
        CircuitElementColumn(name="kva"),
        CircuitElementColumn(name="mva"),
        CircuitElementColumn(name="x_d"),
        CircuitElementColumn(name="x_dp"),
        CircuitElementColumn(name="x_dpp"),
        CircuitElementColumn(name="h"),
        CircuitElementColumn(name="d"),
        CircuitElementColumn(name="user_model"),
        CircuitElementColumn(name="user_data"),
        CircuitElementColumn(name="shaft_model"),
        CircuitElementColumn(name="shaft_data"),
        CircuitElementColumn(name="debug_trace"),
    ],
    show_toolbar=True, deletable=True,
    filters=[EvalFilterTemplate, MenuFilterTemplate, RuleFilterTemplate],
    search=RuleTableFilter(),
    row_factory=Generator,
#    row_factory_kw={"__table_editor__": ""}
)

#------------------------------------------------------------------------------
#  Standalone call:
#------------------------------------------------------------------------------

if __name__ == "__main__":
    Generator().configure_traits()

# EOF -------------------------------------------------------------------------
