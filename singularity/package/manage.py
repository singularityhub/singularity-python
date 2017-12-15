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

from glob import glob
import os
import re

from singularity.logger import bot
from singularity.utils import get_installdir
import json
import sys
import tempfile
import zipfile

install_dir = get_installdir()


######################################################################################
# Package Data
######################################################################################

def get_packages(family=None):
    '''get packages will return a list of packages (under some family)
    provided by singularity python.If no name is specified, the default (os) will
    be used.
    :param name: the name of the package family to load
    '''
    package_base = get_package_base()
    package_folders = glob("%s/*" %(package_base))
    package_families = [os.path.basename(x) for x in package_folders]
    if family == None:
        family = "docker-os"
    family = family.lower()
    if family in package_families:
        package_folder = "%s/%s" %(package_base,family)
        packages = glob("%s/*.zip" %(package_folder))
        bot.info("Found %s packages in family %s" %(len(packages),family))
        return packages

    bot.warning("Family %s not included. Options are %s" %(family,", ".join(package_families)))
    return None


def list_package_families():
    '''return a list of package families (folders) provided by singularity python
    '''
    package_base = get_package_base()
    return glob("%s/*" %(package_base))


def get_package_base():
    '''returns base folder of packages'''
    return "%s/package/data" %(install_dir)


def list_package(package_path):
    '''list_package will list the contents of a package, without reading anything into memory
    :package_path: the full path to the package
    '''
    zf = zipfile.ZipFile(package_path, 'r')
    return zf.namelist()


def load_package(package_path,get=None):
    '''load_package will return the contents of a package, read into memory
    :param package_path: the full path to the package
    :param get: the files to load. If none specified, all things loaded
    '''
    if get == None:
        get = list_package(package_path)

    # Open the zipfile
    zf = zipfile.ZipFile(package_path, 'r')

    # The user might have provided a string and not a list
    if isinstance(get,str): 
        get = [get]

    retrieved = dict()

    for g in get:

        filename,ext = os.path.splitext(g)

        # Extract image
        if ext in [".img"]:
            tmpdir = tempfile.mkdtemp()
            print("Extracting image %s to %s..." %(g,tmpdir))
            image_extracted_path = zf.extract(g,tmpdir)
            retrieved[g] = image_extracted_path


        # Extract text
        elif ext in [".txt"] or g == "runscript":
            retrieved[g] = zf.read(g).decode('utf-8').split('\n')
        elif g in ["VERSION","NAME"]:
            retrieved[g] = zf.read(g).decode('utf-8')

        # Extract json or metadata
        elif ext in [".json"]:
            retrieved[g] = json.loads(zf.read(g).decode('utf-8'))

        else:
            bot.debug("Unknown extension %s, skipping %s" %(ext,g))

    return retrieved
