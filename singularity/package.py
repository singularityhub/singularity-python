#!/usr/bin/env python

'''
package.py: part of singularity package

'''

from singularity.utils import export_image, zip_up
import tarfile
import os

def package(image,runscript=True,software=True):
    
    tmptar = export_image(image)
    tar = tarfile.open(tmptar)
    members = tar.getmembers()

    # Look for runscript
    if runscript == True:
        print("Adding runscript to package!")
    

    if software == True:
        print("Adding software list to package!")

    # Do zip up here

    # Return package to user!

