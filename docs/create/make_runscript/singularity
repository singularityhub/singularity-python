#!/usr/bin/env python

'''
runscript.py: template executable for an application

'''

# import your functions here
import argparse
import sys
import os

def get_parser():
    '''get_parser returns the arg parse object, for use by an external application (and this script)
    '''
    parser = argparse.ArgumentParser(
    description="This is a description of your tool's functionality.")
    parser.add_argument("--string", dest='string', help="This is a string argument with default None", type=str, default=None)
    parser.add_argument("--integer", dest='integer', help="This is a string argument with default None", type=int, default=9999)
    parser.add_argument('--boolean', dest='boolean', help="This is a boolean argument that defaults to False, and when set, returns True", default=False, action='store_true')
    return parser

def main():
    parser = get_parser()
    try:
        args = parser.parse_args()
    except:
        parser.print_help()
        sys.exit(0)

    # What is the integer argument set to?
    if args.integer == 9999:
        print("The argument --integer is set to its default, 9999.")
    else:
        print("The argument --integer is set to be %s" %(args.integer))


    # What is the string argument set to?
    if args.string == None:
        print("The argument --string is set to its default, None.")
    else:
        print("The argument --string is set to %s." %(args.string))


    # What is the boolean argument set to?
    if args.boolean == False:
        print("The argument --boolean is not specified, returns %s" %(args.boolean))
    else:
        print("The argument --boolean is specified, set to %s." %(args.boolean))


if __name__ == '__main__':
    main()
