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

from singularity.utils import (
    get_installdir, 
    read_file,
    write_file
)

from spython.main import Client
import unittest
import tempfile
import shutil
import json
import os

print("######################################################## test_reproduce")

# Pull images for all tests
tmpdir = tempfile.mkdtemp()
image1 = Client.pull('docker://ubuntu:14.04', pull_folder=tmpdir)
image2 = Client.pull('docker://busybox:1', pull_folder=tmpdir)

class TestReproduce(unittest.TestCase):

    def setUp(self):
        self.pwd = get_installdir()
        self.tmpdir = tmpdir
        self.image1 = image1
        self.image2 = image2
        
    def tearDown(self):
        pass

    def test_get_image_hashes(self):
        from singularity.analysis.reproduce import get_image_hashes, get_image_hash

        print("Case 1: No specification of version returns latest")
        hashes = get_image_hashes(self.image1)
        for key in ['BASE','RUNSCRIPT','LABELS','ENVIRONMENT',
                    'REPLICATE','IDENTICAL','RECIPE']:
            self.assertTrue(key in hashes)

        print("Case 2: Specification of 2.2 does not return LABELS")
        hashes = get_image_hashes(self.image1, version=2.2)
        self.assertTrue('LABELS' not in hashes)

        print("Case 3: Testing to retrieve one particular hash")
        hashy = get_image_hash(self.image1,level="REPLICATE")
        self.assertTrue('LABELS' not in hashes)
        self.assertTrue(len(hashy)==32)


    def test_assess_differences(self):
        from singularity.analysis.reproduce import assess_differences

        print("Testing function to calculate hash differences between two images")
        diffs = assess_differences(image_file1=self.image1,image_file2=self.image2)
        self.assertTrue(isinstance(diffs, dict))
        self.assertTrue('scores' in diffs)

    def test_get_custom_level(self):
        from singularity.analysis.reproduce import get_custom_level
        print("Testing singularity.analysis.reproduce.get_custom_level")
        mylevel = get_custom_level(regexp="*",
                                   description="This is my new level",
                                   skip_files=["/usr/bin","/.singularity.d"],
                                   include_files=["/tmp"])
        for key in ['include_files','skip_files','regexp','description']:
            self.assertTrue(key in mylevel)
        self.assertTrue(isinstance(mylevel['skip_files'],set))
        self.assertTrue(isinstance(mylevel['include_files'],set))

    def test_get_level(self):
        from singularity.analysis.reproduce import get_level
        print("Testing singularity.analysis.reproduce.get_level")
        level = get_level('REPLICATE')
        for key in ['assess_content','skip_files','regexp','description']:
            self.assertTrue(key in level)

    def test_get_levels(self):
        from singularity.analysis.reproduce import get_levels
        print("Testing singularity.analysis.reproduce.get_levels")

        print("Case 1: Singularity version 2.3 and up")
        levels = get_levels()
        for key in ['BASE','RUNSCRIPT','LABELS','ENVIRONMENT',
                    'REPLICATE','IDENTICAL','RECIPE']:
            self.assertTrue(key in levels)


        print("Case 2: Singularity version 2.2")
        levels = get_levels(version=2.2)
        self.assertTrue('LABELS' not in levels)


    def test_get_content_hashes(self):
        from singularity.analysis.reproduce import get_content_hashes
        print("Testing singularity.analysis.reproduce.get_content_hashes")
        hashes = get_content_hashes(self.image1)
        for key in ['hashes','sizes','root_owned']:
            self.assertTrue(key in hashes)
        self.assertEqual(len(hashes['hashes']), 8819)


    def test_extract_guts(self):
        from singularity.analysis.reproduce.utils import extract_guts
        from singularity.analysis.reproduce import (
            get_image_tar,
            get_levels )

        print("Testing singularity.analysis.reproduce.extract_guts")
        levels = get_levels()
        file_obj,tar = get_image_tar(self.image1)
        guts = extract_guts(image_path=self.image1,
                            tar=tar,
                            file_filter=levels['REPLICATE'])
        for key in ['root_owned','sizes','hashes']:
            self.assertTrue(key in guts)
        tar.close()


if __name__ == '__main__':
    unittest.main()
    shutil.rmtree(tmpdir)
