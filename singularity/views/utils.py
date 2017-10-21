#!/usr/bin/env python

'''
singularity: views/utils.py: part of singularity package
utility functions for views

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

import os
from singularity.logger import bot
from singularity.utils import (
    get_installdir,
    read_file
)

import sys


def get_template(template_name,fields=None):
    '''get_template will return a template in the template folder,
    with some substitutions (eg, {'{{ graph | safe }}':"fill this in!"}
    '''
    template = None
    if not template_name.endswith('.html'):
        template_name = "%s.html" %(template_name)
    here = "%s/cli/app/templates" %(get_installdir())
    template_path = "%s/%s" %(here,template_name)
    if os.path.exists(template_path):
        template = ''.join(read_file(template_path))
    if fields is not None:
        for tag,sub in fields.items():
            template = template.replace(tag,sub)
    return template
