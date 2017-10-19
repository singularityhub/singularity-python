'''

Copyright (c) 2016-2017 Vanessa Sochat, All Rights Reserved

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

from singularity.logger import bot
from glob import glob
import tempfile
import os


def get_image(image,return_existed=False,size=None,debug=False,pull_folder=None):
    '''get_image will return the file, if it exists, or if it's docker or
    shub, will use the Singularity command line tool to generate a temporary image
    :param image: the image file or path (eg, docker://)
    :param return_existed: if True, will return image_path,existed to tell if
    an image is temporary (if existed==False)
    :param sudopw: needed to create an image, if docker:// provided
    '''
    from singularity.cli import Singularity
    existed = True

    # Is the image a docker or singularity hub image?
    if image.startswith('docker://') or image.startswith('shub://'):
        existed = False
        cli = Singularity(debug=debug)
        if pull_folder is None:
            pull_folder = tempfile.mkdtemp()

        if image.startswith('docker://'):
            image_name = "%s.simg" %image.replace("docker://","").replace("/","-")
            bot.info("Found docker image %s, pulling..." %image_name)

        elif image.startswith('shub://'):
            image_name = "%s.simg" %image.replace("shub://","").replace("/","-")
            bot.info("Found shub image %s, pulling..." %image_name)


        image_path = "%s/%s" %(pull_folder,image_name)
        cli.pull(image_path=image,
                 pull_folder=pull_folder,
                 image_name=image_name,
                 size=size)

        image = image_path


    if os.path.exists(image):
        image = os.path.abspath(image)
        if return_existed == True:
            return image,existed
        return image
    return None



def clean_up(image,existed):
    '''clean up will remove an image file if existed is False (meaning it was
    created as temporary for the script
    '''
    if existed == False:
        if os.path.exists(image):
            bot.info("%s created was temporary, removing" %image)
            os.remove(image)
