#!/usr/bin/env python
#------------------------------------------------------------------
#- Description: Make plots of BNN training
#  Created: 15-Jan-2015 CMSDAS 2015 Bari Harrison B. Prosper
#------------------------------------------------------------------
import os, sys
from histutil import *
from time import sleep
from array import array
from ROOT import *
#------------------------------------------------------------------
SCOLOR = kCyan+1
BCOLOR = kMagenta+1
FSTYLE = 3001

RCOLOR = kBlue
VARS = '''
deltaetajj
massjj
'''
VARS = split(strip(VARS))
#------------------------------------------------------------------
def readAndFill(filename, treename, bnn, c, h):
    inputs = vector('double')(2)
    ntuple = Ntuple(filename, treename)
    D = []
    # loop over ntuple
    for rownumber, event in enumerate(ntuple):
        inputs[0] = event.deltaetajj
        inputs[1] = event.massjj
        D.append( bnn(inputs) )
        h.Fill(D[-1], event.weight)
        if rownumber % 100 == 0:
            c.cd()
            h.Draw("hist")
            c.Update()
    c.cd()
    h.Draw("hist")
    c.Update()
    return D
#------------------------------------------------------------------
def writeD(outfilename, D):
    # plant tree
    rfile = TFile(outfilename, 'recreate')
    tree  = TTree("Analysis", "analysis")

    # create a struct to write out discriminant
    cmd = 'struct Row { float D; };'
    gROOT.ProcessLine(cmd)

    # make struct known to Python
    from ROOT import Row
    
    # grow branches on the tree
    row = Row()
    tree.Branch("D", AddressOf(row, "D"),'D/F')
    for rownumber, d in enumerate(D):
        row.D = d
        tree.Fill()
        if rownumber % 100 == 0: print rownumber
    rfile.Write()
    rfile.Close()
#------------------------------------------------------------------    
def main():
    setStyle()

    #----------------------------------------------------------
    # compile bnn function
    BNNname= 'vbfggf'
    gROOT.ProcessLine('.L %s.cpp+' % BNNname)        
    bnn = eval(BNNname)
    treename    = "Analysis"
    weightname  = "weight"
    sigfilename = '../data/root/vbf13TeV_test.root'
    bkgfilename = '../data/root/ggf13TeV_test.root'

    # ---------------------------------------------------------
    # plot stuff
    # ---------------------------------------------------------
    postfix = BNNname

    cbnn  = TCanvas("fig_%s" % postfix, BNNname, 10, 10, 500, 500)    
    nbins = 40
    hs = mkhist1("hs", "D_{BNN}", "", nbins, 0, 1)
    hs.Sumw2()
    hs.SetLineWidth(1)
    hs.SetLineColor(SCOLOR)
    hs.SetFillColor(SCOLOR)
    hs.SetFillStyle(FSTYLE)
    hs.GetXaxis().SetNdivisions(505)
    hs.GetYaxis().SetNdivisions(505)
    sD = readAndFill(sigfilename, treename, bnn, cbnn, hs)
    hs.Scale(1.0/hs.Integral())
    
    hb = mkhist1("hb", "D_{BNN}", "", nbins, 0, 1)
    hb.Sumw2()
    hb.SetLineWidth(1)
    hb.SetLineColor(BCOLOR)
    hb.SetFillColor(BCOLOR)
    hb.SetFillStyle(FSTYLE)
    hb.GetXaxis().SetNdivisions(505)
    hb.GetYaxis().SetNdivisions(505)
    bD = readAndFill(bkgfilename, treename, bnn, cbnn, hb)
    hb.Scale(1.0/hb.Integral())
    
    k = int(1.3*max(hb.GetMaximum(), hs.GetMaximum())/0.1)
    ymax = (k+1) * 0.1
    hb.SetMaximum(ymax)
    hs.SetMaximum(ymax)

    cbnn.cd()
    hs.Draw("hist")
    hb.Draw("hist same")
    cbnn.Update()
    sleep(5)
    
    #------------------------------------------------------------------
    # write out discriminants and run RGS on them
    #------------------------------------------------------------------
    print "\n==> run RGS"
    writeD("sig_D.root", sD)
    
    writeD("bkg_D.root", bD)

    # create rgs.vars file
    open('rgs.vars', 'w').write('D >\n')            

    cmd = '''
    runrgs.py sig_D.root bkg_D.root
    '''
    os.system(cmd)
#----------------------------------------------------------------------
try:
    main()
except KeyboardInterrupt:
    print "ciao!"
    
