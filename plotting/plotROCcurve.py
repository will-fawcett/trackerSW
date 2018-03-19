#!/usr/bin/python
'''
Script to read JSON files produced by c++ thing 
'''

from colours import colours
import json
from utils import rand_uuid, prepareLegend

from ROOT import *
gROOT.SetBatch(1)

gStyle.SetPadLeftMargin(0.15) # increase space for left margin
gStyle.SetPadTickX(1)
gStyle.SetPadTickY(1)

def main(verbose):

    BDTMode = False
    DeltaKappaMode = not BDTMode

    #pileups = range(0, 1100, 100)
    pileups = [100, 200, 1000]
    

    spacings = [
        "Tracks10", 
        "Tracks20",
        "Tracks30",
        "Tracks40",
        "Tracks50",
        ]
    
    colourMap = {
        "Tracks10" : colours.blue, 
        "Tracks20" : colours.orange, 
        "Tracks30" : colours.red, 
        "Tracks40" : colours.green,
        "Tracks50" : colours.grey
        }

    bdtCuts = [-0.7, -0.6, -0.5, -0.4, -0.3, -0.2, -0.1, 0, 0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 0.9]
    deltaKappaCuts = range(20, 301, 25)
    deltaKappaCuts = [float(x)/100000.0 for x in range(25, 201, 25) ] # would limit to 301, but already a harsher cut is implemented

    if BDTMode:
        cutList = bdtCuts
    else:
        cutList = deltaKappaCuts


    for PILEUP in pileups:

        can = TCanvas("can"+rand_uuid(), "can", 500, 500)
        theGraphs = {} 
        leg = prepareLegend("bottomLeft")
        for spacing in spacings: 
            print 'Drawing for spacing', spacing
            counter = 0
            theGraphs[spacing] = TGraph()
            theGraphs[spacing].SetMarkerColor(colourMap[spacing])
            theGraphs[spacing].SetLineColor(colourMap[spacing])
            theGraphs[spacing].SetMaximum(1)
            theGraphs[spacing].SetMinimum(0.995)
            theGraphs[spacing].SetMarkerStyle(20)
            leg.AddEntry(theGraphs[spacing], spacing, 'lp')
            print "Cut\t<efficiency>\t1-<fake rate>"
            for cut in cutList: 


                if BDTMode:
                    jFileName = "/atlas/data4/userdata/wfawcett/delphes/results/processedTracks_ROCscan_BDTspecific_{0}/hits_ttbar_pu{1}_multiGeometry.json".format(cut, PILEUP)
                else:
                    jFileName = "/atlas/data4/userdata/wfawcett/delphes/results/processedTracks_ROCscan_deltaKappa_{0}/hits_ttbar_pu{1}_multiGeometry.json".format(cut, PILEUP)
                #print 'reading', jFileName

                # load json file
                with open(jFileName) as data_file:
                    trackDict = json.load(data_file)

                # want to plot efficiency and fake rejection for tracks with pT > 2 
                trackInfo = trackDict[spacing] 

                # number of tracks surviving
                nFakesPt2 = float(trackInfo["FakeSurviving"]["Pt2"])
                nTruesPt2  = float(trackInfo["TrueSurviving"]["Pt2"])

                # fake rate is the fraction of (surviving) tracks that are fakes
                averageFakeRate = nFakesPt2 / ( nFakesPt2 + nTruesPt2) 

                # Average efficiency is fraction of true tracks surviving
                nTrueOriginalPt2 = float(trackInfo["TrueOriginal"]["Pt2"])
                averageEfficiency = nTruesPt2 / nTrueOriginalPt2

                print '{0} \t {1:.4f} \t {2:.4f}'.format(cut, averageEfficiency, 1-averageFakeRate)

                theGraphs[spacing].SetPoint(counter, averageEfficiency, 1-averageFakeRate)
                counter += 1
    
        #___________________________________________________________
        mg = TMultiGraph()
        for spacing in spacings:
            mg.Add(theGraphs[spacing], 'lp')
        if BDTMode:
            mg.SetTitle("BDT pileup={0};Average efficiency;1 - Fake Rate".format(PILEUP))
        if DeltaKappaMode:
            mg.SetTitle("|#Delta#kappa| pileup={0};Average efficiency;1 - Fake Rate".format(PILEUP))
        mg.Draw('a')
        leg.Draw()

        if BDTMode:
            can.SaveAs("BDT_ROC_pu{0}.pdf".format(PILEUP))
        if DeltaKappaMode:
            can.SaveAs("Dk_ROC_pu{0}.pdf".format(PILEUP))


if __name__ == "__main__":

    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("-v", "--verbose", help="Turn on verbose messages", action="store_true", default=False)
    args = parser.parse_args()
    verbose = args.verbose

    main(verbose)
