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

from singularity.logger import bot
import os

def estimate_image_size(spec_file,sudopw=None,padding=None):
    '''estimate_image_size will generate an image in a directory, and add
    some padding to it to estimate the size of the image file to generate
    :param sudopw: the sudopw for Singularity, root should provide ''
    :param spec_file: the spec file, called "Singuarity"
    :param padding: the padding (MB) to add to the image
    '''
    from .build import build_from_spec
    
    if padding == None:
        padding = 200

    if not isinstance(padding,int):
        padding = int(padding)

    image_folder = build_from_spec(spec_file=spec_file, # default will package the image
                                   sudopw=sudopw,       # with root should not need sudo
                                   build_folder=True,
                                   debug=False)

    original_size = calculate_folder_size(image_folder)
    
    bot.debug("Original image size calculated as %s" %original_size)
    padded_size = original_size + padding
    bot.debug("Size with padding will be %s" %padded_size)
    return padded_size



def calculate_folder_size(folder_path,truncate=True):
    '''calculate_folder size recursively walks a directory to calculate
    a total size (in MB)
    :param folder_path: the path to calculate size for
    :param truncate: if True, converts size to an int
    '''
    total_size = 0
    for dirpath, dirnames, filenames in os.walk(folder_path):
        for filey in filenames:
            file_path = os.path.join(dirpath, filey)
            if os.path.isfile(file_path) and not os.path.islink(file_path):
                total_size += os.path.getsize(file_path) # this is bytes
    size_mb = total_size / 1000000
    if truncate == True:
        size_mb = int(size_mb)
    return size_mb
