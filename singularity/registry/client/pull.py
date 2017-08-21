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
import sys
import os


def pull(self, images, file_name=None):

    for image in images:

        q = parse_image_name(image, ext='img.gz')

        # Verify image existence, and obtain id
        url = "%s/container/%s/%s:%s" %(self.base, q['collection'], q['image'], q['tag'])
        result = self.get(url)
        if file_name is None:
            file_name = q['storage'].replace('/','-')
    
        image_file = self.download(url=result['image'],
                                   file_name=file_name,
                                   show_progress=True)

        if os.path.exists(image_file):
            # If compressed, decompress   
            try:
                cli = Singularity()
                sys.stdout.write('Decompressing image ')
                bot.spinner.start()
                image_file = cli.decompress(image_file)
                bot.spinner.stop()
            except KeyboardInterrupt:
                bot.warning('Decompression cancelled.')
            except:
                bot.info('Image is not compressed.')
                image_file = os.rename(image_file,image_file.replace('.gz',''))
                pass

            bot.custom(prefix="Success!", message=image_file)
