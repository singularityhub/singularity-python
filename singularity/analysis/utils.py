'''
analysis/utils.py: part of singularity package
utilities for working with analysis / data

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

from glob import glob
import os
import re
import requests

import shutil
import simplejson
from singularity.logger import bot
from singularity.utils import get_installdir
import sys

import subprocess
import tempfile
import zipfile

install_dir = get_installdir()


def remove_unicode_dict(input_dict):
    '''remove unicode keys and values from dict, encoding in utf8
    '''
    if isinstance(input_dict, collections.Mapping):
        return dict(map(remove_unicode_dict, input_dict.iteritems()))
    elif isinstance(input_dict, collections.Iterable):
        return type(input_dict)(map(remove_unicode_dict, input_dict))
    else:
        return input_dict


def update_dict(input_dict,key,value):
    '''update_dict will update lists in a dictionary. If the key is not included,
    if will add as new list. If it is, it will append.
    :param input_dict: the dict to update
    :param value: the value to update with
    '''
    if key in input_dict:
        input_dict[key].append(value)
    else:
        input_dict[key] = [value]
    return input_dict


def update_dict_sum(input_dict,key,increment=None,initial_value=None):
    '''update_dict sum will increment a dictionary key 
    by an increment, and add a value of 0 if it doesn't exist
    :param input_dict: the dict to update
    :param increment: the value to increment by. Default is 1
    :param initial_value: value to start with. Default is 0
    '''
    if increment == None:
        increment = 1

    if initial_value == None:
        initial_value = 0

    if key in input_dict:
        input_dict[key] += increment
    else:
        input_dict[key] = initial_value + increment
    return input_dict
