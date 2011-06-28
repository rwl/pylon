# Copyright (C) 2011 Richard Lincoln
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published
# by the Free Software Foundation, either version 3 of the License,
# or (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program. If not, see <http://www.gnu.org/licenses/>.

from os.path import abspath, dirname, join
from setuptools import setup, find_packages

cwd = abspath(dirname(__file__))
f = open(join(cwd, "README"))
kwds = {"long_description": f.read()}
f.close()

setup(name="Pylon",
      author="Richard Lincoln",
      author_email="r.w.lincoln@gmail.com",
      description="PYPOWER frontend",
      url="http://pypi.python.org/pypi/Pylon",
      version="0.5",
      entry_points={"console_scripts": ["pylon = pylon.main:main"]},
      install_requires=["pypower", "pycim"],
      license="Apache License, Version 2.0",
      include_package_data=False,
      packages=find_packages(),
      zip_safe=True,
      **kwds)
