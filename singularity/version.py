'''

Copyright (C) 2017 The Board of Trustees of the Leland Stanford Junior
University.
Copyright (C) 2016-2017 Vanessa Sochat.

This program is free software: you can redistribute it and/or modify it
under the terms of the GNU Affero General Public License as published by
the Free Software Foundation, either version 3 of the License, or (at your
option) any later version.

This program is distributed in the hope that it will be useful, but WITHOUT
ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or
FITNESS FOR A PARTICULAR PURPOSE.  See the GNU Affero General Public
License for more details.

You should have received a copy of the GNU Affero General Public License
along with this program.  If not, see <https://www.gnu.org/licenses/>.

'''

__version__ = "2.5"
AUTHOR = 'Vanessa Sochat'
AUTHOR_EMAIL = 'vsochat@stanford.edu'
NAME = 'singularity'
PACKAGE_URL = "http://www.github.com/singularityware/singularity-python"
KEYWORDS = 'singularity containers hub reproducibility package science visualization'
DESCRIPTION = "command line tools for visualization and analysis of singularity containers."
LICENSE = "LICENSE"

INSTALL_REQUIRES = (
    ('spython', {'min_version': '0.0.35'}),
    ('requests', {'min_version': '2.18.4'}),
    ('retrying', {'min_version': '1.3.3'}),
    ('pygments', {'min_version': '2.1.3'}),
)

################################################################################
# Submodule Requirements (no database, just client)


# Container comparison and analysis metrics

# can we remove this?

INSTALL_METRICS = (
    ('pandas', {'min_version': '0.20.3'}),
)

INSTALL_BUILD_GOOGLE = (
    ('google-api-python-client', {'min_version': "1.6.4"}),
    ('oauth2client', {'exact_version': '3.0'})
)

INSTALL_ALL = (INSTALL_REQUIRES +
               INSTALL_METRICS +
               INSTALL_BUILD_GOOGLE)
