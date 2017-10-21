'''
size.py: calculating sizes for packages

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
