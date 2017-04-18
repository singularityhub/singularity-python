

## Reproducibility

Singularity Python has commands that will generate content hashes for all files in a container, and use a (just submitted paper) algorithm to derive similarity scores of containers on different levels of reproducibility. 

### Levels
You can see the levels by loading them programatically:

```python
from singularity.reproduce import get_levels
levels = get_levels()
```

and print their description:

```python
for name,level in levels.items():
    print("%s: %s" %(name,level['description']))
```

I've put them into a list for easier reading here:

- `RECIPE`: recipe looks at everything on the level of the Singularity image, meaning the runscript, and environment for version 2.2
- `LABELS`: only look at the container labels, if they exist (singularity version 2.3)
- `RUNSCRIPT`: runscript is a level that assesses only the executable runscript in the  image. This is a fast approach to sniff if the container is broadly doing the same thing
- `BASE`: base ignores the core Singularity files, and focuses on the base operating system, and omits files in variable locations (eg, /tmp and /var)
- `IDENTICAL`: The image is exactly the same, meaning the file itself. This is what should be achieved if you download the same image multiple times. The entire contents of the image are used to generate the hash.
- `ENVIRONMENT`: only look at the container's environment. This level will only look at the environment files when assessing similarity.
- `REPLICATE`: replicate assumes equivalence in the core Singularity files, plus the base operating system, but not including files in variable locations (eg, /tmp and /var)
```


### Compare Containers
We can use these levels to assess two containers. Let's first write a function to generate images:

```python
from singularity.cli import Singularity


def create_image(image_path,import_uri):
    S = Singularity()
    S.create(image_path)
    S.importcmd(image_path,import_uri)
    return image_path

image1 = create_image('/tmp/ubuntu.img','docker://ubuntu')
image2 = create_image('/tmp/centos.img','docker://centos')
```

Note that you don't have to create images in this fashion, you can use images that you already have on your machine. Now let's run a function to compare the images on all of our reproducibility levels.

```python
from singularity.reproduce import assess_differences
diffs = assess_differences(image1,image2,levels=levels)

diffs.keys()
dict_keys(['RECIPE', 'LABELS', 'IDENTICAL', 'scores', 'BASE', 'RUNSCRIPT', 'ENVIRONMENT', 'REPLICATE'])
```

Diffs will give you, for each level, a score:

```python
diffs['scores']
{'BASE': 0.8571428571428571,
 'ENVIRONMENT': 0.8571428571428571,
 'IDENTICAL': 0.7142857142857143,
 'LABELS': 0.8571428571428571,
 'RECIPE': 0.8571428571428571,
 'REPLICATE': 0.8571428571428571,
 'RUNSCRIPT': 0.8571428571428571}
```

along with, for each level, a summary of shared and different files.


### Hashes
You may want to generate image hashes for your own purposes. Here we are still using `image1` and `image2` from above, and you can use your own image path generated otherwise.

```python
from singularity.reproduce import (
    get_content_hashes,
    get_image_hashes,
    get_image_hash
)

hashes = get_content_hashes(image1)
```

This first command will give you dictionary of hashes, sizes, and root owned, each a dictionary with the file name as key, and the hash (md5 sum), size (MB), and root_owned (True/False) as values. The last function generates static values to summarize all files.

```
hashes = get_image_hashes(image1,levels=levels)
hashes
{'BASE': 'efd4eb00a00ffb439f5528f6682bfd0e',
 'ENVIRONMENT': '71c5744cd7f55fe0143aa3a1ce069a0c',
 'IDENTICAL': '6aef501712498da737185f4bec509be9',
 'LABELS': '99914b932bd37a50b983c5e7c90ae93b',
 'RECIPE': '09cf246ab36162254154a77650cc6b43',
 'REPLICATE': '9ef624976f03d9f685fe980e26da003f',
 'RUNSCRIPT': '5187f75325abc813444dd3e35bf0bdb4'}
```

We advise you to only save the level `IDENTICAL`, `ENVIRONMENT`, `RUNSCRIPT`, and `RECIPE` for later comparison with other images. The other levels, when doing a comparison, are reliant on reading the bytes content and comparing to the other image. To make the algorithm faster, this is only done when the original files aren't in agreement.


### Visualization
You can generate a package or interactive tree to compare containers.

`diffs` here will be a pandas data frame, with rows and columns corresponding to identical containers, and the index being the names. You can produce this using the assess_differences function, and putting the scores into a dataframe. You can also use the function to generate this matric, from a list of image paths:

```python
from singularity.analysis.compare import compare_singularity_images
image_files = [image1,image2]
diffs = compare_singularity_images(image_paths1=image_files)
```

Once you have this dataframe:

```python
from singularity.views.utils import get_template
from singularity.views.trees import make_package_tree
import os

labels = [os.path.basename(x) for x in diffs.index.tolist()]
fig = make_package_tree(matrix=diffs,labels=labels,title="Singularity Hub Replication Scores")

# This will show your figure
fig.show()

# or save it to file
fig.savefig('diffs_tree.png')
```

You can make an interactive tree, which will be a static web page that you can render on a server:

```
from singularity.views.trees import make_interactive_tree
import json

# Interactive tree
tree = make_interactive_tree(matrix=diffs,labels=labels)
fields = {"{{ graph | safe }}",json.dumps(tree)}
template = get_template("comparison_tree",fields)
#http://www.vanessasaur.us/singularity-python/docs/hub/paper/index.html
write_file('index.html' template)
```

You can also make a simple heatmap, here I am using plotly.

```python
import plotly.plotly as py
import plotly.graph_objs as go
from scipy.cluster.hierarchy import linkage, dendrogram

Z = linkage(diffs, 'ward')

d=dendrogram(Z,
             leaf_rotation=90.,  # rotates the x axis labels
             leaf_font_size=font_size,  # font size for the x axis l
             labels=labels)

index = d['leaves']
D = numpy.array(diffs)
D=D[index,:]
D=D[:,index]
data = [
    go.Heatmap(
        z=D,
        x=labels,
        y=labels
    )
]
py.iplot(data,filename='diffs_heatmap')
```

Finally, you can do RSA (representational similarity analysis) to compare two data frames:

```python
from singularity.analysis.compare import RSA

pearsonr_sim = RSA(diffs1,diffs2)
# 0.74136458648818637
```

You can look at more specific examples at:

- [generate_image_hash.py](generate_image_hash.py)
- [assess_replication.py](assess_replication.py)
