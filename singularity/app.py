from flask import Flask, render_template, request
from flask_restful import Resource, Api
from werkzeug import secure_filename
from singularity.views import tree
import webbrowser
import tempfile
import shutil
import random
import os

# SERVER CONFIGURATION ##############################################
class SingularityServer(Flask):

    def __init__(self, *args, **kwargs):
        super(SingularityServer, self).__init__(*args, **kwargs)

        # Set up temporary directory on start of application
        self.tmpdir = tempfile.mkdtemp()
        self.viz = None # Holds the visualization
        self.package = None

# SUPPORTING FUNCTIONS #############################################

# API VIEWS #########################################################
# eventually we can have views or functions served in this way...

app = SingularityServer(__name__)
#api = Api(app)    
#api.add_resource(apiExperiments,'/experiments')
#api.add_resource(apiExperimentSingle,'/experiments/<string:exp_id>')

# WEB INTERFACE VIEWS ##############################################

app.config['ALLOWED_EXTENSIONS'] = set(['png', 'jpg', 'jpeg','gif'])

# INTERACTIVE CONTAINER EXPLORATION ################################
@app.route('/container/tree')
def container_tree():
    # The server will store the package name and result object for query
    if app.viz == None:
        app.viz = tree(app.package)
    container_name = os.path.basename(app.package).split(".")[0]
    return render_template('container_tree.html',graph=app.viz['graph'],
                                                 files=app.viz['files'],
                                                 container_name=container_name)
    

# START FUNCTIONS ##################################################

# Function to start server (not yet tested).
def start(port=8088):
    if port==None:
        port=8088
    print "I'm in a nutshell! Who put me into this nutshell?"
    webbrowser.open("http://localhost:%s" %(port))
    app.run(host="0.0.0.0",debug=True,port=port)
    
# Function to start server (not yet tested).
def make_tree(package,port=None):
    app.package = package
    if port==None:
        port=8088
    print "I'm in a nutshell! Who put me into this nutshell?"
    webbrowser.open("http://localhost:%s/container/tree" %(port))
    app.run(host="0.0.0.0",debug=True,port=port)

if __name__ == '__main__':
    app.debug = True
    app.run(host='0.0.0.0')
