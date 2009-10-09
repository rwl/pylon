__author__ = 'Richard W. Lincoln, r.w.lincoln@gmail.com'

import random

from pybrain.rl.learners.rllearner import RLLearner
from pybrain.structure.modules.module import Module

#class Action:
#    """ For classes representing the operations that an agent can perform in a
#        particular simulation. This may simply indicate an operation or may
#        fully encapsulate data and methods actually used in performing the
#        operation.
#    """
#    def getID(self):
#        """ Retrieve the identifier for this Action.
#        """
#
#class ActionDomain:
#    """ Representation of the space of possible operations an agent can perform
#        in a particular environment.
#
#        The type of Action as well as action identifier may be paramertized.
#        These are similar to the Key/Value types that may be parameterized for
#        Hasthtable.
#    """
#
#    def getAction(self, ID):
#        """ Retrieves the Action indicated by the id object. Should return null
#            if the id does not match an existing Action.
#        """
#
#    def getIDList(self):
#        """ Retrieve a list of the identifiers for all Actions in this domain.
#        """
#
#    def size(self):
#        """ Reports the number of Actions in this domain.
#        """

#class SimpleEventGenerator:
#    """ Generate discrete random events from a given distribution.
#    """
#
#    def __init__(self, distrib):
#        # Probability distribution function.
#        distrib = []
#
#        engine = Random()
#
#
#    def nextEvent(self):
#        eventIndex = 0
#        randValue = self.engine.nextDouble()
#
#        while (randValue > 0.0) and (eventIndex < len(self.distrib)):
#            randValue -= self.distrib[eventIndex]
#            eventIndex += 1
#
#        return eventIndex - 1


def eventGenerator(distrib):
    eventIndex = 0
    randValue = random.random()

    while (randValue > 0.0) and (eventIndex < len(distrib)):
        randValue -= distrib[eventIndex]
        eventIndex += 1

    yield eventIndex - 1


class PropensityTable(Module):
    """ Interface for building a stateless reinforcement learning policy. This
        type of policy simply maintains a distribution guiding action choice
        irrespective of the current state of the world. That is, it simply
        maintains a likelihood of selection for each action for all world
        states.

        This is essentially a discrete probability distribution governing the
        choice of Action from a given ActionDomain, irrespective of the state
        of the world.
    """

    def __init__(self, numActions, actionDomain, initProbs=None, name=None):
        Module.__init__(self, 1, 1, name)
        self.numStates = numStates
        self.numActions = numActions

        # Each possible action has a propensity associated with it. Essentially
        # the likelyhood that each action will be chosen.
        self.propensities = zeros(self.numActions)

        # Here a probability distribution function (pdf) is an array of
        # probability values. When used in conjuction with the eventGenerator,
        # a value indicates the likelihood that its index will be selected.
        #
        # Each Action has an ID and each Action ID has an index in the list of
        # IDs kept by the ActionDomain. The corresponding index in this
        # probability distribution function contains a probability value for
        # that ID. So we have a mapping from probabilities to Action IDs and
        # from Action IDs to Actions. This allows the evenGenerator to use the
        # pdf to select Actions from the ActionDomain according to the
        # specified probability distribution.
        #
        # The probability values are modified by a RLLearner according to the
        # implemented learning algorithm.
#        self.probDistFunction = zeros(numActions)
#        # Initialize to uniform distribution.
#        for i in range(numActions):
#            self.probDistFunction[i] = 1.0 / numActions
        self.probDistFunction = array(1.0 / numActions, (numActions, 1))

        # Random number eventGenerator needed for the randomEngine event
        # eventGenerator.
        self.randomEngine = random.Random()

        # Generates randomEngine events (action selections) according to the
        # probabilities over all actions in the ActionDomain. Probabilities
        # are maintained in probDistFunction.
        self.eventGenerator = eventGenerator

        # The collection of possible Actions an agent is allowed to perform.
#        domain = [0, 1, 2, 3] # N S E W
        self.domain = actionDomain

        # List of action ID's in the domain. Allows us to map from int values
        # chosen given by the event generator to actions in the domain.
        self.actionIDList = []

        # Records the last action choosen by this policy.
        self.lastAction = None

        self.init()


    def _forwardImplementation(self, inbuf, outbuf):
        """ Actual forward transformation function.
        """
#        outbuf[0] = self.getMaxAction(inbuf[0])
        outbuf[0] = self.generateAction()


    def init(self):
        self.actionIDList = self.domain.keys()
#        self.eventGenerator = SimpleEventGenerator(self.probDistFunction,
#                                                   self.randomEngine)
        self.eventGenerator = eventGenerator
        # Need to init the lastAction to something. Choose a random action.
        self.lastAction = self.generateAction()

        self.propensities = zeros(self.numActions)


    def getPropensity(self, ID):
        index = self.actionIDList.index(ID)
        return self.propensities[index]


    def setPropensity(self, ID, prop):
        index = self.actionIDList.index(ID)
        self.propensities[index] = prop


    def generateAction(self):
        """ Choose an Action according to the current probability distribution
            function.
        """
        # Pick the index of an action. Note: indexes start at 0.
        chosenIndex = self.eventGenerator.next(self.probDistFunction)
        chosenID = self.actionIDList.get(chosenIndex)
        chosenAction = self.domain[chosenID]

        self.lastAction = chosenAction

        return chosenAction


    def reset(self):
        """ Reset this policy. Reverts to a uniform probability distribution
            over the domain of actions. This only modifies the probability
            distribution. It does not reset the RandomEngine.
        """
        numActions = self.numActions
        for i in range(numActions):
            self.probDistFunction[i] = 1.0 / numActions


    def setDistribution(self, distrib):
        """ Set the probability distribution used in selecting actions from the
            action domain. The distribution is given as an array of floats.
        """
        self.probDistFunction = distrib
#        self.eventGenerator.setState(distrib)


    def getProbability(self, actionID):
        """ Gets the current probability of choosing an action. Parameter
            actionIndex indicates which action in the policy's domain to
            lookup.
        """
        index = self.actionIDList.index(actionID)
        return self.probDistFunction[index]


    def setProbability(self, actionID, value):
        """ Updates the probability of choosing the indicated Action.
        """
        index = self.actionIDList.index(actionID)
        self.probDistFunction[index] = value
#        self.eventGenerator.setState(self.probDistFunction)


class RothErev(RLLearner):
    """ For classes that implement reinforcement learning algorithms. Classes
        implementing this interface are responsible for driving the learning
        process of specific algorithms.

        Reinforcement learning algorithms make use of a policy to represent
        learned knowledge. Policies themselves require access to the space of
        possible actions, represented by ActionDomains. As such an
        ReinforcementLearner will make use of with a StatelessPolicy and an
        ActionDomain.

        Experimentation, initial propensity and recency.

        A. E. Roth, I. Erev, D. Fudenberg, J. Kagel, J. Emilie and R. X. Xing,
        "Learning in Extensive-Form Games: Experimental Data and Simple Dynamic
        Models in the Intermediate Term," Games and Economic Behavior,
        Special Issue: Nobel Symposium, vol. 8, January 1995, 164-212.

        A. E. Roth, I. Erev, "Predicting How People Play Games with Unique
        Mixed-Strategy Equilibria," American Economics Review, Volume 88,
        1998, 848-881.
    """

    def __init__(self, boltzmannTemp=10.0, useBoltz=False, experimentation=0.5,
                 initialPropensity=100.0, recency=0.5):
        # Cooling parameter for Gibbs-Boltmann cooling.
        # For the Gibbs-Boltzmann probability method used in VRELearner.
        self.boltzmannTemp = boltzmannTemp
        self.useBoltz = useBoltz

        # The tendency for experimentation among action choices. The algorithm
        # will sometimes choose non-optimal Actions in favour of exploring the
        # domain. This allows the algortithm to get a more accurate picture of
        # the domain and find Actions that yield better rewards than previously
        # known.
        self.experimentation = experimentation

        # The initial propensity value assigned to all actions. Used instead of
        # a scaling parameter.
        self.initialPropensity = initialPropensity

        # The degree to which actions are 'forgotten'. Used to degrade the
        # propensity for choosing actions. Meant to make recent experience more
        # prominent than past experience in the action choice process.
        self.recency = recency

        # Number of possible actions.
        self.domainSize = -1

        # Represents learned knowledge.
#        self.policy = REPolicy()

        # Last action chosen from the policy.
        self.lastSelectedAction = None

        # List of action ID's in the domain. Allows us to map from propensities
        # to actions in the domain.
        self.actionIDList = []

        # How many times this learner has been updated.
        self.period = 0

        # Initialise the choice probabilities.
        if policy is not None:
            self.updateProbabilities()

        self.init()


    def setModule(self, module):
        super(RothErev, self).setModule(module)
        self.domainSize = len(module.actionDomain)
        self.actionIDList = module.actionDomain.keys()


    def init(self):
        """ Finishes initialising the learner.
        """
        self.domainSize = len(self.module.actionDomain)
        self.actionIDList = self.module.actionDomain.keys()

        initProp = self.initialPropensity

        for ID in self.actionIDList:
            self.module.setPropensity(ID, initProp)

        self.lastSelectedAction = self.chooseAction()


    def updatePropensities(self, reward):
        """ Update the propensities for all actions. The propensity for last
            action chosen will be updated using the feedback value that
            resulted from performing the action.

            If j is the index of the last action chosen, r_j is the reward
            received for performing j, i is the current action being updated,
            q_i is the propensity for i, and phi is the recency parameter,
            then this update function can be expressed as

                    q_i = (1-phi) * q_i + E(i, r_j)
        """
        phi = self.recency

        for i in range(self.domainSize):
            carryOver = (1 - phi) * self.module.getPropensity(i)
            experience = self.experience(i, reward)
            self.module.setPropensity(i, carryOver + experience)
#            propensities[i] = (1 - r) * propensities[i] + experience(i, reward)


    def experience(self, actionIndex, reward):
        """ This is the standard experience function for the Roth-Erev
            algorithm. Here propensities for all actions are updated and
            similarity does not come into play. That is, all action choices are
            assumed to be equally similar. If the actionIndex points to the
            action the reward is associated with (usually the last action
            taken) then simply adjust the weight by the experimentation.
            Otherwise, adjust the weight by a smaller portion of the reward.

            If j is the index of the last action chosen, r_j is the reward
            received for performing j, i is the current action being updated,
            n is the size of the action domain and e is the experimentation
            parameter, then this experience function  can be expressed as
                           _
                          |  r_j * (1-e)         if i = j
              E(i, r_j) = |
                          |_ r_j * (e /(n-1))    if i != j
        """
        e = self.experimentation
        rewardedIndex = self.actionIDList.index(self.lastSelectedAction)

        if actionIndex == rewardedIndex:
            experience = reward * (1 - e)
        else:
            experience = reward * (e / (self.domainSize - 1))

        return experience


    def updateProbabilities(self):
        """ Updates the probability for each action to be chosen in the policy.
            Uses a proportional probability unless the given parameters say to
            use a Gibbs-Bolztmann distribution.
        """
        if self.parameters.useBoltz:
            self.generateBoltzmanProbs()
        else:
            # Proportional probability method.
            propensities = self.module.propensities

            summedProps = 0.0
            for prop in propensities:
                summedProps += prop

            for index, actionID in enumerate(self.actionIDList):
                newProb = propensities[index] / summedProps
                self.module.setProbability(actionID, newProb)


    def generateBoltzmanProbs(self):
        """ Generate action probabilities using a Boltzmann distribution with a
            constant temperature.
        """
        propensities = self.module.propensities
        coolingParam = self.boltzmannTemp

        summedExps = 0.0
        for prop in propensities:
            summedExps += math.exp(prop / coolingParam)

        # For each action calculate the associated choice probability.
        #    p(i) = [ e ^(q(i)/T) ] / [ Sum_over_all_j(e ^ (q(j)/T)) ]
        for index, actionID in enumerate(self.actionIDList):
            newProb = math.exp(propensities[index] / coolingParam) / summedExps
            self.module.setProbability(actionID, newProb)


    def learn(self):
        """ Learn on the current dataset, for a single epoch.

            This activates the learning process according to the modified
            Roth-Erev learning algorithm. Feedback is interpreted as reward
            for the last action chosen by this engine. Entries in the policy
            associated with this Action are updated accordingly.

            Initiate the learning process using given feedback. Feedback is
            associated with a the last Action chosen by this engine and is
            interpreted as a reward for that Action. It is used to update the
            probability for choosing the Action according to the specific
            learning algorithm.

            Feedback is parameterized since required input will vary depending
            on the specific reinforcement learning algorithm and the particular
            simulation environment.

            Note: Most often feedback is for the last Action chosen, so given
            ActionID will usually point to this Action. As such, many RLEnigine
            implementations may also provide update() methods that simply
            accept feedback and associate it with the last Action chosen.
        """
#        reward = self.ds.getSequence(self.ds.getNumSequences())[2]
        rewards = self.ds['reward']
        self.updatePropensities(rewards[-1])
        self.updateProbabilities()
        self.period += 1


#    def getAction(self):
#        """ Activates the module with the last observation and stores the
#            result as last action.
#
#            Elicits a new choice of action. The action will be chosen according
#            to selection rule of the SimpleStatelessPolicy. Actions are chosen
#            from a DiscreteFiniteDomain.
#        """
##        nextAction = self.policy.generateAction()
#        nextAction = super(RothErev, self).getAction()
##        self.lastSelectedAction = nextAction
#        return nextAction


    def reset():
        """ Clear all learned knowledge. The Action propensities are set to the
            current initial value and the probability values in the policy.
        """
        super(RothErev, self).reset()
        self.init()


#    def makeParameters(self):
#        """ Create a default set of parameters that can be used with this
#            learner.
#        """
#        raise NotImplementedError


    def validateParameters(self):
        """ Checks that the current values for all parameters are valid.
        """
        valid = True
        if self.boltzmannTemp < 0.0:
            raise ValueError, "Cooling parameter for Gibbs/Bolzmann "
            "probability generation must be a positive value."
            valid = False
        if not 0.0 <= self.experimentation <= 1.0:
            raise ValueError, "Experimentation value must be between "
            "zero and one."
            valid = False
        if self.initialPropensity < 0.0:
            raise ValueError, "Initial propensity value must be "
            "nonnegative."
            valid = False
        if not 0.0 <= self.recency <= 1.0:
            raise ValueError, "Recency value must be between zero and one."
            valid = False
        return valid


class VRELearner(RELearner):
    """ Variant Roth-Erev Learner

        This ReinforcementLearner implements a variation of the Roth-Ere'ev
        algorithm as presented in:

            James Nicolaisen, Valentin Petrov, and Leigh Tesfatsion, "Market
            Power and Efficiency in a Computational Electricity Market with
            Discriminatory Double-Auction Pricing," IEEE Transactions on
            Evolutionary Computation, Volume 5, Number 5, 2001, 504-523.

        See RELearner for details on the original Roth-Erev algorithm
    """
    def updateProbabilities(self):
        """ Updates the probability for each action to be chosen in the policy.
        """
        self.generateBoltzmanProbs()

    def experience(self, actionIndex, reward):
        """ This is an altered version of the experience function for used in
            the standard Roth-Erev algorithm.  Like in RELearner, propensities
            for all actions are updated and similarity does not come into play.
            If the actionIndex points to the action the reward is associated
            with (usually the last action taken) then simply adjust the weight
            by the experimentation. Otherwise increase the weight of the action
            by a small portion of its current propensity.

            If j is the index of the last action chosen, r_j is the reward
            received for performing j, i is the current action being updated,
            q_i is the propensity for i, n is the size of the action domain and
            e is the experimentation parameter, then this experience function
            can be expressed as:

                          |  r_j * (1-e)         if i = j
              E(i, r_j) = |
                          |_ q_i * (e /(n-1))    if i != j
        """
        e = self.parameters.experimentation
        rewardedIndex = self.actionIDList.index(self.lastSelectedAction)

        if actionIndex == rewardedIndex:
            experience = reward * (1 - e)
        else:
            propensity = self.policy.getPropensity(actionIndex)
            experience = propensity * (e / (self.domainSize - 1))

        return experience


class AREParameters(REParameters):
    """ Parameters required for the Advanced version of the Roth-Erev
        reinforcement learning algorithm. These parameters include setting for
        features extended from the standard Roth-Erev algorithm. This includes:

            Alternative methods to generate Action probabilities.
            Alternative methods of reward spillover among similar actions
            Ability to specify similar measures for Action comparison
    """

    def __init__(self):
        # Which method of reward spillover to use.
        selectedSpillover = None

        # List of available spillover methods.
        spilloverList = []


    def init(self):
        if self.spilloverList is None:
            self.spilloverList = []

        self.buildSpilloverSelector()


    def buildSpilloverSelector(self):
        # Add no-spillover option if not already present.
        if NoSpillover not in self.spilloverList:
            noSpill = NoSpillover()
            self.spilloverList.append(noSpill)

        # Add standard spillover if not already present
        if StandardSpillover not in self.spilloverList:
            standard = StandardSpillover(self.getExperimentation(),
                                         self.getNumberOfActions())
            self.spilloverList.append(standard)


class ARELearner(RELearner):
    """ An extension of the VRELearner. This engine implements the same
        modified version of the Roth-Erev reinforcement learning algorithm with
        added features.
    """

    def __init__(self):
        # Flag to use relative propensities to generate action probabilities
        # from action propensities. This is used by default. The probability
        # for each action is the propensity for that action over the total
        # propesities over all actions.
        #
        # P(i) = q(i) / Sum_all_j(q(j))
        #
        # Where P(i) is the probability of choosing action i, q(i) is the
        # propensity for action i and j runs from 1 to n (the total number of
        # actions).
        USE_RELATIVE_PROPENSITY_PROBABILITY = 10101

        # Flag to use the Boltzman distribution to generate action probabilities
        # from action propensities.
        #
        #    P(i) = e ^(q(i)/T) / Sum_all_j(e ^(q(j)/T))
        #
        # Where P(i) is the probability of choosing action i, q(i) is the
        # propensity for action i and j runs from 1 to n (the total number of
        # actions). T is the temperature parameter...
        # TODO: Look up info about Gibbs/Boltzmann temperature
        USE_BOLTZMAN_PROBABILITY = 11212

        # Flag indicating which method of response weighting to use in updating
        # the propensities of actions from a given reward. This determines how
        # much of the reward value is "spilled over" to actions that are
        # similar to the action that the reward is associated with (usually the
        # last one chosen). Similarity between actions is defined by the given
        # similarity measure.
        spilloverType = -1

        spillover = SpilloverWeightGenerator()

        EXPONENTIAL_SPILLOVER = 20101

        LOGARITHMIC_SPILLOVER = 21212

        LINEAR_SPILLOVER = 22323

        STANDARD_SPILLOVER = 23434

        NO_SPILLOVER = 29999


    def init(self):
        super(ARELearner, self).init()
        self.spillover = None


    def experience(self, actionIndex, reward):
        if self.spillover is None:
            return super(ARELearner, self).experience(actionIndex, reward)

        responseValue = 0
        domain = self.policy.getActionDomain()

        action = domain.getAction(actionIDList.get(actionIndex))

        responseValue = reward * self.spillover.generateWeight(action)

        return responseValue


class AdvancedRothErevLearner(RELearner):
    """ An extension of the MRELearner. This engine implements the same
        modified version of the Roth-Erev reinforcement learning algorithm with
        added features.
    """

    def experience(self, actionIndex, reward):
        if self.spillover is None:
            return super(ARELearner, self).experience(actionIndex, reward)

        responseValue = 0.0
        weight = 0.0
        similarity = 0.0

        domain = self.policy.getActionDomain()

        action = domain.getAction(actionIDList.get(actionIndex))

        responseValue = reward * self.spillover.generateWeight(action)

        return responseValue


    def updateProbabilities(self):
        """ pdates the probability for each action to be chosen in the policy.
        """
        method = self.parameters.getProbabilityMethod()

        if method == self.USE_RELATIVE_PROPENSITY_PROBABILITY:
            self.generateProportionalProbs()
        elif method == self.USE_BOLTZMAN_PROBABILITY:
            self.generateBoltzmanProbs()
        else:
            self.generateBoltzmanProbs()


    def generateProportionalProbs(self):
        """ Generate action probabilities using a proportional distribution.
            Warning: In situations where the MRELearner may receive negative
            reward values, this probability method may yield negative
            probabilities. This can be avoided by setting the intial propensity
            to a sufficiently value. However, it is recommended that MRELearner
            only be used in the simulations with positive reward values.
        """
        summedProps = 0.0
        newProb = 0.0

        for actID in self.actionIDList:
            summedProps += self.policy.getPropensity(actID)

        # For each Action, divide its propensity by the sum of all
        # propensities. Then set its probability value to the result.
        for actID in self.actionIDList:
            newProb = self.policy.getPropensity(actID) / summedProps
            self.policy.setProbability(actID, newProb)

