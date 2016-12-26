#!/usr/bin/python

"""
Test packaging

"""

from numpy.testing import (
    assert_array_equal, 
    assert_almost_equal, 
    assert_equal
)

from singularity.package import *
from singularity.utils import (
    get_installdir, 
    read_file
)

from singularity.cli import Singularity
import unittest
import tempfile
import shutil
import json
import os

class TestPackage(unittest.TestCase):

    def setUp(self):
        self.pwd = get_installdir()
        self.tmpdir = tempfile.mkdtemp()
        self.image1 = "%s/tests/data/busybox-2016-02-16.img" %(self.pwd)
        self.image2 = "%s/tests/data/cirros-2016-01-04.img" %(self.pwd)
        # We can't test creating the packages, because requires sudo :/
        self.pkg1 = "%s/tests/data/busybox-2016-02-16.img.zip" %(self.pwd)
        self.pkg2 = "%s/tests/data/cirros-2016-01-04.img.zip" %(self.pwd)

        
    def tearDown(self):
        shutil.rmtree(self.tmpdir)

    def test_packaging(self):

        # Check content of packages
        print("TESTING content extraction of packages")
        self.pkg1_includes = list_package(self.pkg1)
        self.pkg2_includes = list_package(self.pkg2)

        includes = ['files.txt', 'VERSION', 'NAME', 'folders.txt']
        for pkg_includes in [self.pkg1_includes,self.pkg2_includes]:
            [self.assertTrue(x in pkg_includes) for x in includes]
        self.assertTrue(os.path.basename(self.image1) in self.pkg1_includes)
        self.assertTrue(os.path.basename(self.image2) in self.pkg2_includes)

        print("TESTING loading packages...")
        pkg1_loaded = load_package(self.pkg1)
        self.assertTrue(len(pkg1_loaded["files.txt"])==12)
        self.assertTrue(len(pkg1_loaded["folders.txt"])==18)
 
        # Did it extract successfully?
        image1_extraction = pkg1_loaded[os.path.basename(self.image1)]
        self.assertTrue(os.path.exists(image1_extraction))
        shutil.rmtree(os.path.dirname(image1_extraction))

if __name__ == '__main__':
    unittest.main()
