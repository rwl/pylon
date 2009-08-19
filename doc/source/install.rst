.. _install:

============
Installation
============

Pylon is a package of Python modules.  It needs to be on the PYTHON_PATH
environment variable and for some core dependencies to be met for model and
solver functionality.  Optionally, easily installed additional libraries
enable other features.

Dependencies
------------

  2.5 <= Python_ < 3.0

  Traits_ 3.0 or later
    Provides Python object attributes with additional characteristics.

  CVXOPT_ 1.0 or later
    CVXOPT is a free software package for convex optimization based on the
    Python programming language.

  NumPy_ 1.2 or later
    NumPy provides additional support for multi-dimentional arrays and 
    matrices.

Strongly recommended
--------------------

  Pyparsing_
    Pyparsing is a versatile Python module for recursive descent parsing.

  PyBrain_
    PyBrain is a modular Machine Learning Library for Python.

  iPython_
    Interactive python interpreter.

  wxPython_
    Cross-platform GUI toolkit for the Python_ programming language.

  Godot_
    Godot uses Graphviz_ Xdot output to provide interactive graph 
    visualisation.

Windows
-------

The `Enthought Python Distribution`_ provides the majority of the dependencies
for Pylon and is free for academic use.  CVXOPT_ is not included, but comes as
a `Windows Installer <http://abel.ee.ucla.edu/cvxopt/download-2.5-win32.php>`_
also.

Setuptools
----------

With Python_ and setuptools_ installed, simply::

  $ easy_install pylon

Virtualenv_ may be used to build a virtual Python environment::

  $ virtualenv env
  $ ./env/bin/easy_install pylon

Installation from source
------------------------

Extract the gzipped tar file::

  $ tar xvf pylon-X.X.tar.gz

Run the ``setup.py`` script::

  $ cd pylon-X.X
  $ python setup.py install

or::

  $ python setup.py develop

Working directory
-----------------

Change in to the source directory and run IPython_::

  $ cd ~/path/to/pylon-X.X
  $ ipython

Access the ``pylon`` application programming inteface.

.. sourcecode:: ipython

  In [1]: from pylon.api import Generator, DCOPF

.. include:: ../links_names.txt
