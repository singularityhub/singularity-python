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

import os
import re

import shutil
from singularity.logger import bot

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
    return the status code and any message run for the test. This comes after
    :param image_path: path to the container image
    '''
    from singularity.utils import run_command
    bot.debug('Testing container exec with a list command.')
    testing_command = ["singularity", "exec", image_path, 'ls']
    return run_command(testing_command)
    

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
        bot.debug("Found template %s" %template_file)

        # Implement when needed - substitute params here
        # Will need to read in file instead of copying below
        # if params != None:
 
        if to_file is not None:
            shutil.copyfile(template_file,to_file)
            bot.debug("Template file saved to %s" %to_file)
            return to_file

        # If the user wants a string
        content = ''.join(read_file(template_file)) 
        return content


    else:
        bot.warning("Template %s not found." %template_file)


######################################################################################
# Software Versions
######################################################################################


def get_singularity_version(singularity_version=None):
    '''get_singularity_version will determine the singularity version for a build
    first, an environmental variable is looked at, followed by using the system
    version.
    '''

    if singularity_version is None:        
        singularity_version = os.environ.get("SINGULARITY_VERSION")
        
    if singularity_version is None:
        try:
            cmd = ['singularity','--version']
            output = run_command(cmd)

            if isinstance(output['message'],bytes):
                output['message'] = output['message'].decode('utf-8')
            singularity_version = output['message'].strip('\n')
            bot.info("Singularity %s being used." % singularity_version)
            
        except:
            singularity_version = None
            bot.warning("Singularity version not found, so it's likely not installed.")

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
                      "simg": 'application/zip',
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
        bot.info("%s --> %s" %(file_path, mime_type))

    return mime_type


def get_script(script_name):
    '''get_script will return a build script_name, if it is included 
    in singularity/build/scripts, otherwise will alert the user and return None
    :param script_name: the name of the script to look for
    '''
    install_dir = get_installdir()
    script_path = "%s/build/scripts/%s" %(install_dir,script_name)
    if os.path.exists(script_path):
        return script_path
    else:
        bot.error("Script %s is not included in singularity-python!" %script_path)
        return None
