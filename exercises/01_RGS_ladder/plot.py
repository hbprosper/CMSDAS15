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
from ROOT import *
# ---------------------------------------------------------------------
def error(message):
    print "** %s" % message
    exit(0)

def cutPlot(cutpoint, xmin, xmax, ymin, ymax, color=kBlack):
    x = array('d')
    y = array('d')
    yy, xx = cutpoint
    y.append(ymax); x.append(xx)
    y.append(yy);   x.append(xx)
    y.append(yy);   x.append(xmax)
    poly = TPolyLine(len(x), x, y)
    poly.SetLineWidth(2)
    poly.SetLineColor(color)
    return poly
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
                    10, 10, 500, 500)    
    
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
            cmass.cd()
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
            cmass.cd()
            hs.Draw('p')
            cmass.Update()

    cmass.cd()
    hs.Draw('p')
    hb.Draw('p same')
    cmass.Update()
    
    # -------------------------------------------------------------
    #  Plot results of RGS
    # -------------------------------------------------------------
    print "\n\t=== RGS"
    ntuple = Ntuple('rgs.root', 'RGS')
    print "number of cut-points: ", ntuple.size()
    
    bmax = 1.00
    smax = 1.00
    color= kBlue+1
    hist = mkhist2("hrgs",
                   "#epsilon_{t#bar{t}}",
                   "#epsilon_{T2tt}",
                   xbins, 0, bmax,
                   ybins, 0, smax,
                   color=color)
    hist.SetMinimum(0)
    
    print "\n\t=== filling RGS histogram..."	
    maxZ =-1
    Z =-1
    R2 = None
    MR = None
    cuts = []
    for row, cut in enumerate(ntuple):
        eb = cut.fraction0   #  background efficiency
        es = cut.fraction1   #  signal efficiency
        b  = cut.count0      #  background
        s  = cut.count1      #  signal

        if b > 5:
            Z = s / sqrt(b)
        else:
            Z = 0.0

        # find outer boundary of cut points
        R2 = cut.R2
        MR = cut.MR
        
        allcutpoints = [None]*len(R2)
        for ii in xrange(len(R2)):
            allcutpoints[ii] = (R2[ii], MR[ii])
        allcutpoints.sort()
        
        cutpoint = [allcutpoints[0]]
        for ii in xrange(1, len(allcutpoints)):
            y0, x0 = cutpoint[-1]
            y1, x1 = allcutpoints[ii]
            if x1 < x0:
                cutpoint.append(allcutpoints[ii])
        cuts.append((Z, cutpoint, allcutpoints, eb, es, b, s))
        hist.Fill(eb, es)

    # now plot by cuts
    cuts.sort()
    cuts.reverse()

    cutplot = []
    for ii in range(1):
        Z, cutpoints, allcutpoints, eb, es, b, s = cuts[ii]

        # plot all cut-points for best cuts
        for cutpoint in allcutpoints:
            r2, mr = cutpoint
            cutplot.append(cutPlot(cutpoint,
                                   xmin, xmax, ymin, ymax,
                                   kRed))
            cutplot[-1].Draw('l same')

        # plot outer boundary of cut-points for best cuts
        for cutpoint in cutpoints:
            r2, mr = cutpoint
            print "\tR2 > %10.3f && MR > %10.1f" % (r2, mr)
            cutplot.append(cutPlot(cutpoint,
                                   xmin, xmax, ymin, ymax,
                                   kBlack))
            cutplot[-1].Draw('l same')
         
    cmass.SaveAs('.png')
    cmass.SaveAs('.pdf')
    
    # -------------------------------------------------------------
    # make final plot
    # -------------------------------------------------------------
    print "\n\t=== plotting RGS histogram..."	
    crgs = TCanvas("fig_rgs", "RGS", 516, 10, 500, 500)
    crgs.cd()
    hist.Draw()
    crgs.Update()
    crgs.SaveAs(".png")
    crgs.SaveAs(".pdf")
    sleep(10)
# ---------------------------------------------------------------------
main()



