#------------------------------------------------------------------------------
# Copyright (C) 2007 Richard W. Lincoln
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

""" The base of all Q-Learning-like algorithms :

 * Provides a structure to memorise or compute the Q(s,a)
 * Contains all the parameters used in the Q-Learning update rules
 * Contains all the parameters used to control convergence

"""

#------------------------------------------------------------------------------
#  Imports:
#------------------------------------------------------------------------------

import logging
import math
from random import Random

from enthought.traits.api import \
    HasTraits, Any, Instance, Int, Enum, Bool, Float, implements

from pyqle.selector.i_selector import ISelector
from pyqle.qlearning.abstract_reward_store import AbstractRewardStore
from pyqle.qlearning.action_state_pair import ActionStatePair

# Setup a logger for this module.
logger = logging.getLogger(__name__)

#------------------------------------------------------------------------------
#  "Selector" class:
#------------------------------------------------------------------------------

# October 4th 2006 : return to the old version, where boltzmann, epsilon-greedy
# *  and rouletteWheel are declared inside this class :
# *  too much problems in defining and monitoring the parameters of each
# *  choosing strategy (epsilon, tau, modifying epsilon...) (fd)

class MemorySelector(HasTraits):
    """ The base of all Q-Learning-like algorithms :

     * Provides a structure to memorise or compute the Q(s,a)
     * Contains all the parameters used in the Q-Learning update rules
     * Contains all the parameters used to control convergence

    """

    implements(ISelector)

    #--------------------------------------------------------------------------
    #  Trait definitions:
    #--------------------------------------------------------------------------

    # Memorising or computing Q(s,a)
    memory = Instance(AbstractRewardStore)

    # The parameter for Boltzmann Action selection Strategy
    tau = Float(0.5)

    # Learning rate
    alpha = Float(0.9)

    # Discount rate
    gamma = Float(0.9)

    epsilon = Float(0.5)

    generator = Instance(Random, Random())

    # Factor by which we multiply alpha at each learning step (geometric
    # decay)
    # Note : geometric decay does no insure convergence.
    decay_alpha = Float(0.999999999)

    # Number of learning steps
    count = Float(1.0)

    # Power of decay when alpha=1/(count^alpha_decay_power)
    #
    # @see http://www.cs.tau.ac.il/~evend/papers/ql-jmlr.ps
    # Learning rates for Q-Learning
    alpha_decay_power = Float(0.8)

    # How convergence is controlled?
    #
    # True: alpha decays geometrically
    # False: alpha decays exponentially
    geometric_decay = Bool(False)

    # How to implement randomness ?
    #
    # epsilon-greedy
    # Roulette wheel selection
    # Boltzmann
    #
    # Note: Roulette wheel or Boltzmann selection makes epsilon useless
    roulette_wheel = Bool(False)

    epsilon_greedy = Bool(True)

    boltzmann = Bool(False)

    #--------------------------------------------------------------------------
    #  Public interface
    #--------------------------------------------------------------------------

    def get_state_action_value(self, state, action):
        """ Get the value of Q(s,a) for a given state-action pair """

        return self.memory[state, action]


    def set_value(self, start_state, action, resulting_state, qsa):
        """ Set the value of Q(s,a) for a given state-action pair """

        self.memory.put(start_state, action, resulting_state, qsa)


    def set_geometric_alpha_decay(self):
        """ Set alpha to decay geometrically """

        self.geometric_decay = True


    def set_exponential_alpha_decay(self):
        """ Set alpha to decay exponentially """

        self.geometric_decay = False


    def set_roulette_wheel(self):
        """ Implement randomness using roulette wheel selection """

        self.roulette_wheel = True
        self.epsilon_greedy = False
        self.boltzmann = False


    def set_epsilon_greedy(self):
        """ Implement randomness using epsilon greedy selection """

        self.epsilon_greedy = True
        self.roulette_Wheel = False
        self.boltzmann = False


    def set_boltzmann(self):
        """ Implement randomness using boltzmann selection """

        self.epsilon_greedy = False
        self.roulette_wheel = False
        self.boltzmann = True


    def learn(self, start_state, chosen_action, arrival_state, reward):
        """ Learning from experience.

        @param start_state
                   the start state.
        @param chosen_action
                   the chosen action.
        http://www.cs.ualberta.ca/~sutton/book/ebook/node65.html
        Sutton & Barto p 149 Q-Learning

        @param arrival_state
                   the arrival state.
        @param reward
                    immediate reward.

        """

        if self.geometric_decay:
            self.alpha *= self.decay_alpha
        else:
            self.alpha = 1 / math.pow(self.count + 1.0, self.alpha_decay_power)

        self.count += 1

        if self.memory.map.has_key(ActionStatePair(chosen_action, start_state)):
            qsa = self.memory.map[ActionStatePair(chosen_action, start_state)]
        else:
            qsa = None

        action_list = arrival_state.get_action_list()
        print "Selector action list:", action_list
        if action_list.n_actions != 0:
            asp = ActionStatePair(chosen_action, start_state)
            if self.memory.map.has_key(asp):
                arrival_state = ArrivalState(action_list[0], arrival_state)
                maxqsap = self.memory.map[arrival_state]
                for action in action_list:
                    aprime = action
                    qsap = self.memory[arrival_state, aprime]
                    if qsap > maxqsap:
                        maxqsap = qsap
                qsa += self.alpha * reward + self.gamma * maxqsap - qsa
                self.memory.put(start_state, chosen_action, arrival_state, qsa)
        else:
            self.memory.put(
                start_state, chosen_action, arrival_state,
                qsa + self.alpha * reward - qsa
            )


    def choose(self, action_list):
        """ Choose one of the legal moves """

        if self.roulette_wheel:
            return self._roulette_wheel_choice(action_list)
        if self.epsilon_greedy:
            return self._epsilon_greedy_choice(action_list)
        if self.boltzmann:
            return self._boltzmann_choice(action_list)
        return

    #--------------------------------------------------------------------------
    #  Protected interface
    #--------------------------------------------------------------------------


    def _roulette_wheel_choice(self, action_list):
        """ Roulette Wheel selection of the next action : the probability
        for an action to be chosen is relative to its Q(s,a) value

        TODO DEBUG : not valid if Q(s,a) can be negative !!!

        """

        if (len(action_list) == 0):
            return
        s = action_list.get_state()
        sum = 0
        for action in action_list:
            index = action_list.index(action)
            sum += self.memory[s, action_list.get(index)] + 1

        choice = self.generator.random() * sum
        indice = 0
        partial_sum = self.memory[s, action_list.get(indice)] + 1

        while choix > partial_sum:
            indice += 1
            partial_sum += 1 + self.memory[s, action_list.get(indice)]

        return action_list[indice]


    def _epsilon_greedy_choice(self, action_list):
        """ Epsilon-greedy choice of next action """

        print "AL:", action_list
        if action_list.n_actions == 0:
            return

        state = action_list.state
        best_action = action_list.actions[0]
        maxqsap = self.memory.get(state, best_action)

        for action in action_list.actions:
            if self.memory.map.has_key(ActionStatePair(action, state)):

                qsap = self.memory.map[ActionStatePair(action, state)]
                if qsap > maxqsap:
                    maxqsap = qsap
                    best_action = action

        # TODO Beginning the method with this test should speed up the program
        if self.generator.random() > self.epsilon:
            return best_action
        else:
            action = self.generator.randint(0, action_list.n_actions-1)
            return action_list.actions[action]


    def _boltzmann_choice(self, action_list):
        """ Chooses an action according to the Boltzmann protocol """

        if (len(action_list) == 0):
            return
        state = action_list.get_state()
        sum = 0
        tab = [float() for idx in range(len(action_list))]

        for action in action_list:
            index = action_list.index(action)
            sum += math.exp(
                self.memory[state, action_list.get(index)] / self.tau
            )
            tab[index] = sum

        choice = self.generator.random() * sum

        for action in action_list:
            index = action_list.index(action)
            if choix <= tab[index]:
                return action_list[index]

        print choice + " " + "Wrong"
        return


#    def best_action(self, state):
#        """ Auxiliary/debug method : find the best action from a state """
#
#        action_list = state.get_action_list()
#
#        if (len(action_list) == 0):
#            return
#
#        best_action = action_list[0]
#        maxqsap = self.memory[state, best_action]
#
#        for action in action_list:
#            qsap = self.memory[s, action]
#            if qsap > maxqsap:
#                maxqsap = qsap
#                best_action = action
#
#        return best_action
#
#
#    def to_string(self):
#        return str(self.memory)
#
#
#    def extract_dataset(self):
#        return self.memory.extract_dataset()

# EOF -------------------------------------------------------------------------
