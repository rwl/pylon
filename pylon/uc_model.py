from CIM13 import Model

from CIM13.Generation.Production \
    import GeneratingUnit, GenUnitOpCostCurve, GenUnitOpSchedule

from CIM13.LoadModel \
    import Load, ConformLoadGroup, ConformLoadSchedule

from enthought.traits.api import Instance, List, Property, on_trait_change

from enthought.traits.ui.api \
    import View, Item, TreeEditor, TreeNode, HGroup

from pylon.ui.view_model.desktop_vm \
    import DesktopViewModel, frame_icon, menubar

class UnitCommitmentModel(Model):

    Loads = Property(List(Instance(Load)), depends_on=["Contains"])

    ConformLoadGroups = Property(List(Instance(ConformLoadGroup)),
        depends_on=["Contains"])

    def _get_Loads(self):
        """ Property getter.
        """
        return [root for root in self.Contains if isinstance(root, Load)]

    def _get_ConformLoadGroups(self):
        """ Property getter.
        """
        return [r for r in self.Contains if isinstance(r, ConformLoadGroup)]

#    def _Loads_changed(self, new):
#        for load in new:
#            load._LoadGroups = self.ConformLoadGroups
#
#    def _Loads_items_changed(self, event):
#        for load in event.added:
#            load._LoadGroups = self.ConformLoadGroups

    @on_trait_change("Loads,ConformLoadGroups")
    def _SetLoadGroups(self):
        for load in self.Loads:
            load._LoadGroups = self.ConformLoadGroups


uc_tree_editor = TreeEditor(
    nodes = [
        TreeNode(node_for=[UnitCommitmentModel], label="=Model", children="",
            view=View()),
        TreeNode(node_for=[UnitCommitmentModel], children="Loads",
                 label="=Loads", add=[Load]),
        TreeNode(node_for=[UnitCommitmentModel], children="ConformLoadGroups",
                 label="=ConformLoadGroups", add=[ConformLoadGroup]),
        TreeNode(node_for=[Load], label="name"),
        TreeNode(node_for=[ConformLoadGroup], label="name")
    ],
    orientation="horizontal", editable=True
)

flat_tree_editor = TreeEditor(
    nodes=[
#        TreeNode(node_for=[Model], label="=Model", children="",
#            view=View()),
        TreeNode(node_for=[Model], children="Contains",
                 label="=Model", add=[Load, ConformLoadGroup], view=View()),
        TreeNode(node_for=[Load], label="name"),
        TreeNode(node_for=[ConformLoadGroup], label="name")
    ]
)

class ModeViewModel(DesktopViewModel):

#    traits_view = View(Item("model", editor=uc_tree_editor, show_label=False))

    traits_view = View( HGroup( Item("model",
                                     editor=flat_tree_editor,
                                     show_label=False ) ),
                        id        = "model_view_model.traits_view",
                        title     = "Common Information Model",
                        icon      = frame_icon,
                        resizable = True,
                        style     = "custom",
                        kind      = "live",
                        buttons   = [],
                        menubar   = menubar,
                        dock      = "vertical" )

if __name__ == "__main__":
    load_group = ConformLoadGroup(name="CLG1")
    load = Load(name="Load 1", LoadGroup=load_group)
    model = UnitCommitmentModel(Contains=[load, load_group])
    view_model = ModeViewModel(model=model)
    view_model.configure_traits()
