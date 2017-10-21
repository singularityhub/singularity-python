#!/usr/bin/python

'''
Test core utils functions for singularity python

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

from singularity.utils import get_installdir
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

print("############################################################ test_utils")

class TestUtils(unittest.TestCase):

    def setUp(self):
        self.pwd = get_installdir()
        self.tmpdir = tempfile.mkdtemp()
        self.spec = "%s/tests/data/Singularity" %(self.pwd)
        
    def tearDown(self):
        shutil.rmtree(self.tmpdir)
        

    def test_write_read_files(self):
        '''test_write_read_files will test the functions write_file and read_file
        '''
        print("Testing utils.write_file...")
        from singularity.utils import write_file
        import json
        tmpfile = tempfile.mkstemp()[1]
        os.remove(tmpfile)
        write_file(tmpfile,"hello!")
        self.assertTrue(os.path.exists(tmpfile))        

        print("Testing utils.read_file...")
        from singularity.utils import read_file
        content = read_file(tmpfile)[0]
        self.assertEqual("hello!",content)

        from singularity.utils import write_json
        print("Testing utils.write_json...")
        print("...Case 1: Providing bad json")
        bad_json = {"Wakkawakkawakka'}":[{True},"2",3]}
        tmpfile = tempfile.mkstemp()[1]
        os.remove(tmpfile)        
        with self.assertRaises(TypeError) as cm:
            write_json(bad_json,tmpfile)

        print("...Case 2: Providing good json")        
        good_json = {"Wakkawakkawakka":[True,"2",3]}
        tmpfile = tempfile.mkstemp()[1]
        os.remove(tmpfile)
        write_json(good_json,tmpfile)
        with open(tmpfile,'r') as filey:
            content = json.loads(filey.read())
        self.assertTrue(isinstance(content,dict))
        self.assertTrue("Wakkawakkawakka" in content)


    def test_check_install(self):
        '''check install is used to check if a particular software is installed.
        If no command is provided, singularity is assumed to be the test case'''
        print("Testing utils.check_install")
        from singularity.utils import check_install
        is_installed = check_install()
        self.assertTrue(is_installed)
        is_not_installed = check_install('fakesoftwarename')
        self.assertTrue(not is_not_installed)


    def test_get_installdir(self):
        '''get install directory should return the base of where singularity
        is installed
        '''
        print("Testing utils.get_installdir")
        from singularity.utils import get_installdir
        whereami = get_installdir()
        self.assertTrue(whereami.endswith('singularity'))


    def test_remove_uri(self):
        print("Testing utils.remove_uri")
        from singularity.utils import remove_uri
        self.assertEqual(remove_uri('docker://ubuntu'),'ubuntu')
        self.assertEqual(remove_uri('shub://vanessa/singularity-images'),'vanessa/singularity-images')


    def test_download_repo(self):
        print("Testing utils.download_repo")
        from singularity.utils import download_repo
        download_repo('https://github.com/singularityware/singularity',destination="%s/singularity" %self.tmpdir)
        self.assertTrue(os.path.exists("%s/singularity" %self.tmpdir))


if __name__ == '__main__':
    unittest.main()
