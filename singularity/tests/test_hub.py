#!/usr/bin/python

'''
Test singularity hub client

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

from singularity.hub.client import Client
import unittest
import tempfile
import shutil
import json
import os

print("############################################################# test_shub")

class TestClient(unittest.TestCase):


    def setUp(self):
        self.cli = Client()
        self.tmpdir = tempfile.mkdtemp()
        self.collection = "vsoch/singularity-images"
        
    def tearDown(self):
        shutil.rmtree(self.tmpdir)


    def test_get_collection(self):
        print('Testing client.get_collection command')
        result = self.cli.get_collection(self.collection)
        for key in ['add_date', 'name', 'enabled', 'modify_date']:
            self.assertTrue(key in result)

    def test_get_container(self):
        print("Testing client.get_container")
        container = self.cli.get_container(self.collection)
        self.assertTrue(os.path.exists(container))

if __name__ == '__main__':
    unittest.main()
