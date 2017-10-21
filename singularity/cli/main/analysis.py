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


    # If we are given an image, ensure full path
    image = args.image
    if image is not None:

        existed = True
        if not os.path.exists(image):
            cli = Singularity(debug=args.debug)
            image = cli.pull(image)
            existed = False

        if image is None:
            bot.error("Cannot find image. Exiting.")
            sys.exit(1)

        # The user wants to estimate the os
        if args.os is True:
            from singularity.analysis.classify import estimate_os
            estimated_os = estimate_os(container=image)
            print(estimated_os)

        # The user wants to get a list of all os
        elif args.oscalc is True:
           from singularity.analysis.classify import estimate_os
           estimated_os = estimate_os(container=image,return_top=False)
           print(estimated_os["SCORE"].to_dict())

        # The user wants to get a list of tags
        elif args.tags is True:
            from singularity.analysis.classify import get_tags
            tags = get_tags(container=image)
            print(tags)

        # The user wants to plot image vs. the docker os
        elif args.osplot is True:
            from singularity.app import plot_os_sims
            plot_os_sims(image)
        
        clean_up(image,existed)


    else:
        print("Please specify an image to analyze with --image")
        subparser.print_help()

