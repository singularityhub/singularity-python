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
    read_file,
    run_command
)

import sys

from subprocess import (
    Popen,
    PIPE,
    STDOUT
)

import tempfile
import zipfile

######################################################################################
# Testing/Retry Functions
######################################################################################

def stop_if_result_none(result):
    '''stop if result none will return True if we should not retry 
    when result is none, False otherwise using retrying python package
    '''
    do_retry = result is not None
    return do_retry


def test_container(image_path):
    '''test_container is a simple function to send a command to a container, and 
    return the status code and any message run for the test. It does it by
    way of sending an echo of some message, which (I think?) should
    work in most linux.
    :param image_path: path to the container image
    '''
    testing_command = ["singularity", "exec", image, 'echo pancakemania']
    output = Popen(testing_command,stderr=STDOUT,stdout=PIPE)
    t = output.communicate()[0],output.returncode
    result = {'message':t[0],
              'return_code':t[1]}
    return result


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


######################################################################################
# Software Versions
######################################################################################


def get_singularity_version(singularity_version=None):
    '''get_singularity_version will determine the singularity version for a build
    first, an environmental variable is looked at, followed by using the system
    version.
    '''
    if singularity_version == None:        
        singularity_version = os.environ.get("SINGULARITY_VERSION",None)
        
    # Next get from system
    if singularity_version == None:
        try:
            cmd = ['singularity','--version']
            singularity_version = run_command(cmd,error_message="Cannot determine Singularity version!").decode('utf-8').strip('\n')
            bot.logger.info("Singularity %s being used.",singularity_version)
        except:
            singularity_version = None
            bot.logger.warning("Singularity version not found, so it's likely not installed.")

    return singularity_version



######################################################################################
# Extensions and Files
######################################################################################


def sniff_extension(file_path,verbose=True):
    '''sniff_extension will attempt to determine the file type based on the extension,
    and return the proper mimetype
    :param file_path: the full path to the file to sniff
    :param verbose: print stuff out
    '''
    mime_types =    { "xls": 'application/vnd.ms-excel',
                      "xlsx": 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
                      "xml": 'text/xml',
                      "ods": 'application/vnd.oasis.opendocument.spreadsheet',
                      "csv": 'text/plain',
                      "tmpl": 'text/plain',
                      "pdf":  'application/pdf',
                      "php": 'application/x-httpd-php',
                      "jpg": 'image/jpeg',
                      "png": 'image/png',
                      "gif": 'image/gif',
                      "bmp": 'image/bmp',
                      "txt": 'text/plain',
                      "doc": 'application/msword',
                      "js": 'text/js',
                      "swf": 'application/x-shockwave-flash',
                      "mp3": 'audio/mpeg',
                      "zip": 'application/zip',
                      "rar": 'application/rar',
                      "tar": 'application/tar',
                      "arj": 'application/arj',
                      "cab": 'application/cab',
                      "html": 'text/html',
                      "htm": 'text/html',
                      "default": 'application/octet-stream',
                      "folder": 'application/vnd.google-apps.folder',
                      "img" : "application/octet-stream" }

    ext = os.path.basename(file_path).split('.')[-1]

    mime_type = mime_types.get(ext,None)

    if mime_type == None:
        mime_type = mime_types['txt']

    if verbose==True:
        bot.logger.info("%s --> %s", file_path, mime_type)

    return mime_type
