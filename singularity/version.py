'''
The MIT License (MIT)

Copyright (c) 2016-2017 Vanessa Sochat

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
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
    ('spython', {'min_version': '0.0.31'}),
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
