#!/usr/bin/env python
#------------------------------------------------------------------
#- File: plot.py
#- Description: Make plots
#  Created: 01-Jun-2013 INFN SOS 2013, Vietri sul Mare, Italy, HBP
#------------------------------------------------------------------
import os, sys
from histutil import *
from time import sleep
from array import array
from ROOT import *
#------------------------------------------------------------------
def readAndFill(filename, treename, h):
    # open ntuple (see histutil.py for implementation)
    ntuple = Ntuple(filename, treename)

    # loop over ntuple
    for rownumber, event in enumerate(ntuple):
        h.Fill(event.f_Z1mass, event.f_Z2mass, event.f_weight)
        if rownumber % 5000 == 0:
            print rownumber
    h.Scale(1.0/h.Integral())
#------------------------------------------------------------------
#------------------------------------------------------------------
def main():
    print "="*80

    setStyle()

    XNBINS= 30
    XMIN  =  0
    XMAX  =150

    YNBINS= 30
    YMIN  =  0
    YMAX  =150

    option = 'p'
    msize = 0.15
    nx = 2
    ny = 1
    pixels = 400
    xpos = 0.45
    ypos = 0.85
    tsize= 0.05
    treename = "Analysis"
    sfilename= '../data/root/sig_HZZ4l_8TeV.root'
    bfilename= '../data/root/bkg_ZZ4l_8TeV.root'

    # compile KDE for signal
    gROOT.ProcessLine('.L skde.cpp+')
    sKDE = skde()

    # compile KDE for background
    gROOT.ProcessLine('.L bkde.cpp+')
    bKDE = bkde()
    # ---------------------------------------------------------
    # make 2-D surface plot
    # ---------------------------------------------------------
    # set up a standard graphics style
    setStyle()

    # fill signal histogram
    hsig = mkhist2('hsig', "m_{Z1} (GeV)", "m_{Z2}",
                   XNBINS, XMIN, XMAX,
                   YNBINS, YMIN, YMAX)
    hsig.SetMarkerSize(msize)
    hsig.SetMarkerColor(kCyan+1)
    readAndFill(sfilename, treename, hsig)

    # fill background histogram
    hbkg = mkhist2('hbkg', "m_{Z1} (GeV)", "m_{Z2}",
                   XNBINS, XMIN, XMAX,
                   YNBINS, YMIN, YMAX)
    hbkg.SetMarkerSize(msize)
    hbkg.SetMarkerColor(kMagenta+1)
    readAndFill(bfilename, treename, hbkg)

    # p(x|S)
    hs = mkhist2("hs", "m_{Z1} (GeV)", "m_{Z2}",
                 XNBINS, XMIN, XMAX, YNBINS, YMIN, YMAX)
    hs.SetMinimum(0)

    # p(x|B)
    hb = mkhist2("hb", "m_{Z1} (GeV)", "m_{Z2}",
                 XNBINS, XMIN, XMAX, YNBINS, YMIN, YMAX)
    hb.SetMinimum(0)

    # compute KDE over a grid of points
    point = vector('double')(2)
    xstep = (XMAX-XMIN)/XNBINS
    ystep = (YMAX-YMIN)/YNBINS
    for i in xrange(XNBINS):
        x = XMIN + (i+0.5)*xstep
        point[0] = x
        for j in xrange(YNBINS):
            y  = YMIN + (j+0.5)*ystep
            point[1] = y
            ps = sKDE(point)
            pb = bKDE(point)
            hs.Fill(x, y, ps)
            hb.Fill(x, y, pb)

    # plot surface
    c  = TCanvas("fig_higgszz", "", 10, 10, nx*pixels, ny*pixels)
    # divide canvas canvas along x-axis
    c.Divide(nx, ny)

    c.cd(1)
    hsig.DrawNormalized(option)
    hs.DrawNormalized('cont1 same')
    s1 = Scribe(xpos, ypos, tsize)
    s1.write('pp #rightarrow H #rightarrow ZZ #rightarrow 4l')
    c.Update()

    c.cd(2)
    hbkg.DrawNormalized(option)
    hb.DrawNormalized('cont1 same')
    s2 = Scribe(xpos, ypos, tsize)
    s2.write('pp #rightarrow ZZ #rightarrow 4l')
    c.Update()

    c.SaveAs(".png")
    c.SaveAs(".pdf")
    sleep(10)
#----------------------------------------------------------------------
main()
