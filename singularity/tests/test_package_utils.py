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

from singularity.utils import get_installdir

import unittest
import tempfile
import shutil
import json
import os

print("#################################################### test_package_utils")

class TestUtils(unittest.TestCase):

    def setUp(self):
        self.pwd = get_installdir()
        self.tmpdir = tempfile.mkdtemp()
        self.spec = "%s/tests/data/Singularity" %(self.pwd)
        
    def tearDown(self):
        shutil.rmtree(self.tmpdir)


    def test_calculate_folder_size(self):
        '''ensure that calculation of folder size is accurate
        '''
        from singularity.package import calculate_folder_size
        size_truncated = calculate_folder_size(self.tmpdir)
        self.assertTrue(isinstance(size_truncated,int))


if __name__ == '__main__':
    unittest.main()
