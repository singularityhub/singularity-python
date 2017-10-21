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
import os
import re
import requests

import shutil
import json
import simplejson
from singularity.logger import bot
from singularity.utils import (
    write_json,
    write_file
)
import sys

import subprocess

import tempfile
import zipfile


############################################################################
## FILE OPERATIONS #########################################################
############################################################################


def zip_up(file_list,zip_name,output_folder=None):
    '''zip_up will zip up some list of files into a package (.zip)
    :param file_list: a list of files to include in the zip.
    :param output_folder: the output folder to create the zip in. If not 
    :param zip_name: the name of the zipfile to return.
    specified, a temporary folder will be given.
    '''
    tmpdir = tempfile.mkdtemp()
   
    # Make a new archive    
    output_zip = "%s/%s" %(tmpdir,zip_name)
    zf = zipfile.ZipFile(output_zip, "w", zipfile.ZIP_DEFLATED, allowZip64=True)

    # Write files to zip, depending on type
    for filename,content in file_list.items():

        bot.debug("Adding %s to package..." %filename)

        # If it's the files list, move files into the archive
        if filename.lower() == "files":
            if not isinstance(content,list): 
                content = [content]
            for copyfile in content:
                zf.write(copyfile,os.path.basename(copyfile))
                os.remove(copyfile)

        else:

            output_file = "%s/%s" %(tmpdir, filename)
        
            # If it's a list, write to new file, and save
            if isinstance(content,list):
                write_file(output_file,"\n".join(content))
        
            # If it's a dict, save to json
            elif isinstance(content,dict):
                write_json(content,output_file)

            # If bytes, need to decode
            elif isinstance(content,bytes):
                write_file(output_file,content.decode('utf-8'))
   
            # String or other
            else: 
                output_file = write_file(output_file,content)

            if os.path.exists(output_file):
                zf.write(output_file,filename)
                os.remove(output_file)

    # Close the zip file    
    zf.close()

    if output_folder is not None:
        shutil.copyfile(output_zip,"%s/%s"%(output_folder,zip_name))
        shutil.rmtree(tmpdir)
        output_zip = "%s/%s"%(output_folder,zip_name)

    return output_zip



############################################################################
## OTHER MISC. #############################################################
############################################################################


def get_container_contents(container=None,gets=None,split_delim=None,image_package=None):
    '''get_container_contents will return a list of folders and or files
    for a container. The environmental variable SINGULARITY_HUB being set
    means that container objects are referenced instead of packages
    :param container: the container to get content for
    :param gets: a list of file names to return, without parent folders
    :param split_delim: if defined, will split text by split delimiter
    :param image_package: if defined, user has provided an image_package
    '''
    from singularity.package import package, load_package

    if container == None and image_package == None:
        bot.error("You must define an image package or container.")
        sys.exit(1)

    # Default returns are the list of files and folders
    if gets == None:
        gets = ['files.txt','folders.txt']
    if not isinstance(gets,list):
        gets = [gets]

    # We will look for everything in guts, then return it
    guts = dict()

    SINGULARITY_HUB = os.environ.get('SINGULARITY_HUB',"False")

    # Visualization deployed local or elsewhere
    if SINGULARITY_HUB == "False":
        tmpdir = tempfile.mkdtemp()
        if image_package == None:
            image_package = package(image_path=container,
                                    output_folder=tmpdir,
                                    remove_image=True)
     
        guts = load_package(image_package,get=gets)
        shutil.rmtree(tmpdir)

    # Visualization deployed by singularity hub
    else:   
        
        # user has provided a package, but not a container
        if container == None:
            guts = load_package(image_package,get=gets)

        # user has provided a container, but not a package
        else:
            for sfile in container.files:
                for gut_key in gets:        
                    if os.path.basename(sfile['name']) == gut_key:
                        if split_delim == None:
                            guts[gut_key] = requests.get(sfile['mediaLink']).text
                        else:
                            guts[gut_key] = requests.get(sfile['mediaLink']).text.split(split_delim)

    return guts
