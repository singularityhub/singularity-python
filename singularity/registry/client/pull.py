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
from singularity.registry.utils import parse_image_name

import requests
import shutil
import sys
import os


def pull(self, images, file_name=None, decompress=True):

    bot.debug('Execution of PULL for %s images' %len(images))

    for image in images:

        # If we need to decompress, it's old ext3 format
        if decompress is True:
            ext = 'img.gz'
        else:
            ext = 'simg'  # squashfs

        q = parse_image_name(image, ext=ext)

        # Verify image existence, and obtain id
        url = "%s/container/%s/%s:%s" %(self.base, q['collection'], q['image'], q['tag'])
        bot.debug('Retrieving manifest at %s' %url)

        manifest = self.get(url)
        bot.debug(manifest)

        if file_name is None:
            file_name = q['storage'].replace('/','-')
    
        image_file = self.download(url=manifest['image'],
                                   file_name=file_name,
                                   show_progress=True)

        bot.debug('Retrieved image file %s' %image_file)
        if os.path.exists(image_file) and decompress is True:
            # If compressed, decompress   
            try:
                cli = Singularity()
                sys.stdout.write('Decompressing image ')
                bot.spinner.start()
                image_file = cli.decompress(image_file, quiet=True)
            except KeyboardInterrupt:
                bot.warning('Decompression cancelled.')
            except:
                bot.info('Image is not compressed.')
                image_name = image_file.replace('.gz','')
                image_file = shutil.move(image_file,image_name)
                pass

            bot.spinner.stop()
            bot.custom(prefix="Success!", message=image_file)
