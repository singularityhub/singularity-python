#!/usr/bin/python

"""
Test build functions and utils

"""

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

class TestBuildTemplate(unittest.TestCase):

    def setUp(self):
        self.pwd = get_installdir()
        self.tmpdir = tempfile.mkdtemp()
        self.spec = "%s/tests/data/Singularity" %(self.pwd)
        print("\n---START----------------------------------------")
        
    def tearDown(self):
        shutil.rmtree(self.tmpdir)
        print("\n---END------------------------------------------")

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
