#!/usr/bin/python
'''
Script to plot the acceptance of some cut on a variable X
'''

from ROOT import *
from utils import getReverseCumulativeHisto, appendSlash, checkDir, prepareLegend
from colours import colours

gROOT.SetBatch(1)
gStyle.SetPadBottomMargin(0.15)
gStyle.SetPadLeftMargin(0.13) # increase space for left margin
gStyle.SetPadTickX(1)
gStyle.SetPadTickY(1)

def main(verbose):

    samples = ['mg_pp_hh', 'py8_pp_minbias']
    pileups = [0, 200, 1000]

    sampleInfo = {
            # cross-sections are in [pb] 
            'py8_pp_minbias' : { 'title' : 'Minbias',  'xsection' : 1.1 * 1e11 },
            'mg_pp_hh' :       { 'title' : 'di-higgs', 'xsection' : 0.65 },
            'mg_pp_tth'      : { 'title' : 'ttH',      'xsection' : 23.37 }, 
            }


    trackBranchNames = [
         "TruthTrack", "Track", "PBMatchedTracks",
         "TracksFromHit30", "SmearedTracksFromHits", "PBMatchedHitTracks",
         ]

    trackPlots = [
            "track1Pt",
            "track2Pt",
            "track3Pt",
            "track4Pt",

            "electron1Pt", 
            "muon1Pt", 
            "lepton1Pt",
            ]

    jetBranchNames = [
        'TruthTrackJets',
        'SmearedTrackJets',
        'PBMatchedTrackJets',

        'TruthHitTrackJets',
        'SmearedHitTrackJets',
        'PBMatchedHitTrackJets',
        ]

    jetPlots = [
            "jet1Pt",
            "jet2Pt",
            "jet3Pt",
            "jet4Pt",
            ]


    for sample in samples:
        for pileup in pileups:

            iFileName = '/atlas/data4/userdata/wfawcett/delphes/results/fromLHE/{0}_pu{1}.root'.format(sample, pileup)
            iFile = TFile.Open(iFileName)
            can = TCanvas("can", "can", 500, 500)
            plotDict = {}

            outputBaseDir = 'TrackPlots/{0}_pu{1}/'.format(sample, pileup)
            checkDir(outputBaseDir)


            for branch in trackBranchNames+jetBranchNames:
                outputDir = outputBaseDir+appendSlash(branch)
                checkDir(outputDir)
                plotDict[branch] = {}
                if branch in trackBranchNames:
                    plotList = trackPlots
                else:
                    plotList = jetPlots
                for plot in plotList:

                    histoName = branch+"_"+plot
                    print 'plotting', histoName
                    h0 = iFile.Get(histoName)
                    xTitle = plot.replace('track', 'Track ').replace('jet', 'Jet ').replace('Pt', ' p_{T}')
                    print xTitle
                    h0.GetXaxis().SetTitle(xTitle+" [GeV]")
                    h0.GetYaxis().SetTitle("Fraction of events")
                    h0.Draw()
                    nbins = h0.GetNbinsX()
                    print h0.Integral()
                    print h0.Integral(1, nbins)
                    print h0.Integral(1, nbins+1) # should include overflow
                    print ''

                    # plot acceptance
                    can.SaveAs(outputDir+plot+".pdf")


                    #acceptance = h0.GetCumulative(False)
                    acceptance = getReverseCumulativeHisto(h0)

                    xaxis = acceptance.GetXaxis()
                    yaxis = acceptance.GetYaxis()

                    xaxis.SetTitle(xTitle+" [GeV]")
                    yaxis.SetTitle("Acceptance")
                    xaxis.SetRangeUser(0, 50) 

                    #acceptance.DrawNormalized()
                    acceptance.Draw()
                    can.SaveAs(outputDir+"acceptance_"+plot+".pdf")

                    efficiency = h0.GetCumulative(True) 
                    #efficiency.DrawNormalized()
                    #efficiency.DrawNormalized()
                    #can.SaveAs(outputDir+"efficiency_"+plot+".pdf")

                    plotDict[branch][plot] = {
                            'efficiency' : efficiency, 
                            'acceptance' : acceptance
                            }

            print plotDict


            gStyle.SetGridStyle(3) 
            gStyle.SetGridColor(kGray)
            #can = TCanvas("can2", "can2", 500, 500)
            can.SetGrid()

            # plot trigger rates (for minbias) in the different scenarios 
            s1 = {
                 #"TruthTrack",
                 "Track"            : {'marker' : 20, 'colour' : colours.red,  'leg' : 'L0'},
                 "PBMatchedTracks"  : {'marker' : 23, 'colour' : colours.blue, 'leg' : 'L0 Pileup suppressed' }
                 }
            s2 = {
                    'SmearedTrackJets'   : {'marker' : 20, 'colour' : colours.red, 'leg' : 'L0' },
                    'PBMatchedTrackJets' : {'marker' : 23, 'colour' : colours.blue,'leg' : 'L0 Pileup suppressed' }
                 }

            s3 = [
                 "TracksFromHit30",
                 "SmearedTracksFromHits",
                 "PBMatchedHitTracks",
                 ]

            can.SetLogy()
            for sSet in [s1, s2]:
                outputDir = outputBaseDir+"Rates/"
                checkDir(outputDir)


                plots = plotDict[sSet.keys()[0]].keys()

                for plot in plots:
                    pCounter = 0
                    leg = prepareLegend('topRight')
                    for scenario in sSet.keys():
                        
                        style = sSet[scenario]
                            
                        # scale to trigger rate
                        rate = plotDict[scenario][plot]['acceptance']
                        titleInfo = sampleInfo[sample]
                        rate.SetTitle("{0} #LT#mu#GT = {1}".format(titleInfo['title'], pileup))
                        rate.Scale(40*1e3) # scale to 40 MHz (appropriate for minbias, not for other samples)  
                        xaxis = rate.GetXaxis()
                        yaxis = rate.GetYaxis()
                        yaxis.SetTitle('Rate [kHz]')

                        if 'track' in plot:
                            xaxis.SetRangeUser(0, 25)
                        if 'jet' in plot:
                            xaxis.SetRangeUser(0, 100)

                        rate.SetMarkerStyle(style['marker'])
                        rate.SetMarkerColor(style['colour'])
                        rate.SetLineColor(style['colour'])

                        if pCounter == 0:
                            rate.Draw()
                        else:
                            rate.Draw('same')
                        pCounter += 1 
            
                        leg.AddEntry(rate, style['leg'], 'lp') 
                        
                    leg.Draw()
                    can.SaveAs(outputDir+'rate_{0}.pdf'.format(plot))

                    

if __name__ == "__main__":

    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("-v", "--verbose", help="Turn on verbose messages", action="store_true", default=False)
    args = parser.parse_args()
    verbose = args.verbose

    main(verbose)
