#!/usr/bin/python

'''
Test singularity analysis functions

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

import unittest
import tempfile
import shutil
import json
import os

print("################################################### test_analysis_utils")

class TestAnalysis(unittest.TestCase):

    def setUp(self):
        self.tmpdir = tempfile.mkdtemp()
        
    def tearDown(self):
        shutil.rmtree(self.tmpdir)


    def test_get_packages(self):
        print("Testing singularity.analysis.utils.get_packages")
        from singularity.package import get_packages

        print("Case 1: Default returns Docker operating systems")
        packages = get_packages()
        self.assertEqual(len(packages),46)

        print("Case 2: Family specified to Docker library")
        packages = get_packages(family="docker-library")
        self.assertEqual(len(packages),117)


    def test_list_package_families(self):
        print("testing singularity.analysis.utils.list_package_families")
        from singularity.package import list_package_families
        families = [os.path.basename(x) for x in list_package_families()]
        for family in ['docker-os','docker-library']:
            self.assertTrue(family in families)    
    
if __name__ == '__main__':
    unittest.main()
