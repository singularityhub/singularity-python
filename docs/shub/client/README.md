
# Singularity Hub Client 

The main Singularity Hub client is accessible by way of Singularity Python.  We can use the client to obtain manifests, and download images with the Singularity Hub API.

```python
from singularity.hub.client import Client
shub = Client() 
```

## Collection Information

```python
container_name = 'vsoch/singularity-hello-world'
collection = shub.get_collection(container_name)

INFO:shub_builder:User: vsoch
INFO:shub_builder:Repo Name: singularity-hello-world
INFO:shub_builder:Repo Tag: latest
DEBUG:shub_builder:GET https://singularity-hub.org/api/collection/vsoch/singularity-hello-world:latest
DEBUG:shub_builder:Headers found: Content-Type
DEBUG:requests.packages.urllib3.connectionpool:Starting new HTTPS connection (1): singularity-hub.org
DEBUG:requests.packages.urllib3.connectionpool:https://singularity-hub.org:443 "GET /api/collection/vsoch/singularity-hello-world:latest HTTP/1.1" 200 None
```

The containers associated with the collection are here:

```python
container_ids = collection['container_set']
```

and here is a simple loop to show downloading them to a temporary directory, and obtaining the metrics for each

```python
import tempfile
storage = tempfile.mkdtemp()

for container_id in container_ids:
   manifest = shub.get_container(container_id)
   image = shub.pull_container(manifest,
                               download_folder=storage,
                               name="%s.img.gz" %(manifest['version']))       

   metrics = shub.load_metrics(manifest)
```


## Containers
If you want to get all containers in Singularity Hub, you can do that too.

```python
containers = shub.get_containers()
```

and then you can download them similarity:

```python
for container_name,container in containers.items():
    for branch, manifest in container.items():        
        name = manifest['name'].replace('/','-')
        uncompressed = "%s-%s.img" %(name,branch)
           image = shub.pull_container(manifest,
                                       download_folder=hub,
                                       name="%s-%s.img.gz" %(name,branch))       
```
