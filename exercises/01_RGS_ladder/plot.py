#!/usr/bin/env python
# ---------------------------------------------------------------------
#  File:        plot.py
#  Description: solution to TTJets/T2tt RGS problem
#               CMSDAS 2015 Bari, Italy
# ---------------------------------------------------------------------
#  Created:     10-Jan-2015 Harrison B. Prosper
# ---------------------------------------------------------------------
import os, sys, re
from string import *
from histutil import *
from time import sleep
from array import array
from solution import LadderPlot
from ROOT import *
# ---------------------------------------------------------------------
def error(message):
    print "** %s" % message
    exit(0)
# ---------------------------------------------------------------------
def main():
    print "="*80
    print "\t\t=== Plot results of Random Grid Search ==="
    print "="*80

    setStyle()

    msize = 0.30
    xbins = 40
    xmin  = 0.0
    xmax  =4000.0

    ybins = 40
    ymin  = 0.0
    ymax  = 1.0    

    cmass = TCanvas("fig_T2tt_TTJets", "",
                    10, 10, 700, 350)    
    # divide canvas canvas along x-axis
    cmass.Divide(2,1)
    
    # -- background

    hb = mkhist2("hb",
                 "M_{R} (GeV)",
                 "R^{2}",
                 xbins, xmin, xmax,
                 ybins, ymin, ymax,
                 color=kMagenta+1)
    hb.Sumw2()
    hb.SetMarkerSize(msize)
    bntuple = Ntuple('../data/root/TTJets.root', 'Analysis')
    for ii, event in enumerate(bntuple):
        hb.Fill(event.MR, event.R2)
        if ii % 100 == 0:
            cmass.cd(2)
            hb.Draw('p')
            cmass.Update()
    
    # -- signal

    hs = mkhist2("hs",
                 "M_{R} (GeV)",
                 "R^{2}",
                 xbins, xmin, xmax,
                 ybins, ymin, ymax,
                 color=kCyan+1)
    hs.Sumw2()
    hs.SetMarkerSize(msize)
    sntuple = Ntuple('../data/root/T2tt_mStop_850_mLSP_100.root',
                     'Analysis')
    for ii, event in enumerate(sntuple):
        hs.Fill(event.MR, event.R2)        
        if ii % 100 == 0:
            cmass.cd(2)
            hs.Draw('p')
            cmass.Update()

    # compute D = p(x|S)/[p(x|S)+p(x|B)]
    hD = hs.Clone('hD'); hD.Scale(1.0/hD.Integral())
    hB = hb.Clone('hB'); hB.Scale(1.0/hB.Integral())
    
    hSum = hD.Clone('hSum')
    hSum.Add(hB)
    hD.Divide(hSum)

    cmass.cd(1)
    hD.Draw('cont')
    
    cmass.cd(2)
    hs.Draw('p')
    hb.Draw('p same')
    cmass.Update()
    
    # -------------------------------------------------------------
    #  Plot results of RGS
    # -------------------------------------------------------------
    print "\n\t=== RGS"
    ntuple = Ntuple('rgs.root', 'RGS')
    print "number of cut-points: ", ntuple.size()
    
    bmax = 0.30
    smax = 1.00
    color= kBlue+1
    hist = mkhist2("hrgs",
                   "#epsilon_{t#bar{t}}",
                   "#epsilon_{T2tt}",
                   xbins, 0.0, 0.30,
                   ybins, 0.5, 1.00,
                   color=color)
    hist.SetMinimum(0)
    
    print "\n\t=== best ladder cut"	
    maxZ =-1
    Z  =-1
    # a creator of a ladder cut plot
    ladderPlot = LadderPlot(xmin, xmax, ymin, ymax)

    for row, cut in enumerate(ntuple):
        eb = cut.fraction0   #  background efficiency
        es = cut.fraction1   #  signal efficiency
        hist.Fill(eb, es)

        # compute measure of significance
        # Z  = sign(LR) * sqrt(2*|LR|)
        # where LR = log(Poisson(s+b|s+b)/Poisson(s+b|b))
        #
        b  = cut.count0      #  background
        s  = cut.count1      #  signal
        if b > 5:
            Z = 2*(s - (s+b)*log((s+b)/b))
            if Z > 0:
                Z = sqrt(Z)
            else:
                Z =-sqrt(-Z)
        else:
            Z = 0.0

        # add ladder cut to ladder plot
        R2 = cut.R2
        MR = cut.MR
        ladderPlot.add(Z, R2, MR)
    
    cmass.cd(2)
    ladderPlot.draw()
    cmass.Update()
    cmass.SaveAs('.png')
    cmass.SaveAs('.pdf')

    # -------------------------------------------------------------
    # roc plot
    # -------------------------------------------------------------
    print "\n\t=== ROC plot"	
    crgs = TCanvas("fig_rgs", "RGS", 516, 10, 500, 500)
    crgs.cd()
    hist.Draw()
    crgs.Update()
    crgs.SaveAs(".png")
    crgs.SaveAs(".pdf")    
    sleep(10)
# ---------------------------------------------------------------------
main()



