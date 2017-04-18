#!/usr/bin/python

'''
Test build converter functions for generating Singularity spec from Dockerfile

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

from numpy.testing import (
    assert_array_equal, 
    assert_almost_equal, 
    assert_equal
)

from singularity.build.utils import get_build_template
from singularity.utils import (
    get_installdir, 
    read_file
)

import unittest
import tempfile
import shutil
import json
import os

class TestBuildConverter(unittest.TestCase):

    def setUp(self):
        self.pwd = get_installdir()
        self.tmpdir = tempfile.mkdtemp()
        self.spec = "%s/tests/data/Singularity" %(self.pwd)
        print("\n---START----------------------------------------")
        
    def tearDown(self):
        shutil.rmtree(self.tmpdir)
        print("\n---END------------------------------------------")


    def test_converter_version(self):
        '''Ensure that correct version of converter is loaded depending
        on user's installed or specified version
        '''
        from singularity.build import converter

        print("Case 1: Testing converter for version 2.2")
        os.environ['SINGULARITY_VERSION'] = "2.2" 
        self.assertEqual(converter.__name__,"singularity.build.converter")

        print("Case 2: Testing converter for version 2.3")
        os.environ['SINGULARITY_VERSION'] = "2.3" 
        self.assertEqual(converter.__name__,"singularity.build.converter")



if __name__ == '__main__':
    unittest.main()
