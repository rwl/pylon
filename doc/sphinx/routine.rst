.. _routine:

********
Routines
********

Pylon includes a selection of routines for solving power flow and optimal power
flow problems.  The routines are translated from MATPOWER_ and use the sparse
matrix types and optimisation routines from SciPy_.

.. _dcpf:

DC Power Flow
=============

The DC power flow routine is made linear by making the assumption that branch
losses are negligible, all bus voltages are 1.0 p.u. and that voltage phase
angles are small.

.. _acpf:

Newton Power Flow
=================

``NewtonRaphson`` is a subclass of ``ACPF`` that solves the power flow
problem using standard Newton's method with a full Jacobian updated each
iteration and sparsity maintained throughout.  ``ACPF`` is a base class
with methods common to all power flow routines using an AC formulation.

DC Optimal Power Flow
=====================


AC Optimal Power Flow
=====================


.. include:: ../links_names.txt

