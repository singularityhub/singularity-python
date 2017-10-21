#!/usr/bin/python

'''
Test singularity analysis comparison functions

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

from singularity.utils import get_installdir
from singularity.cli import Singularity
import unittest
import pandas
import tempfile
import shutil
import json
import os

print("################################################# test_analysis_compare")

class TestAnalysisCompare(unittest.TestCase):

    def setUp(self):
        self.tmpdir = tempfile.mkdtemp()
        self.cli = Singularity()
        self.container = self.cli.pull('docker://ubuntu:16.04', 
                                       pull_folder=self.tmpdir)

        self.comparator = self.cli.pull('docker://ubuntu:12.04',
                                         pull_folder=self.tmpdir)
        
    def tearDown(self):
        os.remove(self.container)
        os.remove(self.comparator)
        shutil.rmtree(self.tmpdir)


    def test_container_similarity(self):
        print("Testing singularity.analysis.compare.container_similarity_vector")
        import pandas
        from singularity.analysis.compare import container_similarity_vector
        from singularity.package import get_packages
        packages_set = get_packages('docker-os')[0:2]
        vector = container_similarity_vector(container1=self.container,
                                             custom_set=packages_set)
        self.assertTrue('files.txt' in vector)
        self.assertTrue(isinstance(vector['files.txt'],pandas.DataFrame))

        print("Testing singularity.analysis.compare.compare_singularity_images")
        from singularity.analysis.compare import compare_singularity_images
        sim = compare_singularity_images(self.container,self.comparator)
        self.assertTrue(isinstance(sim,pandas.DataFrame))
        self.assertTrue(sim.loc[self.container,self.comparator] - 0.4803262269280298 < 0.01)

        print("Testitng singularity.analysis.compare.compare_containers")
        from singularity.analysis.compare import compare_containers
        comparison = compare_containers(self.container,self.comparator)
        self.assertTrue('files.txt' in comparison)
        for key in ['total1', 'total2', 'intersect', 'unique2', 'unique1']:
            self.assertTrue(key in comparison['files.txt'])
     
        print("Testing singularity.analysis.compare.calculate_similarity")
        from singularity.analysis.compare import calculate_similarity
        sim = calculate_similarity(self.container,self.comparator)
        self.assertTrue(sim['files.txt'] -0.4921837537163134 < 0.01)

    def test_information_coefficient(self):
        print("Testing singularity.analysis.metrics.information_coefficient")
        from singularity.analysis.metrics import information_coefficient
        self.assertEqual(information_coefficient(100,100,range(0,50)),0.5)
        self.assertEqual(information_coefficient(100,100,range(0,100)),1.0)
 
    
if __name__ == '__main__':
    unittest.main()
