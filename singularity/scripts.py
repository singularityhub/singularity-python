#!/usr/bin/env python

'''
script.py: part of singularity command line tool
Runtime executable, "shub"

'''

from singularity.api import build_spec
from singularity.app import make_tree, make_difference_tree, make_sim_tree
from singularity.utils import check_install, getsudo
from singularity.package import package
from glob import glob
import argparse
import sys
import os

def main():
    parser = argparse.ArgumentParser(
    description="Singularity Hub command line tool")

    # Single image, must be string
    parser.add_argument("--image", dest='image', 
                        help="full path to singularity image (for use with --package and --tree)", 
                        type=str, default=None)

    # Build a singularity image from a spec file, push to singularity hub
    parser.add_argument("--push", dest='push', 
                        help="build a Singularity image from a spec (Singularity) file, push to Singularity hub", 
                        action='store_true', default=False)

    # The user must specify a collection id to push to the hub
    parser.add_argument("--collection", dest='collection', 
                        help="The collection ID to push to, where the user has permission to push.", 
                        type=str, default=None)

    # The user must specify a collection id to push to the hub
    parser.add_argument("--name", dest='name', 
                        help="The name of the image, must be all lowercase without spaces and special characters other than '-'", 
                        type=str, default=None)

    # The user must specify a collection id to push to the hub
    parser.add_argument("--size", dest='size', 
                        help="The size of the image to build. If None provided, will use 1024", 
                        type=str, default=None)

    # The user must specify a collection id to push to the hub
    parser.add_argument("--collection", dest='collection', 
                        help="build a Singularity image from a spec (Singularity) file, push to Singularity hub", 
                        type=str, default=None)


    # Multiple images, separated by commas
    parser.add_argument("--images", dest='images', 
                        help="full path to singularity images,separated with commas (for use with --difftree)", 
                        type=str, default=None)
 
    # Output folder, if needed
    parser.add_argument("--outfolder", dest='outfolder', 
                        help="full path to folder for output, if not specified, will go to pwd", 
                        type=str, default=None)

    # Input folder, if different from pwd
    parser.add_argument("--infolder", dest='infolder', 
                        help="full path to input directory (with Singularity file), if not specified, will use pwd", 
                        type=str, default=None)

    # Does the user want to package an image?
    parser.add_argument('--package', dest="package", 
                        help="package a singularity container for singularity hub", 
                        default=False, action='store_true')

    # View the guts of a Singularity image
    parser.add_argument('--tree', dest='tree', 
                        help="view the guts of an singularity image", 
                        default=False, action='store_true')

    # View the difference between two Singularity images
    parser.add_argument('--difftree', dest='difftree', 
                       help="view files and folders unique to an image or package, specify --images base.img,subtraction.img",
                       default=False, action='store_true')
    
    # View similarities between two Singularity images
    parser.add_argument('--simtree', dest='simtree', 
                        help="view common files and folders between two images, specify with --images",
                        default=False, action='store_true')

    try:
        args = parser.parse_args()
    except:
        parser.print_help()
        sys.exit(0)

    # Output folder will be pwd if not specified
    if args.outfolder == None:
        output_folder = os.getcwd()
    else:
        output_folder = args.outfolder

    # We can only continue if singularity is installed
    if check_install() == True:

       # If we are given an image, ensure full path
       if args.image != None:
           image = os.path.abspath(args.image)


       ###############################################
       # What does the user want to do?
       ###############################################

       # The user wants to build and push an image
       if args.push == True:
           push_spec(build=True,
                     source_dir=args.infolder,
                     build_dir=args.outfolder,
                     size=args.size)

       # the user wants to make a tree
       elif args.tree == True:
           make_tree(image)

       # The user wants to package the image
       elif args.package == True:
           package(image_path=image,
                   output_folder=output_folder,
                   runscript=True,
                   software=True)

       # MULTIPLE IMAGE FUNCTIONS
       elif args.images != None: 
           images = [os.path.abspath(x) for x in args.images.split(',')]
        
           # Difference tree
           if args.difftree == True:
               make_difference_tree(images[0],images[1])

           # Similar tree
           elif args.simtree == True:
               make_sim_tree(images[0],images[1])

       else:
          print("Please specify a singularity image with --image(s)")


if __name__ == '__main__':
    main()
