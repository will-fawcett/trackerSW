#!/usr/bin/python
'''
Quick script to plot kappa distributions
'''

from ROOT import *
gROOT.SetBatch(1)

def main(verbose):

    spacings = [10, 20, 30, 40, 50]
    spacings = [10, 50]
    pTcuts = [0, 2, 10, 50]
    pTcuts = [0, 2, 10, 20, 30, 40, 50]
    pileup  = 200

    
    for spacing in spacings:
        for pTcut in pTcuts:
            print 'Apply pT > ', pTcut
            iFileName = "/atlas/users/wfawcett/fcc/delphes/results/kappaOptimisation/hits_ttbar_pu{0}_multiGeometry_tracks{1}.root".format(pileup, spacing)
            compareKappasPlot(iFileName, pTcut, pileup, spacing)

def compareKappasPlot(iFileName, pTcut, pileup, spacing):

    iFile = TFile.Open(iFileName)
    print 'Opening file', iFileName
    REBIN = 5 

    # oohhh 
    REBIN = 2
    true = iFile.Get("deltaKappaTruePt{0}".format(pTcut))
    true.Rebin(REBIN)
    fake = iFile.Get("deltaKappaFakePt{0}".format(pTcut))
    fake.Rebin(REBIN)
    #print fake.GetEntries()

    # declare canvas 
    can = TCanvas("can", "can", 500, 500)
    can.SetLogy()

    # axes
    xaxis = true.GetXaxis()
    yaxis = true.GetYaxis()
    
    xaxis.SetTitle("#kappa_{123} #minus #kappa_{013} [mm^{#minus1}]" )
    xaxis.SetRangeUser(-0.005, 0.005) 


    # histogram drawing 
    true.SetMinimum(1)
    true.SetStats(0)
    true.SetTitle('Pileup = {0}, spacing {1} mm, pT > {2} GeV'.format(pileup, spacing, pTcut))
    true.Draw()

    fake.SetLineColor(2)
    fake.Draw('same')

    # Legend 
    leg = TLegend(0.1, 0.7, 0.4, 0.9)
    #leg.SetHeader()
    leg.AddEntry(fake, 'Fake tracks', 'l')
    leg.AddEntry(true, 'True tracks', 'l')
    leg.Draw()

    can.SaveAs('kappaOptimisation/kappa_pu{0}_{1}mm_{2}GeV.pdf'.format(pileup, spacing, pTcut))

    iFile.Close()

if __name__ == "__main__":

    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("-v", "--verbose", help="Turn on verbose messages", action="store_true", default=False)
    args = parser.parse_args()
    verbose = args.verbose

    main(verbose)
