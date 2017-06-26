#!/usr/bin/env python

'''
utils.py: part of singularity package

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

import collections
import errno
import os
import re
import requests

import shutil
import json
import simplejson
from singularity.logger import bot
import subprocess
import sys


######################################################################################
# Local commands and requests
######################################################################################


def check_install(software=None):
    '''check_install will attempt to run the singularity command, and return an error
    if not installed. The command line utils will not run without this check.
    '''    
    if software == None:
        software = "singularity"
    cmd = [software,'--version']
    version = run_command(cmd,error_message="Cannot find %s. Is it installed?" %software)
    if version != None:
        bot.info("Found %s version %s" %(software.upper(),version))
        return True
    else:
        return False


def get_installdir():
    '''get_installdir returns the installation directory of the application
    '''
    return os.path.abspath(os.path.dirname(__file__))


def getsudo():
    sudopw = input('[sudo] password for %s: ' %(os.environ['USER']))
    os.environ['pancakes'] = sudopw
    return sudopw



def run_command(cmd,error_message=None,sudopw=None,suppress=False):
    '''run_command uses subprocess to send a command to the terminal.
    :param cmd: the command to send, should be a list for subprocess
    :param error_message: the error message to give to user if fails, 
    if none specified, will alert that command failed.
    :param execute: if True, will add `` around command (default is False)
    :param sudopw: if specified (not None) command will be run asking for sudo
    '''
    if sudopw == None:
        sudopw = os.environ.get('pancakes',None)

    if sudopw is not None:
        cmd = ' '.join(["echo", sudopw,"|","sudo","-S"] + cmd)
        if suppress == False:
            output = os.popen(cmd).read().strip('\n')
        else:
            output = cmd
            os.system(cmd)
    else:
        try:
            process = subprocess.Popen(cmd,stdout=subprocess.PIPE,stderr=subprocess.PIPE)
            output, err = process.communicate()
        except: 
            bot.error(error)
            return None
    
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
            bot.error("Error creating path %s, exiting." %path)
            sys.exit(1)


############################################################################
## FILE OPERATIONS #########################################################
############################################################################

def write_file(filename,content,mode="w"):
    '''write_file will open a file, "filename" and write content, "content"
    and properly close the file
    '''
    with open(filename,mode) as filey:
        filey.writelines(content)
    return filename


def write_json(json_obj,filename,mode="w",print_pretty=True):
    '''write_json will (optionally,pretty print) a json object to file
    :param json_obj: the dict to print to json
    :param filename: the output file to write to
    :param pretty_print: if True, will use nicer formatting   
    '''
    with open(filename,mode) as filey:
        if print_pretty == True:
            filey.writelines(simplejson.dumps(json_obj, indent=4, separators=(',', ': ')))
        else:
            filey.writelines(simplejson.dumps(json_obj))
    return filename


def read_file(filename,mode="r"):
    '''write_file will open a file, "filename" and write content, "content"
    and properly close the file
    '''
    with open(filename,mode) as filey:
        content = filey.readlines()
    return content


def read_json(filename,mode='r'):
    '''read_json reads in a json file and returns
    the data structure as dict.
    '''
    with open(filename,mode) as filey:
        data = json.load(filey)
    return data


def clean_up(files):
    '''clean up will delete a list of files, only if they exist
    '''
    if not isinstance(files,list):
        files = [files]

    for f in files:
        if os.path.exists(f):
            bot.verbose3("Cleaning up %s" %f)
            os.remove(f)


def format_container_name(name,special_characters=None):
    '''format_container_name will take a name supplied by the user,
    remove all special characters (except for those defined by "special-characters"
    and return the new image name.
    '''
    if special_characters == None:
        special_characters = []
    return ''.join(e.lower() for e in name if e.isalnum() or e in special_characters)


def remove_uri(container):
    '''remove_uri will remove docker:// or shub:// from the uri
    '''
    return container.replace('docker://','').replace('shub://','')


def download_repo(repo_url,destination,commit=None):
    '''download_repo
    :param repo_url: the url of the repo to clone from
    :param destination: the full path to the destination for the repo
    '''
    command = "git clone %s %s" %(repo_url,destination)
    os.system(command)
    return destination
