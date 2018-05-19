#!/usr/bin/python

'''

Copyright (C) 2017 The Board of Trustees of the Leland Stanford Junior
University.
Copyright (C) 2016-2017 Vanessa Sochat.

This program is free software: you can redistribute it and/or modify it
under the terms of the GNU Affero General Public License as published by
the Free Software Foundation, either version 3 of the License, or (at your
option) any later version.

This program is distributed in the hope that it will be useful, but WITHOUT
ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or
FITNESS FOR A PARTICULAR PURPOSE.  See the GNU Affero General Public
License for more details.

You should have received a copy of the GNU Affero General Public License
along with this program.  If not, see <https://www.gnu.org/licenses/>.

'''

from numpy.testing import (
    assert_array_equal, 
    assert_almost_equal, 
    assert_equal
)

from singularity.utils import get_installdir
from spython.main import Client
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
        self.cli = Client
        self.container = self.cli.pull('docker://ubuntu:16.04', 
                                       pull_folder=self.tmpdir)

        self.comparator = self.cli.pull('docker://ubuntu:12.04',
                                         pull_folder=self.tmpdir)
        
    def tearDown(self):
        os.remove(self.container)
        os.remove(self.comparator)
        shutil.rmtree(self.tmpdir)


    def test_container_similarity(self):

        print("Testing singularity.analysis.compare.compare_singularity_images")
        from singularity.analysis.compare import compare_singularity_images
        sim = compare_singularity_images(self.container,self.comparator)
        self.assertTrue(isinstance(sim,pandas.DataFrame))
        self.assertTrue(sim.loc[self.container,self.comparator] - 0.4803262269280298 < 0.01)

        print("Testitng singularity.analysis.compare.compare_containers")
        from singularity.analysis.compare import compare_containers
        comparison = compare_containers(self.container, self.comparator)
        for key in ['total1', 'total2', 'intersect', 'unique2', 'unique1']:
            self.assertTrue(key in comparison)
     
        print("Testing singularity.analysis.compare.calculate_similarity")
        from singularity.analysis.compare import calculate_similarity
        sim = calculate_similarity(self.container,self.comparator)
        self.assertTrue(sim - 0.474603405617814 < 0.01)

    def test_information_coefficient(self):
        print("Testing singularity.analysis.metrics.information_coefficient")
        from singularity.analysis.metrics import information_coefficient
        self.assertEqual(information_coefficient(100,100,range(0,50)),0.5)
        self.assertEqual(information_coefficient(100,100,range(0,100)),1.0)
 
    
if __name__ == '__main__':
    unittest.main()
