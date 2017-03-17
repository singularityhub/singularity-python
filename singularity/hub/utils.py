#!/usr/bin/env python

'''
utils.py: general http functions (utils) for som api

'''

from singularity.logman import bot
from singularity.hub.auth import get_headers

import requests
import os
import sys


def api_get(url,headers=None,token=None,data=None, return_json=True, stream_to=None):
    '''api_get will use requests to get a particular url
    :param url: the url to send file to
    :param headers: a dictionary with headers for the request
    :param putdata: additional data to add to the request
    :param return_json: return json if successful
    :param stream_to: stream the response to file
    '''
    bot.logger.debug("GET %s",url)

    stream = False
    if stream_to is not None:
        stream = True

    if headers == None:
        headers = get_headers(token=token)

    if data == None:
        response = requests.get(url,         
                                headers=headers,
                                stream=stream)
    else:
        response = requests.get(url,         
                                headers=headers,
                                json=data,
                                stream=stream)

    if response.status_code == 200 and return_json and not stream:
        return response.json()

   
    chunk_size = 1 << 20
    with open(stream_to,'wb') as filey:
        for chunk in response.iter_content(chunk_size=chunk_size):
            filey.write(chunk)

    return stream_to 



def api_put(url,headers=None,token=None,data=None, return_json=True):
    '''api_put will send a read file (spec) to Singularity Hub with a particular set of headers
    :param url: the url to send file to
    :param headers: the headers to get
    :param headers: a dictionary with headers for the request
    :param data: additional data to add to the request
    :param return_json: return json if successful
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
                                json=data)
    
    if response.status_code == 200 and return_json:
        return response.json()

    return response


def api_post(url,headers=None,data=None,token=None,return_json=True):
    '''api_get will use requests to get a particular url
    :param url: the url to send file to
    :param headers: a dictionary with headers for the request
    :param data: additional data to add to the request
    :param return_json: return json if successful
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
                                 json=data)

    if response.status_code == 200 and return_json:
        return response.json()

    return response


######################################################################
# OS/IO and Formatting Functions
######################################################################


def is_number(container_name):
    '''is_number determines if the user is providing a singularity hub
    number (meaning the id of an image to download) vs a full name)
    '''
    if isinstance(container_name,dict):
        return False
    try:
        float(container_name)
        return True
    except ValueError:
        return False


def parse_container_name(image):
    '''parse_container_name will return a json structure with a repo name, tag, user.
    '''
    container_name = image
    if not is_number(image):
        image = image.replace(' ','')

    # If the user provided a number (unique id for an image), return it
    if is_number(image) == True:
        bot.logger.info("Numeric image ID %s found.", image)
        return int(image)

    image = image.split('/')

    # If there are two parts, we have username with repo (and maybe tag)
    if len(image) >= 2:
        user = image[0]
        image = image[1]

    # Otherwise, we trigger error (not supported just usernames yet)
    else:
        bot.logger.error('You must specify a repo name and username, %s is not valid',container_name)
        sys.exit(1)

    # Now split the name by : in case there is a tag
    image = image.split(':')
    if len(image) == 2:
        repo_name = image[0]
        repo_tag = image[1]

    # Otherwise, assume latest of an image
    else:
        repo_name = image[0]
        repo_tag = "latest"

    bot.logger.info("User: %s", user)
    bot.logger.info("Repo Name: %s", repo_name)
    bot.logger.info("Repo Tag: %s", repo_tag)

    parsed = {'repo_name':repo_name,
              'repo_tag':repo_tag,
              'user':user }

    return parsed
