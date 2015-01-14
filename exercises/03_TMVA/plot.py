#!/usr/bin/env python
#------------------------------------------------------------------
#- File: plot.py
#- Description: Make plots
#  Created: 01-Jun-2013 INFN SOS 2013, Vietri sul Mare, Italy, HBP
#------------------------------------------------------------------
import os, sys
from ROOT import *
from histutil import *
from time import sleep
from array import array
#------------------------------------------------------------------
def readAndFill(filename, treename, h):
    # open ntuple (see histutil.py for implementation)
    ntuple = Ntuple(filename, treename)
    
    # loop over ntuple
    count = 0
    for rownumber, event in enumerate(ntuple):
        if event.f_pt4l < 0: continue
        count += 1
        h.Fill(event.f_Z1mass, event.f_Z2mass, event.f_weight)
        if count % 5000 == 0:
		print count
    h.Scale(1.0/h.Integral())
#------------------------------------------------------------------
def readAndFillAgain(filename, treename, reader, which, c, h):

    ntuple = Ntuple(filename, treename)
    # loop over ntuple
    count = 0
    for rownumber, event in enumerate(ntuple):
        if event.f_pt4l < 0: continue
        count += 1
        
        gROOT.ProcessLineFast('x = %f' % event.f_Z1mass)
        gROOT.ProcessLineFast('y = %f' % event.f_Z2mass)
            
        D = reader.EvaluateMVA(which)
        h.Fill(D, event.f_weight)

        if count % 5000 == 0:
            c.cd()
            h.Draw()
            c.Update()
                
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

	# ---------------------------------------------------------
	# make 2-D surface plot
	# ---------------------------------------------------------
	# set up a standard graphics style
	setStyle()
        option = 'p'
        msize = 0.15
        nx = 2
        ny = 2
        pixels = 250
        which = 'BDT'
	c  = TCanvas("fig_higgszz_%s" % which, "",
                     10, 10, nx*pixels, ny*pixels)
	# divide canvas canvas along x-axis
	c.Divide(nx, ny)
        
        treename = "HZZ4LeptonsAnalysis"

	# Fill signal histogram
	sfilename = 'sig_gg-H-ZZ-2e2mu_8TeV_126GeV.root'
	hsig = mkhist2('hsig', "m_{Z1} (GeV)", "m_{Z2} (GeV)",
                       XNBINS, XMIN, XMAX,
                       YNBINS, YMIN, YMAX)
        hsig.SetMarkerSize(msize)
        hsig.SetMarkerColor(kCyan+1)        
	readAndFill(sfilename, treename, hsig)

	# Fill background histogram
        bfilename = 'bkg_ZZ-2e2mu_8TeV.root'
	hbkg = mkhist2('hbkg', "m_{Z1} (GeV)", "m_{Z2}",
                       XNBINS, XMIN, XMAX,
                       YNBINS, YMIN, YMAX)
        hbkg.SetMarkerSize(msize)
        hbkg.SetMarkerColor(kMagenta+1)        
	readAndFill(bfilename, treename, hbkg)
		
        # plot surface
	c.cd(1)

	hsig.SetMinimum(0)
        hsig.Draw(option)

        xpos = 0.45
        ypos = 0.85
        tsize= 0.05
        s1 = Scribe(xpos, ypos, tsize)
        s1.write('pp #rightarrow H #rightarrow ZZ #rightarrow 4l')
        c.Update()

        c.cd(2)
        hbkg.Draw(option)
        s2 = Scribe(xpos, ypos, tsize)
        s2.write('pp #rightarrow ZZ #rightarrow 4l')
        c.Update()        

        hD = hsig.Clone('hD')
        hSum = hsig.Clone('hSum')
	hSum.Add(hbkg)
	hD.Divide(hSum)
	hD.SetMinimum(0)
	hD.SetMaximum(1)

        c.cd(3)
	hD.Draw('cont1')
        s3 = Scribe(xpos, ypos, tsize)
        s3.write('D(m_{Z_{1}}, m_{Z_{2}}) (actual)')
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
	reader.AddVariable("f_Z1mass", xp)
	reader.AddVariable("f_Z2mass", yp)
	reader.BookMVA(which, 'weights/higgszz_%s.weights.xml' % which)
        
	h1 = mkhist2("h1", "m_{Z1} (GeV)", "m_{Z2}",
		     XNBINS, XMIN, XMAX, YNBINS, YMIN, YMAX)
	h1.SetMinimum(0)
	
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
			
			D = reader.EvaluateMVA(which)
			h1.Fill(x, y, D)

        c.cd(4)
        h1.Draw('cont1')
        s4 = Scribe(xpos, ypos, tsize)
        s4.write('D(m_{Z_{1}}, m_{Z_{2}}) (%s)' % which)
        c.Update()
        
	c.SaveAs(".gif")
	c.SaveAs(".pdf")
        
	# ---------------------------------------------------------
        # plot distributions of D
        # ---------------------------------------------------------
	c1  = TCanvas("fig_higgszz_D_%s" % which, "",
                      510, 310, 500, 500)
        
	hs = mkhist1("hs", "D(m_{Z1}, m_{Z2})", "", 50, 0, 1)
        hs.SetFillColor(kBlue)
        hs.SetFillStyle(3001)
        readAndFillAgain(sfilename, treename, reader, which, c1, hs)

        sleep(1)

	hb = mkhist1("hb", "D(m_{Z1}, m_{Z2})", "", 50, 0, 1)
        hb.SetFillColor(kRed)
        hb.SetFillStyle(3001)
        readAndFillAgain(bfilename, treename, reader, which, c1, hb)

        c1.cd()
        hb.Draw()
        hs.Draw("same")
        c1.Update()
        c1.SaveAs(".gif")
        c1.SaveAs(".pdf")
        #gApplication.Run()
        sleep(10)
#----------------------------------------------------------------------
main()
