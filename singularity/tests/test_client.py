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

class TestClient(unittest.TestCase):

    def setUp(self):
        self.pwd = get_installdir()
        self.cli = Singularity()
        self.tmpdir = tempfile.mkdtemp()
        self.image1 = "%s/tests/data/busybox-2016-02-16.img" %(self.pwd)
        self.image2 = "%s/tests/data/cirros-2016-01-04.img" %(self.pwd)
        
    def tearDown(self):
        shutil.rmtree(self.tmpdir)

    def test_create(self):
        print('Testing client.create command')
        container = "%s/container.img" %(self.tmpdir)
        created_container = create_container(container)
        self.assertEqual(created_container,container)
        self.assertTrue(os.path.exists(container))


    def test_import(self):
        from singularity.build.utils import test_container
        print("Testing client.import command")
        container = create_container()

        # Container should not be valid
        print("Case 1: Before import, container is not valid")
        result = test_container(container)
        self.assertEqual(result['return_code'],255)
      
        print("Case 2: After import, container is valid")
        self.cli.importcmd(container,'docker://ubuntu')
        result = test_container(container)
        self.assertEqual(result['return_code'],0)

    def test_run(self):
        print("Testing client.run command")
        container = create_container(do_import=True)
        result = self.cli.run(container)
        self.assertEqual(result,'')

    def test_exec(self):
        print('Testing client.execute command')
        container = create_container(do_import=True) 
        result = self.cli.execute(container,'ls /')
        if isinstance(result,bytes):
            result = result.decode('utf-8')
        self.assertEqual(result,"bin\nboot\ndev\nenvironment\netc\nhome\nlib\nlib64\nlost+found\nmedia\nmnt\nopt\nproc\nroot\nrun\nsbin\nsingularity\nsrv\nsys\ntmp\nusr\nvar\n")


    def test_pull(self):
        print("Testing client.pull command")

        print("Case 1: Testing naming pull by image name")
        image = self.cli.pull("shub://vsoch/singularity-images")
        print(image)
        self.assertTrue(os.path.exists(image))
        self.assertTrue("vsoch-singularity-images" in image)

        print("Case 2: Testing naming pull by image commit")
        image = self.cli.pull("shub://vsoch/singularity-images",name_by="commit")
        print(image)
        self.assertTrue(os.path.exists(image))
        self.assertTrue("7a75cd7a32192e5d50f267982e0c30aff794076b" in image)

        print("Case 3: Testing naming pull by image hash")
        image = self.cli.pull("shub://vsoch/singularity-images",name_by="hash")
        print(image)
        self.assertTrue(os.path.exists(image))
        self.assertTrue("a989bc72cb154d007aa47a5034978328" in image)


    def test_get_image(self):
        print("Testing singularity.cli.get_image")
        from singularity.cli import get_image
        from singularity.build.utils import test_container
        tmpimg = get_image('docker://ubuntu')
        self.assertTrue(os.path.exists(tmpimg))
        result = test_container(tmpimg)
        self.assertEqual(result['return_code'],0)


def create_container(container=None,do_import=False):
    '''supporting function to create empty container
    '''
    cli = Singularity()
    if container is None:
        container = "%s/container.img" %(self.tmpdir)
    if do_import is True:
        cli.importcmd(container,'docker://ubuntu')
    return cli.create(container)


if __name__ == '__main__':
    unittest.main()
