#!/usr/bin/env python

'''
runscript.py: module for working with singularity runscripts

'''

from singularity.utils import get_installdir, read_file
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
    :param runscript: the full path to the run script
    '''
    if os.path.exists(runscript):
        content = read_file(runscript)
        try:
            language = guess_lexer(''.join(content))
            if language.name == "Python":
                return "python"
            else:
                print("Language %s is not yet supported." %(language.name))
        except ClassNotFound:
            print("Cannot detect language.")
    else:
        print("Cannot find %s" %runscript)
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


def get_parameters(runscript):
    '''get_parameters is a general wrapper for language-specific methods to
    extract acceptable input arguments from a script
    :param runscript: the path to the runscript
    '''
    language = detect_language(runscript)
    if language == 'python':
        params = get_parameters_python(runscript)
    

def get_parameters_python(runscript):
    '''get_parameters_python returns parameters for a python script
    :param runscript: the path to the runscript
    '''
    tmpdir = tempfile.mkdtemp()
    # Move runscript to a temporary directory, as python for import
    pwd = os.getcwd()
    tmp_module = "%s/runscript.py" %tmpdir
    shutil.copy(runscript,tmp_module)
    os.chdir(tmpdir)
    try:
        from runscript import get_parser
        parser = get_parser()
        actions = parser.__dict__['_option_string_actions']
        for command_arg, options in actions.iteritems():
            print(command_arg)
            #options
            #not written yet!
    except:
        print("Cannot find get_parser function in runscript, make sure to use singularity template (shub --runscript py) for your runscript!")
