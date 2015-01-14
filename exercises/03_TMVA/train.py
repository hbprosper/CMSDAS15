#!/usr/bin/env python
#----------------------------------------------------------------------
# File: train.py
# Description: example of classification with TMVA
# Created: 01-June-2013 INFN SOS 2013, Vietri sul Mare, Italy, HBP
#----------------------------------------------------------------------
import os, sys, re
from ROOT import *
from math import *
from string import *
from time import sleep
from array import array
from histutil import *
#----------------------------------------------------------------------
def getTree(filename):
    hfile = TFile(filename)
    if not hfile.IsOpen():
        print "** can't open file %s" % filename
        sys.exit()
        
    treename = 'HZZ4LeptonsAnalysis'
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
    
    # get signal and background data
    sigFile, sigTree = getTree("sig_gg-H-ZZ-2e2mu_8TeV_126GeV.root")
    bkgFile, bkgTree = getTree("bkg_ZZ-2e2mu_8TeV.root")

    # everything is done via a factory
    outputFile = TFile("TMVAhiggszz.root", "RECREATE")
    factory = TMVA.Factory("higgszz", outputFile,
                           "!V:Transformations=I;N;D")

    # define input variables
    factory.AddVariable("f_Z1mass", 'D')
    factory.AddVariable("f_Z2mass", 'D')

    # define from which trees data are to be taken
    factory.AddSignalTree(sigTree)
    factory.AddBackgroundTree(bkgTree)

    # remove problematic events and specify how
    # many events are to be used
    # for training and testing
    factory.PrepareTrainingAndTestTree(TCut("f_pt4l > 0 &&"\
                                            " f_eta4l > -10"),
                                       TCut("f_pt4l > 0 &&"\
                                            " f_eta4l > -10"),
                                       "nTrain_Signal=2500:"\
                                       "nTest_Signal=2500:"\
                                       "nTrain_Background=2500:"\
                                       "nTest_Background=2500:"\
                                       "!V" )

    # ok, almost done, define multivariate methods to be run
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
