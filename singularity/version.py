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

__version__ = "2.4.1"
AUTHOR = 'Vanessa Sochat'
AUTHOR_EMAIL = 'vsochat@stanford.edu'
NAME = 'singularity'
PACKAGE_URL = "http://www.github.com/singularityware/singularity-python"
KEYWORDS = 'singularity containers hub reproducibility package science visualization'
DESCRIPTION = "Command line tool for working with singularity-hub and packaging singularity containers."
LICENSE = "LICENSE"

INSTALL_REQUIRES = (

    ('demjson', {'exact_version': "2.2.4"}),
    ('python-dateutil', {'exact_verison': "2.5.3"}),
    ('pandas', {'exact_verison': '0.20.3'}),
    ('requests', {'exact_version': '2.18.4'}),
    ('requests-toolbelt', {'exact_version': '0.8.0'}),
    ('retrying', {'exact_version': '1.3.3'}),
    ('pygments', {'min_version': '2.1.3'}),
    ('google-api-python-client', {'min_version': "1.6.4"}),
    ('oauth2client', {'exact_version': '3.0'})
)
