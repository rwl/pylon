from enthought.traits.api import HasTraits, Interface, implements, Instance
from enthought.enable.api import BaseTool
from enthought.enable.tools.traits_tool import Fifo, get_nested_components

class IMenuItemTool(Interface):

    menu_item = Instance(HasTraits)


class ContextMenuTool(BaseTool):
    """ Takes all tools of the parent component that implement the MenuItemTool
    and adds their menu items to a context menu that is displayed when the
    component is right clicked in 'normal' mode.

    """

    def normal_right_down(self, event):
        """ Handles the right mouse button being clicked when the tool is in
        the 'normal' state.

        If the event occurred on this tool's component (or any contained
        component of that component), the method opens a context menu with
        menu items from any tool of the parent component that implements
        MenuItemTool interface i.e. has a get_item() method.

        """

        x = event.x
        y = event.y

        # First determine what component or components we are going to hittest
        # on.  If our component is a container, then we add its non-container
        # components to the list of candidates.
#        candidates = []
        component = self.component
#        if isinstance(component, Container):
#            candidates = get_nested_components(self.component)
#        else:
#            # We don't support clicking on unrecognized components
#            return
#
#        # Hittest against all the candidate and take the first one
#        item = None
#        for candidate, offset in candidates:
#            if candidate.is_in(x-offset[0], y-offset[1]):
#                item = candidate
#                break

        for tool in component.tools:
            component.active_tool = self
            # Do it
            event.handled = True
            component.active_tool = None
            component.request_redraw()

        return


# EOF -------------------------------------------------------------------------
