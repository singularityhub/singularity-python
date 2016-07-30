#!/usr/bin/python

"""
Test views

"""

from numpy.testing import assert_array_equal, assert_almost_equal, assert_equal
from singularity.utils import get_installdir, read_file, write_file
from singularity.views import tree, make_package_tree
from singularity.package import load_package
import unittest
import tempfile
import shutil
import json
import os

class TestViews(unittest.TestCase):

    def setUp(self):
        self.pwd = get_installdir()
        self.tmpdir = tempfile.mkdtemp()
        self.image1 = "%s/testing/data/busybox-2016-02-16.img" %(self.pwd)
        self.image2 = "%s/testing/data/cirros-2016-01-04.img" %(self.pwd)
        self.pkg1 = "%s/testing/data/busybox-2016-02-16.img.zip" %(self.pwd)
        self.pkg2 = "%s/testing/data/cirros-2016-01-04.img.zip" %(self.pwd)

        
    def tearDown(self):
        shutil.rmtree(self.tmpdir)

    def test_tree(self):

        # Can we generate a package tree?
        print("TESTING generation of tree!")

        # We will render an index.html to link to all tested views
        views = {}

        # This template has actual paths to static files instead of Flask
        html_template = " ".join(read_file("%s/templates/container_tree_circleci.html" %(self.pwd)))
        viz = tree(self.pkg1)
        # Make replacements in the template
        html_template = html_template.replace("{{ graph | safe }}",json.dumps(viz["graph"]))
        html_template = html_template.replace("{{ files | safe }}",json.dumps(viz["files"]))
        container_name = os.path.basename(self.pkg1).split(".")[0]
        html_template = html_template.replace("{{ container_name }}",container_name)
        write_file("tree.html",html_template)
        views["Similarity Tree"] = 'tree.html'

        # Finally, write the index page
        links = ''
        for viewname,view_file in views.iteritems():
            links = '%s\n<h3><a href="%s">%s</a></h3>' %(links,view_file,viewname)
        html_template = " ".join(read_file("%s/templates/index_circleci.html" %(self.pwd)))
        html_template = html_template.replace("{{ links }}",links)
        write_file("index.html",html_template)

        # Test the package tree
        pkg1_includes = load_package(self.pkg1)
        package_tree = make_package_tree(folders=pkg1_includes["folders.txt"],
                                         files=pkg1_includes["folders.txt"])
        self.assertTrue(package_tree['depth']==3)
        self.assertTrue(isinstance(package_tree['lookup'],dict))
 
        # Remove temporary package
        image1_extraction = pkg1_includes[os.path.basename(self.image1)]
        shutil.rmtree(os.path.dirname(image1_extraction))

if __name__ == '__main__':
    unittest.main()
