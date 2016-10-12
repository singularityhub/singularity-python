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

def api_put(url,filepath,headers):
    '''api_put will send a filepath to singularity hub with a particular set of headers
    :param url: the url to send file to
    :param filepath: the complete path to the file
    :param headers: a dictionary with headers for the request
    '''

    # Option 1: stream via a memory mapped file?
    #filey = open(filepath,'rb')
    #mmapped_file = mmap.mmap(filey.fileno(), 0, access=mmap.ACCESS_READ)

    # Do the request
    #request = urllib2.Request(url, mmapped_file)
    #for header_name,header_content in headers.items():
    #    request.add_header(header_name,header_content)
    #response = urllib2.urlopen(request)

    # Close everything
    #mmapped_file.close()
    #filey.close()

    # Option 2: standard requests
    with open(filepath) as filey:
        data = filey.read()
        response = requests.put(url,                        
                                headers=headers,
                                data={'file': filepath})
    # TODO: not yet written, need to do work on shub server
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

        # Build the image from the spec, get back the temporary directory
        image_package = build_from_spec(spec=singularityfile,
                                        build_dir=build_dir,
                                        size=size)

        # Prepare headers for request
        headers = dict()
        filename = os.path.basename(image_package)
        headers["Content-Disposition"] = "attachment; filename=%s" %(filename)
        headers["Authentication"] = "Token %s" %(token)
        headers["Content-Type"] = "application/zip" 

        #r = requests.post(url, files=files)
        #r.text

        #-F "file=@img.jpg;type=image/jpg"
        #url = "%s/upload/%s/%s" %(api_base,collection,name)

        # Send image to singularity hub
        api_put(url=url,
                headers=headers,
                filepath=image_package)
        
        # STOPPED HERE - need to do this!
        

    else:
        print('''Error: No build file "Singularity" found in present working directory.
                 Please create or properly name the file, and run command again.''')   
 
