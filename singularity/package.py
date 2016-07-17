#!/usr/bin/env python

'''
package.py: part of singularity package

'''

from singularity.runscript import get_runscript_parameters
from singularity.utils import zip_up, read_file
from singularity.cli import Singularity
import tempfile
import tarfile
import hashlib
import zipfile
import json
import os


def package(image_path,output_folder=None,runscript=True,software=True,remove_image=False,verbose=False,S=None):
    '''package will take an image and generate a zip (including the image
    to a user specified output_folder.
    :param image_path: full path to singularity image file
    :param runscript: if True, will extract runscript to include in package as runscript
    :param software: if True, will extract files.txt and folders.txt to package
    :param remove_image: if True, will not include original image in package (default,False)
    :param verbose: be verbose when using singularity --export (default,False)
    :param S: the Singularity object (optional) will be created if not required.
    '''    
    if S == None:
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


def list_package(package_path):
    '''list_package will list the contents of a package, without reading anything into memory
    :package_path: the full path to the package
    '''
    zf = zipfile.ZipFile(package_path, 'r')
    return zf.namelist()
    

def calculate_similarity(pkg1,pkg2,include_files=False,include_folders=True):
    '''calculate_similarity will calculate similarity of images in packages based on
    a comparator list of (files or folders) in each package, default will calculate
    2.0*len(intersect) / total package1 + total package2
    :param pkg1: packaged image 1
    :param pkg2: packaged image 2
    :param include_files: boolean, default False. If true, will include files
    :param include_folders: boolean, default True. If true, will include files
    '''
    # Base names will be indices for full lists for comparator return object
    pkg1_name = os.path.basename(pkg1)
    pkg2_name = os.path.basename(pkg2)

    comparison = compare_package(pkg1,pkg2,include_files=include_files,include_folders=include_folders)
    score = 2.0*len(comparison["intersect"]) / (len(comparison[pkg1_name])+len(comparison[pkg2_name]))
    
    # Alert user if one is a child/parent (might want a data structure for this in future)
    if score == 1.0:
        print("Package %s and %s are identical by this metric!" %(pkg1_name,pkg2_name))

    return score


def compare_package(pkg1,pkg2,include_files=False,include_folders=True):
    '''compare_package will return the lists of files or folders (or both) that are 
    different and equal between two packages
    :param pkg1: package 1
    :param pkg1: package 2
    :param include_files: boolean, default False. If true, will include files
    :param include_folders: boolean, default True. If true, will include files
    :param get_score: if True, will calculate overall similarity as 2*len(intersect) / len(uniques) + len(intersect) 
    '''
    if include_files == False and include_folders == False:
        print("Please specify include_files and/or include_folders to be True.")
    else:

        # For future reference
        pkg1_name = os.path.basename(pkg1)
        pkg2_name = os.path.basename(pkg2)

        # Lists for all comparators for each package
        pkg1_comparators = []
        pkg2_comparators = []

        pkg1_includes = list_package(pkg1)
        pkg2_includes = list_package(pkg2)

        # Include files in comparison?
        if include_files == True:
            if "files.txt" in pkg1_includes and "files.txt" in pkg2_includes:
                pkg1_comparators += load_package(pkg1,get="files.txt")["files.txt"]
                pkg2_comparators += load_package(pkg2,get="files.txt")["files.txt"]

        # Include folders in comparison?
        if include_folders == True:
            if "folders.txt" in pkg2_includes and "folders.txt" in pkg2_includes:
                pkg1_comparators += load_package(pkg1,get="folders.txt")["folders.txt"]
                pkg2_comparators += load_package(pkg2,get="folders.txt")["folders.txt"]


        # Do the comparison
        intersect = [x for x in pkg1_comparators if x in pkg2_comparators]
        unique_pkg1 = [x for x in pkg1_comparators if x not in pkg2_comparators]
        unique_pkg2 = [x for x in pkg2_comparators if x not in pkg1_comparators]

        # Return data structure
        comparison = {"intersect":intersect,
                      "unique_%s" %(pkg1_name): unique_pkg1,
                      "unique_%s" %(pkg2_name): unique_pkg2,
                      pkg1_name:pkg1_comparators,
                      pkg2_name:pkg2_comparators}

        return comparison


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
            print("Found image %s, skipping as not feasible to load into memory." %(g))
        elif ext in [".txt"] or g == "runscript":
            retrieved[g] = zf.read(g).split('\n')
        elif g == "VERSION":
            retrieved[g] = zf.read(g)
        elif ext in [".json"]:
            retrieved[g] = json.loads(zf.read(g))
        else:
            print("Unknown extension %s, skipping %s" %(ext,g))

    return retrieved


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
