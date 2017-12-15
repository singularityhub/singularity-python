'''

Copyright (C) 2017 The Board of Trustees of the Leland Stanford Junior
University.
Copyright (C) 2016-2017 Vanessa Sochat.

This program is free software: you can redistribute it and/or modify it
under the terms of the GNU Affero General Public License as published by
the Free Software Foundation, either version 3 of the License, or (at your
option) any later version.

This program is distributed in the hope that it will be useful, but WITHOUT
ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or
FITNESS FOR A PARTICULAR PURPOSE.  See the GNU Affero General Public
License for more details.

You should have received a copy of the GNU Affero General Public License
along with this program.  If not, see <https://www.gnu.org/licenses/>.

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
