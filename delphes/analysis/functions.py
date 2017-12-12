#!/usr/bin/python

#____________________________________________________________________________
def appendSlash(path):
    if path[-1] != '/':
        return path+'/'
    else:
        return path

#____________________________________________________________________________
def getReverseCumulativeHisto(histo):
    import ROOT
    '''
    Function to return the cumulative efficiency curve from a
    differential efficiency curve
    '''
    nbins = histo.GetNbinsX()
    error = ROOT.Double()
    cumulHisto = histo.Clone()
    cumulHisto.Reset()
    for bin in range(1,nbins+1):
        integral = histo.IntegralAndError(bin,nbins,error)
        integralErr = error
        cumulHisto.SetBinContent(bin,integral)
        cumulHisto.SetBinError(bin,integralErr)
    return cumulHisto
