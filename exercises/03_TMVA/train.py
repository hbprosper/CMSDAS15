#!/usr/bin/env python
#----------------------------------------------------------------------
# File: train.py
# Description: example of classification with TMVA
# Created: 01-June-2013 INFN SOS 2013, Vietri sul Mare, Italy, HBP
#   adapted for CMSDAS 2015 Bari HBP
#----------------------------------------------------------------------
import os, sys, re
from math import *
from string import *
from time import sleep
from array import array
from histutil import *
from ROOT import *
#----------------------------------------------------------------------
def getTree(filename, treename):
    hfile = TFile(filename)
    if not hfile.IsOpen():
        print "** can't open file %s" % filename
        sys.exit()
    tree = hfile.Get(treename)
    if tree == None:
        print "** can't find tree %s" % treename
        sys.exit()
    return (hfile, tree)
#----------------------------------------------------------------------
#----------------------------------------------------------------------
def main():
    print "\n", "="*80
    print "\tclassification with TMVA"
    print "="*80

    treename    = "Analysis"    
    # get signal and background data for training/testing
    sigfilename = '../data/root/vbf13TeV.root'
    bkgfilename = '../data/root/ggf13TeV.root'    
    sigFile, sigTree = getTree(sigfilename, treename)
    bkgFile, bkgTree = getTree(bkgfilename, treename)
    
    # everything is done via a TMVA factory
    outputFile = TFile("TMVA.root", "recreate")
    factory = TMVA.Factory("vbfggf", outputFile,
                           "!V:Transformations=I;N;D")

    # define input variables
    factory.AddVariable("deltaetajj", 'D')
    factory.AddVariable("massjj", 'D')

    # define from which trees data are to be taken
    factory.AddSignalTree(sigTree)
    factory.AddBackgroundTree(bkgTree)

    # remove problematic events and specify how
    # many events are to be used
    # for training and testing
    factory.PrepareTrainingAndTestTree(TCut("njets > 1"),
                                       TCut("njets > 1"),
                                       "nTrain_Signal=1000:"\
                                       "nTest_Signal=2000:"\
                                       "nTrain_Background=1000:"\
                                       "nTest_Background=2000:"\
                                       "!V" )

    # define multivariate methods to be run
    factory.BookMethod( TMVA.Types.kMLP,
                        "MLP",
                        "!H:!V:"\
                        "VarTransform=N:"\
                        "HiddenLayers=10:"\
                        "TrainingMethod=BFGS")

    factory.BookMethod( TMVA.Types.kBDT,
                        "BDT",
                        "!V:"\
                        "BoostType=AdaBoost:"\
                        "NTrees=200:"\
                        "nEventsMin=100:"\
                        "nCuts=50")
  
    factory.TrainAllMethods()  
    factory.TestAllMethods()
    factory.EvaluateAllMethods()
    
    outputFile.Close()
#----------------------------------------------------------------------
try:
    main()
except KeyboardInterrupt:
    print "\nciao"
