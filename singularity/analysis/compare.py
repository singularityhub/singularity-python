'''
compare.py: part of singularity package
functions to compare packages and images

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

import os
import re
from singularity.logger import bot
from singularity.utils import get_installdir
from singularity.analysis.reproduce import (
    get_image_tar,
    delete_image_tar
)

from .metrics import information_coefficient
import pandas



def compare_singularity_images(image_paths1,image_paths2=None):
    '''compare_singularity_images is a wrapper for compare_containers to compare
    singularity containers. If image_paths2 is not defined, pairwise comparison is done
    with image_paths1
    '''
    repeat = False
    if image_paths2 is None:
        image_paths2 = image_paths1
        repeat = True

    if not isinstance(image_paths1,list):
        image_paths1 = [image_paths1]

    if not isinstance(image_paths2,list):
        image_paths2 = [image_paths2]

    dfs = pandas.DataFrame(index=image_paths1,columns=image_paths2)

    comparisons_done = []
    for image1 in image_paths1:
        fileobj1,tar1 = get_image_tar(image1)

        members1 = [x.name for x in tar1]
        for image2 in image_paths2:
            comparison_id = [image1,image2]
            comparison_id.sort()
            comparison_id = "".join(comparison_id)
            if comparison_id not in comparisons_done:
                if image1 == image2:
                    sim = 1.0
                else:
                    fileobj2,tar2 = get_image_tar(image2)
                    members2 = [x.name for x in tar2]
                    c = compare_lists(members1,members2)
                    sim = information_coefficient(c['total1'],c['total2'],c['intersect'])
                    delete_image_tar(fileobj2, tar2)
                        
                dfs.loc[image1,image2] = sim
                if repeat:
                    dfs.loc[image2,image1] = sim
                comparisons_done.append(comparison_id)
        delete_image_tar(fileobj1, tar1)
    return dfs
