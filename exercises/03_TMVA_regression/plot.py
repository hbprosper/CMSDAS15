#!/usr/bin/env python
#------------------------------------------------------------------------------
# File: plot.py
# Description: plot results of regression with TMVA
# Created: 29 May 2013 INFN SOS 2013, Salerno, Italy, HBP
#   adapted for CMSDAS 2015 Bari
#------------------------------------------------------------------------------
import os, sys
from histutil import *
from time import sleep
from array import array
from ROOT import *
#------------------------------------------------------------------------------

#------------------------------------------------------------------
def main():
    print "\n", "="*80
    print "\tPlot regression results"
    print "="*80

    # ---------------------------------------------------------
    # AddVariable requires the address of the variable, so
    # create the variables in Root and make their addresses
    # known to Python
    # ---------------------------------------------------------
    gROOT.ProcessLine('float x; float* xp = &x;'\
                      'float y; float* yp = &y;')
    from ROOT import xp, yp

    # create a TMVA reader
    reader = TMVA.Reader("!Color:!Silent")
    reader.AddVariable("x", xp)
    reader.AddVariable("y", yp)
    name = "BDT"
    reader.BookMVA('Leila', 'weights/sinxcosy_%s.weights.xml' % name)

    # ---------------------------------------------------------
    # make plots
    # ---------------------------------------------------------
    # set up a standard graphics style
    setStyle()

    c  = TCanvas("fig_regresssion_%s" % name, "", 10, 10, 700, 350)
    # divide canvas canvas along x-axis
    c.Divide(2,1)

    XNBINS= 40
    XMIN  = -2.0
    XMAX  =  2.0

    YNBINS= 40
    YMIN  = -2.0
    YMAX  =  2.0
    h1 = mkhist2("h1", "x", "y", XNBINS, XMIN, XMAX, YNBINS, YMIN, YMAX)
    h2 = mkhist2("h2", "x", "y", XNBINS, XMIN, XMAX, YNBINS, YMIN, YMAX)

    xstep = (XMAX-XMIN)/XNBINS
    ystep = (YMAX-YMIN)/YNBINS

    for i in xrange(XNBINS):

        # x is a Python variable. Be sure
        # to set its twin within Root
        x = XMIN + (i+0.5)*xstep
        gROOT.ProcessLineFast('x = %f' % x)

        for j in xrange(YNBINS):
            y = YMIN + (j+0.5)*ystep
            gROOT.ProcessLineFast('y = %f' % y)

            zexact  = sin(x)*cos(y)
            zapprox = reader.EvaluateRegression('Leila')[0]

            h1.Fill(x, y, zexact)
            h2.Fill(x, y, zapprox)

    c.cd(1)
    h1.Draw("SURF1")
    c.cd(2)
    h2.Draw("SURF1")
    c.Update()
    c.SaveAs(".png")
    c.SaveAs(".pdf")
    sleep(10)
#------------------------------------------------------------------------------
main()
