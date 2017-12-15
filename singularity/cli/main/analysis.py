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

