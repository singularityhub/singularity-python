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

import singularity
import argparse
import sys
import os


def get_parser():
    parser = argparse.ArgumentParser(description="Singularity Registry tools")


    # Global Variables
    parser.add_argument("--version", dest='version', 
                        help="show software version", 
                        default=False, action='store_true')


    parser.add_argument('--debug', dest="debug", 
                        help="use verbose logging to debug.", 
                        default=False, action='store_true')

    parser.add_argument("--secrets", dest='secrets', 
                        help="full path to credential secrets (.sregistry) default in $HOME", 
                        type=str, default=None)


    subparsers = parser.add_subparsers(help='sreg actions',
                                       title='actions',
                                       description='actions for Singularity Registry tools',
                                       dest="command")


    # List or search containers
    ls = subparsers.add_parser("list",
                               help="list and search for containers")


    ls.add_argument("query", nargs='*', 
                     help="container search query, don't specify for all", 
                     type=str, default="*")

    ls.add_argument('--runscript','-r', dest="runscript", 
                    help="show the runscript for each container", 
                    default=False, action='store_true')

    ls.add_argument('--def','-df', dest="deffile", 
                    help="show the deffile for each container.", 
                    default=False, action='store_true')

    ls.add_argument('--env','-e', dest="environ", 
                    help="show the environment for each container.", 
                    default=False, action='store_true')

    ls.add_argument('--test','-t', dest="test", 
                    help="show the test for each container.", 
                    default=False, action='store_true')

    # Push an image
    push = subparsers.add_parser("push",
                                 help="push one or more images to a registry")


    push.add_argument("image", nargs=1,
                       help="full path to image file", 
                       type=str)

    push.add_argument("--tag", dest='tag', 
                       help="tag for image. If not provided, defaults to latest", 
                       type=str, default=None)

    push.add_argument("--name", dest='name', 
                       help='name of image, in format "library/image"', 
                       type=str, required=True)

    push.add_argument('--no-compress', dest="nocompress", 
                      help="show the test for each container.", 
                      default=False, action='store_true')


    # Pull an image
    pull = subparsers.add_parser("pull",
                                 help="pull an image from a registry")

    pull.add_argument("image", nargs=1,
                       help="full uri of image", 
                       type=str)

    pull.add_argument("--name", dest='name', 
                       help='custom name for image', 
                       type=str, default=None)

    pull.add_argument('--no-decompress', dest="nodecompress", 
                      help="extract a gzip compressed image", 
                      default=False, action='store_true')

    # List or search labels
    labels = subparsers.add_parser("labels",
                                    help="query for labels")

    labels.add_argument("--key", "-k", dest='key', 
                         help="A label key to search for", 
                         type=str, default=None)

    labels.add_argument("--value", "-v", dest='value', 
                         help="A value to search for", 
                         type=str, default=None)

    # Remove
    delete = subparsers.add_parser("delete",
                                    help="delete an image from the registry.")

    delete.add_argument('--force','-f', dest="force", 
                        help="don't prompt before deletion", 
                        default=False, action='store_true')

    delete.add_argument("image", nargs=1,
                        help="full path to image file", 
                        type=str)



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
        os.environ['MESSAGELEVEL'] = "INFO"

    if args.version is True:
        print(singularity.__version__)
        sys.exit(0)

    if args.command == "labels":
        from .labels import main

    if args.command == "list":
        from .ls import main

    if args.command == "push":
        from .push import main

    if args.command == "pull":
        from .pull import main

    if args.command == "delete":
        from .delete import main

    # Pass on to the correct parser
    try:
        main(args=args,
             parser=parser,
             subparser=subparsers[args.command])
    except UnboundLocalError:
        parser.print_help()



if __name__ == '__main__':
    main()
