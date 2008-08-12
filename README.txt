Pylon 
===== 

Open source power system analysis tool. 

Pylon provides simple and powerful analysis of electric energy systems. This is 
achieved by the following: 

* Building on the strengths of Python as a high-level programming language, the 
code should be easily understandable for scientists and engineers with limited 
programming experience 
* Using the [http://code.enthought.com/traits/ Traits] package from the 
[http://code.enthought.com/ets/ Enthought Tool Suite] to allow a power system 
data model to be defined in strict yet simple terms, and to be extended easily 
* Performing calculations with the [http://abel.ee.ucla.edu/cvxopt CVXOPT] 
convex optimisation package, which (along with Traits) uses C extensively to 
enhance computational performance 
* Using CVXOPT's interfaces to packages such as LAPACK, BLAS, UMFPACK, CHOLMOD, 
GLPK and MOSEK for matrix algebra and mathematical optimisation 

Additionally, the core of Pylon has been structured such that it may be reused 
in '''your''' applications and easily extended to provide new functionality. 

---- 

== Introduction == 

Pylon is a general purpose, open standards driven, cross-platform tool for 
simulation of electric power systems. Its current features include: 

* DC load flow 
* DC Optimal Power Flow 
* AC load flow (Newton-Raphson method) 

Note: Much of the code for the above features is translated from the excellent 
work of Ray D. Zimmerman, Carlos E. Murillo-Sanchez & Deqiang (David) Gan for 
the [http://www.pserc.cornell.edu/matpower MATPOWER] project and Frederico 
Milano for the [http://www.power.uwaterloo.ca/~fmilano/psat.htm PSAT] project. 

The GUI currently has the follwing features: 

* [http://www.graphviz.org/ Graphviz] network representation made interactive by 
the [http://code.enthought.com/kiva/ Kiva] and 
[https://svn.enthought.com/enthought/wiki/EnableProject Enable] packages 
* Editable tables of network plant and infrastructure data 
* Plotting of results using [http://code.enthought.com/chaco/ Chaco] 
* The beginnings of a GIS and network visualisation using [http://mapnik.org/ 
Mapnik] 

Pylon has been designed from the ground up with scriptability and extensibility 
in mind. New functionality may be added with reasonable ease and the core 
package has reduced dependencies and may be embedded in other applications. 

== Technical details == 

Pylon provides a conventional bus-branch model of an electric power system and a 
series of engines for calculating the flows of power. 

The {{{pylon}}} package is responsible for maintaining the state of the model. 
As such, when the {{{solve}}} method of an engine from the {{{pylon.engine}}} 
package is called the data it uses should be in a feasible state and the 
necessity for sanity checking is reduced. The {{{pylon.engine}}} package 
currently offers three engines that have been largely translated from the 
[http://www.pserc.cornell.edu/matpower MATPOWER] project and have the following 
features: 

* Linear DC load flow 
* Uses CVXOPT's interface to [http://www.cise.ufl.edu/research/sparse/umfpack/ 
UMFPACK] 
* DC Optimal Power Flow 
* Quadratic cost curves 
* Choice of default CVXOPT QP solver or MOSEK solver 
* AC load flow 
* Standard Newton's method 
* Full Jacobian updated each iteration 

Full use is made of CVXOPT's sparse matrix support throughout these features. 
Future Pylon releases will include (among other things): 

* AC load flow using Gauss-Siedel 
* Fast-decoupled load flow 
* AC Optimal Power Flow using IPM translated from the wonderful 
[http://www.power.uwaterloo.ca/~fmilano/psat.htm PSAT] project 

Pylon may be used from the command-line or via a toolkit independant GUI 
(screenshots are available [wiki:pylon/screenshots here]). 


Credits 
======= 

Pylon is maintained by Richard W. Lincoln of The University of Strathclyde and
was developed as part of the SUPERGEN 3: Highly Distributed Power Systems
project.

The power flow routines are derived from the MATPOWER project by
Ray D. Zimmerman, Carlos E. Murillo-Sánchez & Deqiang (David) Gan and the PSAT
project by Federico Milano. See http://www.pserc.cornell.edu/matpower/ and
http://www.power .uwaterloo.ca/~fmilano/psat.htm for further details. 

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

Tel. +44 (0)141 548 4840 
Fax +44 (0)141 548 4872 
Email: richard.lincoln@eee.strath.ac.uk 
Web: http://pylon.eee.strath.ac.uk 

