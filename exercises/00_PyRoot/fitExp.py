#!/usr/bin/env python
#-------------------------------------------------------------
# File: fitExp.py
# Description: A Python/PyRoot/RooFit tutorial!
#              Implementation of Glen Cowan's exercise:
#
# Fit and exponential to data
#
# Created: 4 June 2013 Harrison B. Prosper
#          INFN SOS 2013, Vietri sul Mare, Italy
#
#    Adapted for CMSDAS 2015, Bari, Italy
#
# Python notes
# ------------
# 1. First line of this file tells the operating system which program
#    is to be used to interpret the instructions that follow. You can
#    make this program executable with the command
#
#          chmod +x expFit.py
#
#    and execute the program using
#
#          ./expFit.py
#
# 2. Python uses indentation to create program blocks.
#    Semicolons are not needed as in C++. It is convenient to use
#    an editor such as emacs that is Python-aware. This will help
#    minimize indentation errors.
#
# 3. Python handles pointers for you! Use "." as in
#
#           TMath.Prob
#
#    instead of TMath::Prob
#
# 4. There are wwo basic ways to load program modules into memory, e.g.:
#
#          import os
#    and
#          from string import replace
#
# 5. Strings can be initialized either with '...' or "...". This is
#    useful when ".." needs to be embedded within a string. Use \ to
#    continue strings onto a new line:
#
#            poem = 'The time has come the walrus said\n'\
#                   'To speak of many things'
#
# 6. Warning: Python uses dynamic typing, which means that the type of
#    a variable is detemined at runtime by its value. Consequently,
#    a variable's type is, well, variable!
#
#    x = 0     this is an integer
#    x = 0.0   this is a float
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
# load the operating system and system modules into memory
import os,sys

# load the sleep function from the time module
from time import sleep

# load everything that is in PyROOT. This is fine if you are
# sure there are no collisions between the names in PyROOT
# and the names in other modules.
from ROOT import *
#-------------------------------------------------------------
# the main function can be called whatever you like. I follow
# C++ and call it main..dull, but clear!
def main():

    # we shall use a package called RooFit, compiled with ROOT
    # in order to fit an exponential function to data.
    #
    # suppress all messages except those that matter
    msgservice = RooMsgService.instance()
    # if a crash occurs, comment out next line
    msgservice.setGlobalKillBelow(RooFit.FATAL)

    # make a workspace so that we can use its factory method
    wspace = RooWorkspace('Glen Cowan')

    #-----------------------------------------------------
    # create double-exponential model
    #-----------------------------------------------------
    # the observable is x and lies in the range [0, 20]
    xmin = 0.0
    xmax =20.0
    # use the factory method of the RooWorkspace object, just
    # created, to create an object called x that represents the
    # observable.
    # syntax:
    #        <name>[value, min-value, max-value]
    #
    # we are using Python's ability to write numbers into strings
    wspace.factory('x[0,%f,%f]' % (xmin, xmax))

    # set the number of bins for display purposes
    wspace.var('x').setBins(20)

    # the parameters or the double-exponential model are
    # alpha, a, b
    wspace.factory('alpha[0.2,0,0.5]')
    wspace.factory('a[1,0.01, 5]')
    wspace.factory('b[5,0.01,10]')

    # the model to be fitted, called "model", is defined by a probability
    # density function (pdf)
    #   p(x|alpha, a, b) = alpha*exp(-x/a) + (1-alpha)*exp(-x/b)
    #
    # use {..} to specify a list of variables (modeled in RooFit as a
    # RooArgList)
    #
    # note use of "\" continuation markers
    # syntax: RooFit class name without the "Roo" in front
    #
    # GenericPdf::<user-defined-name>("<function>", {...})
    #
    # a powerful tip: a function can be a call to a C++
    # function (with double and int arguments), compiled
    # using gROOT.ProcessLine('.L <function>.cc+')
    #
    # if you need to make the compiler and linker happy by including headers
    # and libraries other the the default set provided by ROOT, do first
    #
    #   gSystem.AddInlcudePath('-I<path1> ...')
    #   gSystem.AddLinkedLibs('-L<libdir> -l<library> ...')
    #
    # before called gROOT.ProcessLine

    wspace.factory('GenericPdf::model'\
                   '("alpha*exp(-x/a) +'\
                   ' (1-alpha)*exp(-x/b)",'\
                   '{x, alpha, a, b})')

    # so far, the "model" is known only to the RooFit workspace.
    # make the model known to Python also
    model = wspace.pdf('model')

    #----------------------------------------------------
    # now we generate some data from the model,
    # then try to fit the latter to these data
    #----------------------------------------------------
    ndata = 400 # number of data to generate
    # define the set obs = (x)
    wspace.defineSet('obs', 'x')

    # make the set obs known to Python
    obs  = wspace.set('obs')

    # now, generate data
    data = model.generate(obs, ndata)

    # and load data into workspace
    getattr(wspace, 'import')(data)

    #----------------------------------------------------
    # Step 1: do an unbinned fit to data
    #----------------------------------------------------
    print "="*80
    print "\t\t unbinned fit to data"
    print "="*80

    # this is obvious, right?!! :)
    swatch = TStopwatch()
    swatch.Start()

    # if more control is needed, you can call RooMinuit
    # directly, which is an interface to Minuit.
    # here, we happy to use the simpler interface "fitTo".
    # remember to save the results of the fit
    results = model.fitTo(data, RooFit.Save())
    print "real time: %10.3f s" % swatch.RealTime()

    # let's see what we get
    print "="*80
    results.Print()

    # print correlation matrix.
    # note use of "," to suppress a newline
    print " ", "-" * 20
    print "  correlation matrix"
    print "%10s" % "",
    for v in ['alpha', 'a', 'b']:
        print "%10s" % v,
    print 
    for v1 in ['alpha', 'a', 'b']:
        print "%-10s" % v1,
        for v2 in ['alpha', 'a', 'b']:
            cor = results.correlation(v1, v2)
            print '%10.3f' % cor,
        print

    #---------
    # plot
    #---------
    # this is how RooFit makes plots. It is not as intuitive
    # as it could have been; indeed, it's seems weird to me!
    #
    # We wish to plot the distribution of the data
    # and superimpose the fitted model as a function of the
    # observable x.
    #
    # In RooFit, one does so as follows:
    # 1. create a frame pertaining to x
    # 2. set the frame's attributes, of which there are many
    # 3. tell the data to place a plot of themselves on
    #    the frame pertaining to x, which we called xframe
    # 4. tell the model to place a plot of itself on xframe
    # 5. tell the model to place its parameters on xframe
    # 6. tell the xframe to draw itself on the active canvas

    xframe = wspace.var('x').frame()
    xframe.SetMinimum(0)     # set minimum y-axis value 
    xframe.SetMaximum(100)   # set maximum y-axis value
    data.plotOn(xframe)
    model.plotOn(xframe)
    model.paramOn(xframe)

    # If you have trouble making the plot look exactly as you
    # wish it to look, try drawing an empty Root histogram
    # first in order to define the plotting area, then draw
    # xframe using the "same" option
    # place upper lefthand corner of canvas at pixel position (10, 10)
    # of your screen. (0,0) is the upper lefthand corner.

    c1 = TCanvas('fig_unbinnedFit', 'fit', 10, 10, 500, 500)
    xframe.Draw()
    c1.SaveAs('.pdf')
    c1.SaveAs('.png')

    #---------------------------------------------------
    # Step 2: create binned single exponential model
    #---------------------------------------------------
    wspace.factory('GenericPdf::model2("exp(-x/a)", {x, a})')
    model2 = wspace.pdf('model2')

    # generate data
    ndata = 100
    data2 = model2.generate(obs, ndata)

    # bin the data
    nbinx = 10
    xmin  = 0.0
    xmax  = 5.0
    wspace.var('x').setBins(nbinx)
    wspace.var('x').setRange(xmin, xmax)

    # note use of set obs, created above, to tell
    # RooDataHist the variable(s) with respect to
    # which the data are to be binned.
    hdata = RooDataHist('hdata', 'binned data', obs)
    hdata.add(data2)  # add the data to the DataHist and bin them
    print "="*40
    hdata.Print('verbose')
    print "="*40

    # do a multinomial fit to the binned data by
    # turning off extended likelihood mode. If you
    # want a multi-Poisson fit, set False to True.
    # (if interested, ask Harrison what all this means!)
    results2 = model2.fitTo(hdata,
                            RooFit.Save(),
                            RooFit.Extended(False))
    results2.Print()

    # plot results of fit on a different frame
    c2 = TCanvas('fig_binned_dataFit', 'fit',
             515, 10, 500, 500)

    xframe2 = wspace.var('x').frame()
    xframe2.SetMaximum(50)
    hdata.plotOn(xframe2)
    model2.plotOn(xframe2)
    model2.paramOn(xframe2)
    xframe2.Draw()

    c2.SaveAs('.pdf')
    c2.SaveAs('.png')
    print "="*80

    #---------------------------------------------------
    # Step 3: let's do a bit of statistics. We shall
    # compute a goodness-of-fit (gof) measure (a p-value)
    #---------------------------------------------------
    # 1. first create an integral over a bin in x and
    # define the set of variables over which to normalize
    # the integral
    normSet = RooFit.NormSet(obs) 

    # 2. define a range variable to represent the bin
    # boundaries
    wspace.var('x').setRange('x-bin', xmin, xmax)

    # 3. ok, now create integral
    integral = model2.createIntegral(obs,
                                     normSet,
                                     RooFit.Range('x-bin'))

    # 4. compute Y = min[-2 ln p(n | v) / p(n | n)],
    # where p(n | v) is a multinomial likelihood; n denotes
    # the counts and v denotes the mean counts.
    #
    # according to Wilks' theorem, the quantity Y has
    # (asymptotically) a chi-squared distribution of N - 1 - M
    # degrees of freedom where
    #   N - number of bins (=number of counts)
    #   M - number of fit parameters

    # find bin width. use float function to make sure we have
    # a float in the numerator
    dx = float(xmax-xmin)/nbinx
    Y = 0.0
    total = 0.0 # to check the total integral
    # range(nbinx) = [0, 1,...nbinx-1]
    print
    print "%5s\t%10s %5s %10s" % ('', 'binlow', "count", "mean")
    for ii in range(nbinx):
        # get count in bin ii
        # yes, this is not as tidy as it could have been!
        ibin = hdata.get(ii)   # get object that models a bin
        ni   = hdata.weight()  # get bin content

        # set the bin boundaries in our previously created
        # range variable
        x = xmin + ii * dx
        wspace.var('x').setRange('x-bin', x, x+dx)

        # compute the integral, with respect to x, over current
        # bin and scale result by the total data count. This
        # gives us the mean count per bin
        vi = integral.getVal() * ndata
        total += vi

        # accumulate Y
        if ni > 0: Y += ni * log(vi/ni)

        print "%5d\t%10.3f %5d %10.1f" % (ii+1, x, ni, vi)
        
    # complete calculation of Y
    Y *= -2

    # 5. compute p-value = Int_Ymin^infinity p(Y) dY
    ndf    = nbinx-1  # number of degrees of freedom
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



