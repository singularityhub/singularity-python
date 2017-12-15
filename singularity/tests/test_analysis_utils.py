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
