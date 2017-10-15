#!/bin/bash

################################################################################
# Instance Update and build
# For Google cloud, Stackdriver/logging should have Write, 
#                   Google Storage should have Full
#                   All other APIs None,
#
################################################################################

# Install Singularity from Github
cd /tmp && git clone -b feature-squashbuild-secbuild https://github.com/cclerget/singularity.git &&
cd /tmp/singularity && ./autogen.sh && ./configure --prefix=/usr/local && make && sudo make install && sudo make secbuildimg

# Singularity python development
cd /tmp && git clone -b development https://www.github.com/vsoch/singularity-python.git &&
cd /tmp/singularity-python && sudo python3 setup.py install

echo "Start Time: $(date)." > /tmp/.shub-log 2>&1
timeout -s KILL 2h sudo python3 -c "from singularity.build.google import run_build; run_build()" >> /tmp/.shub-log 2>&1
ret=$?

echo "Return value of ${ret}." >> /tmp/.shub-log 2>&1

if [ $ret -eq 137 ]
then
    echo "Killed: $(date)." >> /tmp/.shub-log 2>&1
else
    echo "End Time: $(date)." >> /tmp/.shub-log 2>&1
fi

# Finish by sending log
sudo python3 -c "from singularity.build.google import finish_build; finish_build()"
