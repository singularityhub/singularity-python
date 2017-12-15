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

