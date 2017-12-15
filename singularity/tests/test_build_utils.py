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

print("###################################################### test_build_utils")

class TestBuildUtils(unittest.TestCase):

    def setUp(self):
        self.pwd = get_installdir()
        self.tmpdir = tempfile.mkdtemp()
        self.spec = "%s/tests/data/Singularity" %(self.pwd)
        
    def tearDown(self):
        shutil.rmtree(self.tmpdir)


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
