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

import os
from singularity.logger import bot
from singularity.utils import (
    get_installdir,
    read_file
)

import sys


def get_template(template_name,fields=None):
    '''get_template will return a template in the template folder,
    with some substitutions (eg, {'{{ graph | safe }}':"fill this in!"}
    '''
    template = None
    if not template_name.endswith('.html'):
        template_name = "%s.html" %(template_name)
    here = "%s/cli/app/templates" %(get_installdir())
    template_path = "%s/%s" %(here,template_name)
    if os.path.exists(template_path):
        template = ''.join(read_file(template_path))
    if fields is not None:
        for tag,sub in fields.items():
            template = template.replace(tag,sub)
    return template
