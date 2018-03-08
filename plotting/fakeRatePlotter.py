from ROOT import *
from colours import colours
from utils import prepareLegend
import os
import math
from array import array

gROOT.SetBatch(1)
gStyle.SetPadBottomMargin(0.15)
gStyle.SetPadLeftMargin(0.13) # increase space for left margin
gStyle.SetPadTickX(1)
gStyle.SetPadTickY(1)

if os.environ["isGeneva"]:
    path = "/atlas/users/wfawcett/fcc/delphes/results/"
    #path += "hits_tolerance01mm_phi1GeV/"
    #path += "hits_tolerance1mm_phi2GeV/"
    #path += "hits_phiEtaSeg_tolerance1mm_phi2GeV/"
    #path += "hits_phiEtaSeg_tolerance01mm_phi2GeV/"
    #path += "hits_phiEtaSeg_tolerance01mm_phi2GeV_curvature001/"
    #path += "hits_phiEtaSeg_tolerance01mm_phi2GeV_curvature0005/"
    #path += "hits_phiEtaSeg_tolerance05mm_phi2GeV_curvature0005/"
    path += "hits_phiEtaSeg_tolerance05mm_phi2GeV_curvature0005_nVertexSigma5/"
else:
    path = "/Users/Will/Desktop/hits/"

outputDir = "FakeRate/"
outputDir = "FakeRate_tolerance01mm_phi1GeV/"
outputDir = "FakeRate_tolerance1mm_phi2GeV/"
outputDir = "FakeRate_phiEta_tolerance1mm_phi2GeV/"
outputDir = "FakeRate_phiEta_tolerance01mm_phi2GeV/"
outputDir = "FakeRate_phiEta_tolerance01mm_phi2GeV_curvature001/"
outputDir = "FakeRate_phiEta_tolerance01mm_phi2GeV_curvature0005/"
outputDir = "FakeRate_phiEta_tolerance05mm_phi2GeV_curvature0005/"
outputDir = "FakeRate_phiEta_tolerance05mm_phi2GeV_curvature0005_nVertexSigma5/"

cols = {
        10: colours.blue,
        20: colours.orange,
        30: colours.red,
        40: colours.green,
        50: colours.grey
    }

binslist  = [0.0, 5.0, 10.0, 15.0, 20.0, 25.0, 30.0, 35.0, 40.0, 50, 60, 80, 100] 
binsarray = array('d', binslist)


#______________________________________________________________________________
def main():

    geometries = [10, 20, 30, 40, 50]
    pileups = [0, 200, 1000]
    pileups = [0, 100, 200, 300]
    pileups = [0, 100, 1000]
    pileups = [400]
    pileups = [0, 100]
    pileups = [0, 1000]
    pileups = [0, 100, 200, 400, 500]
    pileups = [0, 100, 200]
    pileups = [0, 100, 200, 300, 400, 500, 700, 800, 900, 1000]


    # For each pileup scenario, plot:
    # efficiency v pT
    # fake rate v pT
    # fake rate v eta 
    # with a multigraph for each geometry 
    for PILEUP in pileups:
        #fName = "/atlas/users/wfawcett/fcc/delphes/test.root"
        fName = path+"hits_ttbar_pu{0}_multiGeometry.root".format(PILEUP) 
        print "Opening file:", fName
        ifile = TFile.Open(fName)
        efficiency(ifile, PILEUP, geometries, "Pt") 
        #efficiency(ifile, PILEUP, geometries, "EtaPt2") 
        fakeRates(ifile, PILEUP, geometries, "Pt")
        #fakeRates(ifile, PILEUP, geometries, "Eta") # Eta probably not calculated correctly
        ifile.Close()

    
    # Make summary plots for efficiency and fake rate 
    efficiencySummaries = {}
    fakeRateSummaries   = {}
    efficiencySummariesPt2 = {}
    fakeRateSummariesPt2   = {}
    for geometry in geometries:
        efficiencySummary = TGraphErrors()
        fakeRateSummary   = TGraphErrors()
        efficiencySummaryPt2 = TGraphErrors()
        fakeRateSummaryPt2   = TGraphErrors()
        counter = 0
        for PILEUP in pileups:
            #fName = "/atlas/users/wfawcett/fcc/delphes/test.root"
            fName = path+"hits_ttbar_pu{0}_multiGeometry.root".format(PILEUP) 
            ifile = TFile.Open(fName)
            # plot histogram of number of tracks (all reconstructed, fake, nHits)
            [efficiencyMean, efficiencyError, fakeRate, fakeRateError] = numberOfTracks(ifile, PILEUP, geometry)
            [efficiencyMeanPt2, efficiencyErrorPt2, fakeRatePt2, fakeRateErrorPt2] = numberOfTracks(ifile, PILEUP, geometry, 2)

            efficiencySummary.SetPoint(counter, PILEUP, efficiencyMean) 
            efficiencySummary.SetPointError(counter, 0, efficiencyError)
            efficiencySummary.SetMarkerColor( cols[geometry] )
            efficiencySummary.SetLineColor( cols[geometry] )
            efficiencySummary.SetMarkerStyle(20)

            efficiencySummaryPt2.SetPoint(counter, PILEUP, efficiencyMeanPt2) 
            efficiencySummaryPt2.SetPointError(counter, 0, efficiencyErrorPt2)
            efficiencySummaryPt2.SetMarkerColor( cols[geometry] )
            efficiencySummaryPt2.SetLineColor( cols[geometry] )
            efficiencySummaryPt2.SetMarkerStyle(20)

            #print 'pileup {0}, fake rate {1}, error {2}'.format(PILEUP, fakeRate, fakeRateError) 
            fakeRateSummary.SetPoint(counter, PILEUP, fakeRate) 
            fakeRateSummary.SetPointError(counter, 0, fakeRateError)
            fakeRateSummary.SetMarkerColor( cols[geometry] )
            fakeRateSummary.SetMarkerStyle(20)
            fakeRateSummary.SetLineColor( cols[geometry] )

            fakeRateSummaryPt2.SetPoint(counter, PILEUP, fakeRatePt2) 
            fakeRateSummaryPt2.SetPointError(counter, 0, fakeRateErrorPt2)
            fakeRateSummaryPt2.SetMarkerColor( cols[geometry] )
            fakeRateSummaryPt2.SetMarkerStyle(20)
            fakeRateSummaryPt2.SetLineColor( cols[geometry] )

            efficiencySummaries[geometry] = efficiencySummary
            fakeRateSummaries[geometry] = fakeRateSummary

            efficiencySummariesPt2[geometry] = efficiencySummaryPt2
            fakeRateSummariesPt2[geometry]   = fakeRateSummaryPt2

            ifile.Close()

            counter += 1
    

    ########################
    # Draw the summary plots
    ########################

    newCan = TCanvas("newCan", "", 500, 500)
    newCan.SetLeftMargin(0.15)

    # Multigraph for efficiency
    effMulti = TMultiGraph()
    leg = prepareLegend("topRight")
    for geometry in geometries:
        effMulti.Add( efficiencySummaries[geometry], 'p')
        effMulti.SetTitle(";Pileup;Average track reconstruction efficiency")
        effMulti.Draw('a')
        leg.AddEntry(efficiencySummaries[geometry], '{0} mm'.format(geometry), 'lp') 
    leg.Draw()
    effMulti.GetHistogram().GetYaxis().SetTitleOffset(1.75)
    newCan.SaveAs(outputDir+"EfficiencySummary.pdf")
    newCan.Clear()

    # Multigraph for efficiency with pT>2 GeV
    effMultiPt2 = TMultiGraph()
    leg = prepareLegend("topRight")
    for geometry in geometries:
        effMultiPt2.Add( efficiencySummariesPt2[geometry], 'p')
        effMultiPt2.SetTitle("p_{T} > 2 GeV;Pileup;Average track reconstruction efficiency")
        effMultiPt2.Draw('a')
        leg.AddEntry(efficiencySummariesPt2[geometry], '{0} mm'.format(geometry), 'lp') 
    leg.Draw()
    effMultiPt2.GetHistogram().GetYaxis().SetTitleOffset(1.75)
    newCan.SaveAs(outputDir+"EfficiencySummaryPt2.pdf")
    newCan.Clear()


    # Multigraph for fakes 
    fakeMulti = TMultiGraph()
    leg = prepareLegend("topLeft")
    for geometry in geometries:
        fakeMulti.Add( fakeRateSummaries[geometry], 'p')
        fakeMulti.SetTitle(";Pileup;Average fake rate")
        fakeMulti.Draw('a')
        leg.AddEntry(fakeRateSummaries[geometry], '{0} mm'.format(geometry), 'lp') 
    fakeMulti.GetHistogram().GetYaxis().SetTitleOffset(1.5)
    leg.Draw()
    newCan.SaveAs(outputDir+"FakeRateSummary.pdf")

    # Multigraph for fakes with pT>2GeV 
    fakeMultiPt2 = TMultiGraph()
    leg = prepareLegend("topLeft")
    for geometry in geometries:
        fakeMultiPt2.Add( fakeRateSummariesPt2[geometry], 'p')
        fakeMultiPt2.SetTitle("p_{T} > 2 GeV;Pileup;Average fake rate")
        fakeMultiPt2.Draw('a')
        leg.AddEntry(fakeRateSummariesPt2[geometry], '{0} mm'.format(geometry), 'lp') 
    fakeMultiPt2.GetHistogram().GetYaxis().SetTitleOffset(1.5)
    leg.Draw()
    newCan.SaveAs(outputDir+"FakeRateSummaryPt2.pdf")

#______________________________________________________________________________
def drawAndSave(hist, name):
    can = TCanvas("can", "can", 500, 500)   
    hist.GetXaxis().SetRangeUser(0, 100)
    hist.Draw()
    can.SaveAs(name)

#______________________________________________________________________________
def binInfo(h1, h2):
    print '{0}\t{1}\t{2}\t{3}'.format('ibin', 'h1', 'h2', 'h1-h2')
    for ibin in range(h1.GetNbinsX()):
        print '{0}\t{1}\t{2}\t{3}'.format(ibin, h1.GetBinContent(ibin), h2.GetBinContent(ibin), h1.GetBinContent(ibin)-h2.GetBinContent(ibin) )

#______________________________________________________________________________
def efficiency(ifile, PILEUP, geometries, label="Pt"):

    can = TCanvas("can", "can", 500, 500)   

    leg = prepareLegend("bottomRight")
    #leg = prepareLegend("bottomLeft")
    ratios = {}
    for geometry in geometries:

        #print 'pu, geo', PILEUP, geometry

        # Number of matched tracks in given pT bin 
        denominatorLabel = "nHits{0}_{1}".format(label, geometry)
        nHitsPt = ifile.Get(denominatorLabel).Clone()
        nHitsPt.Sumw2()
        #drawAndSave(nHitsPt, "nHitsPt.pdf")

        # Number of true tracks as a function of pT 
        #recoTrackPt_true = ifile.Get("recoTrackPt_true_{0}".format(geometry)).Clone()
        numeratorLabel = "recoTrackHit{0}_true_{1}".format(label, geometry)
        recoTrackPt_true = ifile.Get(numeratorLabel).Clone()
        recoTrackPt_true.Sumw2() 

        #print denominatorLabel, numeratorLabel 
        #drawAndSave(recoTrackPt_true, "recoTrackPt_true.pdf")

        # Rebin
        REBIN = 1 
        recoTrackPt_true.Rebin(REBIN)
        nHitsPt.Rebin(REBIN)

        #binInfo(nHitsPt, recoTrackPt_true)

        # Reconstruction efficiency 
        UseTGraph = True
        if UseTGraph:
            recoEfficiency = TGraphAsymmErrors( recoTrackPt_true, nHitsPt )
        else:
            recoEfficiency = recoTrackPt_true.Clone()
            recoEfficiency.Divide( nHitsPt )
        recoEfficiency.SetTitle("Pileup {0}".format(PILEUP))
        recoEfficiency.SetMarkerColor(cols[geometry])
        recoEfficiency.SetLineColor(cols[geometry])
        yaxis = recoEfficiency.GetYaxis()
        xaxis = recoEfficiency.GetXaxis()
        if label == "Pt": 
            xaxis.SetRangeUser(0, 50)
            yaxis.SetRangeUser(0.8, 1.1)
            xaxis.SetTitle("Track (hit) p_{T} [GeV]")
        elif label == "EtaPt2":
            xaxis.SetRangeUser(-3, 3)
            xaxis.SetTitle("Track (hit) #eta")
            #yaxis.SetRangeUser(0.8, 1.1)

        yaxis.SetTitle("Reconstruction efficiency")
        ratios[geometry] = recoEfficiency
        
        if geometry == 10:
            if UseTGraph:
                recoEfficiency.Draw("APEl")
            else:
                recoEfficiency.Draw("PEl")
        else:
            recoEfficiency.Draw("PElsame")

    for geometry in geometries:

        leg.AddEntry(ratios[geometry], "{0} mm".format(geometry), 'lp')

    leg.Draw()
    can.SaveAs(outputDir+"efficiency_{0}_pu{1}.pdf".format(label, PILEUP))

#______________________________________________________________________________
def fakeRates(ifile, PILEUP, geometries, label):
    '''
    Create plot of fake rate as a function of <label> (e.g. pT) 
    Fake rate = number of fakes / number of reco tracks [in a given pT bin] 
    (i.e. the fraction of reconstructed tracks that are fake)
    '''
    can = TCanvas("can", "can", 500, 500)   

    fakeRates = {} 
    leg = prepareLegend('topLeft')
    for geometry in geometries:
        nReco = ifile.Get("recoTrack{0}_{1}".format(label, geometry)).Clone()
        nReco.Sumw2()
        nRecoFake = ifile.Get("recoTrack{0}_fake_{1}".format(label, geometry)).Clone()
        nRecoFake.Sumw2()

        if label == "Pt":
            REBIN = 10
        elif label == "Eta":
            REBIN = 2


        nReco.Rebin(REBIN)
        nRecoFake.Rebin(REBIN)

        # rebin for variable bin widths
        nReco     = rebin_plot(nReco,     binsarray)
        nRecoFake = rebin_plot(nRecoFake, binsarray) 

        fakeRate = TGraphAsymmErrors(nRecoFake, nReco)
        #fakeRate = nRecoFake.Clone()
        #fakeRate.Divide(nReco)
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
        yaxis.SetRangeUser(0, 0.25)
        yaxis.SetTitleOffset(1.5)

        yaxis.SetTitle("Fake Rate")
        fakeRate.SetTitle("Pileup {0}".format(PILEUP))

        leg.AddEntry(fakeRate, "{0} mm".format(geometry), "lp")
        fakeRate.SetMarkerColor(cols[geometry]) 
        fakeRate.SetLineColor(cols[geometry])
        
        if geometry == 10:
            fakeRate.Draw("APE")
        else: 
            fakeRate.Draw("PEsame")

    leg.Draw() 
    can.SaveAs(outputDir+"fakeRate_{0}_pu{1}.pdf".format(label, PILEUP))


#______________________________________________________________________________
def numberOfTracks(ifile, PILEUP, geometry, PT=None):

    can = TCanvas("can", "can", 500, 500)

    # get histograms 
    if PT:
        nRecoTracks = ifile.Get("nRecoTracksPt{0}_{1}".format(PT, geometry))
        nRecoTracksMatched = ifile.Get("nRecoTracksMatchedPt{0}_{1}".format(PT, geometry))
        nDelphesHits = ifile.Get("nDelphesHitsPt{0}_{1}".format(PT, geometry))
    else:
        nRecoTracks = ifile.Get("nRecoTracks_"+str(geometry))
        nRecoTracksMatched = ifile.Get("nRecoTracksMatched_"+str(geometry))
        nDelphesHits = ifile.Get("nDelphesHits_"+str(geometry))

    # stats
    baseHistogram = nDelphesHits.Clone();

    # styling
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


    x_range = (0, 5000)
    if PILEUP==0:
        x_range = (0, 500)
        REBIN = 1
    elif PILEUP == 100:
        x_range = (0, 2000)
        REBIN = 1 
    elif PILEUP==200:
        x_range = (1000, 3000)
        REBIN = 10 
    else:
        REBIN = 1 

    if PT:
        x_range = (0, 500)

    baseHistogram.Rebin(REBIN)
    baseHistogram.Draw() # draw again to make sure everything taken into account ... 

    # Add legend and other plots
    leg = prepareLegend("topRight")
    addLegendEntry(leg, baseHistogram, "Hits")
    addPlot(nRecoTracks, colours.green, REBIN, leg, "Reco")
    addPlot(nRecoTracksMatched, colours.red, REBIN, leg, "Reco matched")
    leg.Draw()

    xaxis.SetRangeUser(x_range[0], x_range[1])
    yaxis.SetRangeUser(0, baseHistogram.GetMaximum()*1.3)

    if PT:
        can.SaveAs(outputDir+"trackComparrison_pu{0}_geometry{1}_Pt{2}.pdf".format(PILEUP, geometry, PT))
    else:
        can.SaveAs(outputDir+"trackComparrison_pu{0}_geometry{1}.pdf".format(PILEUP, geometry))

    #efficiencyHist = nRecoTracksMatched.Clone()
    #efficiencyHist.Divide(nDelphesHits)
    #efficiency = efficiencyHist.GetMean()
    #efficiencyError = efficiencyHist.GetMeanError()
    #print '{0} pm {1}'.format(efficiency, efficiencyError) 
    
    # Calculate mean efficiency 
    efficiency = nRecoTracksMatched.GetMean() / nDelphesHits.GetMean() 
    efficiencyError = efficiency * math.sqrt( (nRecoTracksMatched.GetMeanError()/nRecoTracksMatched.GetMean() )**2 + (nDelphesHits.GetMeanError()/nDelphesHits.GetMean())**2 ) 
    #print '{0} pm {1}'.format(efficiency, efficiencyError) 
    
    # Calculate mean fake rate 
    nFakesMean = nRecoTracks.GetMean() - nRecoTracksMatched.GetMean()
    nFakesError = math.sqrt( nRecoTracks.GetMeanError()**2 + nRecoTracksMatched.GetMean()**2 )

    fakeRate =  nFakesMean / ( nRecoTracks.GetMean() )   
    fakeRateError = fakeRate * math.sqrt( (nFakesError/nFakesMean)**2 + ( nRecoTracks.GetMeanError()/nRecoTracks.GetMean()  ) ) 
    fakeRateError = 0 



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


#____________________________________________________________________________
def rebin_plot(histogram, bins_array):
    """Will rebin the histogram
    Draws a legend onto the plot with the specified histograms.

    Bin edges and overflow bins must be carefully considered, see the documentation
    https://root.cern.ch/doc/master/classTH1.html#aff6520fdae026334bf34fa1800946790
    Bin 0 contains the underflow
    Nbins+1 contains the overflow

    The Rebin function is also a bit messy:
    Double_t xbins[25] = {...} // array of low-edges (xbins[25] is the upper edge of last bin)
    h1->Rebin(24,"hnew",xbins);  //creates a new variable bin size histogram hnew

    Args:
        histogram: A single histogram
        bins_array: an array containing the list of bin edges
    """
    newname = histogram.GetName()+'_rebinned'
    newplot = histogram.Rebin(len(bins_array)-1, newname, bins_array)
    newplot.SetDirectory(0)

    return newplot

#______________________________________________________________________________
if __name__ == "__main__":
    main()
