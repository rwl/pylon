from enthought.traits.api import Enum, Property

color_scheme_trait = Enum(
    "X11", "Accent", "Blues", "BRBG", "BUGN", "BUPU", "Dark", "GUBU",
    "Greens", "Greys", "Oranges", "OORD", "Paired", "Pastel", "PIYG",
    "PRGN", "PUBU", "PUBUGN", "PUOR", "PURD", "Purples", "RDBU", "RDGY",
    "RDPU", "RDYLBU", "RDYLGN", "Reds", "Set", "Spectral", "YLGN",
    "YLGNBU", "YLORBR", "YLORRD", desc="a color scheme namespace",
    label="Color scheme"
)

def Alias(name, desc=""):
    """ Syntactically concise alias trait but creates a pair of lambda
    functions for every alias you declare.

    class MyClass(HasTraits):
        line_width = Float(3.0)
        thickness = Alias("line_width")

    """

    return Property(
        lambda obj: getattr(obj, name),
        lambda obj, val: setattr(obj, name, val),
        desc=desc
    )

# EOF -------------------------------------------------------------------------
