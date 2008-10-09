""" An action set for the Lorenz plug-in """

#------------------------------------------------------------------------------
#  Imports:
#------------------------------------------------------------------------------

from enthought.envisage.ui.action.api import Action, Group, Menu, ToolBar

from enthought.envisage.ui.workbench.api import WorkbenchActionSet

#------------------------------------------------------------------------------
#  "LorenzActionSet" class:
#------------------------------------------------------------------------------

class LorenzActionSet(WorkbenchActionSet):
    """ An action set for the Lorenz plug-in """

    #--------------------------------------------------------------------------
    #  "ActionSet" interface:
    #--------------------------------------------------------------------------

    # The action set"s globally unique identifier:
    id = "enthought.plugins.lorenz.action_set"

#    menus = [
#        Menu(
#            name="&File", path="MenuBar",
#            groups=[
#                "OpenGroup", "CloseGroup", "SaveGroup",
#                "ImportGroup", "ResourceGroup", "ExitGroup"
#            ]
#        ),
#        Menu(
#            name="&New", path="MenuBar/File", group="OpenGroup",
#            groups=["ContainerGroup", "ComponentGroup", "OtherGroup"]
#        )
#    ]

    actions = [
        Action(
            path="MenuBar/File/New", group="ComponentGroup",
            class_name="enthought.plugins.lorenz.new_lorenz_action:"
            "NewLorenzAction"
        )
    ]
