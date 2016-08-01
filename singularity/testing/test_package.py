#!/usr/bin/python

"""
Test packaging

"""

from numpy.testing import assert_array_equal, assert_almost_equal, assert_equal
from singularity.package import *
from singularity.utils import get_installdir, read_file
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
        self.def_file = "%s/testing/data/defian.def" %(self.pwd)
        self.image1 = "%s/testing/data/busybox-2016-02-16.img" %(self.pwd)
        self.image2 = "%s/testing/data/cirros-2016-01-04.img" %(self.pwd)
        # We can't test creating the packages, because requires sudo :/
        self.pkg1 = "%s/testing/data/busybox-2016-02-16.img.zip" %(self.pwd)
        self.pkg2 = "%s/testing/data/cirros-2016-01-04.img.zip" %(self.pwd)

        
    def tearDown(self):
        shutil.rmtree(self.tmpdir)

    def test_packaging(self):

        # Function that uses extension to determine if package or image
        print("TESTING is_package...")
        self.assertTrue(is_package(self.pkg1))
        self.assertTrue(is_package(self.pkg2))
        self.assertTrue(is_package(self.image1,extension=".img"))
        self.assertTrue(is_package(self.image2,extension=".img"))

        # Check content of packages
        print("TESTING content extraction of packages")
        self.pkg1_includes = list_package(self.pkg1)
        self.pkg2_includes = list_package(self.pkg2)

        includes = ['files.txt', 'VERSION', 'NAME', 'folders.txt']
        for pkg_includes in [self.pkg1_includes,self.pkg2_includes]:
            [self.assertTrue(x in pkg_includes) for x in includes]
        self.assertTrue(os.path.basename(self.image1) in self.pkg1_includes)
        self.assertTrue(os.path.basename(self.image2) in self.pkg2_includes)

        # Calculate similarity, folders
        print("TESTING calculation of similarity between packages...")
        sim_folders = calculate_similarity(self.pkg1,self.pkg2,include_files=False,include_folders=True)
        assert_almost_equal(0.34782608695652173,sim_folders)

        # Calculate similarity, files
        sim_files = calculate_similarity(self.pkg1,self.pkg2,include_files=True,include_folders=False)
        assert_almost_equal(0.0786026,sim_files)

        # Calculate similarity, files and folders
        sim_both = calculate_similarity(self.pkg1,self.pkg2,include_files=True,include_folders=True)
        assert_almost_equal(0.1557632,sim_both)

        # Calculate similarity, this should fail
        sim_fail = calculate_similarity(self.pkg1,self.pkg2,include_files=False,include_folders=False)
        assert_equal(sim_fail,None)

        print("TESTING comparison of packages...")
        # Cannot compare without folder or files specified, should return None
        compare_fail = compare_package(self.pkg1,self.pkg2,include_files=False,include_folders=False)
        assert_equal(sim_fail,None)

        compare_files = compare_package(self.pkg1,self.pkg2,include_files=True,include_folders=False)
        assert_equal(len(compare_files['intersect']),9)
        includes = [os.path.basename(self.pkg1),
                    os.path.basename(self.pkg2),
                    "unique_%s" %os.path.basename(self.pkg1),
                    "unique_%s" %os.path.basename(self.pkg2),
                    "intersect"]
        for included,file_list in compare_files.iteritems():
            self.assertTrue(included in includes)
            self.assertTrue(file_list >= 3)

        print("TESTING loading packages...")
        pkg1_loaded = load_package(self.pkg1)
        self.assertTrue(len(pkg1_loaded["files.txt"])==12)
        self.assertTrue(len(pkg1_loaded["folders.txt"])==18)

        # Is the unique ID (md5 sum, the version) equal?
        #pkg1_hash = get_image_hash(self.image1)
        #self.assertTrue(pkg1_loaded['VERSION'] == pkg1_hash)
 
        # Did it extract successfully?
        image1_extraction = pkg1_loaded[os.path.basename(self.image1)]
        self.assertTrue(os.path.exists(image1_extraction))
        shutil.rmtree(os.path.dirname(image1_extraction))

if __name__ == '__main__':
    unittest.main()
