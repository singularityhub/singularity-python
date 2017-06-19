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

        # If it's a list, write to new file, and save
        elif isinstance(content,list):
            filey = write_file("%s/%s" %(tmpdir,filename),"\n".join(content))
            zf.write(filey,filename)
            os.remove(filey)

        # If it's a dict, save to json
        elif isinstance(content,dict):
            filey = write_json(content,"%s/%s" %(tmpdir,filename))
            zf.write(filey,filename)
            os.remove(filey)

        # If it's a string, do the same
        elif isinstance(content,str):
            filey = write_file("%s/%s" %(tmpdir,filename),content)
            zf.write(filey,filename)
            os.remove(filey)

        # Otherwise, just write the content into a new archive
        elif isinstance(content,bytes):
            filey = write_file("%s/%s" %(tmpdir,filename),content.decode('utf-8'))
            zf.write(filey,filename)
            os.remove(filey)

        else: 
            zf.write(content,filename)

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


def calculate_folder_size(folder_path,truncate=True):
    '''calculate_folder size recursively walks a directory to calculate
    a total size (in MB)
    :param folder_path: the path to calculate size for
    :param truncate: if True, converts size to an int
    '''
    total_size = 0
    for dirpath, dirnames, filenames in os.walk(folder_path):
        for filey in filenames:
            file_path = os.path.join(dirpath, filey)
            if os.path.isfile(file_path) and not os.path.islink(file_path):
                total_size += os.path.getsize(file_path) # this is bytes
    size_mb = total_size / 1000000
    if truncate == True:
        size_mb = int(size_mb)
    return size_mb
