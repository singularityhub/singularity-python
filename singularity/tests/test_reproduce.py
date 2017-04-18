#!/usr/bin/python

'''
Test reproducibility metric scripts

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

class TestReproduce(unittest.TestCase):

    def setUp(self):
        self.pwd = get_installdir()
        self.cli = Singularity()
        self.tmpdir = tempfile.mkdtemp()
        self.image1 = "%s/tests/data/busybox-2016-02-16.img" %(self.pwd)
        self.image2 = "%s/tests/data/cirros-2016-01-04.img" %(self.pwd)
        
    def tearDown(self):
        shutil.rmtree(self.tmpdir)

    def test_get_memory_tar(self):
        from singularity.reproduce import get_memory_tar
        import io
        import tarfile

        print("Case 1: Testing functionality of get memory tar...")
        file_obj,tar = get_memory_tar(self.image1)
        self.assertTrue(isinstance(file_obj,io.BytesIO))
        self.assertTrue(isinstance(tar,tarfile.TarFile))
        file_obj.close()                

    def test_get_image_hashes(self):
        from singularity.reproduce import get_image_hashes, get_image_hash

        print("Case 1: No specification of version returns latest")
        hashes = get_image_hashes(self.image1)
        for key in ['BASE','RUNSCRIPT','LABELS','ENVIRONMENT',
                    'REPLICATE','IDENTICAL','RECIPE']:
            self.assertTrue(key in hashes)

        print("Case 2: Specification of 2.2 does not return LABELS")
        hashes = get_image_hashes(self.image1,version=2.2)
        self.assertTrue('LABELS' not in hashes)

        print("Case 3: Testing to retrieve one particular hash")
        hashy = get_image_hash(self.image1,level="REPLICATE")
        self.assertTrue('LABELS' not in hashes)
        self.assertTrue(len(hashy)==32)


    def test_assess_differences(self):
        from singularity.reproduce import assess_differences

        print("Testing function to calculate hash differences between two images")
        diffs = assess_differences(image_file1=self.image1,image_file2=self.image2)
        self.assertTrue(isinstance(diffs,dict))
        self.assertTrue('scores' in diffs)

    def test_get_custom_level(self):
        from singularity.reproduce import get_custom_level
        print("Testing singularity.reproduce.get_custom_level")
        mylevel = get_custom_level(regexp="*",
                                   description="This is my new level",
                                   skip_files=["/usr/bin","/.singularity.d"],
                                   include_files=["/tmp"])
        for key in ['include_files','skip_files','regexp','description']:
            self.assertTrue(key in mylevel)
        self.assertTrue(isinstance(mylevel['skip_files'],set))
        self.assertTrue(isinstance(mylevel['include_files'],set))

    def test_get_level(self):
        from singularity.reproduce import get_level
        print("Testing singularity.reproduce.get_level")
        level = get_level('REPLICATE')
        for key in ['assess_content','skip_files','regexp','description']:
            self.assertTrue(key in level)

    def test_get_levels(self):
        from singularity.reproduce import get_levels
        print("Testing singularity.reproduce.get_levels")

        print("Case 1: Singularity version 2.3 and up")
        levels = get_levels()
        for key in ['BASE','RUNSCRIPT','LABELS','ENVIRONMENT',
                    'REPLICATE','IDENTICAL','RECIPE']:
            self.assertTrue(key in levels)


        print("Case 2: Singularity version 2.2")
        levels = get_levels(version=2.2)
        self.assertTrue('LABELS' not in levels)


    def test_get_content_hashes(self):
        from singularity.reproduce import get_content_hashes
        print("Testing singularity.reproduce.get_content_hashes")
        hashes = get_content_hashes(self.image1)
        for key in ['hashes','sizes','root_owned']:
            self.assertTrue(key in hashes)
        self.assertEqual(len(hashes['hashes']),372)


    def test_extract_guts(self):
        from singularity.reproduce import (
            extract_guts, 
            get_memory_tar,
            get_levels )

        print("Testing singularity.reproduce.extract_guts")
        levels = get_levels()
        file_obj,tar = get_memory_tar(self.image1)
        guts = extract_guts(image_path=self.image1,
                            tar=tar,
                            file_filter=levels['REPLICATE'])
        for key in ['root_owned','sizes','hashes']:
            self.assertTrue(key in guts)

    def test_get_image_file_hash(self):
        from singularity.reproduce import get_image_file_hash
        print("Testing singularity.reproduce.get_image_file_hash")
        hashy = get_image_file_hash(self.image1)
        self.assertEqual('9d2edcd19328d09f51c86192990050c5',hashy)


if __name__ == '__main__':
    unittest.main()
