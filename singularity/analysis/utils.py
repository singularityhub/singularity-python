#!/usr/bin/env python

'''
analysis/utils.py: part of singularity package
utilities for working with analysis / data

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
        family = "os"
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
