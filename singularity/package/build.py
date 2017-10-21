'''
build.py: part of singularity package

The MIT License (MIT)

Copyright (c) 2016-2017 Vanessa Sochat

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

from singularity.logger import bot

from singularity.package.utils import zip_up
from singularity.package.size import calculate_folder_size
from singularity.utils import (
    format_container_name,
    read_file, 
    run_command
)

from singularity.cli import Singularity

from singularity.analysis.reproduce import (
    delete_image_tar,
    get_image_tar,
    get_image_file_hash,
    get_image_hashes,
    extract_content
)
import tempfile
import tarfile
import hashlib
import zipfile
import shutil
import json
import io
import os
import re
import sys


def build_from_spec(spec_file=None,
                    build_dir=None,
                    build_folder=False,
                    sandbox=False,
                    isolated=False,
                    debug=False):

    '''build_from_spec will build a "spec" file in a "build_dir" and return the directory
    :param spec_file: the spec file, called "Singuarity"
    :param build_dir: the directory to build in. If not defined, will use tmpdir.
    :param isolated: "build" the image inside an isolated environment (>2.4)
    :param sandbox: ask for a sandbox build
    :param debug: ask for verbose output from builder
    '''

    if spec_file == None:
        spec_file = "Singularity"

    if build_dir == None:
        build_dir = tempfile.mkdtemp()

    bot.debug("Building in directory %s" %build_dir)

    # Copy the spec to a temporary directory
    bot.debug("Spec file set to %s" % spec_file)
    spec_path = os.path.abspath(spec_file)
    bot.debug("Spec file for build should be in %s" %spec_path)
    image_path = "%s/build.simg" %(build_dir)
    

    # Run create image and bootstrap with Singularity command line tool.
    cli = Singularity(debug=debug)
    print("\nBuilding image...")

    # Does the user want to "build" into a folder or image?
    result = cli.build(image_path=image_path,
                       spec_path=spec_path,
                       sandbox=sandbox,
                       isolated=isolated)

    print(result)

    # If image, rename based on hash
    if sandbox is False:
        version = get_image_file_hash(image_path)
        final_path = "%s/%s.simg" %(build_dir,version)
        os.rename(image_path,final_path)
        image_path = final_path

    bot.debug("Built image: %s" %image_path)
    return image_path


def package(image_path,
            spec_path=None,
            output_folder=None,
            remove_image=False,
            verbose=False,
            S=None):

    '''generate a zip (including the image) to a user specified output_folder.
    :param image_path: full path to singularity image file
    :param runscript: if True, will extract runscript to include in package as runscript
    :param software: if True, will extract files.txt and folders.txt to package
    :param remove_image: if True, will not include original image in package (default,False)
    :param verbose: be verbose when using singularity --export (default,False)
    :param S: the Singularity object (optional) will be created if not required.
    '''    

    # Run create image and bootstrap with Singularity command line tool.
    S = Singularity(debug=verbose)

    file_obj, tar = get_image_tar(image_path,S=S)

    members = tar.getmembers()
    image_name, ext = os.path.splitext(os.path.basename(image_path))
    zip_name = "%s.zip" %(image_name.replace(" ","_"))

    # Include the image in the package?
    to_package = dict()
    if not remove_image:
        to_package["files"] = [image_path]

    # If the specfile is provided, it should also be packaged
    if spec_path is not None:
        singularity_spec = "".join(read_file(spec_path))
        to_package['Singularity'] = singularity_spec
        to_package["VERSION"] = get_image_file_hash(image_path)
    
    try:
        inspection = S.inspect(image_path)       
        to_package["inspect.json"] = inspection
        inspection = json.loads(inspection)
        to_package['runscript'] = inspection['data']['attributes']['runscript']
    except:
        bot.warning("Trouble extracting container metadata with inspect.")


    bot.info("Adding software list to package.")
    files = [x.path for x in members if x.isfile()]
    folders = [x.path for x in members if x.isdir()]
    to_package["files.txt"] = files
    to_package["folders.txt"] = folders

    # Do zip up here - let's start with basic structures
    zipfile = zip_up(to_package,zip_name=zip_name,output_folder=output_folder)
    bot.debug("Package created at %s" %(zipfile))

    if not delete_image_tar(file_obj):
        bot.warning("Could not clean up temporary tarfile.")
    
    # return package to user
    return zipfile
