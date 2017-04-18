#!/usr/bin/python

'''
Test build functions and utils

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

class TestBuildUtils(unittest.TestCase):

    def setUp(self):
        self.pwd = get_installdir()
        self.tmpdir = tempfile.mkdtemp()
        self.spec = "%s/tests/data/Singularity" %(self.pwd)
        print("\n---START----------------------------------------")
        
    def tearDown(self):
        shutil.rmtree(self.tmpdir)
        print("\n---END------------------------------------------")


    def test_stop_if_result_none(self):
        '''the retry function should return None if result is None
        '''
        from singularity.build.utils import stop_if_result_none

        print("Case 1: Testing that None result returns False")
        do_retry = stop_if_result_none(None)
        self.assertTrue(not do_retry)

        print("Case 1: Testing that non-None result returns True")
        do_retry = stop_if_result_none("not None")
        self.assertTrue(do_retry)


    def test_test_container(self):
        '''the retry function should return None if result is None
        '''
        from singularity.build.utils import test_container
        from singularity.cli import Singularity
        cli = Singularity()
       
        unfinished_container = cli.create("%s/container.img" %self.tmpdir)
        print("Case 1: Testing that errored container does not run")
        result = test_container(unfinished_container)
        self.assertEqual(result["return_code"], 255)
        
        print("Case 2: Testing that finished container does run")
        finished_container = cli.importcmd(unfinished_container,'docker://ubuntu')
        result = test_container(finished_container)
        self.assertEqual(result["return_code"], 0)



    def test_get_singularity_version(self):
        '''ensure that singularity --version returns a valid version string
        '''
        from singularity.build.utils import get_singularity_version
        version = get_singularity_version()
        self.assertTrue(len(version)>0)

        version = get_singularity_version(2.2)
        self.assertEqual(version,2.2)

        os.environ['SINGULARITY_VERSION'] = "2.xx"
        version = get_singularity_version()
        self.assertEqual(version,"2.xx")

    def test_sniff_extension(self):
        '''sniff extension should return the correct file type based
        on the extension. The purpose is to correctly send data to
        object storage'''
    
        from singularity.build.utils import sniff_extension
        self.assertEqual(sniff_extension('container.img'),'application/octet-stream')
        self.assertEqual(sniff_extension('container.tar.gz'),'text/plain')
        self.assertEqual(sniff_extension('container.zip'),'application/zip')



    def test_get_script(self):
        '''get_script should return a script included in scripts or return None
        if it's not defined'''
        from singularity.build.utils import get_script
        script_path = get_script('singularity-build-latest.sh')
        self.assertTrue(os.path.exists(script_path))
        fake_script = get_script('noodles.txt')
        self.assertEqual(fake_script,None)


if __name__ == '__main__':
    unittest.main()
