#!/usr/bin/python

'''
Test base singularity client

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
