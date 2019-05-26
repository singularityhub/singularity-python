'''

Copyright (C) 2017-2019 Vanessa Sochat.

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

from googleapiclient.discovery import build
from oauth2client.client import GoogleCredentials

import re
import requests


################################################################################
# GOOGLE GENERAL API ###########################################################
################################################################################

def get_google_service(service_type=None, version=None):
    '''
    get a google service using the discovery client.
    :param service_type: the service to get (default is storage)
    :param version: version to use (default is v1)
    '''
    if service_type == None:
        service_type = "storage"
    if version == None:
        version = "v1"

    credentials = GoogleCredentials.get_application_default()
    return build(service_type, version, credentials=credentials)
