#!/usr/bin/env python

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

import argparse
import sys
import os


def get_parser():
    parser = argparse.ArgumentParser(description="Singularity Hub command line tools")


    # Global Variables

    parser.add_argument('--debug', dest="debug", 
                        help="use verbose logging to debug.", 
                        default=False, action='store_true')

    parser.add_argument("--size", dest='size', 
                        help="If using Docker or shub image, you can change size (default is 1024)", 
                        type=int, default=1024)

    subparsers = parser.add_subparsers(help='shub actions',
                                       title='actions',
                                       description='actions for Singularity Hub tools',
                                       dest="command")


    # Package
    package = subparsers.add_parser("package", 
                                    help="package a container")

    package.add_argument("--outfolder", dest='outfolder', 
                        help="full path to folder for output, stays in tmp (or pwd) if not specified", 
                        type=str, default=None)

    package.add_argument("--image", dest='image', 
                          help="full path to singularity image", 
                          type=str, default=None)

    package.add_argument('--include-image', dest="include_image", 
                        help="include image file in the package", 
                        default=False, action='store_true')
    

    # Compare
    compare = subparsers.add_parser("compare",
                                    help = "views and functions to compare two containers. Default calculates score.")

    compare.add_argument("--outfolder", dest='outfolder', 
                         help="full path to folder for output, stays in tmp (or pwd) if not specified", 
                         type=str, default=None)

    compare.add_argument("--images", dest='images', 
                         help="images, separated by commas", 
                         type=str, default=None)

    compare.add_argument('--simtree', dest='simtree', 
                         help="view common guts between two images (use --images)", 
                         default=False, action='store_true')

    compare.add_argument('--subtract', dest='subtract', 
                         help="subtract one container image from the second to make a difference tree (use --images first,subtract)", 
                         default=False, action='store_true')



    # Analysis
    analysis = subparsers.add_parser("analysis", 
                                     help="estimate OS, container metrics, and generate container tags.")

    analysis.add_argument('--os', dest="os", 
                           help="estimate the operating system of your container.", 
                           default=False, action='store_true')

    analysis.add_argument('--oscalc', dest="oscalc", 
                          help="calculate similarity score for your container vs. docker library OS.", 
                          default=False, action='store_true')

    analysis.add_argument("--outfolder", dest='outfolder', 
                         help="full path to folder for output, stays in tmp (or pwd) if not specified", 
                         type=str, default=None)

    analysis.add_argument("--image", dest='image', 
                          help="full path to singularity image", 
                          type=str, default=None)

    analysis.add_argument('--osplot', dest="osplot", 
                           help="plot similarity scores for your container vs. docker library OS.", 
                           default=False, action='store_true')

    analysis.add_argument('--tags', dest="tags", 
                          help="retrieve list of software tags for an image, itself minus it's base", 
                          default=False, action='store_true')


    # Create
    create = subparsers.add_parser("create", help="create recipe templates")
    create.add_argument("--recipe", dest='recipe', 
                        help="create template recipe", 
                        action='store_true', default=False)

    create.add_argument("--app", dest='app', 
                        help="the name of an app to include in the recipe", 
                        type=str, default=None)

    create.add_argument("--from", dest='bootstrap_from', 
                        help="the bootstrap 'from', should coincide with 'bootstrap' type", 
                        type=str, default=None)

    create.add_argument("--bootstrap", dest='bootstrap', 
                        help="the bootstrap type, default is docker", 
                        type=str, default='docker')

    create.add_argument("--outfolder", dest='outfolder', 
                        help="full path to folder for output, stays in tmp (or pwd) if not specified", 
                        type=str, default=None)

    # Inpsect
    inspect = subparsers.add_parser("inspect", help="inspect a single container.")
    inspect.add_argument("--image", dest='image', 
                          help="full path to singularity image", 
                          type=str, default=None)

    # View the guts of a Singularity image
    inspect.add_argument('--tree', dest='tree', 
                          help="view the guts of an singularity image (use --image)", 
                          default=False, action='store_true')


    return parser


def get_subparsers(parser):
    '''get_subparser will get a dictionary of subparsers, to help with printing help
    '''

    actions = [action for action in parser._actions 
               if isinstance(action, argparse._SubParsersAction)]

    subparsers = dict()
    for action in actions:
        # get all subparsers and print help
        for choice, subparser in action.choices.items():
            subparsers[choice] = subparser

    return subparsers



def main():

    parser = get_parser()
    subparsers = get_subparsers(parser)

    try:
        args = parser.parse_args()
    except:
        sys.exit(0)

    # Not running in Singularity Hub environment
    os.environ['SINGULARITY_HUB'] = "False"

    # if environment logging variable not set, make silent
    if args.debug is False:
        os.environ['MESSAGELEVEL'] = "CRITICAL"
    
    # Always print the version
    from singularity.logger import bot
    import singularity
    bot.info("Singularity Python Version: %s" % singularity.__version__)

    if args.command == "create":
        from .create import main

    if args.command == "compare":
        from .compare import main

    elif args.command == "analysis":
        from .analysis import main

    elif args.command == "inspect":
        from .inspect import main

    elif args.command == "package":
        from .package import main


    # Pass on to the correct parser
    if args.command is not None:
        main(args=args,
             parser=parser,
             subparser=subparsers[args.command])
    else:
        parser.print_help()


if __name__ == '__main__':
    main()
