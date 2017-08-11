'''

Copyright (c) 2017 Vanessa Sochat, All Rights Reserved

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
