#------------------------------------------------------------------------------
# Copyright (C) 2009 Richard W. Lincoln
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

""" Simulates energy trade in a power system.
"""

#------------------------------------------------------------------------------
#  Imports:
#------------------------------------------------------------------------------

import sys
import optparse

from os.path import dirname, join

from numpy import array

from pybrain.tools.shortcuts import buildNetwork
from pybrain.rl.agents import LearningAgent, PolicyGradientAgent
from pybrain.rl.learners import SPLA, ENAC
from pybrain.structure.modules import SigmoidLayer

from pylon import Case, Bus, Generator, Load
from pylon import DCOPF

from pylon.main import read_case

from pylon.readwrite import MATPOWERReader, ReSTWriter
from pylon.readwrite.rst_writer import ReSTExperimentWriter

from environment import ParticipantEnvironment
from experiment import MarketExperiment
from task import ProfitTask

#------------------------------------------------------------------------------
#  "PyretoApplication" class:
#------------------------------------------------------------------------------

class PyretoApplication(object):
    """ Simulates energy trade in a power system.
    """

    def __init__(self, file_name="", type="any", interactions=24, ac=False):
        """ Initialises a new PyretoApplication instance.
        """
        # Name of the input file.
        self.file_name = file_name
        # Format in which the case is stored.  Possible values are: 'any',
        # 'matpower', 'psat', 'matlab' and 'psse'.
        self.type = type
        # Number of interactions to perform.
        self.interactions = interactions
        # Use AC OPF routine?
        self.ac = ac

    #--------------------------------------------------------------------------
    #  Runs the application:
    #--------------------------------------------------------------------------

    def __call__(self, input, output):
        """ Forms a case from the input, associates an agent with each
            generator, performs the specified number of interactions and
            writes a report to the output.
        """
        # Get the case from the input.
        power_sys = read_case(input, self.type, self.file_name)

        experiment = one_for_one(power_sys)

        experiment.doInteractions(self.interactions)

        writer = ReSTExperimentWriter()
        writer(experiment, output)

#------------------------------------------------------------------------------
#  Associate one agent with each generator in the network:
#------------------------------------------------------------------------------

def one_for_one(smart_market):
    """ Associates an agent and a task with each generator in the network.
    """
    tasks = []
    agents = []

    for generator in smart_market.case.online_generators:
        # Create the world in which the trading agent acts.
        env = ParticipantEnvironment(asset=generator, market=smart_market)

        # Create a task that connects each agent to it's environment. The task
        # defines what the goal is for an agent and how the agent is rewarded
        # for it's actions.
        task = ProfitTask(env)

        # Create a linear controller network. Each agent needs a controller
        # that maps the current state to an action.
#        net = buildNetwork( 3, 6, 1, bias = False, outclass = SigmoidLayer )
        net = buildNetwork(1, 1, bias=False)

        net._setParameters(array([0.5]))

        # Create agent. The agent is where the learning happens. For continuous
        # problems a policy gradient agent is required.  Each agent has a
        # module (network) and a learner, that modifies the module.
#        agent = LearningAgent( module = net, learner = ENAC() )
#        agent.name = "LearningAgent-%s" % generator.name
        agent = PolicyGradientAgent(module=net, learner=ENAC())
        agent.name = "PolicyGradientAgent-%s" % generator.name

        # Backpropagation parameters.
        gradient_descent = agent.learner.gd
        # Learning rate (0.1-0.001, down to 1e-7 for RNNs).
        agent.alpha = 0.1

        # Alpha decay (0.999; 1.0 = disabled).
#        gradient_descent.alphadecay = 1.0
#
#        # momentum parameters (0.1 or 0.9)
#        gradient_descent.momentum = 0.0
#        gradient_descent.momentumvector = None
#
#        # --- RProp parameters ---
#        gradient_descent.rprop = False
#        # maximum step width (1 - 20)
#        gradient_descent.deltamax = 5.0
#        # minimum step width (0.01 - 1e-6)
#        gradient_descent.deltamin = 0.01

        # Collect tasks and agents.
        tasks.append(task)
        agents.append(agent)

    experiment = MarketExperiment(tasks, agents, power_sys)

    return experiment

#------------------------------------------------------------------------------
#  Pyreto entry point:
#------------------------------------------------------------------------------

def main():
    """ Defines the entry point for Pyreto.
    """
    parser = optparse.OptionParser("usage: pyreto [options] input_file")

    parser.add_option("-o", "--output", dest="output", metavar="FILE",
        help="Write report to FILE.")

    parser.add_option("-t", "--input-type", dest="type", metavar="TYPE",
        default="any", help="The argument following the -t is used to "
        "indicate the format type of the input data file. The types which are "
        "currently supported include: matpower, psat, psse.  If not "
        "specified Pyreto will attempt to determine the type according to the "
        "file name extension and the file header.")

    parser.add_option("-n", "--interactions", dest="interactions",
        metavar="INTERACTIONS", default=24, help="The argument following the "
        "-n is used to set the number of interactions between agents that "
        "will be performed before returning the report.")

    parser.add_option("--ac", dest="ac", default=False,
        help="Use AC OPF routine.")

    parser.add_option("-q", "--quiet", action="store_true", dest="quiet",
        default=False, help="Print less information.")

    parser.add_option("-d", "--debug", action="store_true", dest="debug",
        default=False, help="Print debug information.")

    (options, args) = parser.parse_args()

    if options.quiet:
        logger.setLevel(logging.CRITICAL)
    elif options.debug:
        logger.setLevel(logging.DEBUG)
    else:
        logger.setLevel(logging.INFO)

    # Output.
    if options.output:
        outfile = options.output
        if outfile == "-":
            outfile = sys.stdout
            logger.setLevel(logging.CRITICAL) # we must stay quiet

    else:
        outfile = sys.stdout

    # Input.
    if len(args) > 1:
        parser.print_help()
        sys.exit(1)

    elif len(args) == 0 or args[0] == "-":
        filename = ""
        if sys.stdin.isatty():
            # True if the file is connected to a tty device, and False
            # otherwise (pipeline or file redirection).
            parser.print_help()
            sys.exit(1)
        else:
            # Handle piped input ($ cat ehv3.raw | pylon | rst2pdf -o ans.pdf).
            infile = sys.stdin

    else:
        filename = args[0]
        infile   = open(filename)

    pyreto = PyretoApplication(file_name=filename, type=options.type,
        interactions=options.interactions, ac=options.ac)

    # Call the Pyreto application.
    pyreto(infile, outfile)

    try:
        infile.close() # Clean-up
    except:
        pass


if __name__ == "__main__":
    import logging
    logger = logging.getLogger()

    # Remove PyBrain handlers.
    for handler in logger.handlers:
        logger.removeHandler(handler)

    logger.addHandler(logging.StreamHandler(sys.stdout))
    logger.setLevel(logging.DEBUG)

    main()

# EOF -------------------------------------------------------------------------
