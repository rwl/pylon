__author__ = 'Richard W. Lincoln, r.w.lincoln@gmail.com'

from pybrain.rl.learners.rllearner import RLLearner

class REParameters:
    """ Parameter settings required for the modified Roth-Erev reinforcement
        learning algorithm. Experimentation, initial propensity and recency.
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

class SimpleStatelessPolicy(StatelessPolicy):
    """ This is essentially a discrete probability distribution governing the
        choice of Action from a given ActionDomain, irrespective of the state
        of the world.
    """
    def __init__(self, actionDomain, initProbs):
        # Here a probability distribution function (pdf) is an array of
        # probability values. When used in conjuction with the eventGenerator,
        # a value indicates the likelihood that its index will be selected.

        # Each Action has an ID and each Action ID has an index in the list of
        # IDs kept by the ActionDomain. The corresponding index in this
        # probability distribution function contains a probability value for
        # that ID. So we have a mapping from probabilities to Action IDs and
        # from Action IDs to Actions. This allows the evenGenerator to use the
        # pdf to select Actions from the ActionDomain according to the
        # specified probability distribution.

        # The probability values are modified by a RLLearner according to the
        # implemented learning algorithm.
        self.probDistFunction = []

        # Random number eventGenerator needed for the randomEngine event
        # eventGenerator.
        self.randomEngine = MersenneTwister()

        # Generates randomEngine events (action selections) according to the
        # probabilities over all actions in the ActionDomain. Probabilities
        # are maintained in probDistFunction.
        self.eventGenerator = SimpleEventGenerator()

        # The collection of possible Actions an agent is allowed to perform.
        domain = ActionDomain()

        # List of action ID's in the domain. Allows us to map from int values
        # chosen given by the event generator to actions in the domain.
        self.actionIDList = []

        # Records the last action choosen by this policy.
        self.lastAction = None

        # Initialize to uniform distribution.
        numActions = len(actionDomain)
        for i in range(numActions):
            self.probDistFunction[i] = 1.0 / numActions

    def init(self):
        self.actionIDList = self.domain.getIDList()
        self.eventGenerator = SimpleEventGenerator(self.probDistFunction,
                                                   self.randomEngine)
        # Need to init the lastAction to something. Choose a random action.
        self.lastAction = self.generateAction()

    def generateAction(self):
        """ Choose an Action according to the current probability distribution
            function.
        """
        # Pick the index of an action. Note: indexes start at 0.
        chosenIndex = self.eventGenerator.nextEvent()
        chosenID = self.actionIDList.get(chosenIndex)
        chosenAction = self.domain.getAction(chosenID)

        self.lastAction = chosenAction

        return chosenAction

    def reset(self):
        """ Reset this policy. Reverts to a uniform probability distribution
            over the domain of actions. This only modifies the probability
            distribution. It does not reset the RandomEngine.
        """
        numActions = len(actionDomain)
        for i in range(numActions):
            self.probDistFunction[i] = 1.0 / numActions

    def setDistribution(self, distrib):
        """ Set the probability distribution used in selecting actions from the
            action domain. The distribution is given as an array of floats.
        """
        self.probDistFunction = distrib
        self.eventGenerator.setState(distrib)

    def getNumActions(self):
        return len(self.domain)

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
        self.eventGenerator.setState(self.probDistFunction)


class REPolicy(SimpleStatelessPolicy):
    def __init__(self):
        # Each possible action has a propensity associated with it. Essentially
        # the likelyhood that each action will be chosen.
        self.propensities = []

    def init(self):
        super(REPolicy, self).init()
        self.propensities = [0.0] * len(self.getActionDomain())

    def getPropensity(self, ID):
        index = self.actionIDList.index(ID)
        return self.propensities[index]

    def setPropensity(self, ID, prop):
        index = self.actionIDList.index(ID)
        self.propensities[index] = prop


class RELearner(RLLearner):
    """ A. E. Roth, I. Erev, D. Fudenberg, J. Kagel, J. Emilie and R. X. Xing,
        "Learning in Extensive-Form Games: Experimental Data and Simple Dynamic
        Models in the Intermediate Term," Games and Economic Behavior,
        Special Issue: Nobel Symposium, vol. 8, January 1995, 164-212.

        A. E. Roth, I. Erev, "Predicting How People Play Games with Unique
        Mixed-Strategy Equilibria," American Economics Review, Volume 88,
        1998, 848-881.
    """

    def __init__(self):
        # Collects and manages parameter settings for the RLLearner.
        self.parameters = REParameters()

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

    def setPolicy(self, policy):
        self.policy = policy
        self.domainSize = len(policy.actionDomain)
        self.actionIDList = policy.actionDomain.idList

    def init(self):
        """ Finishes initialising the learner.
        """
        self.domainSize = len(self.policy.actionDomain)
        self.actionIDList = self.policy.actionDomain.idList

        initProp = self.parameters.initialPropensity

        for ID in self.actionIDList:
            self.policy.setPropensity(ID, initProp)

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
        phi = self.parameters.recency

        for i in range(self.domainSize):
            carryOver = (1 - phi) * self.policy.getPropensity(i)
            experience = self.experience(i, reward)
            self.policy.setPropensity(i, carryOver + experience)
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
        e = self.parameters.experimentation
        rewardedIndex = self.actionIDList.index(self.lastSelectedAction)

        if actionIndex == rewardedIndex:
            experience = reward * (1 - e)
        else:
            experience = reward * (e / (self.domainSize - 1))

    def updateProbabilities(self):
        """ Updates the probability for each action to be chosen in the policy.
            Uses a proportional probability unless the given parameters say to
            use a Gibbs-Bolztmann distribution.
        """
        if self.parameters.useBoltz:
            self.generateBoltzmanProbs()
        else:
            # Proportional probability method.
            propensities = self.policy.getPropensities()

            summedProps = 0.0
            for prop in propensities:
                summedProps += prop

            for index, actionID in enumerate(self.actionIDList):
                newProb = propensities[index] / summedProps
                self.policy.setProbability(actionID, newProb)

    def generateBoltzmanProbs(self):
        """ Generate action probabilities using a Boltzmann distribution with a
            constant temperature.
        """
        propensities = self.policy.getPropensities()
        coolingParam = self.parameters.boltzmannTemp

        summedExps = 0.0
        for prop in propensities:
            summedExps += math.exp(prop / coolingParam)

        # For each action calculate the associated choice probability.
        #    p(i) = [ e ^(q(i)/T) ] / [ Sum_over_all_j(e ^ (q(j)/T)) ]
        for index, actionID in enumerate(self.actionIDList):
            newProb = math.exp(propensities[index] / coolingParam) / summedExps
            self.policy.setProbability(actionID, newProb)

    def update(self, feedback):
        """ This activates the learning process according to the modified
            Roth-Erev learning algorithm. Feedback is interpreted as reward
            for the last action chosen by this engine. Entries in the policy
            associated with this Action are updated accordingly.
        """
        self.updatePropensities(feedback)
        self.updateProbabilities()
        self.period += 1

    def chooseAction(self):
        nextAction = self.policy.generateAction()
        self.lastSelectedAction = nextAction
        return nextAction

    def reset():
        """ Clear all learned knowledge. The Action propensities are set to the
            current initial value and the probability values in the policy.
        """
        self.init()

#    def learn(self):
#        """ learn on the current dataset, for a single epoch.
#        """
#        pass
