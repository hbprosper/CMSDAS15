#!/usr/bin/env python
# ---------------------------------------------------------------------
#  File:        plot.py
#  Description: Plot results of Random Grid Search
# ---------------------------------------------------------------------
#  Created:     02-Jun-2013 Harrison B. Prosper
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
# ---------------------------------------------------------------------
def main():
	print "="*80
	print "\t\t=== Plot results of Random Grid Search ==="
	print "="*80

	setStyle()

	# -------------------------------------------------------------
	# Plot Z2mass vs Z1mass
	# -------------------------------------------------------------
	msize = 0.15
	nbins = 25
	
	hb = mkhist2("hb",
                 "m_{Z_{1}} (GeV)",
                 "m_{Z_{2}} (GeV)",
                 nbins, 0, 150,
                 nbins, 0, 150,
                 color=kMagenta+1)
	hb.SetMarkerSize(msize)
	nrows = 4000
	bntuple = Ntuple('../data/root/bkg_ZZ4l_8TeV.root', 'Analysis')
	btotal = 0.0
	for event in bntuple:
		btotal += event.f_weight
		if event < nrows:
			hb.Fill(event.f_Z1mass, event.f_Z2mass, event.f_weight)

	# ------------------------------------------------------------
	hs = mkhist2("hs",
                 "m_{Z_{1}} (GeV)",
                 "m_{Z_{2}} (GeV)",
                 nbins, 0, 150,
                 nbins, 0, 150,
                 color=kCyan+1)
	hs.SetMarkerSize(msize)
	sntuple = Ntuple('../data/root/sig_HZZ4l_8TeV.root', 'Analysis')
	stotal = 0.0
	for event in sntuple:
		stotal += event.f_weight
		if event < nrows:
			hs.Fill(event.f_Z1mass, event.f_Z2mass, event.f_weight)

	print "ZZ yield:    %10.1f events" % btotal
	print "H->ZZ yield: %10.1f events" % stotal
	
	cmass = TCanvas("fig_Z2mass_Z1mass", "Z masses",
                    10, 10, 500, 500)
	hb.DrawNormalized('p')
	hs.DrawNormalized('p same')
	hb.Draw('cont1 same')
	hs.Draw('cont1 same')
	
	# -------------------------------------------------------------
	#  Plot results of RGS
	# -------------------------------------------------------------
	print "\n\t=== RGS"
	ntuple = Ntuple('rgs.root', 'RGS')
	
	# -------------------------------------------------------------
	# create empty histograms
	bmax = 0.1
	smax = 1.0
	color= [kGreen+2, kBlue, kMagenta, kBlack, kRed+1]
	nh = len(color)
	hist = nh*[0]
	
	for i in xrange(nh):
		hname = "hist%d" % i
		hist[i] = mkhist2(hname,
                          "#epsilon_{ZZ #rightarrow 4l}",
                          "#epsilon_{H #rightarrow ZZ #rightarrow 4l}",
                          nbins, 0, bmax,
                          nbins, 0, smax,
                          color=color[i])
        hist[i].SetMinimum(0)
	
	# -------------------------------------------------------------
	#  fill 2D histogram
	# -------------------------------------------------------------
	print "\n\t=== filling RGS histogram..."	
	maxZ =-1
	maxEs=0.0
	maxEb=0.0
	Z1mass0 = Z1mass1 = 0
	Z2mass0 = Z2mass1 = 0
	for row, cut in enumerate(ntuple):
		eb = cut.fraction0   #  background efficiency
		es = cut.fraction1   #  signal efficiency
		
		# Compute a simple measure of significance
		# using the Asimov datum n = s + b
		# first scale counts correctly
		s = es * stotal
		b = eb * btotal
		#print "s = %10.3f\tb = %10.3f" % (s, b)
		
		n = s + b
		psb = TMath.Poisson(n, n)
		pb  = TMath.Poisson(n, b)
		if psb > 0 and pb > 0:
			Z = sqrt(2*log(psb/pb))
		else:
			Z = 0.0
		if Z > maxZ:
			maxZ = Z
			Z1mass0, Z1mass1 = cut.f_Z1mass
			Z2mass0, Z2mass1 = cut.f_Z2mass
			maxEs = es
			maxEb = eb
			maxS  = s
			maxB  = b
			
		#  Plot es vs eb
		if row < nrows:
			index = min(int(Z), 5)
			hist[index].Fill(eb, es)	
	hist[-1].Fill(maxEb, maxEs)
	hist[-1].SetMarkerSize(1.5)
	# -------------------------------------------------------------
	# make final plot
	# -------------------------------------------------------------
	print "\n\t=== plotting RGS histogram..."	
	crgs = TCanvas("fig_rgs", "RGS", 516, 10, 400, 400)
	crgs.cd()
	hist[0].Draw()
	for j in xrange(1, nh): hist[j].Draw("same")
	crgs.Update()
	crgs.SaveAs(".png")
	crgs.SaveAs(".pdf")

	print "max(Z) = %8.1f" % maxZ
	print "%10.1f < m(Z1) < %-10.1f  (GeV)" % (Z1mass0, Z1mass1)
	print "%10.1f < m(Z2) < %-10.1f  (GeV)" % (Z2mass0, Z2mass1)
	print "yields: background = %-10.1f (eff(b) = %6.3f)\n"\
	      "        signal     = %-10.1f (eff(s) = %6.3f)" % (maxB, maxEb,
                                                             maxS, maxEs)

	print "\t=== plot cuts ==="
	x = array('d'); x.append(0); x.append(0)
	y = array('d'); y.append(0); y.append(0)

	cmass.cd()
	x[0] = Z1mass0; x[1] = Z1mass1
	y[0] = Z2mass0; y[1] = Z2mass0
	g1 = TGraph(2, x, y); g1.SetLineWidth(2)
	g1.Draw('l same')
	
	x[0] = Z1mass1; x[1] = Z1mass1
	y[0] = Z2mass0; y[1] = Z2mass1
	g2 = TGraph(2, x, y); g2.SetLineWidth(2)
	g2.Draw('l same')
	
	x[0] = Z1mass1; x[1] = Z1mass0
	y[0] = Z2mass1; y[1] = Z2mass1
	g3 = TGraph(2, x, y); g3.SetLineWidth(2)
	g3.Draw('l same')

	x[0] = Z1mass0; x[1] = Z1mass0
	y[0] = Z2mass1; y[1] = Z2mass0
	g4 = TGraph(2, x, y); g4.SetLineWidth(2)
	g4.Draw('l same')

	cmass.Update()
	cmass.SaveAs('.png')
	cmass.SaveAs('.pdf')
	sleep(10)
# ---------------------------------------------------------------------
main()



