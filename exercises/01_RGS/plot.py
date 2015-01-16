#!/usr/bin/env python
# ---------------------------------------------------------------------
#  File:        plot.py
#  Description: Plot results of Random Grid Search
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
# ---------------------------------------------------------------------
def main():
    print "="*80
    print "\t\t=== Plot results of Random Grid Search ==="
    print "="*80

    setStyle()

    msize = 0.30
    xbins = 50
    xmin  = 0.0
    xmax  =10.0

    ybins = 50
    ymin  = 0.0
    ymax  =5000.0    

    cmass = TCanvas("fig_vbf_ggf", "VBF/ggF",
                    10, 10, 500, 500)    
    
    # -- background

    hb = mkhist2("hb",
                 "#Delta#eta_{jj}",
                 "m_{jj} (GeV)",
                 xbins, xmin, xmax,
                 ybins, ymin, ymax,
                 color=kMagenta+1)
    hb.Sumw2()
    hb.SetMarkerSize(msize)
    bntuple = Ntuple('../data/root/ggf13TeV_test.root', 'Analysis')
    btotal = 0.0
    total = 0
    for ii, event in enumerate(bntuple):
        btotal += event.weight
        total += 1
        hb.Fill(event.deltaetajj, event.massjj, event.weight)
        if total % 100 == 0:
            cmass.cd()
            hb.Draw('p')
            cmass.Update()
    
    # -- signal

    hs = mkhist2("hs",
                 "#Delta#eta_{jj}",
                 "m_{jj} (GeV)",
                 xbins, xmin, xmax,
                 ybins, ymin, ymax,
                 color=kCyan+1)
    hs.Sumw2()
    hs.SetMarkerSize(msize)
    sntuple = Ntuple('../data/root/vbf13TeV_test.root', 'Analysis')
    stotal = 0.0
    total = 0
    for event in sntuple:
        stotal += event.weight
        hs.Fill(event.deltaetajj, event.massjj, event.weight)
        total += 1
        if total % 100 == 0:
            cmass.cd()
            hs.Draw('p')
            cmass.Update()
            
    print "VBF yield: %10.1f events" % stotal
    print "ggF yield: %10.1f events" % btotal

    cmass.cd()
    hs.Draw('p')
    hb.Draw('p same')
    cmass.Update()
    cmass.SaveAs('.png')
    cmass.SaveAs('.pdf')
    
    # -------------------------------------------------------------
    #  Plot results of RGS
    # -------------------------------------------------------------
    print "\n\t=== RGS"
    ntuple = Ntuple('rgs.root', 'RGS')
    print "number of cut-points: ", ntuple.size()
    
    bmax = 0.06
    smax = 0.60
    color= kBlue+1
    hist = mkhist2("hrgs",
                   "#epsilon_{ggF}",
                   "#epsilon_{VBF}",
                   xbins, 0, bmax,
                   ybins, 0, smax,
                   color=color)
    hist.SetMinimum(0)
    
    print "\n\t=== filling RGS histogram..."	
    maxZ =-1
    maxEs=0.0
    maxEb=0.0
    deltaetajj0 = deltaetajj1 = 0
    massjj0 = massjj1 = 0
    for row, cut in enumerate(ntuple):
        eb = cut.fraction0   #  background efficiency
        es = cut.fraction1   #  signal efficiency

        # Compute a naive measure of significance
        # first scale counts correctly
        s = es * stotal
        b = eb * btotal
        if b > 5.0:
            Z = s / sqrt(b)
        else:
            Z = 0.0
            
        if Z > maxZ:
            maxZ = Z
            deltaetajj0, deltaetajj1 = cut.deltaetajj
            massjj0, massjj1 = cut.massjj
            maxEs = es
            maxEb = eb
            maxS  = s
            maxB  = b

        #  Plot es vs eb
        hist.Fill(eb, es)	
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

    print "max(Z) = %8.1f" % maxZ
    print "%10.1f < deta  < %-10.1f  (GeV)" % (deltaetajj0, deltaetajj1)
    print "%10.1f < dmass < %-10.1f  (GeV)" % (massjj0, massjj1)
    print "yields: ggF = %-10.1f (eff(b) = %6.3f)\n"\
          "        VBF = %-10.1f (eff(s) = %6.3f)" % (maxB, maxEb,
                                                      maxS, maxEs)

    print "\t=== plot cuts ==="
    x = array('d'); x.append(0); x.append(0)
    y = array('d'); y.append(0); y.append(0)

    cmass.cd()
    x[0] = deltaetajj0; x[1] = deltaetajj1
    y[0] = massjj0; y[1] = massjj0
    g1 = TGraph(2, x, y); g1.SetLineWidth(2)
    g1.Draw('l same')

    x[0] = deltaetajj1; x[1] = deltaetajj1
    y[0] = massjj0; y[1] = massjj1
    g2 = TGraph(2, x, y); g2.SetLineWidth(2)
    g2.Draw('l same')

    x[0] = deltaetajj1; x[1] = deltaetajj0
    y[0] = massjj1; y[1] = massjj1
    g3 = TGraph(2, x, y); g3.SetLineWidth(2)
    g3.Draw('l same')

    x[0] = deltaetajj0; x[1] = deltaetajj0
    y[0] = massjj1; y[1] = massjj0
    g4 = TGraph(2, x, y); g4.SetLineWidth(2)
    g4.Draw('l same')

    cmass.Update()
    cmass.SaveAs('.png')
    cmass.SaveAs('.pdf')
    sleep(10)
# ---------------------------------------------------------------------
main()



