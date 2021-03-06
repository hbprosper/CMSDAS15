#!/usr/bin/env python
# -----------------------------------------------------------------------------
#  File:        train.py
#  Description: Random Grid Search to find cuts that best separate the VBF
#               ggF Higgs boson production modes
#  Created:     10-Jan-2015 Harrison B. Prosper
# -----------------------------------------------------------------------------
import os, sys, re
from string import *
from ROOT import *
# -----------------------------------------------------------------------------
def error(message):
    print "** %s" % message
    exit(0)
def nameonly(s):
    import posixpath
    return posixpath.splitext(posixpath.split(s)[1])[0]    
# -----------------------------------------------------------------------------
def main():
    print "="*80
    print "\t\t=== Random Grid Search ==="
    print "="*80

    # ---------------------------------------------------------------------
    #  Load RGS class and that we have all that we need
    # ---------------------------------------------------------------------
    gSystem.AddLinkedLibs("-L$ROOTSYS/lib -lTreePlayer")
    gROOT.ProcessLine(".L RGS.cc+")

    varfilename = "rgs.vars"
    if not os.path.exists(varfilename):
        error("unable to open variables file %s" % varfilename)

    sigfilename = "../data/root/vbf13TeV_train.root"
    if not os.path.exists(sigfilename):
        error("unable to open signal file %s" % sigfilename)

    bkgfilename = "../data/root/ggf13TeV_train.root"
    if not os.path.exists(bkgfilename):
        error("unable to open background file %s" % bkgfilename)

    # ---------------------------------------------------------------------
    #  Create RGS object
    #  Need:
    #   A file of cut-points - usually a signal file, which ideally is
    #   not the same as the signal file on which the RGS algorithm is run.
    # ---------------------------------------------------------------------
    print "==> create RGS object"
    
    cutfilename= sigfilename
    start      = 0           # start row (after event selection)
    maxcuts    = 1000        # maximum number of cut-points to consider
    treename   = "Analysis"  # name of Root tree 
    weightname = "weight"    # name of event weight variable
    
    rgs = RGS(cutfilename, start, maxcuts,
              treename, weightname)

    # ---------------------------------------------------------------------
    #  Add signal and background data to RGS object
    #  Weight each event using the value in the field weightname, if it
    #  exists.
    #  NB: We asssume all files are of the same format
    # ---------------------------------------------------------------------
    start    = 0 #  start row
    numrows  = 0 #  scan all the data from the files

    print "==> load background data"
    rgs.add(bkgfilename, start, numrows)
    print

    print "==> load signal data"
    rgs.add(sigfilename, start, numrows)
    print
    # ---------------------------------------------------------------------	
    #  Run RGS and write out results
    # ---------------------------------------------------------------------	    
    rgs.run(varfilename)
    rgsfilename = "%s.root" % nameonly(varfilename)
    rfile = rgs.save(rgsfilename)
# -----------------------------------------------------------------------------
try:
    main()
except KeyboardInterrupt:
    print "\tciao!\n"



