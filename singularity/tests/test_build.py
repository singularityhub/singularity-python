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

print("############################################################ test_build")

class TestBuildTemplate(unittest.TestCase):

    def setUp(self):
        self.pwd = get_installdir()
        self.tmpdir = tempfile.mkdtemp()
        self.spec = "%s/tests/data/Singularity" %(self.pwd)
        
    def tearDown(self):
        shutil.rmtree(self.tmpdir)

    def test_read_template(self):
        '''test_read_template should read in a template script, and
        return the script as a string, or read to file'''

        # Check content of packages
        print("Case 1: Test reading of build template")
        template = get_build_template('singularity-build-latest.sh')        
        self.assertTrue(isinstance(template,str))
        self.assertTrue(len(template)>15)

        print("Case 2: Non existing script returns None")
        template = get_build_template('singularity-build-pizza.sh')        
        self.assertEqual(template,None)
 


if __name__ == '__main__':
    unittest.main()
