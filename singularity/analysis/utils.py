#!/usr/bin/env python

'''
analysis/utils.py: part of singularity package
utilities for working with analysis / data

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
import requests

import shutil
import simplejson
from singularity.logman import bot
from singularity.utils import get_installdir
import sys

import subprocess
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
    package_base = "%s/analysis/packages" %(install_dir)
    package_folders = glob("%s/*" %(package_base))
    package_families = [os.path.basename(x) for x in package_folders]
    if family == None:
        family = "docker-os"
    family = family.lower()
    if family in package_families:
        package_folder = "%s/%s" %(package_base,family)
        packages = glob("%s/*.zip" %(package_folder))
        bot.logger.info("Found %s packages in family %s",len(packages),family)
        return packages

    bot.logger.warning("Family %s not included. Options are %s",family,", ".join(package_families))
    return None


def list_package_families():
    '''return a list of package families (folders) provided by singularity python
    '''
    package_base = "%s/analysis/packages" %(install_dir)
    return glob("%s/*" %(package_base))


def get_package_base():
    '''returns base folder of packages'''
    return "%s/analysis/packages" %(install_dir)
