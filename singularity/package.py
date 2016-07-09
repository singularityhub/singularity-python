#!/usr/bin/env python

'''
package.py: part of singularity package

'''

from singularity.utils import export_image, zip_up
import tempfile
import tarfile
import os


def package(image,output_folder=None,runscript=True,software=True,remove_image=False):
    '''package will take an image and generate a zip (including the image
    to a user specified output_folder.
    :param runscript: if True, will extract runscript to include in package as runscript
    :param software: if True, will extract files.txt and folders.txt to package
    :param remove_image: if True, will not include original image in package (default,False)
    '''    

    tmptar = export_image(image)
    tar = tarfile.open(tmptar)
    members = tar.getmembers()
    image_name = os.path.basename(image)
    zip_name = "%s.zip" %(image_name.replace(" ","_"))

    # Include the image in the package?
    if remove_image:
       to_package = dict()
    else:
       to_package = {image_name:image}

    # Look for runscript
    if runscript == True:
        try:
            runscript_member = tar.getmember("./singularity")
            runscript_file = tar.extractfile("./singularity")
            runscript = runscript_file.read()
            to_package["runscript"] = runscript
            print("Found runscript!")
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
