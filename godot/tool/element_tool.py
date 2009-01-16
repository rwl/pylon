from enthought.enable.api import BaseTool
from enthought.enable.tools.traits_tool import Fifo, get_nested_components

class ElementTool(BaseTool):
    """ Tool to edit the traits of a HasTraits element referenced an  Enable
    component when double clicked. Handles containers and canvases so that they
    get edited only if their background regions are clicked.

    """

    # This tool does not have a visual representation (overrides BaseTool).
    draw_mode = "none"
    # This tool is not visible (overrides BaseTool).
    visible = False


    def normal_left_dclick(self, event):
        """ Handles the left mouse button being double-clicked when the tool
        is in the 'normal' state.

        If the event occurred on this tool's component (or any contained
        component of that component), the method opens a Traits UI view on the
        object referenced by the 'element' trait of the component that was
        double-clicked, setting the tool as the active tool for the duration
        of the view.

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

        if hasattr(component, "element"):
            if component.element is not None:
                component.active_tool = self
                component.element.edit_traits(kind="livemodal")
                event.handled = True
                component.active_tool = None
                component.request_redraw()
        return

# EOF -------------------------------------------------------------------------
