'''
manage.py: part of singularity package

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
