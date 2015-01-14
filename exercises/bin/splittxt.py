#!/usr/bin/env python
# split text files into one for training and another for testing
# -----------------------------------------------------------------------------
import os, sys
from histutil import nameonly
from string import *
from random import shuffle
# -----------------------------------------------------------------------------
def writeOut(outfname, header, records):
    print "==> write file %s" % outfname
    recs    = [header] + records
    open(outfname, 'w').writelines(recs)
# -----------------------------------------------------------------------------
argv = sys.argv[1:]
argc = len(argv)
if argc < 1:
    print '''
Usage:
    splittxt.py input-filename [fraction=0.5] 
    '''
    sys.exit()
# -----------------------------------------------------------------------------
ifilename = argv[0]
if not os.path.exists(ifilename):
    print "** can't find file %s" % ifilename
    sys.exit()
    
name = nameonly(ifilename)
fraction = 0.5
if argc > 1:
    fraction = atof(argv[1])

records = open(ifilename).readlines()
header  = records[0]
records = records[1:]
shuffle(records)

nn = int(fraction*len(records))
writeOut('%s_train.txt' % name, header, records[:nn])
writeOut('%s_test.txt'  % name, header, records[nn:])



