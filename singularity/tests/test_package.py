#!/usr/bin/python

'''
Test packaging

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

class TestPackage(unittest.TestCase):

    def setUp(self):
        self.pwd = get_installdir()
        self.cli = Singularity()
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

    '''
    def test_estimate_from_size(self):
        """test estimate from size will ensure that we correctly estimate the size
        of a container build plus some optional padding
        Note: we currently can't test this in CI due to needing 
        sudo password for bootstrap
        """
        from singularity.package import estimate_image_size
        spec = "From: ubuntu:16.04\nBootstrap: docker"        
        spec_file = "%s/Singularity" %(self.tmpdir)
        spec_file = write_file(spec_file,spec)     
        print("Case 1: Testing that no specification of padding uses default 200")   
        image_size = estimate_image_size(spec_file)        

    '''
    def test_package(self):
        '''test package will ensure that we can generate an image package'''
        from singularity.package import package
        container = self.cli.create("%s/container.img" %self.tmpdir)
        container = self.cli.importcmd(container,"docker://ubuntu")
        image_package = package(image_path=container,output_folder=self.tmpdir,S=self.cli)
        self.assertTrue(os.path.exists(image_package))


if __name__ == '__main__':
    unittest.main()
