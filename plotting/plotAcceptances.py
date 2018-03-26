#!/usr/bin/python
'''
Script to plot the acceptance of some cut on a variable X
'''

from ROOT import *
from utils import getReverseCumulativeHisto, appendSlash, checkDir

gROOT.SetBatch(1)
gStyle.SetPadBottomMargin(0.15)
gStyle.SetPadLeftMargin(0.13) # increase space for left margin
gStyle.SetPadTickX(1)
gStyle.SetPadTickY(1)

def main(verbose):



    branchNames = [
         "TruthTrack",
         "Track",
         "PBMatchedTracks",

         "TracksFromHit30",
         "SmearedTracksFromHits",
         "PBMatchedHitTracks",
         ]

    plots = [
            "track1Pt",
            "track2Pt",
            "track3Pt",
            "track4Pt",
            ]


    iFile = TFile.Open("/atlas/users/wfawcett/fcc/delphes/test.root")
    can = TCanvas("can", "can", 500, 500)
    for branch in branchNames:
        outputDir = "TrackPlots/"+appendSlash(branch)
        checkDir(outputDir)
        for plot in plots:

            h0 = iFile.Get(branch+plot)
            h0.GetXaxis().SetTitle(plot+" [GeV]")
            h0.GetYaxis().SetTitle("Fraction of events")
            h0.Draw()
            nbins = h0.GetNbinsX()
            print h0.Integral()
            print h0.Integral(1, nbins)
            print h0.Integral(1, nbins+1) # should include overflow
            print ''

    

            can.SaveAs(outputDir+plot+".pdf")

            #acceptance = h0.GetCumulative(False)
            acceptance = getReverseCumulativeHisto(h0)

            xaxis = acceptance.GetXaxis()
            yaxis = acceptance.GetYaxis()

            xaxis.SetTitle(plot+" [GeV]")
            yaxis.SetTitle("Acceptance")
            xaxis.SetRangeUser(0, 50) 

            #acceptance.DrawNormalized()
            acceptance.Draw()
            can.SaveAs(outputDir+"acceptance_"+plot+".pdf")

            #efficiency = h0.GetCumulative(True) 
            #efficiency.DrawNormalized()
            #efficiency.DrawNormalized()
            #can.SaveAs(outputDir+"efficiency_"+plot+".pdf")
            



if __name__ == "__main__":

    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("-v", "--verbose", help="Turn on verbose messages", action="store_true", default=False)
    args = parser.parse_args()
    verbose = args.verbose

    main(verbose)


