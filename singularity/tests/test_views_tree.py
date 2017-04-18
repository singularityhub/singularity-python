#!/usr/bin/python

'''
Test singularity views trees function

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

from singularity.cli import get_image
from singularity.utils import get_installdir
import unittest
import tempfile
import shutil
import json
import os

class TestViewsTree(unittest.TestCase):

    def setUp(self):
        self.pwd = get_installdir()
        self.tmpdir = tempfile.mkdtemp()
        self.container = get_image('docker://ubuntu:16.04')
        self.comparator = get_image('docker://ubuntu:12.04')
        
    def tearDown(self):
        shutil.rmtree(self.tmpdir)


    def test_tree(self):
        import json
        from singularity.views.utils import get_template, get_container_contents
        from singularity.views.trees import container_tree
        print("Testing generation of container tree")
        viz = container_tree(self.container)
        for key in ['files', 'graph', 'depth', 'lookup']:
            self.assertTrue(key in viz)
        fields = {'{{ graph | safe }}': json.dumps(viz["graph"])}
        template = get_template("container_tree_circleci",fields)
  
    
if __name__ == '__main__':
    unittest.main()
