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

from singularity.cli import get_image
from singularity.utils import check_install           
from singularity.logger import bot
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
        image1,existed1 = get_image(image1,
                                    return_existed=True,
                                    size=args.size)
        image2,existed2 = get_image(image2,
                                    return_existed=True,
                                    size=args.size)

        if image1 is None or image2 is None:
            bot.error("Cannot find image. Exiting.")
            sys.exit(1)

        # the user wants to make a similarity tree
        if args.simtree is True:
            from singularity.cli.app import make_sim_tree
            make_sim_tree(image1,image2)

        # the user wants to make a difference tree
        elif args.subtract is True:
            from singularity.cli.app import make_diff_tree
            make_diff_tree(image1,image2)

        elif args.simcalc is True:
            from singularity.analysis.compare import calculate_similarity
            score = calculate_similarity(image1,image2,by="files.txt")
            print(score["files.txt"])

        clean_up(image1,existed1)
        clean_up(image2,existed2)

    else:
        print("Please specify images to compare with --images")
        subparser.print_help()
