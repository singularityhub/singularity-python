#!/usr/bin/env python

'''
utils.py: general http functions (utils) for som api

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

from singularity.logman import bot
from singularity.hub.auth import get_headers

import requests
import os
import tempfile
import sys

try:
    from urllib.error import HTTPError
except ImportError:
    from urllib2 import HTTPError


def paginate_get(url,headers=None,token=None,data=None,return_json=True,stream_to=None,
                 start_page=None):
    '''paginate_get is a wrapper for api_get to get results until there isn't an additional page
    '''
    if start_page == None:
        url = '%s&page=1' %(url)
    else:
        url = '%s&page=%s' %(url,start_page)

    results = []
    while url is not None:
        result = api_get(url)
        if 'results' in result:
            results = results + result['results']
        url = result['next']
    return results
        


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


######################################################################
# Downloading
######################################################################


def download_atomically(url,file_name,headers=None):
    '''download atomically will stream to a temporary file, and
    rename only upon successful completion. This is to ensure that
    errored downloads are not found as complete in the cache
    :param file_name: the file name to stream to
    :param url: the url to stream from
    :param headers: additional headers to add to the get (default None)
    '''
    try:               # file_name.tmp.XXXXXX
        fd, tmp_file = tempfile.mkstemp(prefix=("%s.tmp." % file_name)) 
        os.close(fd)
        response = api_get(url,headers=headers,stream_to=tmp_file)
        if isinstance(response, HTTPError):
            bot.logger.error("Error downloading %s, exiting.", url)
            sys.exit(1)
        os.rename(tmp_file, file_name)
    except:
        download_folder = os.path.dirname(os.path.abspath(file_name))
        bot.logger.error("Error downloading %s. Do you have permission to write to %s?", url, download_folder)
        try:
            os.remove(tmp_file)
        except:
            pass
        sys.exit(1)
    return file_name
