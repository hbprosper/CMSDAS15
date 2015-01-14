#!/usr/bin/env python
#----------------------------------------------------------------------
# File: train.py
# Description: example of kernel density estimation
# Created: 01-June-2013 INFN SOS 2013, Vietri sul Mare, Italy, HBP
#----------------------------------------------------------------------
import os, sys, re
from math import *
from string import *
from histutil import *
from ROOT import *
#----------------------------------------------------------------------
def buildKDE(ntuple, kde, name):
    point = vector('double')(2)
    for rownumber, event in enumerate(ntuple):
        if rownumber % 1000 == 0: print count
        point[0], point[1] = event.f_Z1mass, event.f_Z2mass
        kde.add(point)
        if rownumber >= 3000: break
    kde.optimize()
    kde.write(name)
#----------------------------------------------------------------------
def main():
    print "\n", "="*80
    print "\t example of kernel density estimation"
    print "="*80

    # compile standalone KDE class
    gROOT.ProcessLine('.L KDE.cc+')

    # create KDE objects
    bkde = KDE('mz1 mz2')
    skde = KDE('mz1 mz2')

    # build KDE approximations
    treename  = "Analysis"
    sfilename = '../data/root/sig_HZZ4l_8TeV.root'
    sntuple = Ntuple(sfilename, treename)
    buildKDE(sntuple, skde, 'skde')
    
    bfilename = '../data/root/bkg_ZZ4l_8TeV.root'
    bntuple = Ntuple(bfilename, treename)
    buildKDE(bntuple, bkde, 'bkde')
#----------------------------------------------------------------------
try:
    main()
except KeyboardInterrupt:
    print "\nciao"
