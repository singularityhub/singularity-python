#!/usr/bin/env python

'''
script.py: part of singularity command line tool
Runtime executable, "shub"

'''

from singularity.app import make_tree, make_difference_tree, make_sim_tree
from singularity.runscript import get_runscript_template
from singularity.utils import check_install, getsudo
from singularity.docker import docker2singularity
from singularity.package import package
from glob import glob
import argparse
import sys
import os

def main():
    parser = argparse.ArgumentParser(
    description="package Singularity containers for singularity hub.")
    parser.add_argument("--image", dest='image', help="full path to singularity image (for use with --package and --tree)", type=str, default=None)
    parser.add_argument("--images", dest='images', help="full path to singularity images/packages,separated with commas (for use with --difftree)", type=str, default=None)
    parser.add_argument("--docker", dest='docker', help="name of Docker image for use with --docker2singularity, --tree, etc.", type=str, default=None)
    parser.add_argument("--outfolder", dest='outfolder', help="full path to folder for output, if not specified, will go to pwd", type=str, default=None)
    parser.add_argument("--runscript", dest='runscript', help="specify extension to generate a runscript template in the PWD, or include --outfolder to change output directory. Currently supported types are py (python).", type=str, default=None)
    parser.add_argument('--package', help="package a singularity container for singularity hub", dest='package', default=False, action='store_true')
    parser.add_argument('--tree', help="view the guts of an singularity image or package, or Docker image.", dest='tree', default=False, action='store_true')
    parser.add_argument('--difftree', help="view files and folders unique to an image or package, specify --images base.img,subtraction.img", dest='difftree', default=False, action='store_true')
    parser.add_argument('--simtree', help="view common files and folders between two images or package, specify with --images", dest='simtree', default=False, action='store_true')
    parser.add_argument('--docker2singularity', help="convert a docker image to singularity", dest='dockerconversion', type=str, default=None)
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

    # If the user wants a runscript template.
    if args.runscript != None:
        get_runscript_template(output_folder=output_folder,
                               script_name="singularity",
                               language=args.runscript)


    # If the user wants to export docker2singularity!
    if args.dockerconversion != None:
        docker2singularity(output_folder=output_folder,
                           docker_image=args.dockerconversion)


    # We can only continue if singularity is installed
    if check_install() == True:

       # Do we have a docker or a singularity image?
       if args.image !=None:
           image = os.path.abspath(args.image)
       elif args.docker != None:
           image = args.docker

       # the user wants to make a tree
       if args.tree == True and args.docker == None:
           make_tree(image)
       elif args.tree == True and args.docker != None:
           print("\nYOU MUST ENTER PASSWORD TO CONTINUE AND USE DOCKER:")
           sudopw = getsudo() 
           make_tree(image,docker=True,sudopw=sudopw)

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
          print("Please specify a singularity image with --image(s), or a docker image with --docker")


if __name__ == '__main__':
    main()
