#!/usr/bin/env python

# This is an example of generating image packages from within python

import os
os.environ['MESSAGELEVEL'] = 'CRITICAL'

from singularity.analysis.classify import get_tags
from singularity.package import get_container_contents

# The algorithm works as follows:
#      1) organize custom files into dict based on folder name
#      2) return search_folders as tags

# Default tags will be returned as software in "bin"
tags = get_tags(container)

# We can also get the raw list of flies
file_list = get_container_contents(container)['all']

# We can specify other folders of interest
folders = ['init','init.d','bin','systemd']
tags = get_tags(container, search_folders=folders)
