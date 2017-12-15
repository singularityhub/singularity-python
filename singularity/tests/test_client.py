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

from singularity.utils import get_installdir
from singularity.logger import bot
from numpy.testing import (
    assert_array_equal, 
    assert_almost_equal, 
    assert_equal
)

from singularity.cli import Singularity
import unittest
import tempfile
import shutil
import json
import os

print("########################################################### test_client")

class TestClient(unittest.TestCase):

    def setUp(self):
        self.pwd = get_installdir()
        self.cli = Singularity()
        self.tmpdir = tempfile.mkdtemp()
        
    def tearDown(self):
        shutil.rmtree(self.tmpdir)

    def test_commands(self):

        print('Testing client.create command')
        container = "%s/container.img" %(self.tmpdir)
        created_container = self.cli.create(container)
        self.assertEqual(created_container,container)
        self.assertTrue(os.path.exists(created_container))
        os.remove(container)

        print("Testing client.pull command")
        print("...Case 1: Testing naming pull by image name")
        image = self.cli.pull("shub://vsoch/singularity-images", pull_folder=self.tmpdir)
        self.assertTrue(os.path.exists(image))
        self.assertTrue('vsoch-singularity-images-master' in image)
        print(image)
        os.remove(image)

        print("...Case 3: Testing docker pull")
        container = self.cli.pull("docker://ubuntu:14.04", pull_folder=self.tmpdir)
        self.assertTrue("ubuntu:14.04" in container)
        print(container)
        self.assertTrue(os.path.exists(container))

        print('Testing client.execute command')
        result = self.cli.execute(container,'ls /')
        print(result)
        self.assertTrue('bin\nboot\ndev' in result)

        print("Testing client.inspect command")
        result = self.cli.inspect(container,quiet=True)
        labels = json.loads(result)
        self.assertTrue('data' in labels)     
        os.remove(container)



if __name__ == '__main__':
    unittest.main()
