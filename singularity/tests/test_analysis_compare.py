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
from singularity.cli import get_image
import unittest
import pandas
import tempfile
import shutil
import json
import os

class TestAnalysisCompare(unittest.TestCase):

    def setUp(self):
        self.tmpdir = tempfile.mkdtemp()
        self.container = get_image('docker://ubuntu:16.04')
        self.comparator = get_image('docker://ubuntu:12.04')
        
    def tearDown(self):
        shutil.rmtree(self.tmpdir)


    def test_container_similarity_vector(self):
        print("Testing singularity.analysis.compare.container_similarity_vector")
        import pandas
        from singularity.analysis.compare import container_similarity_vector
        from singularity.analysis.utils import get_packages
        packages_set = get_packages('docker-os')[0:2]
        vector = container_similarity_vector(container1=self.container,
                                             custom_set=packages_set)
        self.assertTrue('files.txt' in vector)
        self.assertTrue(isinstance(vector['files.txt'],pandas.DataFrame))


    def test_compare_singularity_images(self):
        import pandas
        print("Testing singularity.analysis.compare.compare_singularity_images")
        from singularity.analysis.compare import compare_singularity_images
        sim = compare_singularity_images(self.container,self.comparator)
        self.assertTrue(isinstance(sim,pandas.DataFrame))
        self.assertTrue(sim.loc[self.container,self.comparator] - 0.4803262269280298 < 0.01)


    def test_compare_containers(self):
        print("Testitng singularity.analysis.compare.compare_containers")
        from singularity.analysis.compare import compare_containers
        comparison = compare_containers(self.container,self.comparator)
        self.assertTrue('files.txt' in comparison)
        for key in ['total1', 'total2', 'intersect', 'unique2', 'unique1']:
            self.assertTrue(key in comparison['files.txt'])
     

    def test_calculate_similarity(self):
        print("Testitng singularity.analysis.compare.calculate_similarity")
        from singularity.analysis.compare import calculate_similarity
        sim = calculate_similarity(self.container,self.comparator)
        self.assertTrue(sim['files.txt'] -0.4921837537163134 < 0.01)


    def test_compare_packages(self):
        print("Testing singularity.analysis.compare.compare_packages")
        from singularity.analysis.compare import compare_packages
        pwd = get_installdir()
        pkg1 = "%s/tests/data/busybox-2016-02-16.img.zip" %(pwd)
        pkg2 = "%s/tests/data/cirros-2016-01-04.img.zip" %(pwd)
        comparison = compare_packages(pkg1,pkg2)
        self.assertTrue('files.txt' in comparison)
        self.assertTrue(isinstance(comparison['files.txt'],pandas.DataFrame))

    def test_information_coefficient(self):
        print("Testing singularity.analysis.compare.information_coefficient")
        from singularity.analysis.compare import information_coefficient
        self.assertEqual(information_coefficient(100,100,range(0,50)),0.5)
        self.assertEqual(information_coefficient(100,100,range(0,100)),1.0)
 
    
if __name__ == '__main__':
    unittest.main()
