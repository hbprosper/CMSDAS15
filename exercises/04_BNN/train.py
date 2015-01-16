#!/usr/bin/env python
#----------------------------------------------------------------------
# File: train.py
# Description: example of how to create a BNN using Radford Neal's
#              fbm package
# Created: 15-Jan-2015 CMSDAS Bari 2015  Harrison B. Prosper
#----------------------------------------------------------------------
import os, sys, re
from math import *
from string import *
from histutil import *
from ROOT import *
#----------------------------------------------------------------------
def main():
    print "\n", "="*80
    print "\tBayesian Neural Networks"
    print "="*80

    # write out names of variables to be used in training
    recs = ['deltaetajj\n', 'massjj\n']
    open('vars.txt', 'w').writelines(recs)

    # 1. unweight signal events
    # 2. unweight background events
    # 3. mix signal and background events
    # 4. create training script
    # 5. run training
    
    cmd = '''
    unweight.py %(sig)s sig.dat %(count)d
    unweight.py %(bkg)s bkg.dat %(count)d
    mixsigbkg.py -v vars.txt %(bnn)s
    mktrain.py %(bnn)s

    source %(bnn)s.sh&
    ''' % {'bnn' : 'vbfggf',
           'sig' : '../data/txt/vbf13TeV_train.txt',
           'bkg' : '../data/txt/ggf13TeV_train.txt',
           'count': 1000}
    print cmd
    os.system(cmd)
#----------------------------------------------------------------------
try:
    main()
except KeyboardInterrupt:
    print "\nciao"
