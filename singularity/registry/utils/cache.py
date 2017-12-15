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
from singularity.utils import mkdir_p
import tempfile
import os
import pwd
import sys


def clean_path(path):
    '''clean_path will canonicalize the path
    :param path: the path to clean
    '''
    return os.path.realpath(path.strip(" "))


def convert2boolean(arg):
    '''convert2boolean is used for environmental variables that must be
    returned as boolean'''
    if not isinstance(arg, bool):
        return arg.lower() in ("yes", "true", "t", "1", "y")
    return arg


def getenv(variable_key, required=False, default=None, silent=False):
    '''getenv will attempt to get an environment variable. If the variable
    is not found, None is returned.
    :param variable_key: the variable name
    :param required: exit with error if not found
    :param silent: Do not print debugging information for variable
    '''
    variable = os.environ.get(variable_key, default)
    if variable is None and required:
        bot.error(
            "Cannot find environment variable %s, exiting." %
            variable_key)
        sys.exit(1)

    if silent:
        bot.verbose2("%s found" % variable_key)
    else:
        if variable is not None:
            bot.verbose2("%s found as %s" % (variable_key, variable))
        else:
            bot.verbose2("%s not defined (None)" % variable_key)

    return variable


def get_cache(subfolder=None, quiet=False):
    '''get_cache will return the user's cache for singularity.
    :param subfolder: a subfolder in the cache base to retrieve, specifically
    '''

    DISABLE_CACHE = convert2boolean(getenv("SINGULARITY_DISABLE_CACHE",
                                           default=False))
    if DISABLE_CACHE:
        SINGULARITY_CACHE = tempfile.mkdtemp()
    else:
        userhome = pwd.getpwuid(os.getuid())[5]
        _cache = os.path.join(userhome, ".singularity")
        SINGULARITY_CACHE = getenv("SINGULARITY_CACHEDIR", default=_cache)

    # Clean up the path and create
    cache_base = clean_path(SINGULARITY_CACHE)

    # Does the user want to get a subfolder in cache base?
    if subfolder is not None:
        cache_base = "%s/%s" % (cache_base, subfolder)

    # Create the cache folder(s), if don't exist
    mkdir_p(cache_base)

    if not quiet:
        bot.debug("Cache folder set to %s" % cache_base)
    return cache_base
