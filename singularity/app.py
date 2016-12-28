from singularity.views import (
    container_tree, 
    container_similarity,
    container_difference
)

from flask import (
    Flask, 
    render_template, 
    request
)

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
        self.image = None
        self.images = None
        self.sudopw = None


# API VIEWS #########################################################
# eventually we can have views or functions served in this way...

app = SingularityServer(__name__)
#api = Api(app)    
#api.add_resource(apiExperiments,'/experiments')
#api.add_resource(apiExperimentSingle,'/experiments/<string:exp_id>')

# INTERACTIVE CONTAINER EXPLORATION ################################

@app.route('/container/tree')
def app_container_tree():
    # The server will store the package name and result object for query
    if app.viz == None:
        app.viz = container_tree(app.image)
    container_name = os.path.basename(app.image).split(".")[0]
    return render_template('container_tree.html',graph=app.viz['graph'],
                                                 files=app.viz['files'],
                                                 container_name=container_name)
    
@app.route('/containers/subtract')
def difference_tree():
    # The server will store the package name and result object for query
    if app.viz == None:
        app.viz = container_difference(app.images[0],app.images[1])
    container1_name,container2_name = get_container_names()
    title = "%s minus %s" %(container1_name,container2_name)
    return render_template('container_tree.html',graph=app.viz['graph'],
                                                 files=app.viz['files'],
                                                 container_name=title)

@app.route('/containers/similarity')
def app_similar_tree():
    # The server will store the package name and result object for query
    if app.viz == None:
        app.viz = container_similarity(app.images[0],app.images[1])
    container1_name,container2_name = get_container_names()
    title = "%s INTERSECT %s" %(container1_name,container2_name)
    return render_template('container_tree.html',graph=app.viz['graph'],
                                                 files=app.viz['files'],
                                                 container_name=title)

def get_container_names():
    '''return container names for one or more images, depending on what
    app initialized for.
    '''
    if app.images != None:
        container1_name = os.path.basename(app.images[0]).split(".")[0]
        container2_name = os.path.basename(app.images[1]).split(".")[0]
        return container1_name,container2_name
    return None

# START FUNCTIONS ##################################################
    
# Function to make single package/image tree
def make_tree(image,port=None,sudopw=None):
    app.image = image
    app.sudopw = sudopw
    if port==None:
        port=8088
    print("It goes without saying. I suspect now it's not going.")
    webbrowser.open("http://localhost:%s/container/tree" %(port))
    app.run(host="0.0.0.0",debug=False,port=port)

# Function to make similar tree to compare images
def make_sim_tree(image1,image2,port=None):
    app.images = [image1,image2]
    if port==None:
        port=8088
    print("The recipe for insight can be reduced to a box of cereal and a Sunday afternoon.")
    webbrowser.open("http://localhost:%s/containers/similarity" %(port))
    app.run(host="0.0.0.0",debug=False,port=port)

# Function to make difference tree for two images
def make_diff_tree(image1,image2,port=None):
    app.images = [image1,image2]
    if port==None:
        port=8088
    print("Pandas... just let them go.")
    webbrowser.open("http://localhost:%s/containers/subtract" %(port))
    app.run(host="0.0.0.0",debug=True,port=port)


if __name__ == '__main__':
    app.debug = False
    app.run(host='0.0.0.0')
