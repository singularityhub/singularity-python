'''

Copyright (C) 2017 The Board of Trustees of the Leland Stanford Junior
University.
Copyright (C) 2017 Vanessa Sochat.

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


from setuptools import setup, find_packages
import codecs
import os

##########################################################################################
# HELPER FUNCTIONS #######################################################################
##########################################################################################

def get_lookup():
    '''get version by way of singularity.version, returns a 
    lookup dictionary with several global variables without
    needing to import singularity
    '''
    lookup = dict()
    version_file = os.path.join('singularity', 'version.py')
    with open(version_file) as filey:
        exec(filey.read(), lookup)
    return lookup


# Read in requirements
def get_reqs(lookup=None, key='INSTALL_REQUIRES'):
    '''get requirements, mean reading in requirements and versions from
    the lookup obtained with get_lookup'''

    if lookup == None:
        lookup = get_lookup()

    install_requires = []
    for module in lookup[key]:
        module_name = module[0]
        module_meta = module[1]
        if "exact_version" in module_meta:
            dependency = "%s==%s" %(module_name,module_meta['exact_version'])
        elif "min_version" in module_meta:
            if module_meta['min_version'] == None:
                dependency = module_name
            else:
                dependency = "%s>=%s" %(module_name,module_meta['min_version'])
        install_requires.append(dependency)
    return install_requires



# Make sure everything is relative to setup.py
install_path = os.path.dirname(os.path.abspath(__file__)) 
os.chdir(install_path)

# Get version information from the lookup
lookup = get_lookup()
VERSION = lookup['__version__']
NAME = lookup['NAME']
AUTHOR = lookup['AUTHOR']
AUTHOR_EMAIL = lookup['AUTHOR_EMAIL']
PACKAGE_URL = lookup['PACKAGE_URL']
KEYWORDS = lookup['KEYWORDS']
DESCRIPTION = lookup['DESCRIPTION']
LICENSE = lookup['LICENSE']
with open('README.md') as filey:
    LONG_DESCRIPTION = filey.read()

##########################################################################################
# MAIN ###################################################################################
##########################################################################################


if __name__ == "__main__":

    INSTALL_REQUIRES = get_reqs(lookup)

    # These requirement DON'T include sqlalchemy, only client

    INSTALL_ALL = get_reqs(lookup,'INSTALL_ALL')
    INSTALL_BUILD_GOOGLE = get_reqs(lookup,'INSTALL_BUILD_GOOGLE')
    INSTALL_METRICS = get_reqs(lookup,'INSTALL_METRICS')

    setup(name=NAME,
          version=VERSION,
          author=AUTHOR,
          author_email=AUTHOR_EMAIL,
          maintainer=AUTHOR,
          maintainer_email=AUTHOR_EMAIL,
          packages=find_packages(), 
          include_package_data=True,
          zip_safe=False,
          url=PACKAGE_URL,
          license=LICENSE,
          description=DESCRIPTION,
          long_description=LONG_DESCRIPTION,
          keywords=KEYWORDS,
          install_requires = INSTALL_REQUIRES,
          extras_require={

              'metrics': [INSTALL_METRICS],
              'google': [INSTALL_BUILD_GOOGLE],
              'all': [INSTALL_ALL]

          },
          classifiers=[
              'Intended Audience :: Science/Research',
              'Intended Audience :: Developers',
              'License :: OSI Approved :: GNU General Public License v3 or later (GPLv3+)',
              'Programming Language :: C',
              'Programming Language :: Python',
              'Topic :: Software Development',
              'Topic :: Scientific/Engineering',
              'Operating System :: Unix',
              'Programming Language :: Python :: 2.7',
              'Programming Language :: Python :: 3',
          ])
