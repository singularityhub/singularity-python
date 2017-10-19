'''
singularity.hub.api: base template for making a connection to an API

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
from requests.exceptions import HTTPError

from singularity.logger import bot
import requests
import tempfile
import json
import sys
import re
import os


class ApiConnection(object):

    def __init__(self, token=None, base=None):
 
        self.headers = None
        if token is not None:
            self.token = token
        self.base = base
        self.update_headers()

# Headers

    def get_headers(self):
        return self.headers

    def _init_headers(self):
        return {'Content-Type':"application/json"}

    def reset_headers(self):
        self.headers = self.__init_headers()

    def update_headers(self,fields=None):
        '''update headers with a token & other fields
        '''
        if self.headers is None:
            headers = self._init_headers()
        else:
            headers = self.headers

        if fields is not None:
            for key,value in fields.items():
                headers[key] = value

        header_names = ",".join(list(headers.keys()))
        bot.debug("Headers found: %s" %header_names)
        self.headers = headers


# Requests


    def delete(self,url,return_json=True):
        '''delete request, use with caution
        '''
        bot.debug('DELETE %s' %url)
        return self.call(url,
                         func=requests.delete,
                         return_json=return_json)


    def put(self,url,data=None,return_json=True):
        '''put request
        '''
        bot.debug("PUT %s" %url)
        return self.call(url,
                         func=requests.put,
                         data=data,
                         return_json=return_json)



    def post(self,url,data=None,return_json=True):
        '''post will use requests to get a particular url
        '''
        bot.debug("POST %s" %url)
        return self.call(url,
                         func=requests.post,
                         data=data,
                         return_json=return_json)




    def get(self,url,headers=None,token=None,data=None,return_json=True):
        '''get will use requests to get a particular url
        '''
        bot.debug("GET %s" %url)
        return self.call(url,
                        func=requests.get,
                        data=data,
                        return_json=return_json)



    def paginate_get(self, url, headers=None, return_json=True, start_page=None):
        '''paginate_call is a wrapper for get to paginate results
        '''
        get = '%s&page=1' %(url)
        if start_page is not None:
            get = '%s&page=%s' %(url,start_page)

        results = []
        while get is not None:
            result = self.get(url, headers=headers, return_json=return_json)
            # If we have pagination:
            if isinstance(result, dict):
                if 'results' in result:
                    results = results + result['results']
                get = result['next']
            # No pagination is a list
            else:
                return result
        return results
        

    def download(self,url,file_name,headers=None,show_progress=True):
        '''stream to a temporary file, rename on successful completion
        :param file_name: the file name to stream to
        :param url: the url to stream from
        :param headers: additional headers to add
        '''

        fd, tmp_file = tempfile.mkstemp(prefix=("%s.tmp." % file_name)) 
        os.close(fd)
        response = self.stream(url,headers=headers,stream_to=tmp_file)

        if isinstance(response, HTTPError):
            bot.error("Error downloading %s, exiting." %url)
            sys.exit(1)
        os.rename(tmp_file, file_name)
        return file_name



    def stream(self,url,headers=None,stream_to=None):
        '''stream is a get that will stream to file_name
        '''

        bot.debug("GET %s" %url)

        if headers == None:
            headers = self._init_headers()

        response = requests.get(url,         
                                headers=headers,
                                stream=True)

        if response.status_code == 200:

            # Keep user updated with Progress Bar?
            content_size = None
            if 'Content-Length' in response.headers:
                progress = 0
                content_size = int(response.headers['Content-Length'])
                bot.show_progress(progress,content_size,length=35)


            chunk_size = 1 << 20
            with open(stream_to,'wb') as filey:
                for chunk in response.iter_content(chunk_size=chunk_size):
                    filey.write(chunk)
                    if content_size is not None:
                        progress+=chunk_size
                        bot.show_progress(iteration=progress,
                                          total=content_size,
                                          length=35,
                                          carriage_return=False)

            # Newline to finish download
            sys.stdout.write('\n')

            return stream_to 

        bot.error("Problem with stream, response %s" %(response.status_code))
        sys.exit(1)



    def call(self,url,func,data=None,return_json=True, stream=False):
        '''call will issue the call, and issue a refresh token
        given a 401 response.
        :param func: the function (eg, post, get) to call
        :param url: the url to send file to
        :param data: additional data to add to the request
        :param return_json: return json if successful
        '''
 
        if data is not None:
            if not isinstance(data,dict):
                data = json.dumps(data)

        response = func(url=url,
                        headers=self.headers,
                        data=data,
                        stream=stream)

        # Errored response, try again with refresh
        if response.status_code in [500,502]:
            bot.error("Beep boop! %s: %s" %(response.reason,
                                            response.status_code))
            sys.exit(1)

        # Errored response, try again with refresh
        if response.status_code == 404:
            bot.error("Beep boop! %s: %s" %(response.reason,
                                            response.status_code))
            sys.exit(1)


        # Errored response, try again with refresh
        if response.status_code == 401:
            bot.error("Your credentials are expired! %s: %s" %(response.reason,
                                                               response.status_code))
            sys.exit(1)

        elif response.status_code == 200:

            if return_json:

                try:
                    response =  response.json()

                except ValueError:
                    bot.error("The server returned a malformed response.")
                    sys.exit(1)

        return response
