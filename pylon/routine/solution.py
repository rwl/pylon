from pylon.api import Bus, Branch

from enthought.traits.api import \
    HasTraits, Int, Float, Range, Tuple, List, Instance, Str

from enthought.traits.ui.api import \
    View, Item, Group, HGroup, VGroup, TableEditor, Spring, Label

from enthought.traits.ui.table_column import ObjectColumn

bus_pf_data_columns  = [
    ObjectColumn(name="name"),
    ObjectColumn(name="v_amplitude", label="Mag(pu)"),
    ObjectColumn(name="v_phase", label="Ang(deg)"),
    ObjectColumn(name="p_supply"),
    ObjectColumn(name="q_supply"),
    ObjectColumn(name="p_demand"),
    ObjectColumn(name="q_demand")
],

bus_pf_data_table = TableEditor(
    columns=bus_pf_data_columns,
    editable=False
)

branch_data_table = TableEditor(
    columns=[
        ObjectColumn(name="name"),
        ObjectColumn(name="source_bus"),
        ObjectColumn(name="target_bus"),
        ObjectColumn(name="p_source"),
        ObjectColumn(name="q_source"),
        ObjectColumn(name="p_target"),
        ObjectColumn(name="q_target"),
        ObjectColumn(name="p_losses"),
        ObjectColumn(name="q_losses")
    ],
    show_toolbar=False,
    deletable=False,
    editable=False
)

class PFSolution(HasTraits):

    # How many?
    n_buses = Int(label="Buses")
    n_generators = Int(label="Generators")
    committed_gens = Int
    n_loads = Int
    n_fixed = Int
    n_despatchable = Int
    shunts = Int
    n_branches = Int
    transformers = Int
    inter_ties = Int
    areas = Int

    # How much?
#    pq_label = Str("(P, Q)", label="")
#    total_gen_capacity = Tuple(Float, Float)#Range(-0.1, 0.1), labels=["P", "Q"], cols=2)
#    online_capacity = Tuple(Float, Float)#Range(-0.1, 0.1), labels=["P", "Q"], cols=2)
#    generation_actual = Tuple(Float, Float, labels=["P", "Q"], cols=2)
#    load = Tuple(Float, Float, labels=["P", "Q"], cols=2)
#    fixed = Tuple(Float, Float, labels=["P", "Q"], cols=2)
#    despatchable = Tuple(Float, Float, labels=["P", "Q"], cols=2)
#    shunt = Tuple(Float, Float, labels=["P", "Q"], cols=2)
#    total_inter_tie_flow = Tuple(Float, Float, labels=["P", "Q"], cols=2)

    total_p_gen_capacity = Float
    total_q_gen_capacity = Range(-0.1, 0.1)
    online_p_capacity = Float
    online_q_capacity = Range(-0.1, 0.1)
    p_generation_actual = Float
    q_generation_actual = Float
    p_load = Float
    q_load = Float
    p_fixed = Float
    q_fixed = Float
    p_dispatchable = Float
    q_dispatchable = Float
    p_shunt = Float
    q_shunt = Float
    p_loss = Float
    q_loss = Float
    p_charging = Float(label="Branch Charging (inj)")
    q_charging = Float(label="Branch Charging (inj)")
    total_p_inter_tie_flow = Float
    total_q_inter_tie_flow = Float

    min_voltage_magnitude = Float
    max_voltage_magnitude = Float
    min_voltage_angle = Float
    max_voltage_angle = Float

    # Buses
    buses = List(Instance(Bus))

    branches = List(Instance(Branch))

    traits_view = View(
        VGroup(
            HGroup(
                VGroup(
                    ["n_buses", "n_generators", "committed_gens", "n_loads",
                    "n_fixed", "n_despatchable", "shunts", "n_branches", "transformers",
                    "inter_ties", "areas"],
                    label="How many?", show_border=True
                ),
    #            VGroup(
    #                ["pq_label", "total_gen_capacity", "online_capacity", "generation_actual",
    #                 "load", "fixed", "despatchable", "shunt",
    #                 "total_inter_tie_flow"],
    #                 label="How much?", show_border=True
    #            ),
                VGroup(
                    HGroup(
                        Item("total_p_gen_capacity", label="Total Gen Capacity"),
                        Item("total_q_gen_capacity", show_label=False),
                    ),
                    ["total_gen_capacity", "online_capacity", "generation_actual",
                     "load", "fixed", "despatchable", "shunt",
                     "total_inter_tie_flow"],
                     label="How much?", show_border=True, springy=True
                )
            ),
            VGroup(
                Item(name="buses", editor=bus_pf_data_table, show_label=False),
                Item(
                    name="branches", editor=branch_data_table, show_label=False
                )
            )
        ),
        style="readonly"
    )

bus_opf_columns = bus_pf_data_columns + [
    ObjectColumn(name="p_lambda"),
    ObjectColumn(name="q_lambda")
]

bus_opf_data_table = TableEditor(
    columns=bus_opf_data_columns,
    editable=False
)

class OPFSolution(HasTraits):

    objective_value = Float(label="Objective Function Value")

    min_p_lambda = Float
    max_p_pambda = Float
    min_q_lambda = Float
    max_q_lambda = Float



if __name__ == "__main__":
    sol = PFSolution()
    sol.configure_traits()

# EOF -------------------------------------------------------------------------
