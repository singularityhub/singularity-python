# Docker images

These docker images are meant to provide a client for [Singularity Hub](Dockerfile.shub)
and [Singularity Registry](Dockerfile.sregistry), respectively. These images are provided on [Docker Hub](https://hub.docker.com/r/vanessa/singularity-python/).


## Singuarity Python Base

**build**
```
docker build -t vanessa/singularity-python .
docker tag vanessa/singularity-python vanessa/singularity-python:2.4.1
docker push vanessa/singularity-python:2.4.1
```

## Singularity Client

**build**
```
docker build -f Dockerfile.shub -t vanessa/singularity-python:shub-2.4.1 .
docker push vanessa/singularity-python:shub-2.4.1
```

**usage**
```
docker run vanessa/singularity-python:shub-2.4.1
```

## Singularity Registry Client

**build**
```
docker build -f Dockerfile.sregistry -t vanessa/singularity-python:sreg-2.4.1 .
docker push vanessa/singularity-python:sreg-2.4.1
```

**usage**
```
docker run vanessa/singularity-python:sreg-2.4.1
```
