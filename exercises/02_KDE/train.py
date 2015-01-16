#!/usr/bin/env python
#----------------------------------------------------------------------
# File: train.py
# Description: example of kernel density estimation
# Created: 01-June-2013 INFN SOS 2013, Vietri sul Mare, Italy, HBP
#          Adapted for CMSDAS Bari 2015
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
        point[0], point[1] = event.deltaetajj, event.massjj
        kde.add(point)
    kde.optimize()
    kde.write(name)
#----------------------------------------------------------------------
def main():
    print "\n", "="*80
    print "\tKernel Density Estimation"
    print "="*80

    treename    = "Analysis"
    sigfilename = '../data/root/vbf13TeV_train.root'
    bkgfilename = '../data/root/ggf13TeV_train.root'
        
    # compile standalone KDE class
    gROOT.ProcessLine('.L KDE.cc+')

    # build KDE approximations
    sntuple = Ntuple(sigfilename, treename)
    skde = KDE('deltaetajj massjj')
    buildKDE(sntuple, skde, 'skde')
    
    bntuple = Ntuple(bkgfilename, treename)
    bkde = KDE('deltaetajj massjj')
    buildKDE(bntuple, bkde, 'bkde')
#----------------------------------------------------------------------
try:
    main()
except KeyboardInterrupt:
    print "\nciao"
