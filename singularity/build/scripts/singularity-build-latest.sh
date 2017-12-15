#!/bin/bash

################################################################################
# Build Latest, only runs build without updating software
# For Google cloud, Stackdriver/logging should have Write, 
#                   Google Storage should have Full
#                   All other APIs None,
#
#
# Copyright (C) 2017 The Board of Trustees of the Leland Stanford Junior
# University.
# Copyright (C) 2016-2017 Vanessa Sochat.
#
# This program is free software: you can redistribute it and/or modify it
# under the terms of the GNU Affero General Public License as published by
# the Free Software Foundation, either version 3 of the License, or (at your
# option) any later version.
#
# This program is distributed in the hope that it will be useful, but WITHOUT
# ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or
# FITNESS FOR A PARTICULAR PURPOSE.  See the GNU Affero General Public
# License for more details.
#
# You should have received a copy of the GNU Affero General Public License
# along with this program.  If not, see <https://www.gnu.org/licenses/>.
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
