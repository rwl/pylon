-----
Pylon
-----

Pylon is a free software package for simulation of electric power systems and
energy markets.  Its purpose is to provide a simple yet powerful tool for
electric power Engineers that is not tied to proprietary software and can be
used and extended easily.

Pylon's features currently include:

* DC and AC power flow,
* DC and AC optimal power flow,
* State estimation,
* PSS/E, MATPOWER_ and PSAT_ data file parsers, and
* Agent-based market simultaion using reinforcement learning methods.

-----------
Quick start
-----------

With Python_, setuptools_ and SciPy_ installed, run::

  $ easy_install pylon

Pylon performs an AC power flow and prints a ReStructuredText_ report by
default::

  $ pylon data_file.raw

Refer to the documentation for detailed usage information or type::

  $ pylon --help

-------
License
-------

Pylon is licensed under the Apache License version 2.0 with the exception of
the ``cvxopf`` module which is licensed under the GNU General Public
License version 3.

-------
Credits
-------

Pylon is developed by Richard Lincoln (r.w.lincoln@gmail.com).

Pylon is a port of MATPOWER_ to the Python programming language.

Pylon was originally funded by the `EPSRC
<http://www.epsrc.ac.uk/default.htm>`_ through `Grant GR/T28836/01
<http://gow.epsrc.ac.uk/ViewGrant.aspx?GrantRef=GR/T28836/01>`_ for the
SUPERGEN `Highly Distributed Power Systems <http://www.supergen-hdps.org>`_
consortium.

.. _Python: http://www.python.org
.. _Setuptools: http://peak.telecommunity.com/DevCenter/setuptools
.. _SciPy: http://www.scipy.org
.. _MATPOWER: http://www.pserc.cornell.edu/matpower/
.. _PSAT: http://www.power.uwaterloo.ca/~fmilano/psat.htm
.. _ReStructuredText: http://docutils.sf.net/rst.html

