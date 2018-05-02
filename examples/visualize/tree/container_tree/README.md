# Container Tree

The functions under analysis will help you show the contents of an image (folders and files) in your web browser.

```python

from singularity.views import ( container_tree, get_template )

files = ["/path/1", .. , "/path/N"]

tree = container_tree(files=files, folders=files)
html = get_template('container_tree', {'files': tree['files'],
                                       'graph': tree['graph'],
                                        'container_name': "My Container Tree"})
```

![../../img/files.png](../../img/files.png)

An [interactive demo](https://singularityware.github.io/singularity-python/examples/container_tree) is also available.

It's suggested that you use a package so it will open automatically - note that if you specify an image file, it will need to be packaged, and the console will hang as it waits for you to type it in and press enter.

![sudopw.png](sudopw.png)

This is a pretty simple start, and the cool thing about this idea is that we can use the same visualization to show commonalities and differences between containers, and it doesn't even limit us to Singularity, this would work for Docker, or your local file system, or any combination of those things. This (comparison of images) is the reason I delved into this in the first place! I will write up the method / thinking soon.
