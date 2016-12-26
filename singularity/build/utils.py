#!/usr/bin/env python

'''
build/utils.py: general building util functions

'''

import os
import re

import shutil
import simplejson
from singularity.logman import bot

from singularity.utils import (
    get_installdir,
    read_file
)

import sys

import subprocess

import tempfile
import zipfile


######################################################################################
# Build Templates
######################################################################################

def get_build_template(template_name,params=None,to_file=None):
    '''get_build template returns a string or file for a particular build template, which is
    intended to build a version of a Singularity image on a cloud resource.
    :param template_name: the name of the template to retrieve in build/scripts
    :param params: (if needed) a dictionary of parameters to substitute in the file
    :param to_file: if defined, will write to file. Default returns string.
    '''
    base = get_installdir()
    template_folder = "%s/build/scripts" %(base)
    template_file = "%s/%s" %(template_folder,template_name)
    if os.path.exists(template_file):
        bot.logger.debug("Found template %s",template_file)

        # Implement when needed - substitute params here
        # Will need to read in file instead of copying below
        # if params != None:
 
        if to_file != None:
            shutil.copyfile(template_file,to_file)
            bot.logger.debug("Template file saved to %s",to_file)
            return to_file

        # If the user wants a string
        content = ''.join(read_file(template_file)) 
        return content


    else:
        bot.logger.warning("Template %s not found.",template_file)
        return None
