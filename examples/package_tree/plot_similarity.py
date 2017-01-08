from scipy.spatial.distance import pdist, squareform
from plotly.tools import FigureFactory as FF
from plotly.graph_objs import *
import plotly.plotly as py
from glob import glob
import numpy as np
import pickle

base = '/home/vanessa/Documents/Dropbox/Code/singularity/singularity-python'
analysis_directory = "%s/examples/package_tree" %(base)


# From https://plot.ly/python/dendrogram/, thanks plotly! :)

data = pickle.load(open('comparisons.pkl','rb'))['files.txt']

#lookup = {x:x.split("-")[0] for x in data.index.tolist()}
#    labels = [lookup[x] for x in data.index.tolist()]

labels = data.index.tolist()
# Initialize figure by creating upper dendrogram
figure = FF.create_dendrogram(data, orientation='bottom', labels=labels)
for i in range(len(figure['data'])):
    figure['data'][i]['yaxis'] = 'y2'

# Create Side Dendrogram
dendro_side = FF.create_dendrogram(data, orientation='right')
for i in range(len(dendro_side['data'])):
    dendro_side['data'][i]['xaxis'] = 'x2'

# Add Side Dendrogram Data to Figure
figure['data'].extend(dendro_side['data'])

# Create Heatmap
dendro_leaves = dendro_side['layout']['yaxis']['ticktext']
dendro_leaves = list(map(int, dendro_leaves))
data_dist = pdist(data)
heat_data = squareform(data_dist)
heat_data = heat_data[dendro_leaves,:]
heat_data = heat_data[:,dendro_leaves]

heatmap = Data([
    Heatmap(
        x = dendro_leaves, 
        y = dendro_leaves,
        z = heat_data,    
        colorscale = 'YIGnBu'
    )
])

heatmap[0]['x'] = figure['layout']['xaxis']['tickvals']
heatmap[0]['y'] = dendro_side['layout']['yaxis']['tickvals']

# Add Heatmap Data to Figure
figure['data'].extend(Data(heatmap))

    # Edit Layout
    figure['layout'].update({'width':800, 'height':800,
                             'showlegend':False, 'hovermode': 'closest',
                             })

    # Edit xaxis
    figure['layout']['xaxis'].update({'domain': [.15, 1],
                                      'mirror': False,
                                      'showgrid': False,
                                      'showline': False,
                                      'zeroline': False,
                                      'ticks':""})
    # Edit xaxis2
    figure['layout'].update({'xaxis2': {'domain': [0, .15],
                                       'mirror': False,
                                       'showgrid': False,
                                       'showline': False,
                                       'zeroline': False,
                                       'showticklabels': False,
                                       'ticks':""}})

    # Edit yaxis
    figure['layout']['yaxis'].update({'domain': [0, .85],
                                      'mirror': False,
                                      'showgrid': False,
                                      'showline': False,
                                      'zeroline': False,
                                      'showticklabels': False,
                                      'ticks': ""})
    # Edit yaxis2
    figure['layout'].update({'yaxis2':{'domain':[.825, .975],
                                       'mirror': False,
                                       'showgrid': False,
                                       'showline': False,
                                       'zeroline': False,
                                       'showticklabels': False,
                                       'ticks':""}})

    # Plot!
    py.iplot(figure, filename='dendrogram_with_heatmap')


# AND TREE
from matplotlib import pyplot as plt
from scipy.cluster.hierarchy import dendrogram, linkage
import numpy as np
Z = linkage(data, 'ward')

from scipy.cluster.hierarchy import cophenet
from scipy.spatial.distance import pdist

c, coph_dists = cophenet(Z, pdist(data))
c


plt.figure(figsize=(10, 8))
plt.scatter(Z[:,0], Z[:,1])  # plot all points
plt.show()

labels = [x.replace(':latest','') for x in data.index.tolist()]
plt.figure(figsize=(25, 10))
plt.title('Docker Library Similarity')
plt.xlabel('image index')
plt.ylabel('distance')
dendrogram(
    Z,
    leaf_rotation=90.,  # rotates the x axis labels
    leaf_font_size=8.,  # font size for the x axis labels
    labels=labels
)
plt.show()
