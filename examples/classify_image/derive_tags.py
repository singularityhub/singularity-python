#!/usr/bin/env python

# This is an example of generating image packages from within python

import os
os.environ['MESSAGELEVEL'] = 'CRITICAL'

from singularity.analysis.classify import get_tags

package = "python:3.6.0.img.zip"

# The algorithm works as follows:
#      1) first compare package to set of base OS (provided with shub)
#      2) subtract the most similar os from image, leaving "custom" files
#      3) organize custom files into dict based on folder name
#      4) return search_folders as tags

# Default tags will be returned as software in "bin"
tags = get_tags(package=package)

# Most similar OS found to be %s debian:7.11

