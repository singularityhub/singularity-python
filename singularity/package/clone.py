'''
package/clone.py: experimenting with cloning a node using singularity

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

import tempfile
from singularity.logger import bot
from singularity.cli import Singularity
from singularity.utils import run_command
import platform
import os
import sys

def package_node(root=None,name=None):
    '''package node aims to package a (present working node) for a user into
    a container. This assumes that the node is a single partition.
  
    :param root: the root of the node to package, default is /
    :param name: the name for the image. If not specified, will use machine's

    psutil.disk_partitions()

    '''

    if name is None:
        name = platform.node()

    if root is None:
        root = "/"

    tmpdir = tempfile.mkdtemp()
    image = "%s/%s.tgz" %(tmpdir,name)

    print("Preparing to package root %s into %s" %(root,name))
    cmd = ["tar","--one-file-system","-czvSf", image, root,"--exclude",image]
    output = run_command(cmd)
    return image


def unpack_node(image_path,name=None,output_folder=None,size=None):
    '''unpackage node is intended to unpackage a node that was packaged with
    package_node. The image should be a .tgz file. The general steps are to:
    1. Package the node using the package_node function
    2. Transfer the package somewhere that Singularity is installed'''

    if not image_path.endswith(".tgz"):
        bot.error("The image_path should end with .tgz. Did you create with package_node?")
        sys.exit(1)

    if output_folder is None:
        output_folder = os.path.dirname(os.path.abspath(image_path))

    image_name = os.path.basename(image_path)
    if name is None:
        name = image_name.replace('.tgz','.img')

    if not name.endswith('.img'):
        name = "%s.img" %(name)

    bot.debug("Preparing to unpack %s to %s." %(image_name,name))
    unpacked_image = "%s/%s" %(output_folder,name)

    S = Singularity(sudo=True) 
    S.create(image_path=unpacked_image,
             size=size)

    cmd = ["gunzip","-dc",image_path,"|","sudo","singularity","import", unpacked_image]
    output = run_command(cmd)

    # TODO: singularity mount the container, cleanup files (/etc/fstab,...)
    # and add your custom singularity files.
    return unpacked_image
