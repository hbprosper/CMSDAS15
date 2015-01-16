#!/usr/bin/env python
#------------------------------------------------------------------
#- File: plot.py
#- Description: Make plots
#  Created: 01-Jun-2013 INFN SOS 2013, Vietri sul Mare, Italy, HBP
#    adapted for CMSDAS 2015 Bari
#------------------------------------------------------------------
import os, sys
from histutil import *
from time import sleep
from array import array
from ROOT import *
#------------------------------------------------------------------
def readAndFill(filename, treename, canvas, h):
    # open ntuple (see histutil.py for implementation)
    ntuple = Ntuple(filename, treename)
    # loop over ntuple
    for rownumber, event in enumerate(ntuple):
        h.Fill(event.deltaetajj, event.massjj, event.weight)
        if rownumber % 100 == 0:
            canvas.cd()
            h.Draw('p')
            canvas.Update()
            print rownumber        
    #h.Scale(1.0/h.Integral())
    canvas.cd()
    h.Draw('p')
    canvas.Update()    
#------------------------------------------------------------------
def plotHists(name, filename, kde, stuff, color=kCyan+1):
    treename = stuff.treename
    
    varx   = stuff.varx
    fieldx = stuff.fieldx
    xbins  = stuff.xbins
    xmin   = stuff.xmin
    xmax   = stuff.xmax
    
    vary   = stuff.vary
    fieldy = stuff.fieldy    
    ybins  = stuff.ybins
    ymin   = stuff.ymin
    ymax   = stuff.ymax
    
    msize  = stuff.msize
       
    # set up a standard graphics style
    setStyle()
    c2 = TCanvas("fig_kde2D_%s" % name, "", 10, 10, 500, 500)

    h2 = mkhist2('h%s' % name, varx, vary,
                 xbins, xmin, xmax,
                 ybins, ymin, ymax)
    h2.SetMarkerSize(msize)
    h2.SetMarkerColor(color)
    h2.SetLineColor(color)
    h2.Sumw2()
    readAndFill(filename, treename, c2, h2)

    k2 = mkhist2("hkde%s" % name, varx, vary,
                 xbins, xmin, xmax, ybins, ymin, ymax)
    k2.SetMinimum(0)
    
    # compute KDE over a grid of points
    point = vector('double')(2)
    xstep = (xmax-xmin)/xbins
    ystep = (ymax-ymin)/ybins
    for i in xrange(xbins):
        x = xmin + (i+0.5)*xstep
        point[0] = x
        for j in xrange(ybins):
            y  = ymin + (j+0.5)*ystep
            point[1] = y
            ps = kde(point)
            k2.Fill(x, y, ps)
    #k2.Scale(1.0/k2.Integral())
    
    c2.cd(1)
    h2.Draw('p')
    h2.Draw('cont3 same')
    k2.Draw('cont1 same')
    c2.Update()
    c2.SaveAs('.png')
    c2.SaveAs('.pdf')
    return (c2, h2, k2)
#------------------------------------------------------------------
def writeD(outfilename, filename, treename, skde, bkde):
    # some PyROOT tricks:
    
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
      
    point = vector('double')(2)
    ntuple = Ntuple(filename, treename)
       
    for rownumber, event in enumerate(ntuple):
        point[0] = event.deltaetajj
        point[1] = event.massjj
        s = skde(point)
        b = bkde(point)
        d = s + b
        if d > 0:
            row.D = s / d
        else:
            row.D = 0.0
        tree.Fill()
        if rownumber % 100 == 0: print rownumber
    rfile.Write()
    rfile.Close()
#------------------------------------------------------------------
def main():
    setStyle()

    xbins = 40
    xmin  =  0.0
    xmax  =  8.0

    ybins = 40
    ymin  =  0.0
    ymax  =2000.0

    fieldx = 'deltaetajj'; varx = '#Delta#eta_{jj}'
    fieldy = 'massjj';     vary = 'm_{jj} (GeV)'

    msize= 0.15
    treename    = "Analysis"
    weightname  = "weight"
    sigfilename = '../data/root/vbf13TeV_test.root'
    bkgfilename = '../data/root/ggf13TeV_test.root'

    class Bucket():
        pass
    stuff = Bucket()
    stuff.treename = treename
    stuff.varx   = varx
    stuff.fieldx = fieldx
    stuff.vary   = vary
    stuff.fieldy = fieldy
    stuff.xbins  = xbins
    stuff.xmin   = xmin
    stuff.xmax   = xmax
    stuff.ybins  = ybins
    stuff.ymin   = ymin
    stuff.ymax   = ymax
    stuff.msize  = msize
       
    # compile KDE for signal
    gROOT.ProcessLine('.L skde.cpp+')
    sKDE = skde()    
    sig  = plotHists('sig', sigfilename, sKDE, stuff, kCyan+1)
    sleep(5)

    # compile KDE for background
    gROOT.ProcessLine('.L bkde.cpp+')
    bKDE = bkde() 
    bkg  = plotHists('bkg', bkgfilename, bKDE, stuff, kMagenta+1)
    sleep(5)
        
    #------------------------------------------------------------------
    # write out discriminants and run RGS on them
    #------------------------------------------------------------------
    print "\n==> run RGS"
    writeD("sig_D.root", sigfilename, treename, sKDE, bKDE)
    
    writeD("bkg_D.root", bkgfilename, treename, sKDE, bKDE)
    cmd = '''
    runrgs.py sig_D.root bkg_D.root
    '''
    os.system(cmd)
#----------------------------------------------------------------------
main()
