#!/usr/bin/env python
#------------------------------------------------------------------------------
# File: train.py
# Description: example of regression with TMVA
# Created: 29 May 2013 INFN SOS 2013, Salerno, Italy, HBP
#   adapted for CMSDAS 2015 Bari
#------------------------------------------------------------------------------
import os, sys, re
from math import *
from string import *
from time import sleep
from array import array
from histutil import *
from ROOT import *
#------------------------------------------------------------------------------
def main():
    print "\n", "="*80
    print "\tregression with TMVA"
    print "="*80
    
    outputFile = TFile("TMVA.root", "recreate")
  
    factory = TMVA.Factory("sinxcosy",
                           outputFile,
                           "!V:Transformations=I,N:"\
                           "AnalysisType=Regression");

    inputFile = TFile("../data/root/sinxcosy.root");
  
    factory.AddVariable("x", 'D')
    factory.AddVariable("y", 'D')
    
    factory.AddTarget("z", 'D')
  
    factory.AddRegressionTree (inputFile.Get("Analysis"))

    factory.PrepareTrainingAndTestTree(TCut(""),
                                       "nTrain_Regression=2000:"\
                                       "nTest_Regression=2000:"\
                                       "SplitMode=Random:"\
                                       "NormMode=None:"\
                                       "!V" )
    
    factory.BookMethod( TMVA.Types.kMLP,
                        "MLP",
                        "!H:!V:"\
                        "VarTransform=N:"\
                        "HiddenLayers=10:"\
                        "TrainingMethod=BFGS:")

    factory.BookMethod( TMVA.Types.kBDT,
                        "BDT",
                        "!V:BoostType=Grad:"\
                        "nCuts=20:"\
                        "NTrees=100:"\
                        "NNodesMax=5" )
  
    factory.TrainAllMethods()  
    factory.TestAllMethods()
    factory.EvaluateAllMethods()
    
    outputFile.Close()
#------------------------------------------------------------------------------
try:
    main()
except KeyboardInterrupt:
    print "\nciao"
