Bootstrap: docker
From: continuumio/miniconda3

%runscript
exec /opt/conda/bin/python "$@"

%labels
maintainer vsochat@stanford.edu

%post
apt-get update && apt-get install -y git

# Dependncies
/opt/conda/bin/conda install -y numpy scikit-learn cython pandas

# Install Singularity Python
cd /opt
git clone https://www.github.com/singularityware/singularity-python
cd singularity-python
/opt/conda/bin/pip install setuptools
/opt/conda/bin/pip install -r requirements.txt
/opt/conda/bin/python setup.py install
