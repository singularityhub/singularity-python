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

from singularity.package import *
from singularity.utils import (
    get_installdir, 
    read_file,
    write_file
)

from singularity.cli import Singularity
import unittest
import tempfile
import shutil
import json
import os

print("########################################################## test_package")

class TestPackage(unittest.TestCase):

    def setUp(self):
        self.pwd = get_installdir()
        self.cli = Singularity()
        self.tmpdir = tempfile.mkdtemp()
        self.image1 = "%s/tests/data/busybox-2017-10-21.simg" %(self.pwd)
        self.image2 = "%s/tests/data/cirros-2017-10-21.simg" %(self.pwd)
        self.pkg1 = "%s/tests/data/busybox-2017-10-21.zip" %(self.pwd)
        self.pkg2 = "%s/tests/data/cirros-2017-10-21.zip" %(self.pwd)

        
    def tearDown(self):
        shutil.rmtree(self.tmpdir)

    def test_packaging(self):

        # Check content of packages
        print("TESTING content extraction of packages")
        self.pkg1_includes = list_package(self.pkg1)
        self.pkg2_includes = list_package(self.pkg2)

        includes = ['files.txt', 'runscript', 'folders.txt'] # VERSION only with spec_file
        for pkg_includes in [self.pkg1_includes,self.pkg2_includes]:
            [self.assertTrue(x in pkg_includes) for x in includes]

        print("TESTING loading packages...")
        pkg1_loaded = load_package(self.pkg1)
        self.assertEqual(len(pkg1_loaded["files.txt"]),20)
        self.assertEqual(len(pkg1_loaded["folders.txt"]),20) 



if __name__ == '__main__':
    unittest.main()
