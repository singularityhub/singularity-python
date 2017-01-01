#!/bin/sh
sudo apt-get update
sudo apt-get -y install git
sudo apt-get install -y build-essential libtool autotools-dev automake autoconf
sudo apt-get install -y python3-pip
cd /tmp && git clone http://www.github.com/singularityware/singularity
cd singularity && ./autogen.sh && ./configure --prefix=/usr/local && make && sudo make install
export SINGULARITY_VERSION=$(singularity --version)
sudo pip3 install --upgrade pip
sudo pip3 install --upgrade google-api-python-client
sudo pip3 install --upgrade google
sudo pip3 install oauth2client==3.0.0
sudo pip3 install gitpython
cd /tmp && git clone https://github.com/singularityware/singularity-python
cd singularity-python && python3 setup.py sdist && sudo python3 setup.py install
python3 -c "from singularity.build.google import run_build; run_build()" > /tmp/.shub-log 2>&1
command=$(echo "from singularity.build.google import finish_build; finish_build(logfile='/tmp/.shub-log')")
python3 -c "$command"
