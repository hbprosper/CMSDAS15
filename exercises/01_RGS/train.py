#!/usr/bin/env python
# -----------------------------------------------------------------------------
#  File:        train.py
#  Description: Run Random Grid Search to find cuts that best separate H->ZZ-4l
#               signal from ZZ background using box cuts
# -----------------------------------------------------------------------------
#  Created:     02-Jun-2013 Harrison B. Prosper
# -----------------------------------------------------------------------------
import os, sys, re
from string import *
from ROOT import *
# -----------------------------------------------------------------------------
def error(message):
	print "** %s" % message
	exit(0)
# -----------------------------------------------------------------------------

# -------------------------------------------
def efflimits(x):
	x1 = sum(x)/len(x)
	x2 = sum(map(lambda z: z*z, x))/len(x)
	x2 = sqrt(x2-x1*x1)
	xmax = x1 + x2
	k = int(xmax/0.05)
	xmax = k*0.05
	return (0.0, xmax)
# -----------------------------------------------------------------------------
# -----------------------------------------------------------------------------
def main():
	print "="*80
	print "\t\t=== Random Grid Search ==="
	print "="*80
	
	# ---------------------------------------------------------------------
	#  Load RGS class
	# ---------------------------------------------------------------------
	gROOT.ProcessLine(".L RGS.cc+")

	# ---------------------------------------------------------------------
	#  Create RGS object
	# 
	#  Need:
	#   A file of cut-points - usually a signal file, which ideally is
	#   not the same as the signal file on which the RGS algorithm is run.
	# ---------------------------------------------------------------------

	# Check that all files are present
	varFile = "rgs.vars"
	if not os.path.exists(varFile):
		error("unable to open variables file %s" % varFile)
		
	sigFile = "../data/root/sig_HZZ4l_8TeV.root"
	if not os.path.exists(sigFile):
		error("unable to open signal file %s" % sigFile)

	bkgFile = "../data/root/bkg_ZZ4l_8TeV.root"
	if not os.path.exists(bkgFile):
		error("unable to open background file %s" % bkgFile)

	treeName = "Analysis"
	# ---------------------------------------------------------------------
	
	print "\t==> create RGS object"
	cutsFile = sigFile
	start = 0    
	maxcuts = 5000 #  maximum number of cut-points to consider

	rgs = RGS(cutsFile, start, maxcuts, treeName)
	
	# ---------------------------------------------------------------------
	#  Add signal and background data to RGS object
	#  Weight each event using the value in the field "f_weight", if it exists.
	#  NB: We asssume all files are of the same format
	# ---------------------------------------------------------------------
	numrows = 0 #  Load all the data from the files
	
	print "\t==> load background data"
	rgs.add(bkgFile, start, numrows, "f_weight")
	print
	
	print "\t==> load signal data"
	rgs.add(sigFile, start, numrows, "f_weight")
	print
	
	#  Run algorithm
	rgs.run(varFile)

	#  Save results to a root file
	rfile = rgs.save("rgs.root")
# -----------------------------------------------------------------------------
try:
	main()
except KeyboardInterrupt:
	print "\tciao!\n"
	


