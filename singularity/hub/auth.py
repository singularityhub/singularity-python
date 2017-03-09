#!/usr/bin/env python

'''
auth.py: authentication functions for singularity hub api
         currently no token / auth for private collections
'''

from singularity.logman import bot
import os
import sys


def get_headers(token=None):
    '''get_headers will return a simple default header for a json
    post. This function will be adopted as needed.
    :param token: an optional token to add for auth
    '''
    headers = dict()
    headers["Content-Type"] = "application/json"
    if token!=None:
        headers["Authorization"] = "Bearer %s" %(token)

    header_names = ",".join(list(headers.keys()))
    bot.logger.debug("Headers found: %s",header_names)
    return headers
