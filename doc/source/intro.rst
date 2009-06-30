.. _intro:

************
INTRODUCTION
************

Pylon is a software package for simulation and analysis of electric power
systems and energy markets.  It provides :class:`Bus <pylon.bus.Bus>`
and :class:`Branch <pylon.branch.Branch>` Python objects for representing
power systems in graph form.  :class:`Generator <pylon.generator.Generator>`
and :class:`Load <pylon.load.Load>` objects may be added to a :class:`Bus
<pylon.bus.Bus>` objects and define levels of active supply and passive demand.

Subpackages of :mod:`pylon <pylon>` define further functionality.

:mod:`pylon.routine <pylon.routine>`
  Routines for solving power flow and optimal power flow problems.  The
  routines are translated from MATPOWER_ and use the sparse matrix types and
  optimisation routines from CVXOPT_.

:mod:`pylon.pyreto <pylon.pyreto>`
  Modules for simulating competitive energy trade using reinforcement learning
  algorithms and artificial neural networks from PyBrain_.

:mod:`pylon.readwrite <pylon.readwrite>`
  Parsers for a selection of power system data file formats including
  MATPOWER_, PSS/E, and PSAT_.
  Export of data in MATPOWER_, CSV and Excel file formats.
  Reports in ReStructuredText_ format.

:mod:`pylon.test <pylon.test>`
  A comprehensive suite of unit tests.

:mod:`pylon.ui` <pylon.ui>`
  Cross-platform, toolkit independent user interfaces via the TraitsGUI_
  package.
  Interactive, publication quality data plots using Chaco_.
  Graphviz_ powered interactive 2D graph visualisation using Godot_.
  Plug-ins for the Envisage_ application framework.

This manual describes how :class:`Network <pylon.network.Network>` models may
be constructed and the subpackages used in their simulation and analysis. 
The routines in Pylon are translated from MATPOWER_, the `user manual
<http://www.pserc.cornell.edu/matpower/manual.pdf>`_ for which will likely
provide a more useful reference.

.. include:: ../links_names.txt
