# Container Tree

The functions under analysis will help you show the contents of an image (folders and files) in your web browser.

```python

from singularity.views import ( make_container_tree, get_template )

files = ["/path/1", .. , "/path/N"]

tree = container_tree(files=files, folders=files)

html = get_template('container_tree', {'{{ files | safe }}': json.dumps(tree['files']),
                                       '{{ graph | safe }}': json.dumps(tree['graph']),
                                       '{{ container_name }}': "My Container Tree"})
```

![../../img/files.png](../../img/files.png)

An [interactive demo](https://singularityware.github.io/singularity-python/examples/container_tree) is also available.
