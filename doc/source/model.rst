.. _model:

******************
Power System Model
******************

This chapter describes the Pylon objects that may be used to model a power
system.  It explains their main features and how they may be associated with
one and other.

.. _network:

Network
=======

.. class:: Network

A ``Network`` object is a representation of a power system as a graph.  It
contains a list of :class:`Bus <pylon.bus.Bus>` objects that define the nodes
of the graph and a list of :class:`Branch <pylon.branch.Branch>` objects that
define the edges.

For convenience, a ``Network`` provides certain read-only properties, such as
``all_generators``, that are used regularly by other modules.

.. sourcecode:: ipython

  In [1]: from pylon import Network
  In [2]: network = Network(name="net1", mva_base=100.0)

.. class:: Bus

A ``Bus`` is a node in the power system graph to which ``Generator`` and
``Load`` objects may be added.

.. sourcecode:: ipython

  In [1]: from pylon import Network, Bus
  In [2]: network = Network()
  In [3]: bus = Bus(name="bus1", v_amplitude_guess=1.1)
  In [4]: network.buses.append(bus)

The objects connected determine the ``mode`` of the ``Bus``, which may be one
of three values:

* PQ

  * Default mode for a plain bus.
  * Set when one or more ``Load`` is present, but no ``Generator``.
  * Set when the connected generation has reached one of it's reactive power 
    limits.
  * Active and reactive power are the known variables.

* PV

  * Set when one or more ``Generator`` is connected to the ``Bus`` and the
    ``slack`` attribute of the ``Bus`` is not set.
  * Active power and voltage magnitude are the known system variables.

* Slack

  * Sometimes known as the "swing" of reference bus.
  * Set when one or more ``Generator`` is connected to the ``Bus`` and the
    ``slack`` attribute is true.
  * No variables to be solved for in the power flow solution.

The shunt conductance and susceptance at the bus are specified by the
``g_shunt`` and ``b_shunt`` attributes respectively.

For convenience, ``Bus`` provides read-only properties that return values of
total supply and demand of power at the node.


.. class:: Branch

Transmission lines and transformers are both defined by the ``Branch`` class
which uses a standard pi-circuit model.  The ``source_bus`` and ``target_bus``
must be specified when creating a ``Branch``.

.. sourcecode:: ipython

  In [1]: network = Network()
  In [2]: bus1, bus2 = Bus(), Bus()
  In [3]: e = Branch(bus1, bus2, r=0.06, x=0.03)
  In [4]: network.branches.append(branch)

.. class:: Generator

A ``Generator`` specifies the voltage magnitude and the active power injected
at a node.  If reactive power limits are enforced then a ``Generator`` may
switch to fixing active and reactive power at a node if a limit is violated.

.. sourcecode:: ipython

  In [1]: bus = Bus()
  In [2]: g = Generator(p=6.0, v_amplitude=1.1)
  In [3]: bus.generators.append(g)
  In [4]: bus.mode
  Out[1]: 'PV'

``Generator`` objects define the despatchable units for the optimal power flow
problem.  The ``p_max_bid`` and ``p_min_bid`` attributes define the range in
which the generator is willing to operate and this must be within the rated
capacity of the unit as defined by ``p_max`` and ``p_min``.  The cost of the
generator with respect to active power is defined using the ``cost_coeffs``
attribute.  This is a triple of floating point values, restricting the
definition of cost curves to quadratic functions.

.. sourcecode:: ipython

  In [1]: g = Generator(p_max=6.0, p_min=1.0, cost_coeffs=(0.0, 6.0, 0.0)
                        p_max_bid=5.0, p_min_bid=1.0)

.. class:: Load

A load fixes active and reactive power demand at a the node.

A ``Load`` may be configured to follow an output profile.  The attribute
``p_profile`` specifies a list of percentages that define how the profile
varies between the limits defined by ``p_max`` and ``p_min``.  ``p_profiled``
is a property that uses a cycle iterator to return the next value in the
profile sequence each time it is called.

.. sourcecode:: ipython

  In [1]: l = Load(p_min=1.0, p_max=2.0, p_profile=[100, 50])
  In [2]: l.p_profiled
  Out[1]: 2.0
  
  In [3]: l.p_profiled
  Out[2]: 1.5
  
  In [4]: l.p_profiled
  Out[3]: 2.0

