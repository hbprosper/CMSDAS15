#!/usr/bin/env python
#------------------------------------------------------------------
# Exercise 0 - Fit Type Ia supernovae data
# Created sometime in the 21st century Harrison B. Prosper
#------------------------------------------------------------------
# load some Python modules into memory
import os,sys          # Operating system, system modules
from histutil import * # Load some utilities built on PyRoot
from time import sleep # Well...kind of obvious, no?
from ROOT import *     # Load PyRoot
#------------------------------------------------------------------
# procedure to make nice plots
def makePlots(data, OM, OL, H, zmin, zmax, mumin, mumax):

    # Copy data into arrays
    xx = array('d')
    ex = array('d')
    yy = array('d')
    ey = array('d')

    ndata = data.numEntries()
    for ii in xrange(ndata):
        row = data.get(ii)
        xx.append(row['z'].getVal())
        ex.append(0)
        yy.append(row['x'].getVal())
        ey.append(row['dx'].getVal())

    g = mkgraphErrors(xx, yy, ex, ey,
              "redshift z",
              "distance modulus #mu", 
              zmin, zmax,
              ymin=mumin,
              ymax=mumax, color=kBlack)
    g.SetMarkerSize(0.2)

    # Create model plot
    nz = 100
    zstep = (zmax-zmin)/nz
    zz = array('d')
    mu = array('d')
    omegaM = OM.getVal()
    omegaL = OL.getVal()
    q = H.getVal()

    for ii in xrange(nz):
        zz.append( (ii+0.5)*zstep )
        mu.append( distanceModulus(zz[-1],
                       omegaM,
                       omegaL, q) )

    gfit = mkgraph(zz, mu,
               "redshift z", "distance modulus #mu", 
               zmin, zmax, color=kRed, lwidth=2)
    return (g, gfit)
#------------------------------------------------------------------	    
def main():
    print "\n","="*80
    print "\t\tType Ia Supernovae"
    print "="*80

    # compile distance modulus function
    gROOT.ProcessLine('.L distanceModulus.cc+')

    # suppress all messages except those that matter
    RooMsgService.instance().setGlobalKillBelow(RooFit.FATAL)

    # make a workspace so that we can use its factory method
    wspace = RooWorkspace('TypeIa')

    # define parameter ranges
    zmin  = 0.0    # min(red-shift)
    zmax  = 1.5    # max(red-shift)
    mumin = 32.0   # min(distance modulus)
    mumax = 48.0   # max(distance modulus)

    # create parameter for name of Type Ia supernova
    name = RooStringVar('name', 'TypeIa', 'name of type Ia')

    # create red shift observable and return it to Python from RooFit
    wspace.factory('z[%f, %f]' % (zmin, zmax))
    z = wspace.var('z')

    # create distance modulus observable
    wspace.factory('x[%f, %f]' % (mumin, mumax))
    x = wspace.var('x')

    # create uncertainty in distance modulus observable
    wspace.factory('dx[0, 2]')
    dx = wspace.var('dx')

    # create model parameters
    # Omega_M
    wspace.factory('OM[0.5, 0, 200]')
    OM = wspace.var('OM')

    # Omega_Lambda
    wspace.factory('OL[0.5, 0, 200]')
    OL = wspace.var('OL')

    # parameter related to Hubble constant
    wspace.factory('H[70, 0, 200]')
    H = wspace.var('H')

    # create distance modulus parameter 
    # note use of compiled C++ program
    mu = RooFormulaVar('mu', '#mu',
                       'distanceModulus(z, OM, OL, H)',
                       RooArgList(z, OM, OL, H))
    # import mu into workspace so the latter "knows" about it
    getattr(wspace,'import')(mu)

    # create model to be fitted
    wspace.factory('Gaussian::model(x, mu, dx)')
    model  = wspace.pdf('model')

    #----------------------------------------------------------
    # read in Type Ia data
    #----------------------------------------------------------
    data = RooDataSet.read('SCPUnion2.1.txt',
                           RooArgList(name, z, x, dx))
    ndata = data.numEntries()
    print "number of observations: %d" % ndata

    # one way to access data from a RooDataSet
    for ii in range(ndata):
        if ii % 100 == 0:
            d = data.get(ii)
            print "%5d %-8s\t%10.3f\t%10.4f +/- %-10.4f"%\
                  (ii,
                   d['name'].getVal(),
                   d['z'].getVal(),
                   d['x'].getVal(),
                   d['dx'].getVal())

    #----------------------------------------------------------
    # now fit model to observations
    #----------------------------------------------------------
    print "="*80
    swatch = TStopwatch()
    swatch.Start()

    # save results of fit
    results = model.fitTo(data, RooFit.Save())
    print "real time: %10.3f s" % swatch.RealTime()
    print "="*80
    results.Print()
    print "="*80

    #----------------------------------------------------------
    # plot results of fit
    #----------------------------------------------------------
    # see histutil.py
    setStyle()

    g, gfit = makePlots(data, OM, OL, H, zmin, zmax, mumin, mumax)

    canvas = TCanvas("fig_results", "SN1a", 10, 10, 500, 500)
    canvas.cd()
    g.Draw("ap")
    gfit.Draw("c same")

    wrtext = Scribe(0.25,0.45)
    wrtext.write("The Union2.1 Compilation")
    wrtext.write("The Supernova Cosmology Project")
    wrtext.write("http://supernova.lbl.gov/Union/figures/")
    wrtext.write("#Omega_{M} = %4.2f #pm%-4.2f    "\
                 "#Omega_{#Lambda} = %4.2f #pm%-4.2f" % (OM.getVal(),
                                                         OM.getError(),
                                                         OL.getVal(),
                                                         OL.getError()))

    canvas.Update()
    canvas.SaveAs(".png")
    canvas.SaveAs(".pdf")

    sleep(10)
#------------------------------------------------------------------
try:
    main()
except KeyboardInterrupt:
    print
    print "bye cruel world!"
    print



