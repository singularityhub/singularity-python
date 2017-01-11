#!/usr/bin/env python

# This is an example of generating image packages from within python

import os
os.environ['MESSAGELEVEL'] = 'CRITICAL'

from singularity.analysis.classify import (
    get_tags,
    get_diff
)

image_package = "python:3.6.0.img.zip"

# The algorithm works as follows:
#      1) first compare package to set of base OS (provided with shub)
#      2) subtract the most similar os from image, leaving "custom" files
#      3) organize custom files into dict based on folder name
#      4) return search_folders as tags

# Default tags will be returned as software in "bin"
tags = get_tags(image_package=image_package)

# We can also get the raw "diff" between the image and it's base
# which is usable in other functions (and we don't have to calc 
# it again)
diff = get_diff(image_package=image_package)

# We can specify other folders of interest
folders = ['init','init.d','bin','systemd']
tags = get_tags(search_folders=folders,diff=diff)
# Most similar OS found to be %s debian:7.11
