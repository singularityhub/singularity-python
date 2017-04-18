'''
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

import logging
import os
import sys

class Logman:

    def __init__(self,stream=True,MESSAGELEVEL=None):
        self.level = get_logging_level(MESSAGELEVEL)
        if stream == True:
            logging.basicConfig(stream=sys.stdout,level=self.level)
        else:
            logging.basicConfig(level=self.level)
        self.logger = logging.getLogger('shub_builder')
        self.formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')


def get_logging_level(MESSAGELEVEL=None):
    '''get_logging_level will return a logging level based on first
    a variable going into the function, then an environment variable
    MESSAGELEVEL, and then the default is DEBUG.
    :param MESSAGELEVEL: the level to get.
    '''
    if MESSAGELEVEL == None:
        MESSAGELEVEL = os.environ.get("MESSAGELEVEL","DEBUG")

    if MESSAGELEVEL in ["DEBUG","INFO"]:
        print("Environment message level found to be %s" %MESSAGELEVEL)

    if MESSAGELEVEL == "FATAL":
        return logging.FATAL

    elif MESSAGELEVEL == "CRITICAL":
        return logging.CRITICAL

    elif MESSAGELEVEL == "ERROR":
        return logging.ERROR

    elif MESSAGELEVEL == "WARNING":
        return logging.WARNING

    elif MESSAGELEVEL == "INFO":
        return logging.INFO

    elif MESSAGELEVEL in "DEBUG":
        return logging.DEBUG

    return logging.DEBUG

bot = Logman()
