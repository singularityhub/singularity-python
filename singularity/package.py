#!/usr/bin/env python

'''
package.py: part of singularity package

'''

from singularity.logman import bot

from singularity.utils import (
    calculate_folder_size,
    format_container_name,
    read_file, 
    zip_up
)

from singularity.cli import Singularity
import tempfile
import tarfile
import hashlib
import zipfile
import shutil
import json
import os


def estimate_image_size(spec_file=None,sudopw=None,padding=50):
    '''estimate_image_size will generate an image in a directory, and add
    some padding to it to estimate the size of the image file to generate
    :param sudopw: the sudopw for Singularity, root should provide ''
    :param spec_file: the spec file, called "Singuarity"
    :param padding: the padding (MB) to add to the image
    '''
    size_dir = tempfile.mkdtemp()
    tmp_dir = tempfile.mkdtemp()
    image_folder = build_from_spec(spec_file=spec_file, # default will package the image
                                   sudopw=sudopw, # with root should not need sudo
                                   output_folder=size_dir,
                                   build_dir=tmp_dir,
                                   build_folder=True)
    original_size = calculate_folder_size(image_folder)    
    bot.logger.debug("Original image size calculated as %s",original_size)
    padded_size = original_size + padding
    bot.logger.debug("Size with padding will be %s",padded_size)
    shutil.rmtree(size_dir)
    os.system('sudo rm -rf %s' %tmp_dir)
    return padded_size


def build_from_spec(spec_file=None,build_dir=None,size=None,sudopw=None,
                    output_folder=None,build_folder=False):
    '''build_from_spec will build a "spec" file in a "build_dir" and return the directory
    :param spec_file: the spec file, called "Singuarity"
    :param sudopw: the sudopw for Singularity, root should provide ''
    :param build_dir: the directory to build in. If not defined, will use tmpdir.
    :param size: the size of the image
    :param output_folder: where to output the image package
    :param build_folder: "build" the image into a folder instead. Default False
    '''
    if spec_file == None:
        spec_file = "Singularity"
    if build_dir == None:
        build_dir = tempfile.mkdtemp()
    bot.logger.debug("Building in directory %s",build_dir)

    # Copy the spec to a temporary directory
    spec_path = "%s/%s" %(build_dir,spec_file)
    if not os.path.exists(spec_path):
        shutil.copyfile(spec_file,spec_path)
    # If name isn't provided, call it Singularity
    image_path = "%s/image" %(build_dir)
    # Run create image and bootstrap with Singularity command line tool.
    if sudopw != None:
        cli = Singularity(sudopw=sudopw)
    else:
        cli = Singularity() # This command will ask the user for sudo
    print("\nCreating and boostrapping image...")
    # Does the user want to "build" into a folder or image?
    if build_folder == True:
        os.mkdir(image_path)
    else:
        cli.create(image_path,size=size)
    result = cli.bootstrap(image_path=image_path,spec_path=spec_path)
    print(result)
    # If image, rename based on hash
    if build_folder == False:
        version = get_image_hash(image_path)
        final_path = "%s/%s" %(build_dir,version)
        os.rename(image_path,final_path)
        image_path = final_path
    bot.logger.debug("Built image: %s",image_path)
    return image_path


def package(image_path,spec_path=None,output_folder=None,runscript=True,
            software=True,remove_image=False,verbose=False,S=None,sudopw=None):
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
            S = Singularity(sudopw=sudopw,verbose=verbose)
        else:
            S = Singularity(verbose=verbose) # This command will ask the user for sudo
    tmptar = S.export(image_path=image_path,pipe=False)
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
    if spec_path != None:
        singularity_spec = "".join(read_file(spec_path))
        to_package['Singularity'] = singularity_spec
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


def get_image_hash(image_path):
    '''get_image_hash will return an md5 hash of the file. Since we don't have git commits
    this seems like a reasonable option to "version" an image, since we can easily say yay or nay
    if the image matches the spec file
    :param image_path: full path to the singularity image
    '''
    hash_md5 = hashlib.md5()
    with open(image_path, "rb") as f:
        for chunk in iter(lambda: f.read(4096), b""):
            hash_md5.update(chunk)
    return hash_md5.hexdigest()
