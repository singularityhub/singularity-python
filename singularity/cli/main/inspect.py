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
