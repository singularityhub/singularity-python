#!/usr/bin/python

'''
Test analysis classification functions

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

from singularity.cli import Singularity
import unittest
import tempfile
import shutil
import json
import os


from singularity.analysis.classify import (
    get_diff, 
    estimate_os,
    file_counts,
    extension_counts
)

print("################################################ test_analysis_classify")

class TestAnalysisClassify(unittest.TestCase):

    def setUp(self):
        self.tmpdir = tempfile.mkdtemp()
        self.cli = Singularity()
        self.container = self.cli.pull('docker://ubuntu:16.04', 
                                       pull_folder=self.tmpdir)
        print(self.container)

        self.comparator = self.cli.pull('docker://ubuntu:12.04',
                                         pull_folder=self.tmpdir)
        print(self.comparator)        

    def tearDown(self):
        shutil.rmtree(self.tmpdir)

    def test_classify(self):
        print("Testing singularity.analysis.classify.get_diff")
        diff = get_diff(self.container)
        self.assertTrue(len(diff)>0)
        print("Testing singularity.analysis.classify.estimate_os")
        estimated_os = estimate_os(self.container)
        self.assertTrue(estimated_os.startswith('ubuntu'))
        counts = file_counts(self.container)
        print("Testing singularity.analysis.classify.extension_counts")
        counts = extension_counts(self.container)
        self.assertTrue(len(counts)>0)


if __name__ == '__main__':
    unittest.main()
