'''
package.py: part of singularity package

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

from singularity.logman import bot

from singularity.utils import (
    calculate_folder_size,
    format_container_name,
    read_file, 
    zip_up
)

from singularity.cli import Singularity
from singularity.reproduce import (
    get_image_file_hash,
    get_image_hashes,
    get_memory_tar,
    extract_content
)
import tempfile
import tarfile
import hashlib
import zipfile
import shutil
import json
import io
import os
import re
import sys


def estimate_image_size(spec_file,sudopw=None,padding=None):
    '''estimate_image_size will generate an image in a directory, and add
    some padding to it to estimate the size of the image file to generate
    :param sudopw: the sudopw for Singularity, root should provide ''
    :param spec_file: the spec file, called "Singuarity"
    :param padding: the padding (MB) to add to the image
    '''
    if padding == None:
        padding = 200

    if not isinstance(padding,int):
        padding = int(padding)

    image_folder = build_from_spec(spec_file=spec_file, # default will package the image
                                   sudopw=sudopw, # with root should not need sudo
                                   build_folder=True,
                                   debug=False)
    original_size = calculate_folder_size(image_folder)
    
    bot.logger.debug("Original image size calculated as %s",original_size)
    padded_size = original_size + padding
    bot.logger.debug("Size with padding will be %s",padded_size)
    return padded_size


def build_from_spec(spec_file=None,build_dir=None,size=None,sudopw=None,
                    build_folder=False,debug=False):
    '''build_from_spec will build a "spec" file in a "build_dir" and return the directory
    :param spec_file: the spec file, called "Singuarity"
    :param sudopw: the sudopw for Singularity, root should provide ''
    :param build_dir: the directory to build in. If not defined, will use tmpdir.
    :param size: the size of the image
    :param build_folder: "build" the image into a folder instead. Default False
    :param debug: ask for verbose output from builder
    '''
    if spec_file == None:
        spec_file = "Singularity"

    if build_dir == None:
        build_dir = tempfile.mkdtemp()

    bot.logger.debug("Building in directory %s",build_dir)

    # Copy the spec to a temporary directory
    bot.logger.debug("Spec file set to %s",spec_file)
    spec_path = "%s/%s" %(build_dir,os.path.basename(spec_file))
    bot.logger.debug("Spec file for build should be in %s",spec_path)

    # If it's not already there
    if not os.path.exists(spec_path):
        shutil.copyfile(spec_file,spec_path)

    image_path = "%s/image" %(build_dir)

    # Run create image and bootstrap with Singularity command line tool.
    if sudopw is not None:
        cli = Singularity(sudopw=sudopw,debug=debug)
    else:
        cli = Singularity(debug=debug)

    print("\nCreating and bootstrapping image...")

    # Does the user want to "build" into a folder or image?
    if build_folder == True:
        bot.logger.debug("build_folder is true, creating %s",image_path)
        os.mkdir(image_path)
    else:
        cli.create(image_path,size=size,sudo=True)

    result = cli.bootstrap(image_path=image_path,spec_path=spec_path)
    print(result)

    # If image, rename based on hash
    if build_folder == False:
        version = get_image_file_hash(image_path)
        final_path = "%s/%s" %(build_dir,version)
        os.rename(image_path,final_path)
        image_path = final_path

    bot.logger.debug("Built image: %s",image_path)
    return image_path


def package(image_path,spec_path=None,output_folder=None,runscript=True,
            software=True,remove_image=False,verbose=False,S=None,sudopw=None,
            old_version=False):
    '''package will take an image and generate a zip (including the image
    to a user specified output_folder.
    :param image_path: full path to singularity image file
    :param runscript: if True, will extract runscript to include in package as runscript
    :param software: if True, will extract files.txt and folders.txt to package
    :param remove_image: if True, will not include original image in package (default,False)
    :param verbose: be verbose when using singularity --export (default,False)
    :param S: the Singularity object (optional) will be created if not required.
    '''    
    # Run create image and bootstrap with Singularity command line tool.
    if S == None:
        if sudopw != None:
            S = Singularity(sudopw=sudopw,debug=verbose)
        else:
            S = Singularity(debug=verbose) # This command will ask the user for sudo

    # Singularity < version 2.3
    if old_version == False:
        file_obj,tar = get_memory_tar(image_path)

    # Singularity 2.3 and up
    else:
        tmptar = S.export(image_path=image_path,old_version=True)
        tar = tarfile.open(tmptar)

    members = tar.getmembers()
    image_name = os.path.basename(image_path)
    zip_name = "%s.zip" %(image_name.replace(" ","_"))

    # Include the image in the package?
    if remove_image:
        to_package = dict()
    else:
        to_package = {"files":[image_path]}

    # If the specfile is provided, it should also be packaged
    if spec_path is not None:
        singularity_spec = "".join(read_file(spec_path))
        to_package['Singularity'] = singularity_spec
        to_package["VERSION"] = get_image_file_hash(image_path)
    

    # Look for runscript
    if runscript is True:
        try:
            to_package["runscript"] = extract_content(image_path,'./singularity',cli=S)
            bot.logger.debug("Found runscript.")
        except KeyError:
            bot.logger.warning("No runscript found")

    if software == True:
        bot.logger.info("Adding software list to package.")
        files = [x.path for x in members if x.isfile()]
        folders = [x.path for x in members if x.isdir()]
        to_package["files.txt"] = files
        to_package["folders.txt"] = folders

    # Do zip up here - let's start with basic structures
    zipfile = zip_up(to_package,zip_name=zip_name,output_folder=output_folder)
    bot.logger.debug("Package created at %s" %(zipfile))

    if old_version == False:
        file_obj.close()
    
    # return package to user
    return zipfile


def list_package(package_path):
    '''list_package will list the contents of a package, without reading anything into memory
    :package_path: the full path to the package
    '''
    zf = zipfile.ZipFile(package_path, 'r')
    return zf.namelist()



def load_package(package_path,get=None):
    '''load_package will return the contents of a package, read into memory
    :param package_path: the full path to the package
    :param get: the files to load. If none specified, all things loaded
    '''
    if get == None:
        get = list_package(package_path)

    # Open the zipfile
    zf = zipfile.ZipFile(package_path, 'r')

    # The user might have provided a string and not a list
    if isinstance(get,str): 
        get = [get]

    retrieved = dict()
    for g in get:

        filename,ext = os.path.splitext(g)

        if ext in [".img"]:
            tmpdir = tempfile.mkdtemp()
            print("Extracting image %s to %s..." %(g,tmpdir))
            image_extracted_path = zf.extract(g,tmpdir)
            retrieved[g] = image_extracted_path
        elif ext in [".txt"] or g == "runscript":
            retrieved[g] = zf.read(g).decode('utf-8').split('\n')
        elif g in ["VERSION","NAME"]:
            retrieved[g] = zf.read(g).decode('utf-8')
        elif ext in [".json"]:
            retrieved[g] = json.loads(zf.read(g).decode('utf-8'))
        else:
            bot.logger.debug("Unknown extension %s, skipping %s", ext,g)

    return retrieved
