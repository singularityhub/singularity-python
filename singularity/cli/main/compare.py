'''

Copyright (c) 2016-2017 Vanessa Sochat, All Rights Reserved

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

from singularity.utils import check_install           
from singularity.logger import bot
from singularity.cli import Singularity
from singularity.cli.utils import clean_up
import sys
import os


def main(args,parser,subparser):

    # We can only continue if singularity is installed
    if check_install() is not True:
        bot.error("Cannot find Singularity! Is it installed?")
        sys.exit(1)

    # Output folder will be pwd if not specified
    output_folder = os.getcwd()
    if args.outfolder is not None:
        output_folder = os.getcwd()


    if args.images is not None:

        image1,image2 = args.images.split(',')
        bot.debug("Image1: %s" %image1)
        bot.debug("Image2: %s" %image2)

        images = dict()
        cli = Singularity(debug=args.debug)
        for image in [image1,image2]:
            existed = True
            if not os.path.exists(image):
                image = cli.pull(image)
                existed = False            
            images[image] = existed

        # Just for clarity
        image1,image2 = list(images.keys())

        # the user wants to make a similarity tree
        if args.simtree is True:
            from singularity.cli.app import make_sim_tree
            make_sim_tree(image1,image2)

        # the user wants to make a difference tree
        elif args.subtract is True:
            from singularity.cli.app import make_diff_tree
            make_diff_tree(image1,image2)

        else: # If none specified, just print score
            from singularity.analysis.compare import calculate_similarity
            score = calculate_similarity(image1,image2,by="files.txt")
            print(score["files.txt"])

        for image,existed in images.items():
            clean_up(image,existed)
   
    else:
        print("Please specify images to compare with --images")
        subparser.print_help()
