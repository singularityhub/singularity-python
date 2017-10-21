'''
metrics.py: part of singularity package, functions to assess
  reproducibility of images

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
from .levels import get_levels
from .utils import extract_content
from .hash import get_content_hashes
import os
import re

def assess_differences(image_file1,
                       image_file2,
                       levels=None,
                       version=None,
                       size_heuristic=False,
                       guts1=None,
                       guts2=None):

    '''assess_differences will compare two images on each level of 
    reproducibility, returning for each level a dictionary with files
    that are the same, different, and an overall score.
    :param size_heuristic: if True, assess root owned files based on size
    :param guts1,guts2: the result (dict with sizes,roots,etc) from get_content_hashes
    '''
    if levels is None:
        levels = get_levels(version=version)

    reports = dict()
    scores = dict()

    for level_name, level_filter in levels.items():
        contenders = []
        different = []
        setdiff = []
        same = 0

        # Compare the dictionary of file:hash between two images, and get root owned lookup
        if guts1 is None:
            guts1 = get_content_hashes(image_path=image_file1,
                                       level_filter=level_filter)
                                       # tag_root=True
                                       # include_sizes=True
        
        if guts2 is None:
            guts2 = get_content_hashes(image_path=image_file2,
                                       level_filter=level_filter)
      
        print(level_name)
        files = list(set(list(guts1['hashes'].keys()) + list(guts2['hashes'].keys())))

        for file_name in files:

            # If it's not in one or the other
            if file_name not in guts1['hashes'] or file_name not in guts2['hashes']:
                setdiff.append(file_name)

            else:
                if guts1['hashes'][file_name] == guts2['hashes'][file_name]:
                    same+=1
                else:

                    # If the file is root owned, we compare based on size
                    if size_heuristic == True:
                        if guts1['root_owned'][file_name] or guts2['root_owned'][file_name]:
                            if guts1['sizes'][file_name] == guts2['sizes'][file_name]:    
                                same+=1
                            else:
                                different.append(file_name)
                        else:
                            # Otherwise, we can assess the bytes content by reading it
                            contenders.append(file_name)
                    else:
                        contenders.append(file_name)

        # If the user wants identical (meaning extraction order and timestamps)
        if level_name == "IDENTICAL":
                different = different + contenders

        # Otherwise we need to check based on byte content
        else:        
            if len(contenders) > 0:
                cli = Singularity()
                for rogue in contenders:
                    hashy1 = extract_content(image_file1,rogue,cli,return_hash=True)
                    hashy2 = extract_content(image_file2,rogue,cli,return_hash=True)
        
                    # If we can't compare, we use size as a heuristic
                    if hashy1 is None or hashy2 is None: # if one is symlink, could be None
                        different.append(file_name)                    
                    elif len(hashy1) == 0 or len(hashy2) == 0:
                        if guts1['sizes'][file_name] == guts2['sizes'][file_name]:    
                            same+=1
                        else:
                            different.append(file_name)                    
                    elif hashy1 != hashy2:
                        different.append(rogue)
                    else:
                        same+=1

        # We use a similar Jacaard coefficient, twice the shared information in the numerator 
        # (the intersection, same), as a proportion of the total summed files
        union = len(guts1['hashes']) + len(guts2['hashes'])

        report = {'difference': setdiff,
                  'intersect_different': different,
                  'same':same,
                  'union': union}
     
        if union == 0:
            scores[level_name] = 0
        else:
            scores[level_name] = 2*(same) / union
        reports[level_name] = report

    reports['scores'] = scores
    return reports

