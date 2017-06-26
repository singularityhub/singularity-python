'''
The MIT License (MIT)

Copyright (c) 2016-2017 Vanessa Sochat

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.

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

