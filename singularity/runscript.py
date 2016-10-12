#!/usr/bin/env python

'''
runscript.py: module for working with singularity runscripts
              currently not in use / needs to be updated
'''

from singularity.utils import get_installdir, read_file, write_file
from singularity.boutiques import get_boutiques_json
from pygments.lexers import guess_lexer
from pygments.util import ClassNotFound
import subprocess
import tempfile
import zipfile
import inspect
import shutil
import imp
import sys
import re
import os

def detect_language(runscript):
    '''detect_language will use pygments to detect the language of a run script
    :param runscript: the full path to the run script, or string of runscript itself
    '''
    if os.path.exists(runscript):
        content = read_file(runscript)
    else:
        content = runscript
    try:
        language = guess_lexer(''.join(content))
        if language.name == "Python":
            return "python"
        else:
            print("Language %s is not yet supported." %(language.name))
    except ClassNotFound:
        print("Cannot detect language.")
    return None    


def get_runscript_template(output_folder=None,script_name="singularity",language="py"):
    '''get_runscript_template returns a template runscript "singularity" for the user
    :param output_folder: output folder for template, if not specified, will use PWD
    :param script_name: the name to give the template script, default is "singularity" to work
    with singularity containers
    :param language: corresponds to language extension, to find script. Default is python (py)
    '''
    base = get_installdir()
    template_folder = "%s/templates" %(base)

    # If no output folder provided, will be returned to PWD
    if output_folder == None:
        output_folder = os.getcwd()

    # If the user gave an extension with dots, remove them first
    while re.search("^[.]",language):
        language = language[1:]
        
    template_file = "%s/runscript.%s" %(template_folder,language)
    if not os.path.exists(template_file):
        print("Template for extension %s is not currently provided.\n please submit an issue to https://github.com/singularityware/singularity-python/issues.")
    else:
        runscript = "%s/%s" %(output_folder,script_name)
        shutil.copyfile(template_file,runscript)
        print("Runscript template saved to %s!\n" %(runscript))
        return runscript
