#!/usr/bin/python
'''
Script to plot the acceptance of some cut on a variable X
'''

from ROOT import *

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
        for plot in plots:

            h = iFile.Get(branch+plot)
            xaxis = h.GetXaxis()
            yaxis = h.GetYaxis()

            xaxis.SetTitle(plot+" [GeV]")
            yaxis.SetTitle(acceptance)
            



if __name__ == "__main__":

    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("-v", "--verbose", help="Turn on verbose messages", action="store_true", default=False)
    args = parser.parse_args()
    verbose = args.verbose

    main(verbose)


