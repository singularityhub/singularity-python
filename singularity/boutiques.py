#!/usr/bin/env python

'''
boutiques.py: part of singularity package
See Boutiques specification at https://github.com/boutiques/schema

'''

from singularity.utils import write_json

def get_boutiques_json(name,version,inputs,command=None,description=None,output_file=None,
                       schema_version='0.2-snapshot',docker_image=None,docker_index=None):

    '''get_boutique returns a Boutiques data structure (json) to describe meta data for a singularity container. The function is not singularity specific and can be used for other cases.
    :param name: the name of the container / object to export
    :param version: the version of the container, should be some hash/uid for the container
    :param inputs: should be a dictionary with keys flags, required, default, type, choices, description, see note below.
    :param command: the command to use on command line for the object / container, if not provided, will use name
    :param description: a description of the container / object to export
    :param docker_image: Name of the Docker image for the object [OPTIONAL]
    :param docker_index: Docker index where the Docker image is stored (e.g. http://index.docker.io) [OPTIONAL]
    ::note
 
      inputs
      A list of {'flags':[...],
                 'name':'',
                 'required':True/False,
                 'default': ..,
                 'type':bool,
                 'choices':OPTIONAL,
                 'description':'This is...']}

      see singularity.runscript.get_parameters for parsing different executable files for input args

    '''
    if command == None:
        command = name

    # Meta data for spec
    json_spec = {'name': name}
    json_spec['command-line'] = "%s " %(command)
    json_spec['tool-version'] = version
    json_spec['schema-version'] = schema_version

    # Description
    if description == None:
        json_spec['description'] = "%s is a singularity container that can be integrated into a workflow." %(name)
    else:
        json_spec['description'] = "%s is a singularity container that can be integrated into a workflow: %s" %(name,description)

    # Inputs and outputs
    json_spec['inputs'] = []
    json_spec['outputs'] = []

    # Containers (not useful, we aren't using docker)
    if docker_image:
        tool_desc['docker-image'] = docker_image
    if docker_index:
        tool_desc['docker-index'] = docker_index

    # Add inputs
    for arg in inputs:
        new_input = get_boutiques_input(arg)
        json_spec['inputs'].append(new_input)
        json_spec['command-line'] += "%s " %(new_input['command-line-key'])

    # Currently, we don't know outputs - they are TBD using singularity-hub
    # not clear if we can determine from container, or generating on cluster

    # Writes JSON string to file
    if output_file != None:
        write_json(json_spec,output_file)
    
    return json_spec


def get_boutiques_input_type(arg_type):
    '''get_boutiques_input_type converts input args to allowable inputs. This will
    be problematic in that argparse will accept a string for a file or path, and the user
    will need to modify this in the workflow (for now).
    :param arg_type: the argument type, as a python object
    ''' 
    # Missing type is File
    if arg_type == bool:
        return "Flag"
    elif arg_type in [int,float]:
        return "Number"
    else:
        return "String"


def get_boutiques_input(arg):
    '''get_boutiques_input returns a boutiques input (json) object for adding to the ['inputs'] list in the boutiques.json
    :param arg: a dictionary with keys flags, name, required, default, type, choices, and description.
    '''

    input = {"id":arg['name']}

    # A human-readable input name. Example: 'Data file'."
    input['name'] = arg['name'].replace('_', ' ').lower()
    input['type'] = get_boutiques_input_type(arg['type'])

    # True if input is a list of value. An input of type \"Flag\" cannot be a list."
    input['list'] = False

    # "A string contained in command-line, substituted by the input value and/or flag at runtime.",
    input['command-line-key'] = "[%s]" %(input['name'].upper())  # input names are unique from argparse
    input['command-line-flag'] = arg['flags'][0] # just use the first for now
    input['description'] = arg['description'] if arg['description'] != None else arg['name']
    input['optional'] = arg['required']
    if arg['default'] != None:
        input['default-value'] = arg['default']

    return input
