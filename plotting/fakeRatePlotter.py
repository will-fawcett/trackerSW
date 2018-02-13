from ROOT import *
from colours import colours
from utils import prepareLegend
import os
import math

gROOT.SetBatch(1)
gStyle.SetPadBottomMargin(0.15)
gStyle.SetPadLeftMargin(0.13) # increase space for left margin
gStyle.SetPadTickX(1)
gStyle.SetPadTickY(1)

if os.environ["isGeneva"]:
    path = "/atlas/users/wfawcett/fcc/delphes/results/hits/"
else:
    path = "/Users/Will/Desktop/hits/"

outputDir = "FakeRate/"

cols = {
        10: colours.blue,
        20: colours.orange,
        30: colours.red,
        40: colours.green,
        50: colours.grey
    }

#______________________________________________________________________________
def main():

    geometries = [10, 20, 30, 40, 50]
    pileups = [0]
    pileups = [0, 200, 1000]


    for PILEUP in pileups:
        fName = path+"hits_ttbar_pu{0}_multiGeometry.root".format(PILEUP) 
        print "Opening file:", fName
        ifile = TFile.Open(fName)
        efficiency(ifile, PILEUP, geometries) 
        fakeRates(ifile, PILEUP, geometries, "Pt")
        fakeRates(ifile, PILEUP, geometries, "Eta")
        ifile.Close()

    
    efficiencySummaries = {}
    fakeRateSummaries   = {}
    for geometry in geometries:
        efficiencySummary = TGraphErrors()
        fakeRateSummary = TGraphErrors()
        counter = 0
        pileups = [0, 200, 300, 400, 500, 600, 700, 800, 900, 1000]
        for PILEUP in pileups:
            fName = path+"hits_ttbar_pu{0}_multiGeometry.root".format(PILEUP) 
            ifile = TFile.Open(fName)
            [efficiencyMean, efficiencyError, fakeRate, fakeRateError] = numberOfTracks(ifile, PILEUP, geometry)

            print "adding point", counter, PILEUP, efficiencyMean
            efficiencySummary.SetPoint(counter, PILEUP, efficiencyMean) 
            efficiencySummary.SetPointError(counter, 0, efficiencyError)
            efficiencySummary.SetMarkerColor( cols[geometry] )
            efficiencySummary.SetLineColor( cols[geometry] )
            efficiencySummary.SetMarkerStyle(20)

            fakeRateSummary.SetPoint(counter, PILEUP, fakeRate) 
            fakeRateSummary.SetPointError(counter, 0, fakeRateError)
            fakeRateSummary.SetMarkerColor( cols[geometry] )
            fakeRateSummary.SetLineColor( cols[geometry] )

            efficiencySummaries[geometry] = efficiencySummary
            fakeRateSummaries[geometry] = fakeRateSummary
            ifile.Close()

            counter += 1
    

    ########################
    # Draw the summary plots
    ########################

    # Multigraph for efficiency
    effMulti = TMultiGraph()
    newCan = TCanvas("newCan", "", 500, 500)
    newCan.SetLeftMargin(0.15)
    for geometry in geometries:
        effMulti.Add( efficiencySummaries[geometry], 'p')
        effMulti.SetTitle(";Pileup;Average track reconstruction efficiency")
        effMulti.Draw('a')
    newCan.SaveAs(outputDir+"EfficiencySummary.pdf")
    newCan.Clear()

    # Multigraph for fakes 
    fakeMulti = TMultiGraph()
    for geometry in geometries:
        fakeMulti.Add( fakeRateSummaries[geometry], 'p')
        fakeMulti.SetTitle(";Pileup;Average fake rate")
        fakeMulti.Draw('a')
    newCan.SaveAs(outputDir+"FakeRateSummary.pdf")








def drawAndSave(hist, name):
    can = TCanvas("can", "can", 500, 500)   
    hist.GetXaxis().SetRangeUser(0, 100)
    hist.Draw()
    can.SaveAs(name)

def binInfo(h1, h2):
    for ibin in range(h1.GetNbinsX()):
        print ibin, h1.GetBinContent(ibin), h2.GetBinContent(ibin), h1.GetBinContent(ibin)-h2.GetBinContent(ibin) 

#______________________________________________________________________________
def efficiency(ifile, PILEUP, geometries):

    can = TCanvas("can", "can", 500, 500)   

    leg = prepareLegend("bottomRight")
    #leg = prepareLegend("bottomLeft")
    ratios = {}
    for geometry in geometries:

        # Number of matched tracks in given pT bin 
        nHitsPt = ifile.Get("nHitsPt_{0}".format(geometry)).Clone()
        nHitsPt.Sumw2()
        #drawAndSave(nHitsPt, "nHitsPt.pdf")

        # Number of true tracks as a function of pT 
        recoTrackPt_true = ifile.Get("recoTrackPt_true_{0}".format(geometry)).Clone()
        recoTrackPt_true.Sumw2() 
        #drawAndSave(recoTrackPt_true, "recoTrackPt_true.pdf")

        # Rebin
        REBIN = 1 
        recoTrackPt_true.Rebin(REBIN)
        nHitsPt.Rebin(REBIN)

        #binInfo(nHitsPt, recoTrackPt_true)

        # Reconstruction efficiency 
        #recoEfficiency = TGraphAsymmErrors( recoTrackPt_true, nHitsPt )
        recoEfficiency = recoTrackPt_true.Clone()
        recoEfficiency.Divide( nHitsPt )
        recoEfficiency.SetTitle("Pileup {0}".format(PILEUP))
        recoEfficiency.SetMarkerColor(cols[geometry])
        recoEfficiency.SetLineColor(cols[geometry])
        yaxis = recoEfficiency.GetYaxis()
        xaxis = recoEfficiency.GetXaxis()
        xaxis.SetRangeUser(0, 50)
        yaxis.SetRangeUser(0, 1.3)
        xaxis.SetTitle("Track p_{T} [GeV]")
        yaxis.SetTitle("Reconstruction efficiency")

        ratios[geometry] = recoEfficiency

        
        if geometry == 10:
            recoEfficiency.Draw("PE")
        else:
            recoEfficiency.Draw("PEsame")

    for geometry in geometries:

        leg.AddEntry(ratios[geometry], "{0} mm".format(geometry), 'lp')

    leg.Draw()
    can.SaveAs(outputDir+"efficiency_Pt_pu{0}.pdf".format(PILEUP))

#______________________________________________________________________________
def fakeRates(ifile, PILEUP, geometries, label):
    can = TCanvas("can", "can", 500, 500)   

    fakeRates = {} 
    leg = prepareLegend('topLeft')
    for geometry in geometries:
        nReco = ifile.Get("recoTrack{0}_{1}".format(label, geometry)).Clone()
        nReco.Sumw2()
        nRecoFake = ifile.Get("recoTrack{0}_fake_{1}".format(label, geometry)).Clone()
        nRecoFake.Sumw2()

        if label == "Pt":
            REBIN = 5
        elif label == "Eta":
            REBIN = 2

        nReco.Rebin(REBIN)
        nRecoFake.Rebin(REBIN)

        fakeRate = nRecoFake.Clone()
        fakeRate.Divide(nReco)
        fakeRates[geometry] = fakeRate

        xaxis = fakeRate.GetXaxis()
        yaxis = fakeRate.GetYaxis()
        if label == "Pt":
            xaxis.SetRangeUser(0, 100)
            xaxis.SetTitle("Reconstructed Track p_{T} [GeV]")
        elif label == "Eta":
            xaxis.SetRangeUser(-2.5, 2.5)
            xaxis.SetTitle("Reconstructed Track #eta")

        # y-range 
        yaxis.SetRangeUser(0, 0.35)

        yaxis.SetTitle("Fake Rate")
        fakeRate.SetTitle("Pileup {0}".format(PILEUP))

        leg.AddEntry(fakeRate, "{0} mm".format(geometry), "lp")
        fakeRate.SetMarkerColor(cols[geometry]) 
        fakeRate.SetLineColor(cols[geometry])
        
        if geometry == 10:
            fakeRate.Draw("PE")
        else: 
            fakeRate.Draw("PEsame")

    leg.Draw() 
    can.SaveAs(outputDir+"fakeRate_{0}_pu{1}.pdf".format(label, PILEUP))


#______________________________________________________________________________
def numberOfTracks(ifile, PILEUP, geometry):

    can = TCanvas("can", "can", 500, 500)
    # histograms
    #nDelphesTracks = ifile.Get("nDelphesTracks")
    #nDelphesTracks1GeV = ifile.Get("nDelphesTracks1GeV")
    #nDelphesTracks10GeV = ifile.Get("nDelphesTracks10GeV")

    nRecoTracks = ifile.Get("nRecoTracks_"+str(geometry))
    nRecoTracksMatched = ifile.Get("nRecoTracksMatched_"+str(geometry))
    nDelphesHits = ifile.Get("nDelphesHits_"+str(geometry))

    # stats
    baseHistogram = nDelphesHits.Clone();

    # styling
    REBIN = 10
    baseHistogram.Draw()
    can.Update()
    ymax2 = gPad.GetUymax()
    xaxis = baseHistogram.GetXaxis()
    yaxis = baseHistogram.GetYaxis()
    xaxis.SetNdivisions(5, 5, 0)
    yaxis.SetTitle("Frequency")
    xaxis.SetTitle("Number of tracks")
    baseHistogram.SetLineColor(colours.blue)
    baseHistogram.SetMarkerSize(0)
    baseHistogram.SetTitle("Triplet spacing {1} mm, Pileup {0}".format(PILEUP, geometry))
    baseHistogram.Rebin(REBIN)

    yaxis.SetRangeUser(0, baseHistogram.GetMaximum()*1.3)
    xaxis.SetRangeUser(0, 500)

    # Add legend and other plots
    leg = prepareLegend("topRight")
    addLegendEntry(leg, baseHistogram, "Hits")

    addPlot(nRecoTracks, colours.green, REBIN, leg, "Reco")
    addPlot(nRecoTracksMatched, colours.red, REBIN, leg, "Reco matched")
    leg.Draw()

    can.SaveAs(outputDir+"trackComparrison_pu{0}_geometry{1}.pdf".format(PILEUP, geometry))

    # Calculate mean efficiency 
    efficiency = nRecoTracksMatched.GetMean() / nDelphesHits.GetMean() 
    efficiencyError = efficiency * math.sqrt( (nRecoTracksMatched.GetMeanError()/nRecoTracksMatched.GetMean() )**2 + (nDelphesHits.GetMeanError()/nDelphesHits.GetMean())**2 ) 
    
    # Calculate mean fake rate 
    nFakesMean = nRecoTracks.GetMean() - nRecoTracksMatched.GetMean()
    nFakesError = math.sqrt( nRecoTracks.GetMeanError()**2 + nRecoTracksMatched.GetMean()**2 )

    fakeRate =  nFakesMean / ( nRecoTracks.GetMean() )   
    fakeRateError = fakeRate * math.sqrt( (nFakesError/nFakesMean)**2 + ( nRecoTracks.GetMeanError()/nRecoTracks.GetMean()  ) ) 



    return [efficiency, efficiencyError, fakeRate, fakeRateError]  

#______________________________________________________________________________
def addLegendEntry(leg, hist, text):
    leg.AddEntry(hist, text, "l")
    leg.AddEntry(0, "mean : {0}".format(round(hist.GetMean())), "")
    #stdDevDelphesTracks = nDelphesTracks1GeV.GetStdDev() # standard deviation not used

#______________________________________________________________________________
def addPlot(histogram, colour, REBIN, legend, legendEntry):
    histogram.SetLineColor(colour)
    histogram.SetMarkerSize(0)
    histogram.Rebin(REBIN)
    histogram.Draw("same")
    addLegendEntry(legend, histogram, legendEntry)
    


#______________________________________________________________________________
if __name__ == "__main__":
    main()
