import sys
import logging

from pylon.api import Network

from pylon.ui.model_view.swarm_mv import SwarmModelView

from pylon.pyreto.api import MarketEnvironment
from pyqle.api import Swarm

#------------------------------------------------------------------------------
#  Logging:
#------------------------------------------------------------------------------

logger = logging.getLogger()

logger.addHandler(logging.StreamHandler(sys.stdout))

logger.setLevel(logging.DEBUG)

#-----------------------------------------------------------------------------
#  "main" function:
#-----------------------------------------------------------------------------

def main(argv=sys.argv):
    """ Configures a swarm model view """
    
    env = MarketEnvironment(network=Network())
    model = Swarm(environment=env)
    mv = SwarmModelView(model=model)
    mv.configure_traits()

#-----------------------------------------------------------------------------
#  Standalone call:
#-----------------------------------------------------------------------------

if __name__ == "__main__":
    sys.exit(main(sys.argv))

# EOF ------------------------------------------------------------------------
