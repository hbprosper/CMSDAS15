#!/usr/bin/env python
# -----------------------------------------------------------------------------
#  File:        runrgs.py
#  Description: Run Random Grid Search and save results to rgs.root
#  CMSDAS 2015 Bari HBP
# -----------------------------------------------------------------------------
import os, sys, re, optparse
from string import *
from histutil import *
from time import sleep
from ROOT import *
# -----------------------------------------------------------------------------
def error(message):
    print "** %s" % message
    exit(0)

def decodeCommandLine():
    VERSION = 'v1.0.0'
    USAGE = '''
    runrgs.py [options] signal-filename background-filename

    options
       -w weight-name   name of weight variable    [weight]
       -c cut-filename  name of cut-file           [same as signal-filename]
       -v var-filename  name of file defining cuts [rgs.vars] 
       -t tree-name     name of tree to be used    [Analysis]
       -e eff-limits    es_max,eb_max              [0.6,0.06]
    '''

    parser = optparse.OptionParser(usage=USAGE, version=VERSION)

    parser.add_option("-w", "--weight",
                      action="store",
                      dest="weight",
                      type="string",
                      default='weight',
                      help="name of weight variable")
    parser.add_option("-c", "--cutfile",
                      action="store",
                      dest="cutfile",
                      type="string",
                      default='',
                      help="name of root file containing cuts")
    parser.add_option("-v", "--varfile",
                      action="store",
                      dest="varfile",
                      type="string",
                      default='rgs.vars',
                      help="name of file defining cuts")   
    parser.add_option("-t", "--treename",
                      action="store",
                      dest="treename",
                      type="string",
                      default='Analysis',
                      help="name of tree to be used")
    parser.add_option("-e", "--efflimits",
                      action="store",
                      dest="efflimits",
                      type="string",
                      default='0.6,0.06',
                      help="maximimum limits of eff(s) and eff(b)")
    parser.add_option("-n", "--nbins",
                      action="store",
                      dest="nbins",
                      type="int",
                      default=50,
                      help="number of bins")                

    options, args = parser.parse_args()
    if len(args) < 2:
        print USAGE
        sys.exit(0)

    sigfile, bkgfile = args[:2]
    weightname = options.weight
    cutfile    = options.cutfile
    if cutfile == '': cutfile = sigfile
    varfile    = options.varfile        
    treename   = options.treename
    efflimits  = map(atof, split(options.efflimits, ','))
    esmax = 0.6
    ebmax = 0.06    
    if len(efflimits) == 1:
        esmax = efflimits[0]
    elif len(efflimits) == 2:
        esmax, ebmax = efflimits
    nbins = options.nbins
    return (weightname, treename, varfile, cutfile, sigfile, bkgfile,
            nbins, esmax, ebmax)
# -----------------------------------------------------------------------------
def plotRGS(rgsfile, nbins, bmax, smax):
    setStyle()
    
    # open RGS ntuple
    ntuple = Ntuple(rgsfile, 'RGS')
    # -------------------------------------------------------------
    #  fill 2D histogram
    # -------------------------------------------------------------
    print "==> filling RGS histogram..."
    outfile = "%splot.root" % nameonly(rgsfile)
    rfile = TFile(outfile, 'recreate')
    color = kBlue
    hname = "hrgs"
    hist  = mkhist2(hname,
                    "#epsilon_{B}",
                    "#epsilon_{S}",
                    nbins, 0, bmax,
                    nbins, 0, smax,
                    color=color)
    for row, cut in enumerate(ntuple):
        eb = cut.fraction0   #  background efficiency
        es = cut.fraction1   #  signal efficiency
        hist.Fill(eb, es)
    hist.SetMarkerSize(0.2)
    hist.SetMinimum(0)

    crgs = TCanvas("fig_rgs", "RGS", 10, 10, 500, 500)
    crgs.cd()
    hist.Draw("p")
    crgs.Update()
    crgs.SaveAs(".png")
    crgs.SaveAs(".pdf")
    
    rfile.cd()
    crgs.Write()
    rfile.Write()
    sleep(10)
# -----------------------------------------------------------------------------
def main():
    print "==> run Random Grid Search"
    weightname,treename,varfile,cutfile,sigfile,bkgfile,nbins,smax,bmax  = \
      decodeCommandLine()

    #  Load RGS class
    status = gSystem.Load("RGS_cc.so")
    if status < 0: sys.exit(status)

    # Check that all files are present
    if not os.path.exists(varfile):
        error("unable to open variables file %s" % varfile)

    if not os.path.exists(cutfile):
        error("unable to open cut file %s" % cutfile)

    if not os.path.exists(sigfile):
        error("unable to open signal file %s" % sigfile)

    if not os.path.exists(bkgfile):
        error("unable to open background file %s" % bkgfile)
    # ---------------------------------------------------------------------

    print "==> create RGS object"
    start = 0    
    maxcuts = 5000 #  maximum number of cut-points to consider
    rgs = RGS(cutfile, start, maxcuts, treename)

    # ---------------------------------------------------------------------
    #  Add signal and background data to RGS object
    #  Weight each event using the value in the field weightname,
    #  if it exists.
    #  NB: We asssume all files are of the same format
    # ---------------------------------------------------------------------
    numrows = 0 #  Load all the data from the files

    print "\t==> load background data"
    rgs.add(bkgfile, start, numrows, weightname)
    print

    print "\t==> load signal data"
    rgs.add(sigfile, start, numrows, weightname)
    print

    # ---------------------------------------------------------------------    
    #  Run algorithm
    # ---------------------------------------------------------------------
    rgs.run(varfile)

    #  Save results to a root file
    outfile = '%s.root' % nameonly(varfile)
    rfile = rgs.save(outfile)

    plotRGS(outfile, nbins, bmax, smax)    
# -----------------------------------------------------------------------------
try:
    main()
except KeyboardInterrupt:
    print "\tciao!\n"



