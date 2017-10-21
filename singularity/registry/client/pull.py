'''

pull.py: pull function for singularity registry

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
