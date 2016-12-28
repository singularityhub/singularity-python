#!/usr/bin/env python

'''
script.py: part of singularity command line tool
Runtime executable, "shub"

'''

from glob import glob
import argparse
import sys
import os

def get_parser():
    parser = argparse.ArgumentParser(
    description="Singularity Hub command line tool")

    # Single image, must be string
    parser.add_argument("--image", dest='image', 
                        help="full path to singularity image (for use with --package and --tree)", 
                        type=str, default=None)

    # Two images, for similarity function
    parser.add_argument("--images", dest='images', 
                        help="images, separated by commas (for use with --simtree)", 
                        type=str, default=None)

    # Does the user want to have verbose logging?
    parser.add_argument('--debug', dest="debug", 
                        help="use verbose logging to debug.", 
                        default=False, action='store_true')

    # Output folder, if needed
    parser.add_argument("--outfolder", dest='outfolder', 
                        help="full path to folder for output, stays in tmp (or pwd) if not specified", 
                        type=str, default=None)

    # Does the user want to package an image?
    parser.add_argument('--package', dest="package", 
                        help="package a singularity container for singularity hub", 
                        default=False, action='store_true')

    # View the guts of a Singularity image
    parser.add_argument('--tree', dest='tree', 
                        help="view the guts of an singularity image (use --image)", 
                        default=False, action='store_true')

    # Compare two images (a similarity tree)
    parser.add_argument('--simtree', dest='simtree', 
                        help="view common guts between two images (use --images)", 
                        default=False, action='store_true')

    # Compare two images (a similarity tree)
    parser.add_argument('--subtract', dest='subtract', 
                        help="subtract one container image from the second to make a difference tree (use --images first,subtract)", 
                        default=False, action='store_true')

    # Compare two images (get numerical comparison)
    parser.add_argument('--simcalc', dest='simcalc', 
                        help="calculate similarity (number) between images based on file contents.", 
                        default=False, action='store_true')

    # Size, if needed
    parser.add_argument("--size", dest='size', 
                        help="If using Docker or shub image, you can change size (default is 1024)", 
                        type=int, default=1024)

    return parser


def main():

    parser = get_parser()

    try:
        args = parser.parse_args()
    except:
        sys.exit(0)

    # Not running in Singularity Hub environment
    os.environ['SINGULARITY_HUB'] = "False"

    # if environment logging variable not set, make silent
    if args.debug == False:
        os.environ['MESSAGELEVEL'] = "CRITICAL"

    # Initialize the message bot, with level above
    from singularity.logman import bot
    from singularity.utils import check_install
    from singularity.cli import get_image

    # Output folder will be pwd if not specified
    if args.outfolder == None:
        output_folder = os.getcwd()
    else:
        output_folder = args.outfolder

    # We can only continue if singularity is installed
    if check_install() == True:

       # If we are given an image, ensure full path
       if args.image != None:

           image,existed = get_image(args.image,
                                     return_existed=True,
                                     size=args.size)

           if image == None:
               bot.logger.error("Cannot find image. Exiting.")
               sys.exit(1)

           # the user wants to make a tree
           if args.tree == True:
               from singularity.app import make_tree
               make_tree(image)
               clean_up(image,existed)


           # The user wants to package the image
           elif args.package == True:
               from singularity.package import package
               package(image_path=image,
                       output_folder=output_folder,
                       runscript=True,
                       software=True)
           else:
               print("Not sure what to do?")
               parser.print_help()

       # If we are given two image, we probably want a similar tree
       elif args.images != None:

           image1,image2 = args.images.split(',')
           bot.logger.debug("Image1: %s",image1)
           bot.logger.debug("Image2: %s",image2)
           image1,existed1 = get_image(image1,
                                       return_existed=True,
                                       size=args.size)
           image2,existed2 = get_image(image2,
                                       return_existed=True,
                                       size=args.size)

           if image1 == None or image2 == None:
               bot.logger.error("Cannot find image. Exiting.")
               sys.exit(1)

           # the user wants to make a similarity tree
           if args.simtree == True:
               from singularity.app import make_sim_tree
               make_sim_tree(image1,image2)

           # the user wants to make a difference tree
           if args.subtract == True:
               from singularity.app import make_diff_tree
               make_diff_tree(image1,image2)


           if args.simcalc == True:
               from singularity.views import calculate_similarity
               score = calculate_similarity(image1,image2,by="files.txt")
               print(score["files.txt"])

           clean_up(image1,existed1)
           clean_up(image2,existed2)
    
       else:
          print("Please specify one or more containers with --image(s)")


def clean_up(image,existed):
    '''clean up will remove an image file if existed is False (meaning it was
    created as temporary for the script
    '''
    from singularity.logman import bot
    if existed == False:
        if os.path.exists(image):
            bot.logger.info("%s created was temporary, removing",image)
            os.remove(image)


if __name__ == '__main__':
    main()
