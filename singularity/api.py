#!/usr/bin/env python

'''
api.py: module for working with singularity hub api

'''

from singularity.boutiques import get_boutiques_json
from singularity.package import build_from_spec
from singularity.utils import get_installdir, read_file, write_file
import subprocess
import tempfile
import zipfile
import inspect
import shutil
import requests
import imp
import sys
import re
import os

api_base = "http://127.0.0.1/api"


def authenticate(domain=None,token_folder=None):
    '''authenticate will authenticate the user with Singularity Hub. This means
    either obtaining the token from the environment, and then trying to obtain
    the token file and reading it, and then finally telling the user to get it.
    :param domain: the domain to direct the user to for the token, default is api_base
    :param token_folder: the location of the token file, default is $HOME (~/)
    '''
    # Attempt 1: Get token from environmental variable
    token = os.environ.get("SINGULARITY_TOKEN",None)

    if token == None:
        # Is the user specifying a custom home folder?
        if token_folder == None:
            token_folder = os.environ["HOME"]

        token_file = "%s/.shub" %(token_folder)
        if os.path.exists(token_file):
            token = read_file(token_file)[0].strip('\n')
        else:
            if domain == None:
                domain = api_base
            print('''Please obtain token from %s/token
                     and save to .shub in your $HOME folder''' %(domain))
            sys.exit(1)
    return token


def get_headers(token=None):
    '''get_headers will return a simple default header for a json
    post. This function will be adopted as needed.
    :param token: an optional token to add for auth
    '''
    headers = dict()
    if token!=None:
        headers["Authentication"] = "Token %s" %(token)
    headers["Content-Type"] = "application/json"
    return headers


def api_put(url,headers,token=None,data=None):
    '''api_post will send a read file (spec) to Singularity Hub with a particular set of headers
    :param url: the url to send file to
    :param filepath: the complete path to the file
    :param headers: a dictionary with headers for the request
    :param putdata: additional data to add to the request
    '''
    if headers == None:
        headers = get_headers(token=token)
    if data == None:
        response = requests.put(url,         
                                headers=headers)
    else:
        response = requests.put(url,         
                                headers=headers,
                                data=data)
    
    return response        



def api_put(url,filename,headers,token=None):
    '''api_post will send a read file (spec) to Singularity Hub with a particular set of headers
    :param url: the url to send file to
    :param filepath: the complete path to the file
    :param headers: a dictionary with headers for the request
    '''
    if headers == None:
        headers = get_headers(token=token)
    
    with open(filename) as fh:
        putdata = fh.read()
        response = requests.put(url,
                                data=putdata,                         
                                auth=('token', token),
                                headers = headers,
                                params={'file': filepath})
    
    return response        



def push_spec(collection,name,build=True,source_dir=None,build_dir=None,size=None):
    '''push_spec will look for a Singularity file in the PWD. If it exists, the file
    is built, the user is authenticated with Singularity Hub, and the image is uploaded.
    :param build: build the image (default is True), currently not in use, as image MUST be built
    :param build_dir: the image base directory where the Singularity build file is located.
    :param size: the size of the image to build. If none specified, function will default to 1024
    :param collection: should be the unique ID of the collection
    :param name: the name of the image to push. By default will go into collection as username/imagename
    '''
    token = authenticate()
    if source_dir == None:
        source_dir = os.getcwd()
    singularityFile = "%s/Singularity" %(source_dir)
    if os.path.exists(singularityFile):

        # Prepare headers for request
        headers = dict()
        filename = os.path.basename(singularityFile)
        headers["Content-Disposition"] = "attachment; filename=%s" %(filename)
        headers["Authentication"] = "Token %s" %(token)
        headers["Content-Type"] = "text/plain" 

        #r = requests.post(url, files=files)
        #r.text

        #-F "file=@img.jpg;type=image/jpg"
        url = "%s/upload/%s" %(api_base,collection)

        # Send image to singularity hub
        response = api_put(url=url,
                           filename=singularityFile,
                           headers=headers,
                           token=token)
        return response 

    else:
        print('''Error: No build file "Singularity" found in present working directory.
                 Please create or properly name the file, and run command again.''')   
 
