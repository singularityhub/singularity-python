'''
reproduce.py: part of singularity package, functions to assess
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
from singularity.logman import bot
from singularity.utils import (
    get_installdir,
    read_json
)
import datetime
import hashlib
import tarfile
import sys
import gc
import os
import re
import io


def assess_differences(image_file1,image_file2,levels=None,version=None,size_heuristic=False,
                       guts1=None,guts2=None):
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
                                       level_filter=level_filter,
                                       tag_root=True,
                                       include_sizes=True)
        
        if guts2 is None:
            guts2 = get_content_hashes(image_path=image_file2,
                                       level_filter=level_filter,
                                       tag_root=True,
                                       include_sizes=True)
      
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

    gc.collect()
    reports['scores'] = scores
    return reports


def get_custom_level(regexp=None,description=None,skip_files=None,include_files=None):
    '''get_custom_level will generate a custom level for the user, 
    based on a regular expression. If used outside the context of tarsum, the user
    can generate their own named and described filters.
    :param regexp: must be defined, the file filter regular expression
    :param description: optional description
    '''
    if regexp == None:
        regexp = "."
    if description is None:
        description = "This is a custom filter generated by the user."
    
    custom = {"description":description,
              "regexp":regexp}

    # Include extra files?
    if include_files is not None:
        if not isinstance(include_files,set):
            include_files = set(include_files)
        custom['include_files'] = include_files

    # Skip files?
    if skip_files is not None:
        if not isinstance(skip_files,set):
            skip_files = set(skip_files)
        custom['skip_files'] = skip_files

    return custom


def get_level(level,version=None,include_files=None,skip_files=None):
    '''get_level returns a single level, with option to customize files
    added and skipped.
    '''

    levels = get_levels(version=version)
    level_names = list(levels.keys())

    if level.upper() in level_names:
        level = levels[level]
    else:
        bot.logger.warning("%s is not a valid level. Options are %s",level.upper(),
                                                                    "\n".join(levels))             
        return None

    # Add additional files to skip or remove, if defined
    if skip_files is not None:
        level = modify_level(level,'skip_files',skip_files)
    if include_files is not None:
        level = modify_level(level,'include_files',include_files)

    level = make_level_set(level)
    return level


def modify_level(level,field,values,append=True):
    '''modify level is intended to add / modify a content type.
    Default content type is list, meaning the entry is appended.
    If you set append to False, the content will be overwritten
    For any other content type, the entry is overwritten.
    '''
    field = field.lower()
    valid_fields = ['regexp','skip_files','include_files']
    if field not in valid_fields:
        bot.logger.warning("%s is not a valid field, skipping. Choices are %s",field,",".join(valid_fields))
        return level
    if append:
        if not isinstance(values,list):
            values = [values]
        if field in level:
            level[field] = level[field] + values
        else:
            level[field] = values
    else:
        level[field] = values

    level = make_level_set(level)

    return level       


def get_levels(version=None):
    '''get_levels returns a dictionary of levels (key) and values (dictionaries with
    descriptions and regular expressions for files) for the user. 
    :param version: the version of singularity to use (default is 2.2)
    :param include_files: files to add to the level, only relvant if
    '''
    valid_versions = ['2.3','2.2']

    if version is None:
        version = "2.3"  
    version = str(version)

    if version not in valid_versions:
        bot.logger.error("Unsupported version %s, valid versions are %s",version,",".join(valid_versions))

    levels_file = os.path.abspath(os.path.join(get_installdir(),
                                                           'hub',
                                                           'data',
                                                           'reproduce_levels.json'))
    levels = read_json(levels_file)
    if version == "2.2":
        # Labels not added until 2.3
        del levels['LABELS']

    levels = make_levels_set(levels)

    return levels


def make_levels_set(levels):
    '''make set efficient will convert all lists of items
    in levels to a set to speed up operations'''
    for level_key,level_filters in levels.items():
        levels[level_key] = make_level_set(level_filters)
    return levels
    

def make_level_set(level):
    '''make level set will convert one level into
    a set'''
    new_level = dict()
    for key,value in level.items():
        if isinstance(value,list):
            new_level[key] = set(value)
        else:
            new_level[key] = value
    return new_level 


def include_file(member,file_filter):
    '''include_file will look at a path and determine
    if it matches a regular expression from a level
    '''
    member_path = member.name.replace('.','',1)

    if len(member_path) == 0:
        return False

    # Does the filter skip it explicitly?
    if "skip_files" in file_filter:
        if member_path in file_filter['skip_files']:
            return False

    # Include explicitly?
    if "include_files" in file_filter:
        if member_path in file_filter['include_files']:
            return True

    # Regular expression?
    if "regexp" in file_filter:
        if re.search(file_filter["regexp"],member_path):
            return True
    return False


def is_root_owned(member):
    '''assess if a file is root owned, meaning "root" or user/group 
    id of 0'''
    if member.uid == 0 or member.gid == 0:
        return True
    elif member.uname == 'root' or member.gname == 'root':
        return True
    return False
    

def assess_content(member,file_filter):
    '''Determine if the filter wants the file to be read for content.
    In the case of yes, we would then want to add the content to the
    hash and not the file object.
    '''
    member_path = member.name.replace('.','',1)

    if len(member_path) == 0:
        return False

    # Does the filter skip it explicitly?
    if "skip_files" in file_filter:
        if member_path in file_filter['skip_files']:
            return False

    if "assess_content" in file_filter:
        if member_path in file_filter['assess_content']:
            return True
    return False


def get_image_hashes(image_path,version=None,levels=None):
    '''get_image_hashes returns the hash for an image across all levels. This is the quickest,
    easiest way to define a container's reproducibility on each level.
    '''
    if levels is None:
        levels = get_levels(version=version)
    hashes = dict()
    for level_name,level_filter in levels.items():
        hashes[level_name] = get_image_hash(image_path,
                                            level_filter=level_filter)
    return hashes


def get_image_hash(image_path,level=None,level_filter=None,
                   include_files=None,skip_files=None,version=None):
    '''get_image_hash will generate a sha1 hash of an image, depending on a level
    of reproducibility specified by the user. (see function get_levels for descriptions)
    the user can also provide a level_filter manually with level_filter (for custom levels)
    :param level: the level of reproducibility to use, which maps to a set regular
    expression to match particular files/folders in the image. Choices are in notes.
    :param skip_files: an optional list of files to skip
    :param include_files: an optional list of files to keep (only if level not defined)
    :param version: the version to use. If not defined, default is 2.3

    ::notes

    LEVEL DEFINITIONS
    The level definitions come down to including folders/files in the comparison. For files
    that Singularity produces on the fly that might be different (timestamps) but equal content
    (eg for a replication) we hash the content ("assess_content") instead of the file.
    '''    

    # First get a level dictionary, with description and regexp
    if level_filter is not None:
        file_filter = level_filter

    elif level is None:
        file_filter = get_level("RECIPE",
                                version=version,
                                include_files=include_files,
                                skip_files=skip_files)

    else:
        file_filter = get_level(level,version=version,
                                skip_files=skip_files,
                                include_files=include_files)
                
    cli = Singularity()
    file_obj,tar = get_memory_tar(image_path)
    hasher = hashlib.md5()

    for member in tar:
        member_name = member.name.replace('.','',1)

        # For files, we either assess content, or include the file
        if member.isdir() or member.issym():
            continue
        elif assess_content(member,file_filter):
            content = extract_content(image_path,member.name,cli)
            hasher.update(content)
        elif include_file(member,file_filter):
            buf = member.tobuf()
            hasher.update(buf)

    digest = hasher.hexdigest()
    file_obj.close()
    return digest


def extract_content(image_path,member_name,cli=None,return_hash=False):
    '''extract_content will extract content from an image using cat.
    If hash=True, a hash sum is returned instead
    '''
    if member_name.startswith('./'):
        member_name = member_name.replace('.','',1)
    if return_hash:
        hashy = hashlib.md5()
    if cli == None:
        cli = Singularity()
    content = cli.execute(image_path,'cat %s' %(member_name))
    if not isinstance(content,bytes):
        content = bytes(content)
    # If permissions don't allow read, return None
    if len(content) == 0:
        return None
    if return_hash:
        hashy.update(content)
        return hashy.hexdigest()
    return content


def get_content_hashes(image_path,level=None,regexp=None,include_files=None,tag_root=True,
                       level_filter=None,skip_files=None,version=None,include_sizes=True):
    '''get_content_hashes is like get_image_hash, but it returns a complete dictionary 
    of file names (keys) and their respective hashes (values). This function is intended
    for more research purposes and was used to generate the levels in the first place.
    If include_sizes is True, we include a second data structure with sizes
    '''    
    if level_filter is not None:
        file_filter = level_filter

    elif level is None:
        file_filter = get_level("REPLICATE",version=version,
                                skip_files=skip_files,
                                include_files=include_files)

    else:
        file_filter = get_level(level,version=version,
                                skip_files=skip_files,
                                include_files=include_files)

    file_obj,tar = get_memory_tar(image_path)
    results = extract_guts(image_path,tar,file_filter,tag_root,include_sizes)
    file_obj.close()
    return results


def extract_guts(image_path, tar,file_filter,tag_root=True,include_sizes=True):
    '''extract_guts will extract the file guts from an in memory tarfile.
    The file is not closed.
    '''

    cli = Singularity()
    results = dict()
    digest = dict()

    if tag_root:
        roots = dict()

    if include_sizes: 
        sizes = dict()

    for member in tar:
        member_name = member.name.replace('.','',1)
        included = False
        if member.isdir() or member.issym():
            continue
        elif assess_content(member,file_filter):
            digest[member_name] = extract_content(image_path,member.name,cli,return_hash=True)
            included = True
        elif include_file(member,file_filter):
            hasher = hashlib.md5()
            buf = member.tobuf()
            hasher.update(buf)
            digest[member_name] = hasher.hexdigest()
            included = True
        if included:
            if include_sizes:
                sizes[member_name] = member.size
            if tag_root:
                roots[member_name] = is_root_owned(member)

    results['hashes'] = digest
    if include_sizes:
        results['sizes'] = sizes
    if tag_root:
        results['root_owned'] = roots
    return results


def get_image_file_hash(image_path):
    '''get_image_hash will return an md5 hash of the file based on a criteria level.
    :param level: one of LOW, MEDIUM, HIGH
    :param image_path: full path to the singularity image
    '''
    hasher = hashlib.md5()
    with open(image_path, "rb") as f:
        for chunk in iter(lambda: f.read(4096), b""):
            hasher.update(chunk)
    return hasher.hexdigest()


def get_memory_tar(image_path):
    '''get an in memory tar of an image (does not require sudo!)'''
    cli = Singularity()
    if "pancakes" in os.environ:
        del os.environ['pancakes']
    byte_array = cli.export(image_path)
    file_object = io.BytesIO(byte_array)
    tar = tarfile.open(mode="r|*", fileobj=file_object)
    return (file_object,tar)
