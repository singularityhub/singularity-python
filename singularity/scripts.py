#!/usr/bin/env python

'''
script.py: part of singularity command line tool
Runtime executable, "shub"

'''

from singularity.package import package
from singularity.utils import check_install
from glob import glob
import argparse
import sys
import os

def main():
    parser = argparse.ArgumentParser(
    description="package Singularity containers for singularity hub.")
    parser.add_argument("--image", dest='image', help="full path to singularity image (for use with --package)", type=str, default=None)
    parser.add_argument("--outfolder", dest='outfolder', help="full path to folder for output, if not specified, will go to pwd", type=str, default=None)
    parser.add_argument('--package', help="package a singularity container for singularity hub", dest='package', default=False, action='store_true')
    try:
        args = parser.parse_args()
    except:
        parser.print_help()
        sys.exit(0)

    # We can only continue if singularity is installed
    if check_install() == True:

       # We also must have an image to work with
       if args.image !=None:
           image = os.path.abspath(args.image)

           # Output folder will be pwd if not specified
           if args.outfolder == None:
               output_folder = os.getcwd()
           else:
               output_folder = args.outfolder

           # Make sure the image exists!
           if os.path.exists(image):

               # The user wants to package the image
               if args.package == True:
                   package(image,output_folder=output_folder,runscript=True,software=True)

       else:
          print("Please specify a singularity image with --image.")


if __name__ == '__main__':
    main()
