#------------------------------------------------------------------------------
# Copyright (C) 2010 Richard Lincoln
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#------------------------------------------------------------------------------

""" Defines various utility functions and classes for Pylon.
"""

#------------------------------------------------------------------------------
#  Imports:
#------------------------------------------------------------------------------

from __future__ import with_statement

import os.path
import pickle

from itertools import count

#from pylon.readwrite import MATPOWERReader, PickleWriter

#------------------------------------------------------------------------------
#  File extension for load/save protocol mapping:
#------------------------------------------------------------------------------

known_extensions = {
    'm': 'matpower',
    'pkl': 'pickle',
    'raw': 'psse',
    'rst': 'rest',
    'csv': 'csv',
    'xls': 'excel',
    'dot': 'dot'}

#------------------------------------------------------------------------------
#  "Named" class:
#------------------------------------------------------------------------------

class Named(object):
    """ Base class taken from PyBrain for objects guaranteed to have a
        unique name.
    """

    _name_ids = count(0)

    def _get_name(self):
        """ Returns the name, which is generated if it has not been already.
        """
        if self._name is None:
            self._name = self._generate_name()
        return self._name


    def _set_name(self, value):
        """ Changes name to 'value'. Uniquity no longer guaranteed.
        """
        self._name = value


    _name = None
    name = property(_get_name, _set_name)


    def _generate_name(self):
        """ Return a unique name for this object.
        """
        return "%s-%i" % (self.__class__.__name__, self._name_ids.next())


#    def __repr__(self):
#        """ The default representation of a named object is its name.
#        """
#        return "<%s '%s'>" % (self.__class__.__name__, self.name)

#------------------------------------------------------------------------------
#  "Serializable" class:
#------------------------------------------------------------------------------

class Serializable(object):
    """ Defines shortcuts to serialize an object.  Taken from PyBrain.
    """

    def save_to_file_object(self, fd, format=None, **kwargs):
        """ Save the object to a given file like object in the given format.
        """
        format = 'pickle' if format is None else format
        save = getattr(self, "save_%s" % format, None)
        if save is None:
            raise ValueError("Unknown format '%s'." % format)
        save(fd, **kwargs)


    @classmethod
    def load_from_file_object(cls, fd, format=None):
        """ Load the object from a given file like object in the given format.
        """
        format = 'pickle' if format is None else format
        load = getattr(cls, "load_%s" % format, None)
        if load is None:
            raise ValueError("Unknown format '%s'." % format)
        return load(fd)


    def save(self, filename, format=None, **kwargs):
        """ Save the object to file given by filename.
        """
        if format is None:
            # try to derive protocol from file extension
            format = format_from_extension(filename)
        with file(filename, 'wb') as fp:
            self.save_to_file_object(fp, format, **kwargs)


    @classmethod
    def load(cls, filename, format=None):
        """ Return an instance of the class that is saved in the file with the
            given filename in the specified format.
        """
        if format is None:
            # try to derive protocol from file extension
            format = format_from_extension(filename)
        with file(filename, 'rbU') as fp:
            obj = cls.load_from_file_object(fp, format)
            obj.filename = filename
            return obj


    def save_pickle(self, fd, protocol=0):
        """ Create portable serialized representation of the object.
        """
        pickle.dump(self, fd, protocol)


    @classmethod
    def load_pickle(cls, fd):
        """ Load portable serialized representation of the object.
        """
        return pickle.load(fd)

#------------------------------------------------------------------------------
#  Infer format from file extension:
#------------------------------------------------------------------------------

def format_from_extension(fname):
    """ Tries to infer a protocol from the file extension."""
    _base, ext = os.path.splitext(fname)
    if not ext:
        return None
    try:
        format = known_extensions[ext.replace('.', '')]
    except KeyError:
        format = None
    return format

#------------------------------------------------------------------------------
#  Pickles MATPOWER case files:
#------------------------------------------------------------------------------

def pickle_matpower_cases(case_paths, case_format=2):
    """ Parses the MATPOWER case files at the given paths and pickles the
        resulting Case objects to the same directory.
    """
    import pylon.readwrite

    if isinstance(case_paths, basestring):
        case_paths = [case_paths]

    for case_path in case_paths:
        # Read the MATPOWER case file.
        case = pylon.readwrite.MATPOWERReader(case_format).read(case_path)

        # Give the new file the same name, but with a different extension.
        dir_path = os.path.dirname(case_path)
        case_basename = os.path.basename(case_path)
        root, _ = os.path.splitext(case_basename)
        pickled_case_path = os.path.join(dir_path, root + '.pkl')

        # Pickle the resulting Pylon Case object.
        pylon.readwrite.PickleWriter(case).write(pickled_case_path)

#------------------------------------------------------------------------------
#  Change all zeros to ones:
#------------------------------------------------------------------------------

def zero2one(x):
    if x != 0.0:
        return x
    else:
        return 1.0

#------------------------------------------------------------------------------
#  'atan2' function:
#------------------------------------------------------------------------------

#def atan2(X, Y):
#    """ atan2 function.
#    """
#    matrix([math.arctan2(Y, X) for k in xrange(nrows * ncols)],
#           (nrows, ncols), 'd')

#------------------------------------------------------------------------------
#  Returns the angle of the complex argument:
#------------------------------------------------------------------------------

#def angle(z, deg=0):
#    """ Returns the angle of the complex argument.
#
#        Parameters
#        ----------
#        z : array_like
#            A complex number or sequence of complex numbers.
#        deg : bool, optional
#            Return angle in degrees if True, radians if False (default).
#
#        Returns
#        -------
#        angle : {ndarray, scalar}
#            The counterclockwise angle from the positive real axis on
#            the complex plane, with dtype as numpy.float64.
#
#        See Also
#        --------
#        arctan2
#
#        Examples
#        --------
#        >>> np.angle([1.0, 1.0j, 1+1j])               # in radians
#        array([ 0.        ,  1.57079633,  0.78539816])
#        >>> np.angle(1+1j, deg=True)                  # in degrees
#        45.0
#    """
#    if deg:
#        fact = 180 / math.pi
#    else:
#        fact = 1.0
##    z = asarray(z)
#    if z.typecode is "z":
#        zimag = z.imag()
#        zreal = z.real()
#    else:
#        zimag = 0
#        zreal = z
#
#    matrix([math.arctan2(z[i].imag(), z[i].real()) for x in z])
#
#    return atan2(zimag, zreal) * fact

#------------------------------------------------------------------------------
#  "CaseReport" class:
#------------------------------------------------------------------------------

class CaseReport(object):
    """ Defines a statistical case report.
    """

    def __init__(self, case):
        """ Initialises a CaseReport instance.
        """
        self.case = case


    @property
    def n_buses(self):
        """ Total number of buses.
        """
        return len(self.case.buses)


    @property
    def n_connected_buses(self):
        """ Total number of non-islanded buses.
        """
        return len(self.case.connected_buses)


    @property
    def n_generators(self):
        """ Total number of generators.
        """
        return len(self.case.generators)


    @property
    def n_online_generators(self):
        """ Total number of generators in service.
        """
        return len(self.case.online_generators)


    @property
    def committed_generators(self):
        """ Generators that have been despatched.
        """
        return [g for g in self.case.generators if g.p > 0.0]


    @property
    def n_committed_generators(self):
        """ Number of committed generators.
        """
        return len(self.committed_generators)


    @property
    def n_loads(self):
        """ Total number of loads.
        """
        return self.n_fixed + self.n_despatchable


#    @property
#    def n_online_loads(self):
#        """ Number of active loads.
#        """
#        return len(self.case.online_loads)


    @property
    def fixed(self):
        """ Fixed loads.
        """
        return self.case.all_loads


    @property
    def n_fixed(self):
        """ Total number of fixed loads.
        """
        return len([bus for bus in self.case.buses if bus.p_demand > 0.0])


    @property
    def despatchable(self):
        """ Generators with negative output.
        """
        return [vl for vl in self.case.generators if vl.is_load]


    @property
    def n_despatchable(self):
        """ Number of despatchable loads.
        """
        return len(self.despatchable)

    # Branch property getters -------------------------------------------------

    @property
    def n_branches(self):
        """ Total number of branches.
        """
        return len(self.case.branches)


    @property
    def n_online_branches(self):
        """ Total number of active branches.
        """
        return len(self.case.online_branches)


    @property
    def transformers(self):
        """ Branches operating as transformers.
        """
        return [e for e in self.case.branches if e.ratio != 0.0]


    @property
    def n_transformers(self):
        """ Total number of transformers.
        """
        return len(self.transformers)

    # "How much?" property getters --------------------------------------------

    @property
    def total_gen_capacity(self):
        """ Total generation capacity.
        """
        p = sum([g.p_max for g in self.case.generators])
        q = sum([g.q_max for g in self.case.generators])

        return complex(p, q)


    @property
    def online_capacity(self):
        """ Total online generation capacity.
        """
        p = sum([g.p for g in self.case.online_generators if not g.is_load])
        q = sum([g.q for g in self.case.online_generators if not g.is_load])

        return complex(p, q)


    @property
    def generation_actual(self):
        """ Total despatched generation.
        """
        Sg = [complex(g.p, g.q) for g in self.case.generators if not g.is_load]

        return sum(Sg)


    @property
    def load(self):
        """ Total system load.
        """
        return self.fixed_load + self.despatchable_load


    @property
    def fixed_load(self):
        """ Total fixed system load.
        """
        Sd = [complex(bus.p_demand, bus.q_demand) for bus in self.case.buses]

        return sum(Sd)


    @property
    def despatchable_load(self):
        """ Total volume of despatchable load.
        """
        Svl = [complex(vl.p, vl.q) for vl in self.despatchable]

        return -sum(Svl)


#    @property
#    def shunt_injection(self):
#        """ Total system shunt injection.
#        """
#        return 0.0 + 0.0j # FIXME: Implement shunts


    @property
    def losses(self):
        """ Total system losses.
        """
        p = sum([e.p_losses for e in self.case.branches])
        q = sum([e.q_losses for e in self.case.branches])

        return complex(p, q)


    @property
    def branch_charging(self):
        """ Total branch charging injections.
        """
        return 0.0 + 0.0j # FIXME: Calculate branch charging injections


#    @property
#    def total_inter_tie_flow(self):
#        """ Total inter-tie flow.
#        """
#        return 0.0 + 0.0j # FIXME: Implement inter-ties


    @property
    def min_voltage_amplitude(self):
        """ Minimum bus voltage amplitude.
        """
        if self.case.buses:
#            l.index(min(l))
            return min([bus.v_magnitude for bus in self.case.buses])
        else:
            return 0.0


    @property
    def max_voltage_amplitude(self):
        """ Maximum bus voltage amplitude.
        """
        if self.case.buses:
            return max([bus.v_magnitude for bus in self.case.buses])
        else:
            return 0.0


    @property
    def min_voltage_phase(self):
        """ Minimum bus voltage phase angle.
        """
        if self.case.buses:
            return min([bus.v_angle for bus in self.case.buses])
        else:
            return 0.0


    @property
    def max_voltage_phase(self):
        """ Maximum bus voltage phase angle.
        """
        if self.case.buses:
            return max([bus.v_angle for bus in self.case.buses])
        else:
            return 0.0


    @property
    def min_p_lmbda(self):
        """ Minimum bus active power Lagrangian multiplier.
        """
        if self.case.buses:
            return min([v.p_lmbda for v in self.case.buses])
        else:
            return 0.0


    @property
    def max_p_lmbda(self):
        """ Maximum bus active power Lagrangian multiplier.
        """
        if self.case.buses:
            return max([v.p_lmbda for v in self.case.buses])
        else:
            return 0.0


    @property
    def min_q_lmbda(self):
        """ Minimum bus reactive power Lagrangian multiplier.
        """
        if self.case.buses:
            return min([v.q_lmbda for v in self.case.buses])
        else:
            return 0.0


    @property
    def max_q_lmbda(self):
        """ Maximum bus reactive power Lagrangian multiplier.
        """
        if self.case.buses:
            return max([v.q_lmbda for v in self.case.buses])
        else:
            return 0.0

# EOF -------------------------------------------------------------------------
