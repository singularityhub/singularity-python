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

from glob import glob
import os
import re
import requests

import shutil
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
