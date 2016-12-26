#!/usr/bin/env python

'''
api.py: module for working with singularity hub api

'''

from singularity.logman import bot
from singularity.package import build_from_spec

from singularity.utils import (
    get_installdir, 
    read_file, 
    write_file
)

import subprocess
import tempfile
import zipfile
import inspect
import shutil
import requests
import imp
import sys
import re
import os

api_base = "https://singularity-hub.org/api"

def authenticate(domain=None,token_folder=None):
    '''authenticate will authenticate the user with Singularity Hub. This means
    either obtaining the token from the environment, and then trying to obtain
    the token file and reading it, and then finally telling the user to get it.
    :param domain: the domain to direct the user to for the token, default is api_base
    :param token_folder: the location of the token file, default is $HOME (~/)
    '''
    # Attempt 1: Get token from environmental variable
    token = os.environ.get("SINGULARITY_TOKEN",None)

    if token == None:
        # Is the user specifying a custom home folder?
        if token_folder == None:
            token_folder = os.environ["HOME"]

        token_file = "%s/.shub" %(token_folder)
        if os.path.exists(token_file):
            token = read_file(token_file)[0].strip('\n')
        else:
            if domain == None:
                domain = api_base
            print('''Please obtain token from %s/token
                     and save to .shub in your $HOME folder''' %(domain))
            sys.exit(1)
    return token


def get_headers(token=None):
    '''get_headers will return a simple default header for a json
    post. This function will be adopted as needed.
    :param token: an optional token to add for auth
    '''
    headers = dict()
    if token!=None:
        headers["Authentication"] = "Token %s" %(token)
    headers["Content-Type"] = "application/json"
    bot.logger.debug("Headers found: %s",headers)
    return headers


def api_get(url,headers=None,token=None,data=None):
    '''api_get will use requests to get a particular url
    :param url: the url to send file to
    :param headers: a dictionary with headers for the request
    :param putdata: additional data to add to the request
    '''
    bot.logger.debug("GET %s",url)

    if headers == None:
        headers = get_headers(token=token)
    if data == None:
        response = requests.get(url,         
                                headers=headers)
    else:
        response = requests.get(url,         
                                headers=headers,
                                data=data)
    return response


def api_put(url,headers=None,token=None,data=None):
    '''api_put will send a read file (spec) to Singularity Hub with a particular set of headers
    :param url: the url to send file to
    :param headers: the headers to get
    :param headers: a dictionary with headers for the request
    :param data: additional data to add to the request
    '''
    bot.logger.debug("PUT %s",url)

    if headers == None:
        headers = get_headers(token=token)
    if data == None:
        response = requests.put(url,         
                                headers=headers)
    else:
        response = requests.put(url,         
                                headers=headers,
                                data=data)
    
    return response


def api_post(url,headers=None,data=None,token=None):
    '''api_get will use requests to get a particular url
    :param url: the url to send file to
    :param headers: a dictionary with headers for the request
    :param data: additional data to add to the request
    '''
    bot.logger.debug("POST %s",url)

    if headers == None:
        headers = get_headers(token=token)
    if data == None:
        response = requests.post(url,         
                                 headers=headers)
    else:
        response = requests.post(url,         
                                 headers=headers,
                                 data=data)
    return response
