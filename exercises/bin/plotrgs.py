#!/usr/bin/env python
# ---------------------------------------------------------------------
#  File:        plotrgs.py
#  Description: Plot results of Random Grid Search
#  CMSDAS 2015 Bari HBP
# ---------------------------------------------------------------------
import os, sys, re, optparse
from string import *
from histutil import *
from time import sleep
from array import array
from ROOT import *
# ---------------------------------------------------------------------
def error(message):
    print "** %s" % message
    exit(0)

def nameonly(s):
    import posixpath
    return posixpath.splitext(posixpath.split(s)[1])[0]

def decodeCommandLine():
    VERSION = 'v1.0.0'
    USAGE = '''
    plotrgs.py RGS-filename
    '''

    parser = optparse.OptionParser(usage=USAGE, version=VERSION)
    options, args = parser.parse_args()
    if len(args) < 1:
        print USAGE
        sys.exit(0)

    rgsfile = args[0]
    return rgsfile
# -----------------------------------------------------------------------------
def main():
	print "==> plot results of Random Grid Search"

    rgsfile = decodeCommandLine()

    # Check that file is present
    if not os.path.exists(rgsfile):
        error("unable to open signal file %s" % rgsfile)

	setStyle()

    # open RGS ntuple
	ntuple = Ntuple(rgsfile, 'RGS')
	# -------------------------------------------------------------
	#  fill 2D histogram
	# -------------------------------------------------------------
	print "==> filling RGS histogram..."
	bmax = 0.1
	smax = 1.0
    
	color= kMagenta+1
    hname = "hrgs"
    hist[i] = mkhist2(hname,
                          "#epsilon_{B}",
                          "#epsilon_{S}",
                          nbins, 0, bmax,
                          nbins, 0, smax,
                          color=color[i])
        hist[i].SetMinimum(0)
	    	
	maxZ =-1
	maxEs=0.0
	maxEb=0.0
	for row, cut in enumerate(ntuple):
		eb = cut.fraction0   #  background efficiency
		es = cut.fraction1   #  signal efficiency
		s  = cut.count0
        b  = cut.count1
		# Compute a simple measure of significance
        n  = s + b
        psb= TMath.Poisson(n, n)
        pb = TMath.Poisson)n, b)
        y  = 2*log(psb/pb)
		if psb > 0 and pb > 0:
            y = 2*log(psb/pb)
            ay= abs(y)
			Z = y/sqrt(y)/ay
		else:
			Z = 0.0
		if Z > maxZ:
			maxZ = Z
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

	sleep(10)
# ---------------------------------------------------------------------
main()



