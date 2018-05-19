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
import os
import re
import requests

import shutil
import json
from singularity.logger import bot
from singularity.utils import (
    write_json,
    write_file
)
import sys
import subprocess

from singularity.analysis.reproduce.utils import (
    extract_guts, 
    delete_image_tar 
)
from singularity.analysis.reproduce import get_image_tar

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


def get_container_contents(container, split_delim=None):
    '''get_container_contents will return a list of folders and or files
    for a container. The environmental variable SINGULARITY_HUB being set
    means that container objects are referenced instead of packages
    :param container: the container to get content for
    :param gets: a list of file names to return, without parent folders
    :param split_delim: if defined, will split text by split delimiter
    '''

    # We will look for everything in guts, then return it
    guts = dict()

    SINGULARITY_HUB = os.environ.get('SINGULARITY_HUB',"False")

    # Visualization deployed local or elsewhere
    if SINGULARITY_HUB == "False":
        file_obj,tar = get_image_tar(container)     
        guts = extract_guts(image_path=container, tar=tar)
        delete_image_tar(file_obj, tar)

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
