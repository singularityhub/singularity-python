#!/bin/bash

################################################################################
# Build Latest, only runs build without updating software
# For Google cloud, Stackdriver/logging should have Write, 
#                   Google Storage should have Full
#                   All other APIs None,
#
################################################################################

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
