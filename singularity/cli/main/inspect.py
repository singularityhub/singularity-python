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
from singularity.package import package
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

    # If we are given an image, ensure full path
    if args.image is not None:

        if not os.path.exists(args.image):
            cli = Singularity(debug=args.debug)
            image = cli.pull(args.image)

        if image is None:
            bot.error("Cannot find image. Exiting.")
            sys.exit(1)

        # the user wants to make a tree
        if args.tree is True:
            from singularity.cli.app import make_tree
            make_tree(image)
            clean_up(image,existed)

    else:
        print("Please specify an image to inspect with --image")
        subparser.print_help()
