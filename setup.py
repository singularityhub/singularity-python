from setuptools import setup, find_packages
import codecs
import os

setup(
    # Application name:
    name="singularity",

    # Version number:
    version="0.66",

    # Application author details:
    author="Vanessa Sochat",
    author_email="vsochat@stanford.edu",

    # Packages
    packages=find_packages(),
 
    # Data files
    include_package_data=True,
    zip_safe=False,

    # Details
    url="http://www.github.com/singularityware/singularity-python",

    license="LICENSE",
    description="Command line tool for working with singularity-hub and packaging singularity containers.",
    keywords='singularity containers hub reproducibility package science',

    install_requires = ['Flask','gitpython','flask-restful','selenium','simplejson','pygments',
                        'requests','oauth2client','google-api-python-client'],

    entry_points = {
        'console_scripts': [
            'shub=singularity.scripts:main',
        ],
    },

)
