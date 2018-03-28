#!/usr/bin/python
from ROOT import *
import plotting as plt
from utils import prepareLegend

gROOT.SetBatch(1)
#gStyle.SetPadBottomMargin(0.15)
#gStyle.SetPadLeftMargin(0.13) # increase space for left margin
gStyle.SetPadTickX(1)
gStyle.SetPadTickY(1)

def main(verbose):

    branchesToCompare = [
            ('TruthTrack',      'TracksFromHit30',       'truth'),
            ('Track',           'SmearedTracksFromHits', 'smeared'),
            ('PBMatchedTracks', 'PBMatchedHitTracks',    'PBmatched'),
            ]

    plots = ['track1Pt', 'track2Pt', 'track3Pt', 'track4Pt']


    for branchPair in branchesToCompare:

        for plot in plots:
            can = TCanvas("can"+plot+branchPair[0], "can", 500, 500)
            rightmargin = 0.1
            leftmargin = 0.2
            
            ## Define upper pad
            upperPad = TPad("upperPad","upperPad",0, 0.3, 1, 1)
            PLOT_MARGINS_WITH_RATIO = (0.125, 0.05, 0.025, 0.1)
            upperPad.SetMargin(*PLOT_MARGINS_WITH_RATIO)
            upperPad.Draw()

            ## Define lower pad
            lowerPad = TPad("lowerPad","lowerPad",0, 0, 1, 0.3)
            lowerPad.SetTopMargin(0)
            lowerPad.Draw()
            PLOT_RATIO_MARGINS = (0.125, 0.05, 0.325, 0.05)
            lowerPad.SetMargin(*PLOT_RATIO_MARGINS)

            # general plot settings 
            RATIO_Y_TITLE = 'Ratio'
            xTitle = plot+' [GeV]'
            yTitle = 'Frequency'
            xRange = [0, 100]

            # Extract histograms
            sample = 'mg_pp_hh'
            pileup = 0
            iFileName = '/atlas/data4/userdata/wfawcett/delphes/results/fromLHE/{0}_pu{1}.root'.format(sample, pileup)
            iFile = TFile.Open(iFileName, "READ")
            h0 = iFile.Get("{0}_{1}".format(branchPair[0], 'track1Pt'))
            h1 = iFile.Get("{0}_{1}".format(branchPair[1], 'track1Pt'))
            REBIN = 2
            h0.Rebin(REBIN)
            h1.Rebin(REBIN)

            # histogram marker styling
            h0.SetLineColor(9)
            h0.SetMarkerStyle(22)
            h0.SetMarkerColor(9)

            h1.SetLineColor(2)
            h1.SetMarkerColor(2)
            h1.SetMarkerStyle(20)

            # histogram axis styling
            x_axis = h0.GetXaxis()
            y_axis = h0.GetYaxis()

            x_axis.SetTitle(xTitle)
            # Get rid of title in case of ratio
            x_axis.SetLabelOffset(999)
            x_axis.SetTitleOffset(999)


            y_axis.SetTitle(yTitle)
            x_axis.SetRangeUser(xRange[0], xRange[1])
            

            #legend 
            leg = prepareLegend('topRight')
            leg.AddEntry(h0, branchPair[0], 'lp')
            leg.AddEntry(h1, branchPair[1], 'lp')


            # Drawing
            upperPad.cd()
            h0.Draw('hits')
            h1.Draw('same')
            leg.Draw()

            # lower pad
            can.cd()
            lowerPad.cd()
            ratio = plt.ratio_histogram(h0, h1, RATIO_Y_TITLE)
            ratio.SetLineColor(1)
            ratio.SetMarkerColor(1)
            ratio_y_axis = ratio.GetYaxis()
            ratio_x_axis = ratio.GetXaxis()
            
            ratio_x_axis.SetTitleSize(0.13)
            PLOT_RATIO_Y_AXIS_TITLE_OFFSET_RATIO = 0.425
            ratio_x_axis.SetTitleOffset(PLOT_RATIO_Y_AXIS_TITLE_OFFSET_RATIO)
            ratio_x_axis.SetLabelOffset(0.01)
            ratio_x_axis.SetTitleOffset(1)
            ratio_x_axis.SetLabelSize(0.12)


            PLOT_RATIO_Y_AXIS_LABEL_SIZE = 0.12
            ratio_y_axis.SetTitleSize(PLOT_RATIO_Y_AXIS_LABEL_SIZE)
            ratio_y_axis.SetLabelSize(PLOT_RATIO_Y_AXIS_LABEL_SIZE)
            ratio_y_axis.SetTitleOffset(PLOT_RATIO_Y_AXIS_TITLE_OFFSET_RATIO)
            ratio_y_axis.SetNdivisions(5, 5, 0)
            
            ratio_y_axis.SetRangeUser(0.5, 1.5)
            ratio.Draw()

            can.SaveAs('branchComparrison/{0}_{1}.pdf'.format(branchPair[2], plot))





            '''
            toPlot = [ (h0, 'hist') , (h1, 'hist') ]

            doRatioPlot = True
            roomForHeader = True
            aplot = plt.Plot('', xTitle, yTitle, roomForHeader, doRatioPlot, xRange)
            #aplot.set_log_scale()
            aplot.draw( *toPlot )

            # create ratio histogram
            ratio.GetXaxis().SetTitle(xTitle)

            noXerror = False
            aplot.draw_ratio_histogram( (ratio, noXerror, RATIO_Y_TITLE) )
            aplot.save('test.pdf')
            '''






if __name__ == "__main__":

    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("-v", "--verbose", help="Turn on verbose messages", action="store_true", default=False)
    args = parser.parse_args()
    verbose = args.verbose

    main(verbose)


