Pylon
=====

Open source power system analysis tool.

Dependencies
============

- enthought.traits
- numpy
- cvxopt

Installation
============

Windows
-------

Get Python from:

 http://python.org/ftp/python/2.5.1/python-2.5.1.msi

and install.

Install the Traits from the Enthought Tool Suite. Either run the Enstaller
script, available from:

 http://code.enthought.com/enstaller/ez_enstaller_setup.py

and use Enstaller (Start Menu -> Programs -> Enstaller) to install the
dependencies.

Or run the ez_setup.py script available from:

  http://peak.telecommunity.com/dist/ez_setup.py

and use ez_install.py to install the required eggs.

 C:\Python25\Lib\site-packages\setuptools*\ez_install.py enthtought.traits

Download the convex optimisation library used for matrix manipulation from:

 http://abel.ee.ucla.edu/cvxopt/download

and install.

Install Pylon with the usual:

 python setup.py install


Source
------

Installation of ETS from source is described thoroughly here:

 https://svn.enthought.com/enthought/wiki/GrabbingAndBuilding

Usage
=====

Needless to say, no installation is needed just to use the module. A mere:

 import pylon

should do it, provided that the directory containing the modules is on Python
module search path.

Pickled networks, available in the data directory, may be loaded using 
the load_pickled_network function.

Credits
=======

Pylon is maintained by Richard W. Lincoln of The University of Strathclyde.

Sections of the load flow engines (dc.py, newton.py) are derived from the
MATPOWER project by Ray D. Zimmerman, Carlos E. Murillo-Sánchez & Deqiang
(David) Gan.  See http://www.pserc.cornell.edu/matpower/ for further details.

Contact
=======

Richard W. Lincoln
Institute for Energy and Environment
Department of Electronic and Electrical Engineering
Room R3-42
The University of Strathclyde
Royal College Building
204 George Street
Glasgow G1 1XW

Tel.    +44 (0)141 548 4840
Fax     +44 (0)141 548 4872
Email:  richard.lincoln@eee.strath.ac.uk
Web:    http://www.eee.strath.ac.uk
