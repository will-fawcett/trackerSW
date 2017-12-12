#!/usr/bin/python

from ROOT import * 
gROOT.SetBatch(1)
gROOT.SetBatch(1)
gStyle.SetGridStyle(3) 
gStyle.SetPadLeftMargin(0.15) # increase space for left margin
gStyle.SetPadBottomMargin(0.15) # increase space for left margin
gStyle.SetGridColor(kGray)
gStyle.SetPadTickX(1) # add tics on top x
gStyle.SetPadTickY(1) # add tics on right y

from extractTrackParameters import prepareLegend
from Colours import Colours
from functions import appendSlash, getReverseCumulativeHisto  

resultsPath = '/atlas/data4/userdata/wfawcett/delphes/results/'
resultsPath = '/Users/Will/Documents/fcc/delphes/results/'

def main(verbose):

    can = TCanvas('can', 'can', 500, 500)
    can.SetLogy()
    can.SetGrid()

    ifile_minbias = TFile.Open(resultsPath+'hist_MinBias_mu200_s80_n1000.root')
    ifile_ttbar = TFile.Open(resultsPath+'hist_ttbar_mu200_s80_n1000.root') 

    colours = Colours()
    
    for nJet in range(1,8):

        nominalName = 'nominalJet{0}Pt'.format(nJet) # jets reconstructed using all tracks with pT > 1GeV
        suppressedName = 'associatedJet{0}Pt'.format(nJet)

        # get jet pT histos from minbias
        mb_nominal = ifile_minbias.Get(nominalName)
        mb_PUsupp  = ifile_minbias.Get(suppressedName)

        # get cumulative histograms for minbias 
        cmb_nominal = getReverseCumulativeHisto(mb_nominal)
        cmb_PUsupp  = getReverseCumulativeHisto(mb_PUsupp)

        # get jet pT histos for ttbar
        tt_nominal = ifile_ttbar.Get(nominalName)
        tt_PUsupp  = ifile_ttbar.Get(suppressedName)

        # get cumulative histograms for ttbar
        ctt_nominal = getReverseCumulativeHisto(tt_nominal)
        ctt_PUsupp  = getReverseCumulativeHisto(tt_PUsupp)

        # now draw
        xaxis = cmb_nominal.GetXaxis()
        xaxis.SetRangeUser(0, 100)
        cmb_nominal.Draw()
        cmb_PUsupp.Draw('same')

        can.SaveAs('test.pdf')
        break

def setStyle(hist, c):
    hist.SetLineColor(c)
    hist.SetMarkerColor(c)


if __name__ == "__main__":

    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("-v", "--verbose", help="Turn on verbose messages", action="store_true", default=False)
    args = parser.parse_args()
    verbose = args.verbose

    main(verbose)


