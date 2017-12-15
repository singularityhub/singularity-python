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

from singularity.hub.client import Client
import unittest
import tempfile
import shutil
import json
import os

print("############################################################# test_shub")

class TestClient(unittest.TestCase):


    def setUp(self):
        self.cli = Client()
        self.tmpdir = tempfile.mkdtemp()
        self.collection = "vsoch/singularity-images"
        
    def tearDown(self):
        shutil.rmtree(self.tmpdir)


    def test_get_collection(self):
        print('Testing client.get_collection command')
        result = self.cli.get_collection(self.collection)
        for key in ['add_date', 'name', 'metadata', 'modify_date']:
            print(key)
            self.assertTrue(key in result)

    def test_get_container(self):
        print("Testing client.get_container")
        container = self.cli.get_container(self.collection)
        self.assertTrue(os.path.exists(container))

if __name__ == '__main__':
    unittest.main()
