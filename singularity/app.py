from singularity.views import tree, diff_tree, sim_tree
from flask import Flask, render_template, request
from flask_restful import Resource, Api
from werkzeug import secure_filename
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
        self.packages = None
        self.docker = False # boolean to designate docker or singularity
        self.sudopw = None # needed for docker view


# API VIEWS #########################################################
# eventually we can have views or functions served in this way...

app = SingularityServer(__name__)
#api = Api(app)    
#api.add_resource(apiExperiments,'/experiments')
#api.add_resource(apiExperimentSingle,'/experiments/<string:exp_id>')

app.config['ALLOWED_EXTENSIONS'] = set(['png', 'jpg', 'jpeg','gif'])



# INTERACTIVE CONTAINER EXPLORATION ################################

@app.route('/container/tree')
def container_tree():
    # The server will store the package name and result object for query
    if app.viz == None:
        if app.docker == False:
            app.viz = tree(app.package)
        else:
            app.viz = tree(app.package,docker=True,sudopw=app.sudopw)
    container_name = os.path.basename(app.package).split(".")[0]
    return render_template('container_tree.html',graph=app.viz['graph'],
                                                 files=app.viz['files'],
                                                 container_name=container_name)
    
@app.route('/container/difftree')
def difference_tree():
    # The server will store the package name and result object for query
    if app.viz == None:
        app.viz = diff_tree(app.packages[0],app.packages[1])
    container1_name = os.path.basename(app.packages[0]).split(".")[0]
    container2_name = os.path.basename(app.packages[1]).split(".")[0]
    title = "%s minus %s" %(container1_name,container2_name)
    return render_template('container_tree.html',graph=app.viz['graph'],
                                                 files=app.viz['files'],
                                                 container_name=title)

@app.route('/container/simtree')
def similar_tree():
    # The server will store the package name and result object for query
    if app.viz == None:
        app.viz = sim_tree(app.packages[0],app.packages[1])
    container1_name = os.path.basename(app.packages[0]).split(".")[0]
    container2_name = os.path.basename(app.packages[1]).split(".")[0]
    title = "%s INTERSECT %s" %(container1_name,container2_name)
    return render_template('container_tree.html',graph=app.viz['graph'],
                                                 files=app.viz['files'],
                                                 container_name=title)

# START FUNCTIONS ##################################################
    
# Function to make single package/image tree
def make_tree(package,docker=False,port=None,sudopw=None):
    app.package = package
    app.docker = docker
    app.sudopw = sudopw
    if port==None:
        port=8088
    print "It goes without saying. I suspect now it's not going."
    webbrowser.open("http://localhost:%s/container/tree" %(port))
    app.run(host="0.0.0.0",debug=False,port=port)

# Function to make difference tree to compare image against base
def make_difference_tree(base_image,subtract,port=None):
    app.packages = [base_image,subtract]
    if port==None:
        port=8088
    print "I'm in a nutshell! Who put me into this nutshell?"
    webbrowser.open("http://localhost:%s/container/difftree" %(port))
    app.run(host="0.0.0.0",debug=True,port=port)

# Function to make similar tree to compare images
def make_sim_tree(image1,image2,port=None):
    app.packages = [image1,image2]
    if port==None:
        port=8088
    print "The recipe for insight can be reduced to a box of cereal and a Sunday afternoon."
    webbrowser.open("http://localhost:%s/container/simtree" %(port))
    app.run(host="0.0.0.0",debug=True,port=port)

if __name__ == '__main__':
    app.debug = True
    app.run(host='0.0.0.0')
