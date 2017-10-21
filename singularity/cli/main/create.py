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

from singularity.utils import (
    check_install, 
    get_installdir,
    read_file,
    write_file
)
from singularity.logger import bot
import uuid
import sys
import os


def main(args,parser,subparser):

    if args.recipe is None:
        subparser.print_help()
        bot.newline()
        print("Please specify creating a recipe with --recipe")
        sys.exit(0)

    # Output folder will be pwd if not specified
    output_folder = os.getcwd()
    if args.outfolder is not None:
        output_folder = os.getcwd()

    bootstrap =''
    if args.bootstrap is not None:
        bootstrap = args.bootstrap
        bot.debug("bootstrap: %s" %bootstrap)
 
    bootstrap_from =''
    if args.bootstrap_from is not None:
        bootstrap_from = args.bootstrap_from
        bot.debug("from: %s" %bootstrap_from)

    template = "Singularity"
    output_file = template
    app = ''
    if args.app is not None:
        app = args.app.lower()
        template = "Singularity.app"
        output_file = "Singularity.%s" %app   

    input_file = "%s/cli/app/templates/recipes/%s" %(get_installdir(), template)
    output_file = "%s/%s" %(output_folder,output_file)

    if os.path.exists(output_file):
        ext = str(uuid.uuid4())[0:4]
        output_file = "%s.%s" %(output_file, ext)

    # Read the file, make substitutions
    contents = read_file(input_file, readlines=False)

    # Replace all occurrences of app
    contents = contents.replace('{{ app }}', app)
    contents = contents.replace('{{ bootstrap }}', bootstrap)
    contents = contents.replace('{{ from }}', bootstrap_from)

    write_file(output_file, contents)
    bot.info("Output file written to %s" %output_file)

