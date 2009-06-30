=======
Welcome
=======

Pylon is a software package for simulation and analysis of electric power
systems and energy markets.  Its purpose is to provide a simple yet powerful
tool for Power Engineering students and researchers that is not tied to
proprietary software and can be used and extended easily.

Pylon's features currently include:

* DC and AC power flow,
* DC and AC optimal power flow,
* PSS/E, MATPOWER_ and PSAT_ data file parsers, and
* Competitive agents using reinforcement learning.

-----------
Quick start
-----------

With Python_ and setuptools_ installed, run::

  $ easy_install pylon

Pylon will attempt to recognise the format of a data file, solve the AC power
flow problem and output a ReStructuredText_ report by default::

  $ pylon ehv3.raw

Full details of the command line options are available::

  $ pylon --help

Refer to the documentation for detailed usage information.

-------
Credits
-------

Pylon is developed by Richard W. Lincoln (r.w.lincoln@gmail.com).

The power flow and optimal power flow routines provided with Pylon are
translated from MATPOWER_ by R. D. Zimmerman, C. E. Murillo-Sanchez & D. Gan.

Pylon is funded by the `Engineering and Physical Sciences Research Council
<http://www.epsrc.ac.uk/default.htm>`_ through `Grant GR/T28836/01
<http://gow.epsrc.ac.uk/ViewGrant.aspx?GrantRef=GR/T28836/01>`_ for the
`SUPERGEN <http://www.supergen-hdps.org>`_ Highly Distributed Power Systems
Consortium.

.. include:: ../links_names.txt
