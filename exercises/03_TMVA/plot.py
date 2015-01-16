#!/usr/bin/env python
#------------------------------------------------------------------
#- File: plot.py
#- Description: plot results of training with TMVA
#  Created: 01-Jun-2013 INFN SOS 2013, Vietri sul Mare, Italy, HBP
#    adapt to CMSDAS 2015 Bari HBP
#------------------------------------------------------------------
import os, sys
from histutil import *
from time import sleep
from array import array
from ROOT import *
#------------------------------------------------------------------
def readAndFill(filename, treename, h):
    print "==> reading %s" % filename
    # open ntuple (see histutil.py for implementation)
    ntuple = Ntuple(filename, treename)
    # loop over ntuple
    for rownumber, event in enumerate(ntuple):
        h.Fill(event.deltaetajj, event.massjj, event.weight)
        if rownumber % 500 == 0:
            print rownumber
    h.Scale(1.0/h.Integral())
#------------------------------------------------------------------
def readAndFillAgain(filename, treename, reader, which, c, h):
    ntuple = Ntuple(filename, treename)
    # loop over ntuple
    for rownumber, event in enumerate(ntuple):
        # tell Root values of variables
        gROOT.ProcessLineFast('x = %f' % event.deltaetajj)
        gROOT.ProcessLineFast('y = %f' % event.massjj)

        # evaluate discriminant
        D = reader.EvaluateMVA(which)
        h.Fill(D, event.weight)

        if rownumber % 100 == 0:
            c.cd()
            h.Draw()
            c.Update()
    h.Scale(1.0/h.Integral())
#------------------------------------------------------------------
def main():
    print "="*80
    # set up a standard graphics style	
    setStyle()

    xbins = 40
    xmin  =  0.0
    xmax  =  8.0

    ybins = 40
    ymin  =  0.0
    ymax  =2000.0

    fieldx = 'deltaetajj'; varx = '#Delta#eta_{jj}'
    fieldy = 'massjj';     vary = 'm_{jj}'

    msize= 0.15
    treename    = "Analysis"
    weightname  = "weight"
    sigfilename = '../data/root/vbf13TeV_test.root'
    bkgfilename = '../data/root/ggf13TeV_test.root'

    # pick discriminant

    which = 'MLP'

    # ---------------------------------------------------------
    # make 2-D surface plot
    # ---------------------------------------------------------

    c  = TCanvas("fig_vbfggf_%s" % which, "", 10, 10, 500, 500)
    # divide canvas canvas along x-axis
    c.Divide(2, 2)

    # Fill signal histogram
    hsig = mkhist2('hsig', varx, vary,
                   xbins, xmin, xmax,
                   ybins, ymin, ymax)
    hsig.SetMarkerSize(msize)
    hsig.SetMarkerColor(kCyan+1)        
    readAndFill(sigfilename, treename, hsig)

    # Fill background histogram
    hbkg = mkhist2('hbkg', varx, vary,
                   xbins, xmin, xmax,
                   ybins, ymin, ymax)
    hbkg.SetMarkerSize(msize)
    hbkg.SetMarkerColor(kMagenta+1)        
    readAndFill(bkgfilename, treename, hbkg)

    # make some plots

    xpos = 0.30
    ypos = 0.85
    tsize= 0.05

    # --- signal

    c.cd(1)
    hsig.SetMinimum(0)
    hsig.Draw('p')
    s1 = Scribe(xpos, ypos, tsize)
    s1.write('VBF #rightarrow H #rightarrow ZZ #rightarrow 4l')
    c.Update()

    # --- background

    c.cd(2)
    hbkg.Draw('p')
    s2 = Scribe(xpos, ypos, tsize)
    s2.write('ggF #rightarrow H #rightarrow ZZ #rightarrow 4l')
    c.Update()        

    # --- p(S|x) = p(x|S) / [p(x|S) + p(x|B)]

    hD = hsig.Clone('hD')
    hSum = hsig.Clone('hSum')
    hSum.Add(hbkg)
    hD.Divide(hSum)
    hD.SetMinimum(0)
    hD.SetMaximum(1)

    c.cd(3)
    hD.Draw('cont1')
    s3 = Scribe(xpos, ypos, tsize)
    s3.write('D(%s, %s) (actual)' % (varx, vary))
    c.Update()

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
    reader.AddVariable(fieldx, xp)
    reader.AddVariable(fieldy, yp)
    reader.BookMVA(which, 'weights/vbfggf_%s.weights.xml' % which)

    h1 = mkhist2("h1", varx, vary,
                 xbins, xmin, xmax,
                 ybins, ymin, ymax)                 
    h1.SetMinimum(0)

    # compute discriminant at a grid of points

    xstep = (xmax-xmin)/xbins
    ystep = (ymax-ymin)/ybins
    for i in xrange(xbins):
        # x is a Python variable. Be sure
        # to set its doppelganger within Root
        x = xmin + (i+0.5)*xstep
        gROOT.ProcessLineFast('x = %f' % x)

        for j in xrange(ybins):
            y = ymin + (j+0.5)*ystep
            gROOT.ProcessLineFast('y = %f' % y)

            D = reader.EvaluateMVA(which)
            h1.Fill(x, y, D)

    # plot MVA approximation to discriminant
    c.cd(4)
    h1.Draw('cont1')
    s4 = Scribe(xpos, ypos, tsize)
    s4.write('D(%s, %s) (%s)' % (varx, vary, which))
    c.Update()

    c.SaveAs(".png")
    c.SaveAs(".pdf")

    # ---------------------------------------------------------
    # plot distributions of D
    # ---------------------------------------------------------
    c1  = TCanvas("fig_zbfggf_D_%s" % which, "",
                  510, 310, 500, 500)

    xm = 0
    if which == "BDT": xm = -1.0
        
    hs = mkhist1("hs", "D(%s, %s)" % (varx, vary), "", 50, xm, 1)
    hs.SetFillColor(kCyan+1)
    hs.SetFillStyle(3001)
    readAndFillAgain(sigfilename, treename, reader, which, c1, hs)

    sleep(2)

    hb = mkhist1("hb", "D(%s, %s)" % (varx, vary), "", 50, xm, 1)
    hb.SetFillColor(kMagenta+1)
    hb.SetFillStyle(3001)
    readAndFillAgain(bkgfilename, treename, reader, which, c1, hb)

    c1.cd()
    hb.Draw()
    hs.Draw("same")
    c1.Update()
    c1.SaveAs(".png")
    c1.SaveAs(".pdf")

    sleep(10)
#----------------------------------------------------------------------
main()
