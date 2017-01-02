#!/bin/sh
sudo apt-get update
sudo apt-get -y install git
sudo apt-get install -y build-essential libtool autotools-dev automake autoconf
sudo apt-get install -y python3-pip
cd /tmp && git clone http://www.github.com/singularityware/singularity
cd singularity && ./autogen.sh && ./configure && make && sudo make install
export SINGULARITY_VERSION=$(singularity --version)
sudo pip3 install --upgrade pip
sudo pip3 install --upgrade google-api-python-client
sudo pip3 install --upgrade google
sudo pip3 install oauth2client==3.0.0
sudo pip3 install gitpython
sudo pip3 install singularity --upgrade
sudo python3 -c "from singularity.build.google import run_build; run_build()" > /tmp/.shub-log 2>&1
export command=$(echo "from singularity.build.google import finish_build; finish_build()")
sudo python3 -c "$command"
