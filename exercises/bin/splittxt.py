#!/usr/bin/env python
# split text files into one for training and another for testing
# -----------------------------------------------------------------------------
import os, sys
from histutil import nameonly
from string import *
from random import shuffle
# -----------------------------------------------------------------------------
def writeOut(outfname, header, records):
    print "==> write file %s" % outfname, len(records)
    recs    = [header] + records
    open(outfname, 'w').writelines(recs)
# -----------------------------------------------------------------------------
argv = sys.argv[1:]
argc = len(argv)
if argc < 1:
    print '''
Usage:
    splittxt.py input-filename [fraction=0.5 or number in training file] 
    '''
    sys.exit()
# -----------------------------------------------------------------------------
ifilename = argv[0]
if not os.path.exists(ifilename):
    print "** can't find file %s" % ifilename
    sys.exit()

records = open(ifilename).readlines()
header  = records[0]
records = records[1:]
## records = []
## for record in recs:
##         t = split(record)
##         njets = atoi(t[-1])
##         if njets < 2: continue
##         records.append(record)
        
shuffle(records)
#print len(records)

name = nameonly(ifilename)
fraction = 0.5
if argc > 1:
    fraction = atof(argv[1])
if fraction > 1:
    nn = atoi(argv[1])
else:
    nn = int(fraction*len(records))
    
writeOut('%s_train.txt' % name, header, records[:nn])
writeOut('%s_test.txt'  % name, header, records[nn:])



