=======
Welcome
=======

Pylon is a port of MATPOWER to the Python programming language.  Its purpose
is to provide a simple yet powerful tool for Power Engineering that is not
tied to proprietary software and can be used and extended with ease.

Pylon's features currently include:

* DC and AC (Newton's and Fast Decoupled method) power flow,
* DC and AC optimal power flow and
* PSS/E, MATPOWER_ and PSAT_ case serialization and de-serialization.

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

Pylon is developed by Richard Lincoln (r.w.lincoln@gmail.com).

Pylon is translated from MATPOWER_ by R. D. Zimmerman, C. E. Murillo-Sanchez &
D. Gan.

Pylon is funded by the `Engineering and Physical Sciences Research Council
<http://www.epsrc.ac.uk/default.htm>`_ through `Grant GR/T28836/01
<http://gow.epsrc.ac.uk/ViewGrant.aspx?GrantRef=GR/T28836/01>`_.

.. include:: ../links_names.txt
