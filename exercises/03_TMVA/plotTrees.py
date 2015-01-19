#!/usr/bin/env python
#------------------------------------------------------------------------------
# File: plotTrees.py
# Description: example of classification with TMVA
# Created: 31-May-2013 INFN SOS 2013, Salerno, Italy, HBP
#  adapt to CMSDAS 2015, Bari, Italy
#------------------------------------------------------------------------------
import os, sys
from math import *
from string import *
from time import sleep
from array import array
from histutil import *
from ROOT import *
#------------------------------------------------------------------------------
def main():
    print "="*80
    Cfilename = 'weights/vbfggf_BDT.class.C'
    treename  = 'Analysis'

    # create a Python equivalent of the TMVA BDT class from
    # the TMVA macro
    bdt = BDT(Cfilename)

    setStyle()
    
    xmin   = 0.0
    ymin   = 0.0
    xmax   = 8.0
    ymax   = 2000.0

    # draw individual trees
    pixels = 150
    nx = 5
    ny = 5
    nn = nx*ny
    c = TCanvas('fig_%dtrees' % nn, 'trees', 10, 10, nx*pixels, ny*pixels)
    c.Divide(nx, ny)
    hist = []
    line = []
    for ii in xrange(nx*ny):
        print
        h = bdt.plot(ii, 'h%2.2d' % ii,
                     '#Delta#eta_{jj}',
                     'm_{jj} (GeV)',
                     xmin, xmax, ymin, ymax)
        graphs = bdt.lines()
        
        hist.append( h )
        line.append( graphs )
        
        c.cd(ii+1)
        h.Draw('col')
        for g in line[-1]:
            g.Draw('l same')
        c.Update()

    c.SaveAs(".pdf")
    c.SaveAs(".png")
    
    # draw 2D plot with increasing numbers of trees
    c1 = TCanvas('fig_forest', 'trees', 820, 10, 600, 600)
    c1.Divide(2,2)
    nx = 50
    ny = 50
    xstep = (xmax-xmin) / nx
    ystep = (ymax-ymin) / ny
    ntrees = [25, 50, 100, 200]

    hh = []
    firstTree = 0
    for ii in xrange(len(ntrees)):
        hname = "h%4.4d" % ntrees[ii]
        lastTree = ntrees[ii]-1
        hh.append(mkhist2(hname,
                          '#Delta#eta_{jj}',
                          'm_{jj} (GeV)',
                          nx, xmin, xmax, ny, ymin, ymax))
        for ix in xrange(nx):
            x = xmin + ix * xstep
            for iy in xrange(ny):
                y = ymin + iy * ystep
                vtuple = (x, y)
                z = bdt(vtuple, firstTree, lastTree)
                hh[-1].SetBinContent(ix+1, iy+1, z);
        c1.cd(ii+1)
        hh[-1].Draw('col')
        addTitle('%5d trees' % ntrees[ii], 0.06)
        c1.Update()
    c1.SaveAs(".pdf")
    c1.SaveAs('.png')
    sleep(5)
    
    ## os.system('rm -rf fig_manytrees.gif')
    ## c1 = TCanvas('fig_manytrees', 'many trees', 610, 310, 2*pixels, 2*pixels)

    ## option = 'col'
    ## for ii in xrange(100):
    ##     print ii
    ##     h.append(bdt.plot(ii, 'hmtree', 'm_{Z_{1}} (GeV)', 'm_{Z_{2}} (GeV)', 0, xmax, 0, ymax))
    ##     h[-1].Draw('col')
    ##     c1.Update()
    ##     c1.Print('fig_manytrees.gif+10')
#------------------------------------------------------------------------------
try:
    main()
except KeyboardInterrupt:
    print "\nciao"
