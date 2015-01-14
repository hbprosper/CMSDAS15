#!/usr/bin/env python
#------------------------------------------------------------------------------
# File: txt2ntp.py
# Description: make ntuple from text file
# Created: 29 May 2013 Bari, Italy, HBP
#------------------------------------------------------------------------------
import os, sys
from ROOT import *
from string import *
#-------------------------------------------------------------------------
def readTable(filename, nrows=0):
    def convert(s):
        try:
            return atof(s)
        except:
            return s
    
    try:
        f = open(filename, 'r')
    except:
        print "** error can't open file %s" % filename
        sys.exit(0)

    # be sure to read header
    header = split(f.readline())
    namemap = {}
    for col in xrange(len(header)):
        namemap[header[col]] = col
        
    # loop over rows
    untilHellFreezesOver = True
    rowcounter = 0
    data = []
    while untilHellFreezesOver:
        rowcounter = rowcounter + 1
        record = f.readline()
        if not record:
            break
        d = map(convert, split(record))
        data.append(d)
        
        if nrows > 0:
            untilHellFreezesOver = rowcounter < nrows
        
    return (namemap, header, data)
#-------------------------------------------------------------------------
#-------------------------------------------------------------------------
def main():
    print "\n", "="*80
    print "\tcreate ntuple from text file"
    print "="*80
    argv = sys.argv[1:]
    if len(argv) == 0:
        print '''
        Usage:
            python txt2ntp.py input-text-filename [tree-name=Analysis]
        '''
        sys.exit(0)
    filename = argv[0]
    if not os.path.exists(filename):
        print "can't find %s" % filename
        sys.exit(0)

    if len(argv) > 1:
        treename = argv[1]
    else:
        treename = 'Analysis'
        
    namemap, header, data = readTable(filename)
    rootname = split(filename,'.')[0]+'.root'
    
    # Make an empty tree
    rfile = TFile(rootname,'RECREATE')
    tree  = TTree(treename, treename)

    # Create a struct
    cmd = 'struct Row {'
    for name in header:
        cmd += 'double %s;' % name
    cmd += "};"
    gROOT.ProcessLine(cmd)

    # Make struct known to Python
    from ROOT import Row
    
    # Create branches in the tree
    row = Row()
    for name in header:
        tree.Branch(name, AddressOf(row, name),'%s/D' % name)
    
    # Fill tree
    for ii, d in enumerate(data):
        if ii % 100 == 0: print ii
        for name in header:
            cmd = 'row.%s = %f' % (name, d[namemap[name]])
            exec(cmd)
        tree.Fill()
        
    rfile.Write()
    rfile.Close()
#-------------------------------------------------------------------------    
main()


