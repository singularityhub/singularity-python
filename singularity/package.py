#!/usr/bin/env python

'''
package.py: part of singularity package

'''

from singularity.runscript import get_runscript_parameters
from singularity.cli import Singularity
from singularity.utils import zip_up
import tempfile
import tarfile
import hashlib
import os


def package(image_path,output_folder=None,runscript=True,software=True,remove_image=False,verbose=False):
    '''package will take an image and generate a zip (including the image
    to a user specified output_folder.
    :param image_path: full path to singularity image file
    :param runscript: if True, will extract runscript to include in package as runscript
    :param software: if True, will extract files.txt and folders.txt to package
    :param remove_image: if True, will not include original image in package (default,False)
    :param verbose: be verbose when using singularity --export (default,False)
    '''    
    S = Singularity(verbose=verbose)
    tmptar = S.export(image_path=image_path,pipe=False)
    tar = tarfile.open(tmptar)
    members = tar.getmembers()
    image_name = os.path.basename(image_path)
    zip_name = "%s.zip" %(image_name.replace(" ","_"))

    # Include the image in the package?
    if remove_image:
       to_package = dict()
    else:
       to_package = {image_name:image_path}

    # Package the image with an md5 sum as VERSION
    version = get_image_hash(image_path)
    to_package["VERSION"] = version

    # Look for runscript
    if runscript == True:
        try:
            runscript_member = tar.getmember("./singularity")
            runscript_file = tar.extractfile("./singularity")
            runscript = runscript_file.read()
            to_package["runscript"] = runscript
            print("Found runscript!")

            # Try to extract input args, only python supported, will return None otherwise
            params_json = get_runscript_parameters(runscript=runscript,
                                                   name=image_name,
                                                   version=version)
            if params_json != None:
                print('Extracted runscript params!')
                to_package['%s.json' %(image_name)] = params_json

        except KeyError:
            print("No runscript found in image!")
        
    if software == True:
        print("Adding software list to package!")
        files = [x.path for x in members if x.isfile()]
        folders = [x.path for x in members if x.isdir()]
        to_package["files.txt"] = files
        to_package["folders.txt"] = folders

    # Do zip up here - let's start with basic structures
    zipfile = zip_up(to_package,zip_name=zip_name,output_folder=output_folder)
    print("Package created at %s" %(zipfile))

    # return package to user
    return zipfile


def get_image_hash(image_path):
    '''get_image_hash will return an md5 hash of the file. Since we don't have git commits
    this seems like a reasonable option to "version" an image, since we can easily say yay or nay
    if the image matches the spec file
    :param image_path: full path to the singularity image
    '''
    print("Generating unique version of image (md5 hash)")
    hash_md5 = hashlib.md5()
    with open(image_path, "rb") as f:
        for chunk in iter(lambda: f.read(4096), b""):
            hash_md5.update(chunk)
    return hash_md5.hexdigest()


def docker2singularity(docker_image,output_folder=None):
    '''docker2singulrity is a wrapper for the Singularity.docker2singularity
    client function. Does not currently include runscript (/singularity) in image,
    but does export full docker image spec under /singularity.json
    :param docker_image: the full docker repo/image,eg "ubuntu:latest"
    :param output_folder: the output folder to create the image in. If not 
    specified, will use pwd.
    '''

    S = Singularity()
    docker_image = S.docker2singularity(docker_image=docker_image,
                                        output_dir=output_folder)
    return docker_image
