'''

Copyright (C) 2017 The Board of Trustees of the Leland Stanford Junior
University.
Copyright (C) 2016-2017 Vanessa Sochat.

This program is free software: you can redistribute it and/or modify it
under the terms of the GNU Affero General Public License as published by
the Free Software Foundation, either version 3 of the License, or (at your
option) any later version.

This program is distributed in the hope that it will be useful, but WITHOUT
ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or
FITNESS FOR A PARTICULAR PURPOSE.  See the GNU Affero General Public
License for more details.

You should have received a copy of the GNU Affero General Public License
along with this program.  If not, see <https://www.gnu.org/licenses/>.

'''

from glob import glob
import json
import os
import re
from singularity.logger import bot


###################################################################################
# METRICS #########################################################################
###################################################################################


def information_coefficient(total1,total2,intersect):
    '''a simple jacaard (information coefficient) to compare two lists of overlaps/diffs
    '''
    total = total1 + total2
    return 2.0*len(intersect) / total



def RSA(m1,m2):
    '''RSA analysis will compare the similarity of two matrices
    '''
    from scipy.stats import pearsonr
    import scipy.linalg
    import numpy

    # This will take the diagonal of each matrix (and the other half is changed to nan) and flatten to vector
    vectorm1 = m1.mask(numpy.triu(numpy.ones(m1.shape)).astype(numpy.bool)).values.flatten()
    vectorm2 = m2.mask(numpy.triu(numpy.ones(m2.shape)).astype(numpy.bool)).values.flatten()
    # Now remove the nans
    m1defined = numpy.argwhere(~numpy.isnan(numpy.array(vectorm1,dtype=float)))
    m2defined = numpy.argwhere(~numpy.isnan(numpy.array(vectorm2,dtype=float)))
    idx = numpy.intersect1d(m1defined,m2defined)
    return pearsonr(vectorm1[idx],vectorm2[idx])[0]

