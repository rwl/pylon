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

from setuptools import setup, find_packages

setup(
    author="Richard W. Lincoln",
    author_email="richard.lincoln@eee.strath.ac.uk",
    description="Open source power system and energy market analysis",
    url="https://pylon.eee.strath.ac.uk",
    version="0.1.8",
    entry_points={
        "gui_scripts": [
            "envisage = pylon.plugin.main:main",
            "pylon = pylon.ui.model_view.main:main",
            "pyreto = pylon.ui.model_view.pyreto:main"
        ]
    },
#    extras_require={},
#    ext_modules=[],
    install_requires=[
        "Traits", "TraitsBackendWX", "Chaco", "EnvisagePlugins", "ConfigObj"
    ],
    license="GPLv2",
    name="Pylon",
    include_package_data=True,
#    exclude_package_data={"": ["*.ecore"]},
#    package_data={"": ["*.txt", "*.rst", "*.png", "*.jpg", "*.ini"]},
#    package_dir={"": "src"},
    packages=find_packages(),#"src"),#exclude=["docs", "docs.*"]),
    namespace_packages=[
        "enthought", "enthought.pyface", "enthought.pyface.ui",
        "enthought.plugins"
    ],
    platforms = ["Windows", "Linux", "Mac OS-X", "Unix", "Solaris"],
    zip_safe=False
)

# EOF -------------------------------------------------------------------------
