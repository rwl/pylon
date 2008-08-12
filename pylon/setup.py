#------------------------------------------------------------------------------
# Copyright (C) 2007 Richard W. Lincoln
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; version 2 dated June, 1991.
#
# This software is distributed in the hope that it will be useful, but
# WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANDABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the GNU
# General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software Foundation,
# Inc., 51 Franklin St, Fifth Floor, Boston, MA 02110-1301 USA
#------------------------------------------------------------------------------

from setuptools import setup

setup(
    author = "Richard W. Lincoln",
    author_email = "richard.lincoln@eee.strath.ac.uk",
    description = "Open source power system analysis",
#    entry_points = {},
#    extras_require = {},
#    ext_modules = [],
#    install_requires = [],
    license = "GPLv2",
    name = "pylon",
#    namespace_packages = [
#        "pylon",
#        "pylon.ui",
#        "pylon.engine",
#        ],
    include_package_data = True,
    url = "https://pylon.eee.strath.ac.uk",
    version = "0.1.0",
    packages = [
        "pylon", "pyqle"],
    package_dir = {'': 'src'},
    zip_safe = False
)

# EOF -------------------------------------------------------------------------
