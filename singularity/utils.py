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
import collections
import errno
import os
import re
import requests

import shutil
import json
from singularity.logger import bot
from subprocess import (
    Popen,
    PIPE,
    STDOUT
)
import sys


##########################################################################
# Local commands and requests
##########################################################################


def check_install(software=None, quiet=True):
    '''check_install will attempt to run the singularity command, and
       return True if installed. The command line utils will not run 
       without this check.
    '''
    if software is None:
        software = "singularity"
    cmd = [software, '--version']
    try:
        version = run_command(cmd,software)
    except: # FileNotFoundError
        return False
    if version is not None:
        if quiet is False and version['return_code'] == 0:
            version = version['message']
            bot.info("Found %s version %s" % (software.upper(), version))
        return True 
    return False


def get_installdir():
    '''get_installdir returns the installation directory of the application
    '''
    return os.path.abspath(os.path.dirname(__file__))



def run_command(cmd, sudo=False):
    '''run_command uses subprocess to send a command to the terminal.
    :param cmd: the command to send, should be a list for subprocess
    :param error_message: the error message to give to user if fails,
    if none specified, will alert that command failed.
    :param sudopw: if specified (not None) command will be run asking for sudo
    '''
    if sudo is True:
        cmd = ['sudo'] + cmd

    output = Popen(cmd,stderr=STDOUT,stdout=PIPE)
    t = output.communicate()[0],output.returncode
    output = {'message':t[0],
              'return_code':t[1]}

    return output


############################################################################
## FOLDER OPERATIONS #########################################################
############################################################################


def mkdir_p(path):
    '''mkdir_p attempts to get the same functionality as mkdir -p
    :param path: the path to create.
    '''
    try:
        os.makedirs(path)
    except OSError as e:
        if e.errno == errno.EEXIST and os.path.isdir(path):
            pass
        else:
            bot.error("Error creating path %s, exiting." % path)
            sys.exit(1)


############################################################################
## FILE OPERATIONS #########################################################
############################################################################

def write_file(filename, content, mode="w"):
    '''write_file will open a file, "filename" and write content, "content"
    and properly close the file
    '''
    with open(filename, mode) as filey:
        filey.writelines(content)
    return filename


def write_json(json_obj, filename, mode="w", print_pretty=True):
    '''write_json will (optionally,pretty print) a json object to file
    :param json_obj: the dict to print to json
    :param filename: the output file to write to
    :param pretty_print: if True, will use nicer formatting
    '''
    with open(filename, mode) as filey:
        if print_pretty:
            filey.writelines(
                json.dumps(
                    json_obj,
                    indent=4,
                    separators=(
                        ',',
                        ': ')))
        else:
            filey.writelines(json.dumps(json_obj))
    return filename


def read_file(filename, mode="r", readlines=True):
    '''write_file will open a file, "filename" and write content, "content"
    and properly close the file
    '''
    with open(filename, mode) as filey:
        if readlines is True:
            content = filey.readlines()
        else:
            content = filey.read()
    return content


def read_json(filename, mode='r'):
    '''read_json reads in a json file and returns
    the data structure as dict.
    '''
    with open(filename, mode) as filey:
        data = json.load(filey)
    return data


def clean_up(files):
    '''clean up will delete a list of files, only if they exist
    '''
    if not isinstance(files, list):
        files = [files]

    for f in files:
        if os.path.exists(f):
            bot.verbose3("Cleaning up %s" % f)
            os.remove(f)


def format_container_name(name, special_characters=None):
    '''format_container_name will take a name supplied by the user,
    remove all special characters (except for those defined by "special-characters"
    and return the new image name.
    '''
    if special_characters is None:
        special_characters = []
    return ''.join(e.lower()
                   for e in name if e.isalnum() or e in special_characters)


def remove_uri(container):
    '''remove_uri will remove docker:// or shub:// from the uri
    '''
    return container.replace('docker://', '').replace('shub://', '')


def download_repo(repo_url, destination, commit=None):
    '''download_repo
    :param repo_url: the url of the repo to clone from
    :param destination: the full path to the destination for the repo
    '''
    command = "git clone %s %s" % (repo_url, destination)
    os.system(command)
    return destination
