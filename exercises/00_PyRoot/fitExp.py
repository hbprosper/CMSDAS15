#!/usr/bin/env python
#-------------------------------------------------------------
# File: fitExp.py
# Description: RooFit solution to Glen Cowan's exercise
# Created: 4 June 2013 Harrison B. Prosper
#          INFN SOS 2013, Vietri sul Mare, Italy
#
# Python notes
# ------------
# 1. First line of file tells the OS the program to use to interpret
#    the instructions that follow. Make this script executable
#    with
#          chmod +x expFit.py
#
#    and execute it using
#
#          ./expFit.py
#
# 2. Python uses indentation to create program blocks.
#    Semicolons are not needed
#
# 3. Python handles pointers for you! Use "." as in
#           TMath.Prob
#
# 4. Two basic ways to load program modules into memory, e.g.:
#          import os
#    and
#          from string import replace
#
# 5. Strings can be either '...' or "...". Useful when ".." needs
#    to be embedded within a string. Use "\" to continue strings onto
#    a new line
#
# 6. Warning: Python uses dynamic typing, which means that the type of
#    a variable is detemined at run-time by its value. Consequently,
#    a variable's type is, well, variable!
#
#    x = 0     this is an integer
#    x = 0.0   this is a real
#    x ='0'    this is a string
#
#    Therefore, beware of
#
#    x = 42
#    y = x / 84
#
#    The answer will be y = 0 because x is an integer!
#
#-------------------------------------------------------------
import os,sys
from time import sleep
from ROOT import *
#-------------------------------------------------------------
def main():

	# suppress all messages except those that matter
	msgservice = RooMsgService.instance()
	msgservice.setGlobalKillBelow(RooFit.FATAL)

	# make a workspace so that we can use its factory
	wspace = RooWorkspace('Glen Cowan')

	#-----------------------------------------------------
	# create double-exponential model
	#-----------------------------------------------------
	# observable: x
	xmin = 0.0
	xmax =20.0
	wspace.factory('x[0,%f,%f]' % (xmin, xmax))
	wspace.var('x').setBins(20)

	# parameters: alpha, xi1, xi2
	wspace.factory('alpha[0.2,0,0.5]')
	wspace.factory('xi1[1,0.01, 5]')
	wspace.factory('xi2[5,0.01,10]')

	# pdf: p(x|alpha, xi1, xi2)
	# use {..} to specify a RooArgList
	# note use of "\" continuation markers
	# Syntax:
	# RooFit class name without the "Roo"
	# GenericPdf::<user-defined-name>("<function>", {...,...})
	#
	# A powerful tip: function can be a call to a C++
	# function (with double and int arguments), compiled
	# using gROOT.ProcessLine('.L <function>.cc+')

	wspace.factory('GenericPdf::model'\
		       '("alpha*exp(-x/xi1) +'\
		       ' (1-alpha)*exp(-x/xi2)",'\
		       '{alpha, xi1, xi2, x})')
	# make the model known to Python
	model = wspace.pdf('model')
	
    #----------------------------------------------------
	# generate data
    #----------------------------------------------------
	K = 2 # scale factor for amount of data to generate
	ndata = 200*K # number of events to generate
	# define the set obs = {x}
	wspace.defineSet('obs', 'x')
	# make the set obs known to Python
	obs  = wspace.set('obs')
	data = model.generate(obs, ndata)
	# load data into workspace
	getattr(wspace, 'import')(data)

	#----------------------------------------------------
	# unbinned fit to data
	#----------------------------------------------------
	print "="*80
	print "\t\t unbinned fit to data"
	print "="*80
	
	swatch = TStopwatch()
	swatch.Start()
	# If more control is needed, can call RooMinuit
	# directly, which is an interface to Minuit
	results = model.fitTo(data, RooFit.Save())
	print "real time: %10.3f s" % swatch.RealTime()
	print "="*80
	results.Print()

	# print correlation matrix
	# Note use of "," to prevent a new line
	print " ", "-" * 20
	print "  correlation matrix"
	print "%10s" % "",
	for v in ['alpha', 'xi1', 'xi2']:
		print "%10s" % v,
	print 
	for v1 in ['alpha', 'xi1', 'xi2']:
		print "%-10s" % v1,
		for v2 in ['alpha', 'xi1', 'xi2']:
			cor = results.correlation(v1, v2)
			print '%10.3f' % cor,
		print

	# plot

	# This is a bit weird!
	# We wish to plot the distribution of the data
	# and the model as a function of x. In RooFit, one
	# does so as follows:
	# 1. create a frame pertaining to x
	# 2. set its attributes, of which there are many
	# 3. tell the data to place a plot of themselves on
	#    the frame pertaining to x (which we called xframe)
	# 4. tell the model to place a plot of itself on
	#    xframe
	# 5. tell the model to place its parameters on xframe
	# 6. tell the xframe to draw itself on the active canvas
	xframe = wspace.var('x').frame()
	xframe.SetMaximum(50*K)
	data.plotOn(xframe)
	model.plotOn(xframe)
	model.paramOn(xframe)

	# If you have trouble making the plot look exactly as you
	# wish it to look, try drawing an empty Root histogram to
	# define the plotting area, then draw xframe using
	# the "same" option
	c1 = TCanvas('fig_unbinnedFit', 'fit', 10, 10, 500, 500)
	xframe.Draw()
	c1.SaveAs('.pdf')
	c1.SaveAs('.png')

	#---------------------------------------------------
	# create binned single exponential model
	#---------------------------------------------------
	wspace.factory('GenericPdf::model2'\
		       '("exp(-x/xi1)", {x, xi1})')
	model2 = wspace.pdf('model2')
	
	# generate and bin data
	ndata = 50*K
	data2 = model2.generate(obs, ndata)

	# bin the data
	nbinx = 10
	xmin  = 0
	xmax  = 5
	wspace.var('x').setBins(nbinx)
	wspace.var('x').setRange(xmin, xmax)
	hdata = RooDataHist('hdata', 'binned data', obs)
	hdata.add(data2)
	print "="*40
	hdata.Print('verbose')
	print "="*40
	
	# do multinomial fit to binned data by
	# turning off extended likelihood mode
	results2 = model2.fitTo(hdata,
				RooFit.Save(),
				RooFit.Extended(False))
	results2.Print()
	
	# plot on a different frame
	c2 = TCanvas('fig_binned_dataFit', 'fit',
		     515, 10, 500, 500)
	
	xframe2 = wspace.var('x').frame()
	xframe2.SetMaximum(25*K)
	hdata.plotOn(xframe2)
	model2.plotOn(xframe2)
	model2.paramOn(xframe2)
	xframe2.Draw()
	
	c2.SaveAs('.pdf')
	c2.SaveAs('.gif')
	print "="*80

	#---------------------------------------------------
	# compute gof (p-value)
	#---------------------------------------------------
	# first create an integral over a range (x-bin)
	
	# define set of variables over which to normalize
	# integral
	normSet = RooFit.NormSet(obs) 
	
	# define a range variable to represent the bin
	# boundaries
	wspace.var('x').setRange('x-bin', xmin, xmax)
	# ok, create integral
	integral = model2.createIntegral(obs, normSet,
					 RooFit.Range('x-bin'))

	# compute Y = min[-2 ln p(n | v)/p(n | n)],
	# which, according to Wilk, has (asymptotically)
	# a chi-squared distribution of N - 1 - M
	# degrees of freedom where
	# N - number of bins
	# M - number of fit parameters
	
	dx = float(xmax-xmin)/nbinx
	Y = 0.0
	total = 0.0 # to check the total integral
	for ii in range(nbinx):
		# get count in bin ii
		# yes, this is not as tidy as it could have been!
		ibin= hdata.get(ii)
		ni  = hdata.weight()

		# set the bin boundaries
		x = xmin + ii * dx
		wspace.var('x').setRange('x-bin', x, x+dx)

		# compute the integral over current bin
		# and scale result by total count
		vi = integral.getVal() * ndata
		total += vi
		
		# accumulate Y
		if ni > 0: Y += ni * log(vi/ni)

		print "%5d\t%10.3f %5d %10.1f" % (ii+1, x, ni, vi)
	Y *= -2
	
	# compute p-value = Int_Ymin^infinity p(Y) dY
	ndf    = nbinx-2
	pvalue = TMath.Prob(Y, ndf)

	print "="*80
	print "Int p(x|xi) dx =%6.1f" % total
	print "ChiSq/ndf = %6.1f/%d" % (Y, ndf)
	print "p-value   = %9.4f" % pvalue
			
	sleep(10)
#------------------------------------------------------------------
try:
	main()
except KeyboardInterrupt:
	print
	print "ciao!"
	print
	


