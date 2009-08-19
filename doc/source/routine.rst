.. _routine:

********
Routines
********

Pylon includes a selection of routines for solving power flow and optimal power
flow problems.  The routines are translated from MATPOWER_ and use the sparse
matrix types and optimisation routines from CVXOPT_.

.. _dcpf:

DC Power Flow
=============

The DC power flow routine is made linear by making the assumption that branch
losses are negligible, all bus voltages are 1.0 p.u. and that voltage phase
angles are small.

CVXOPT_ provides interfaces to CHOLMOD_ and UMFPACK, both of which provide
routines for solving sets of sparse linear equations.  The ``routine``
attribute of ``DCPF`` specifies which library to use and defaults
to 'UMFPACK'.

.. _acpf:

Newton Power Flow
=================

``NewtonRaphson`` is a subclass of ``ACPF`` that solves the power flow
problem using standard Newton's method with a full Jacobian updated each
iteration and sparsity maintained throughout.  ``ACPF`` is a base class
with methods common to all power flow routines using an AC formulation.

DC Optimal Power Flow
=====================

The DC formulation of the optimal power flow routine uses the ``qp`` solver
from CVXOPT_ for solving quadratic programs.  Optionally, the ``solver``
attribute of the routine may be set to 'mosek' if MOSEK_ version 5 is
available.

AC Optimal Power Flow
=====================

The AC optimal power flow routine uses the ``cp`` solver from CVXOPT_ to
minimise a non-linear objective function that is subject to non-linear
constraints.  The solver is written in Python and may be found in the
``cvxprog.py`` module in the CVXOPT_ distribution.

.. include:: ../links_names.txt

