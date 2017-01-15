__version__ = "1.0.4"
AUTHOR = 'Vanessa Sochat'
AUTHOR_EMAIL = 'vsochat@stanford.edu'
NAME = 'singularity'
PACKAGE_URL = "http://www.github.com/singularityware/singularity-python"
KEYWORDS = 'singularity containers hub reproducibility package science visualization'
DESCRIPTION = "Command line tool for working with singularity-hub and packaging singularity containers."
LICENSE = "LICENSE"

INSTALL_REQUIRES = (

    ('flask', {'min_version': '0.12'}),
    ('flask-restful', {'min_version': None}),
    ('pandas', {'min_version': '0.19.2'}),
    ('requests', {'min_version': '2.12.4'}),
    ('retrying', {'min_version': '1.3.3'}),
    ('selenium', {'min_version': '3.0.2'}),
    ('simplejson', {'min_version': '3.10.0'}),
    ('pygments', {'min_version': '2.1.3'}),
    ('scikit-learn', {'min_version': '0.18.1'}),
    ('google-api-python-client', {'min_version': None}),
    ('oauth2client', {'exact_version': '3.0'})
)
