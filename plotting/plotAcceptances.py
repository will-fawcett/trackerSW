#!/usr/bin/python
'''
Script to plot the acceptance of some cut on a variable X
'''

from ROOT import *
from utils import getReverseCumulativeHisto, appendSlash, checkDir, prepareLegend, myText
from colours import colours

gROOT.SetBatch(1)
gStyle.SetPadBottomMargin(0.15)
gStyle.SetPadLeftMargin(0.13) # increase space for left margin
gStyle.SetPadTickX(1)
gStyle.SetPadTickY(1)

TEXT_SIZE = 0.04
gStyle.SetLabelSize(TEXT_SIZE, 'X')
gStyle.SetLabelSize(TEXT_SIZE, 'Y')
gStyle.SetTitleSize(TEXT_SIZE, 'X')
gStyle.SetTitleSize(TEXT_SIZE, 'Y')
gStyle.SetHistLineWidth(3)

# Stuff for legend
gStyle.SetCanvasColor(-1)
gStyle.SetPadColor(-1)
gStyle.SetFrameFillColor(-1)
gStyle.SetHistFillColor(-1)
gStyle.SetTitleFillColor(-1)
gStyle.SetFillColor(-1)
gStyle.SetFillStyle(4000)
gStyle.SetStatStyle(0)
gStyle.SetTitleStyle(0)
gStyle.SetCanvasBorderSize(0)
gStyle.SetFrameBorderSize(0)
gStyle.SetLegendBorderSize(0)
gStyle.SetStatBorderSize(0)
gStyle.SetTitleBorderSize(0)


INPUT_DIR = '/atlas/data4/userdata/wfawcett/delphes/results/fromLHE/'
INPUT_DIR = '/Users/Will/Documents/fcc/trackerSW/particleProperties/'
OUTPUD_BASE_DIR = "/Users/Will/Documents/fcc/trackerSW/plotting/TrackPlots2"

def main(verbose):

    samples = ['mg_pp_hh', 'py8_pp_minbias']
    samples += ['mg_pp_tth']
    #samples = ['py8_pp_minbias']
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

    
    can = TCanvas("can", "can", 500, 500)

    # plot acceptances for (all) signal models for each of the track multiplicities
    for pu in pileups:
        TRACK = False
        hhFName = INPUT_DIR+'mg_pp_hh_pu{0}.root'.format(pu)
        tthFName = INPUT_DIR+'mg_pp_tth_pu{0}.root'.format(pu)
        print 'opening file', hhFName
        hhFile  = TFile.Open(hhFName)
        tthFile = TFile.Open(tthFName)
        if TRACK: 
            theBranchNames = trackBranchNames
        else:
            theBranchNames = jetBranchNames
        for branch in theBranchNames:
            for i in xrange(1, 5):
                if TRACK:
                    histName = '{1}_track{0}Pt'.format(i, branch)
                else:
                    histName = '{1}_jet{0}Pt'.format(i, branch)

                hhPlot_base  = hhFile.Get(histName)
                #tthPlot = getReverseCumulativeHisto(tthFile.Get(histName))
                tthPlot_base = tthFile.Get(histName)
                
                print type(hhPlot_base)
                
                hhPlot = getReverseCumulativeHisto(hhPlot_base)
                tthPlot = getReverseCumulativeHisto(tthPlot_base)



                REBIN = 1
                hhPlot.Rebin(REBIN)
                tthPlot.Rebin(REBIN)
                hhPlot.SetLineColor(colours.darkRed)
                hhPlot.SetMarkerColor(colours.darkRed)
                tthPlot.SetLineColor(colours.darkBlue)
                tthPlot.SetMarkerColor(colours.darkBlue)

                hhPlot.SetMarkerStyle(24)
                tthPlot.SetMarkerStyle(32)

                # Legend
                aLeg = TLegend(0.57, 0.55, 0.85, 0.7) 
                aLeg.SetTextSize(TEXT_SIZE)
                aLeg.AddEntry(hhPlot, 'HH', 'lp') 
                aLeg.AddEntry(tthPlot, 'ttH', 'lp')

                xaxis = hhPlot.GetXaxis()
                yaxis = hhPlot.GetYaxis()
                yaxis.SetTitle('Acceptance')

            
                # For tracks
                if TRACK: 
                    xaxis.SetTitle('Track {0}'.format(i)+' p_{T} [GeV]')
                    xaxis.SetRangeUser(0, 175)
                    if i==1:
                        xaxis.SetRangeUser(0, 175)
                    if i==2:
                        xaxis.SetRangeUser(0, 150)
                    if i==3:
                        xaxis.SetRangeUser(0, 70)
                    if i==4: 
                        xaxis.SetRangeUser(0, 50)
                else:
                    # for jets
                    xaxis.SetTitle('Jet {0}'.format(i)+' p_{T} [GeV]')
                    xaxis.SetRangeUser(0, 500)
                    if i==1:
                        xaxis.SetRangeUser(0, 600)
                    if i==2:
                        xaxis.SetRangeUser(0, 500)
                    if i==3:
                        xaxis.SetRangeUser(0, 500)
                    if i==4: 
                        xaxis.SetRangeUser(0, 400)
                #yaxis.SetRangeUser(0, 1)


                hhPlot.Draw()
                myText(0.57, 0.84, '#sqrt{s} = 100 TeV', TEXT_SIZE)
                myText(0.57, 0.78, 'Madgraph+pythia8', TEXT_SIZE)
                myText(0.57, 0.72, '#LT#mu#GT = {0}'.format(pu), TEXT_SIZE)
                myText(0.6, 0.5, '|#eta| < 2.0', TEXT_SIZE)
                tthPlot.Draw('same')
                aLeg.Draw()

                
                can.SaveAs(OUTPUD_BASE_DIR+'/signalAcceptances/{2}_pu{0}_jet{1}Pt.pdf'.format(pu, i, branch))

    return 

    for sample in samples:
        print 'Plotting for sample', sample
        for pileup in pileups:

            print '\tPlotting for pileup', pileup

            iFileName = INPUT_DIR + '{0}_pu{1}.root'.format(sample, pileup)
            iFile = TFile.Open(iFileName)
            plotDict = {}

            outputBaseDir = OUTPUD_BASE_DIR+'/{0}_pu{1}/'.format(sample, pileup)
            checkDir(outputBaseDir)


            for branch in trackBranchNames+jetBranchNames:
                print '\t\tPlotting for branch', branch
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
                    #print xTitle
                    h0.GetXaxis().SetTitle(xTitle+" [GeV]")
                    h0.GetYaxis().SetTitle("Fraction of events")
                    h0.Draw()
                    nbins = h0.GetNbinsX()
                    #print h0.Integral()
                    #print h0.Integral(1, nbins)
                    #print h0.Integral(1, nbins+1) # should include overflow
                    #print ''

                    # plot acceptance
                    can.SaveAs(outputDir+plot+".pdf")


                    #acceptance = h0.GetCumulative(False)
                    acceptance = getReverseCumulativeHisto(h0)

                    xaxis = acceptance.GetXaxis()
                    yaxis = acceptance.GetYaxis()

                    xaxis.SetTitle(xTitle+" [GeV]")
                    yaxis.SetTitle("Acceptance")
                    if 'jet' in branch.lower():
                        xaxis.SetRangeUser(200, 600) 
                    else:
                        xaxis.SetRangeUser(0, 100)

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

            #print plotDict

            gStyle.SetGridStyle(3) 
            gStyle.SetGridColor(kGray)
            #can = TCanvas("can2", "can2", 500, 500)
            can.SetGrid()

            # plot trigger rates (for minbias) in the different scenarios 
            s1 = {
                    #"TruthTrack",
                    "Track"            : {'marker' : 20, 'colour' : colours.red,  'leg' : 'All tracks'},
                    "PBMatchedTracks"  : {'marker' : 23, 'colour' : colours.blue, 'leg' : 'Tracks from PB' }
                    }
            s2 = {
                    'SmearedTrackJets'   : {'marker' : 20, 'colour' : colours.red, 'leg' : 'All tracks' },
                    'PBMatchedTrackJets' : {'marker' : 23, 'colour' : colours.blue,'leg' : 'Tracks from PB' }
                    }
            s3 = {  
                    'SmearedHitTrackJets' : {'marker' : 20, 'colour' : colours.red, 'leg' : 'All tracks'},
                    'PBMatchedHitTrackJets' : {'marker' : 23, 'colour' : colours.blue, 'leg': 'Tracks from PB' }
                    }
            s4 = {
                    'SmearedTracksFromHits' : {'marker' : 20, 'colour' : colours.red, 'leg' : 'All tracks'},
                    'PBMatchedHitTracks' : {'marker' : 23, 'colour' : colours.blue, 'leg': 'Tracks from PB' }

                    }

            s00 = [
                 "TracksFromHit30",
                 "SmearedTracksFromHits",
                 "PBMatchedHitTracks",
                 ]


            ############################
            # Make plots of trigger rate
            ############################

            can.SetLogy()
            for scenarioSet in [s1, s2, s3, s4]:
                # scenario set contains the "nominal" objects and the PB matched objects
                outputDir = outputBaseDir+"Rates/"
                checkDir(outputDir)
                outputDir = outputDir+scenarioSet.keys()[0]+'/'
                checkDir(outputDir)

                plots = plotDict[scenarioSet.keys()[0]].keys()

                for plot in plots:
                    pCounter = 0
                    #leg = prepareLegend('topRight')
                    leg = TLegend(0.55, 0.55, 0.8, 0.70)
                    leg.SetTextSize(TEXT_SIZE)
                    for scenario in scenarioSet.keys():
                        
                        # get style dict
                        style = scenarioSet[scenario]
                            
                        # scale to trigger rate
                        rate = plotDict[scenario][plot]['acceptance']
                        titleInfo = sampleInfo[sample]
                        rate.Scale(40*1e3) # scale to 40 MHz (appropriate for minbias, not for other samples)  

                        # style 
                        #rate.SetTitle("{0} #LT#mu#GT = {1}".format(titleInfo['title'], pileup))
                        xaxis = rate.GetXaxis()
                        yaxis = rate.GetYaxis()
                        yaxis.SetTitle('Rate [kHz]')
                        myText(0.55, 0.80, '#sqrt{s} = 100 TeV', TEXT_SIZE)
                        myText(0.55, 0.75, '{0}'.format(titleInfo['title']), TEXT_SIZE)
                        myText(0.55, 0.70, "#LT#mu#GT = {0}".format(pileup), TEXT_SIZE)

                        if 'track' in plot:
                            xaxis.SetRangeUser(0, 175)
                            if '1Pt' in plot:
                                xaxis.SetRangeUser(0, 175)
                            if '2Pt' in plot: 
                                xaxis.SetRangeUser(0, 150)
                            if '3Pt' in plot:
                                xaxis.SetRangeUser(0, 70)
                            if '4Pt' in plot:
                                xaxis.SetRangeUser(0, 50)
                        if 'jet' in plot:
                            xaxis.SetRangeUser(0, 300)

                        rate.SetMarkerStyle(style['marker'])
                        rate.SetMarkerColor(style['colour'])
                        rate.SetLineColor(style['colour'])

                        if pCounter == 0:
                            rate.Draw()
                            #elif 'jet' in plot: # only draw PU supressed for jet histograms 
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
