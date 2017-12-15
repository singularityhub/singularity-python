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

from singularity.cli import Singularity
from singularity.logger import bot
from singularity.registry.utils import (
    parse_image_name,
    parse_header
)
from singularity.logger import ProgressBar
from requests_toolbelt import (
    MultipartEncoder,
    MultipartEncoderMonitor
)

import requests
import json
import sys
import os

from singularity.registry.auth import (
    generate_signature,
    generate_credential,
    generate_timestamp
)


def push(self, path, name, tag=None, compress=False):
    '''push an image to Singularity Registry'''

    path = os.path.abspath(path)
    image = os.path.basename(path)
    bot.debug("PUSH %s" % path)

    if not os.path.exists(path):
        bot.error('%s does not exist.' %path)
        sys.exit(1)

    cli = Singularity()
    metadata = cli.inspect(image_path=path, quiet=True)
    metadata = json.loads(metadata)

    # Try to add the size
    try:
        image_size = os.path.getsize(path) >> 20
        if metadata['data']['attributes']['labels'] is None:
            metadata['data']['attributes']['labels'] = {'SREGISTRY_SIZE_MB': image_size }
        else:
            metadata['data']['attributes']['labels']['SREGISTRY_SIZE_MB'] = image_size

    except:
        bot.warning("Cannot load metadata to add calculated size.")
        pass


    if "deffile" in metadata['data']['attributes']:
        if metadata['data']['attributes']['deffile'] is not None:
            fromimage = parse_header(metadata['data']['attributes']['deffile'],
                                     header="from",
                                     remove_header=True) 
            metadata['data']['attributes']['labels']['SREGISTRY_FROM'] = fromimage
            bot.debug("%s was built from a definition file." % image)

    if compress is True:
        ext = 'img.gz'  # ext3 format
    else:
        ext = 'simg'  # ext3 format

    metadata = json.dumps(metadata)
    names = parse_image_name(name,tag=tag, ext=ext)
    url = '%s/push/' % self.base

    if compress is True:
        try:
            sys.stdout.write('Compressing image ')
            bot.spinner.start()
            upload_from = cli.compress(path)
            bot.spinner.stop()
        except KeyboardInterrupt:
            print('Upload cancelled')
            if os.path.exists("%s.gz" %path):
                os.remove("%s.gz" %path)
            sys.exit(1)
    else:
        upload_from = path

    upload_to = os.path.basename(names['storage'])

    SREGISTRY_EVENT = self.authorize(request_type="push",
                                     names=names)

    encoder = MultipartEncoder(fields={'collection': names['collection'],
                                       'name':names['image'],
                                       'metadata':metadata,
                                       'tag': names['tag'],
                                       'datafile': (upload_to, open(upload_from, 'rb'), 'text/plain')})

    progress_callback = create_callback(encoder)
    monitor = MultipartEncoderMonitor(encoder, progress_callback)
    headers = {'Content-Type': monitor.content_type,
               'Authorization': SREGISTRY_EVENT }

    try:
        r = requests.post(url, data=monitor, headers=headers)
        message = self.read_response(r)

        print('\n[Return status {0} {1}]'.format(r.status_code, message))

    except KeyboardInterrupt:
        print('\nUpload cancelled.')

    # Clean up
    if compress is True:
        if os.path.exists("%s.gz" %path):
            os.remove("%s.gz" %path)


def create_callback(encoder):
    encoder_len = encoder.len / (1024*1024.0)
    bar = ProgressBar(expected_size=encoder_len,
                      filled_char='=')

    def callback(monitor):
        bar.show(monitor.bytes_read / (1024*1024.0))

    return callback
