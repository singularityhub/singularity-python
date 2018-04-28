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

from spython.main import Client
import tempfile
from singularity.logger import bot
from singularity.utils import run_command
import platform
import os
import sys

def package_node(root=None, name=None):
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
 
    if not os.path.exists(unpacked_image):
        os.mkdir(unpacked_image)

    cmd = ["gunzip","-dc",image_path,"|","sudo","singularity","import", unpacked_image]
    output = run_command(cmd)

    # TODO: singularity mount the container, cleanup files (/etc/fstab,...)
    # and add your custom singularity files.
    return unpacked_image
