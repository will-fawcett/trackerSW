from ROOT import *
import json
from colours import colours
from utils import prepareLegend, checkDir, rand_uuid, myText
import os
import math
from array import array

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

if os.environ["isGeneva"]:
    basePath = "/atlas/users/wfawcett/fcc/delphes/results/"
    #plotDir = "hits_tolerance01mm_phi1GeV/"
    #plotDir = "hits_tolerance1mm_phi2GeV/"
    #plotDir = "hits_phiEtaSeg_tolerance1mm_phi2GeV/"
    #plotDir = "hits_phiEtaSeg_tolerance01mm_phi2GeV/"
    #plotDir = "hits_phiEtaSeg_tolerance01mm_phi2GeV_curvature0005/"
    #plotDir = "hits_phiEtaSeg_tolerance05mm_phi2GeV_curvature0005/"
    #plotDir = "hits_phiEtaSeg_tolerance05mm_phi2GeV_curvature0005_nVertexSigma5/"
    #plotDir = "processedTracks/"
    #plotDir = "hits_tolerance05mm_phi2GeV_multiCurvature_nVertexSigma5/"
    #plotDir = "hits_phiEtaSeg_tolerance01mm_phi2GeV_curvature001/"
    plotDir = "processedTracks_kappa_deltaPhi_zresiduum_BDT/"
    plotDir = "processedTracks_BDT07_both/"
    plotDir = "processedTracks_kappa_deltaPhi_zresiduum_BDT_specific/"
    plotDir = "processedTracks_kappa_deltaPhi_zresiduum_BDT07_specific/"
    plotDir = "processedTracks_kappa_deltaPhi_zresiduum/"
    path = basePath + plotDir
else:
    path = "/Users/Will/Desktop/hits/"

#outputDir = "FakeRate/"
#outputDir = "FakeRate_tolerance01mm_phi1GeV/"
#outputDir = "FakeRate_tolerance1mm_phi2GeV/"
#outputDir = "FakeRate_phiEta_tolerance1mm_phi2GeV/"
#outputDir = "FakeRate_phiEta_tolerance01mm_phi2GeV/"
#outputDir = "FakeRate_phiEta_tolerance01mm_phi2GeV_curvature0005/"
#outputDir = "FakeRate_phiEta_tolerance05mm_phi2GeV_curvature0005/"
#outputDir = "FakeRate_phiEta_tolerance05mm_phi2GeV_curvature0005_nVertexSigma5/"
#outputDir = "processedTracks/"
##outputDir = "FakeRate_tolerance05mm_phi2GeV_multiCurvature_nVertexSigma5/"
#outputDir = "processedTracks_kappa_deltaPhi/"
#outputDir = "FakeRate_phiEta_tolerance01mm_phi2GeV_curvature001/"
#outputDir = "processedTracks_kappa_deltaPhi_zresiduum_BDT/"
#outputDir = "processedTracks_kappa_deltaPhi_zresiduum/"

outputDir = path.split('/')[-2]+'/'
print outputDir, path

checkDir(outputDir)

cols = {
        10: colours.blue,
        20: colours.orange,
        30: colours.red,
        40: colours.green,
        50: colours.grey
    }

binslist  = range(0, 21) + range(22, 31, 2) + [35.0, 40.0, 50.0, 100.0] 
print binslist

#binslist = [0.0, 5.0, 10.0, 15.0, 30.0, 40.0, 60.0, 100.0]
binsarray = array('d', binslist)


#______________________________________________________________________________
def main():

    pileups = [0, 200, 1000]
    pileups = [0, 100, 1000]
    pileups = [0, 100]
    pileups = [0, 100, 200, 400, 500]
    pileups = [500]
    pileups = [0, 100, 200]
    pileups = [0, 100, 200, 300]
    pileups = [200]
    pileups = [0, 100, 200, 300, 400, 500, 600, 700, 800]
    pileups = [0, 100, 200, 300, 400, 500, 600, 700, 800, 900, 1000]

    geometries = [50]
    geometries = [10, 20, 30, 40, 50]
    geometries = [30]


    # For each pileup scenario, plot:
    # efficiency v pT
    # fake rate v pT
    # fake rate v eta 
    # with a multigraph for each geometry 
    for PILEUP in pileups:
        break
        #fName = "/atlas/users/wfawcett/fcc/delphes/test.root"
        fName = path+"hits_ttbar_pu{0}_multiGeometry.root".format(PILEUP) 
        print "Opening file:", fName
        ifile = TFile.Open(fName)
        efficiency(ifile, PILEUP, geometries, "Pt") 
        #efficiency(ifile, PILEUP, geometries, "EtaPt2") 
        fakeRates(ifile, PILEUP, geometries, "Pt")
        #fakeRates(ifile, PILEUP, geometries, "Eta") # Eta probably not calculated correctly
        ifile.Close()

    
    # Plots for a given triplet spacing, but different pileup scenarios  
    for spacing in [30]:
        pus = [0, 200, 1000]
        #fakeRatePerSpacing(path, spacing, pus)
        efficiencyPerSpacing(path, spacing, pus)

    
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
            '''
            [efficiencyMean, efficiencyError, fakeRate, fakeRateError] = numberOfTracks(ifile, PILEUP, geometry)
            [efficiencyMeanPt2, efficiencyErrorPt2, fakeRatePt2, fakeRateErrorPt2] = numberOfTracks(ifile, PILEUP, geometry, 2)
            '''
            try:
                [fakeRate, fakeRateError] = calculateAverageFakeRate(ifile, PILEUP, geometry, 0)
            except:
                [fakeRate, fakeRateError] = calculateAverageFakeRate(ifile, PILEUP, geometry, 0, debug=True)
            #fakeRateError = 0
            [fakeRatePt2, fakeRateErrorPt2] = calculateAverageFakeRate(ifile, PILEUP, geometry, 2)
            #fakeRateErrorPt2 = 0

            # would / could use cumulative histograms for average efficieny as a function of pT 
            [efficiencyMean, efficiencyError] = calculateAverageEfficiency(ifile, PILEUP, geometry, 0)
            #efficiencyError = 0 
            [efficiencyMeanPt2, efficiencyErrorPt2] = calculateAverageEfficiency(ifile, PILEUP, geometry, 2)
            #efficiencyErrorPt2 = 0

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

    outNameJson = 'averageFakeRatePt2.json'
    print 'Writing to json', outNameJson
    with open(outNameJson, 'w') as fp:
        json.dump(fakeRateSummariesPt2, fp, sort_keys=True, indent=2)

    sys.exit()
    

    ########################
    # Draw the summary plots
    ########################
    
    drawMultigraph("topRight", ";Pileup;Average track reconstruction efficiency", outputDir+"EfficiencySummary.pdf", geometries, efficiencySummaries )
    drawMultigraph("topRight", "p_{T} > 2 GeV;Pileup;Average track reconstruction efficiency", outputDir+"EfficiencySummaryPt2.pdf", geometries, efficiencySummariesPt2 )
    drawMultigraph("topLeft",  ";Pileup;Average fake rate", outputDir+"FakeRateSummary.pdf", geometries, fakeRateSummaries )
    drawMultigraph("topLeft",  ";Pileup;Average fake rate", outputDir+"FakeRateSummaryPt2.pdf", geometries, fakeRateSummariesPt2 )

#______________________________________________________________________________
def drawMultigraph(legendPosition, title, saveName, geometries, graphDict):


    newCan = TCanvas("newCan"+title+rand_uuid(), "", 500, 500)
    newCan.SetLeftMargin(0.15)

    smallestYvalue = 999.0
    largestYvalue = -11.0

    theGraph = TMultiGraph(rand_uuid(), rand_uuid())
    leg = prepareLegend(legendPosition)
    for geometry in geometries:
        # find min and max of the TGraphs ... kinda defeats the point of the multigraph ... but yeah ... 
        minX = Double(0.)
        minY = Double(0.)
        maxY = Double(0.)
        dummy = graphDict[geometry].GetPoint(0, minX, minY)
        dummy = graphDict[geometry].GetPoint(graphDict[geometry].GetN()-1, minX, maxY)
        if float(minY) < smallestYvalue:
            smallestYvalue = minY
        if float(maxY) > largestYvalue:
            largestYvalue = maxY
        
        theGraph.Add( graphDict[geometry], 'p' )
        theGraph.SetTitle(title)
        leg.AddEntry( graphDict[geometry], '{0} mm'.format(geometry), 'lp')
    theGraph.Draw('a')
    theGraph.GetHistogram().GetYaxis().SetTitleOffset(1.75)
    leg.Draw()
    newCan.SaveAs(saveName)


    # Draw with log y
    theGraph.GetHistogram().SetMinimum(smallestYvalue / 5) 
    theGraph.GetHistogram().SetMaximum(largestYvalue * 5) 
    newCan.SetLogy(1)
    saveName = saveName.replace(".pdf", "_log.pdf")
    newCan.SaveAs(saveName)



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
    '''
    Plot reconstruction efficiency for different triplet spacing
    '''

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
        UseTGraph = False
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
def fakeRatePerSpacing(path, geometry, pileups, label="Pt"):
    '''
    Create plot of fake rate as a function of <label> (e.g. pT)
    for a given triplet spacing, varying pileup
    '''
    can = TCanvas("can"+rand_uuid(), "can", 500, 500)   
    fakeRates = {} 

    leg = prepareLegend('topRight')
    leg.SetHeader('ttbar + pileup')

    counter = 0 
    for pu in pileups:
        #print 'getting input histograms'
        fName = path + "hits_ttbar_pu{0}_multiGeometry.root".format(pu)
        ifile = TFile.Open(fName)
        nReco = ifile.Get("recoTrack{0}_{1}".format(label, geometry)).Clone()
        nReco.Sumw2()
        nRecoFake = ifile.Get("recoTrack{0}_fake_{1}".format(label, geometry)).Clone()
        nRecoFake.Sumw2()

        # rebin and create fake rate
        #print 'rebin'
        nReco     = rebin_plot(nReco,     binsarray)
        nRecoFake = rebin_plot(nRecoFake, binsarray) 
        #print 'create rate'
        fakeRate = TGraphAsymmErrors(nRecoFake, nReco)
        fakeRate.SetName( fakeRate.GetName() + rand_uuid() )

        fakeRates[pu] = fakeRate

        #print 'style'
        xaxis = fakeRate.GetXaxis()
        yaxis = fakeRate.GetYaxis()
        xaxis.SetRangeUser(0, 100)
        xaxis.SetTitle("Reconstructed Track p_{T} [GeV]")
        yaxis.SetRangeUser(0, 0.05)
        yaxis.SetTitleOffset(1.5)
        yaxis.SetTitle("Fake Rate")
        fakeRate.SetTitle('')
        myText(0.2, 0.75, 'Triplet spacing: 30 mm', TEXT_SIZE)

        # colour
        if counter == 0:
            icol = colours.blue
        elif counter == 1:
            icol = colours.orange
        elif counter == 2:
            icol =  colours.red
        fakeRate.SetMarkerColor(icol) 
        fakeRate.SetLineColor(icol)

        leg.AddEntry(fakeRate, "#LT#mu#GT = {0}".format(pu), "lp")
        
        if counter == 0:
            fakeRate.Draw("APE")
        else: 
            fakeRate.Draw("PE same")
        fakeRate.GetHistogram().GetYaxis().SetTitleOffset(1.75)
        counter +=1 


    leg.Draw() 
    can.SaveAs('fakeRate{0}mm.pdf'.format(geometry))

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
        if PILEUP > 700: 
            yaxis.SetRangeUser(0, 0.3)
        else:
            yaxis.SetRangeUser(0, 0.05)
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
def calculateAverageEfficiency(ifile, PILEUP, geometry, ptThreshold):
    '''
    Functon to calculate average efficiency of track reconstruction ofter cuts
    (to be used with "processed tracks")
    Efficiency defined as : 
        number of surviving (true) tracks 
        ---------------------------------
        number of original (true) tracks

    This is a bit different from the "nominal" definition, which is
    number of true tracks / number of hits 
    (with number of hits as a proxy for the number of true tracks that could possibly have been reconstructed, howevver it is assumed that the original track reconstruction efficiency was 100%, so this is a relative efficiency) 
    '''

    originalTracks  = ifile.Get("nHitsPt_{0}".format(geometry)).Clone()
    survivingTracks = ifile.Get("recoTrackHitPt_true_{0}".format(geometry)).Clone()
    
    errorOriginal = Double(0.)
    errorSurviving = Double(0.)
    nOriginalTracks  = originalTracks.IntegralAndError(  originalTracks.FindBin(ptThreshold), -1, errorOriginal)
    nSurvivingTracks = survivingTracks.IntegralAndError( survivingTracks.FindBin(ptThreshold), -1, errorSurviving)
    averageEfficiency = nSurvivingTracks / nOriginalTracks 

    error = calculateErrorDivision(nSurvivingTracks, errorSurviving, nOriginalTracks, errorOriginal)


    return [averageEfficiency, error]


#______________________________________________________________________________
def calculateAverageFakeRate(ifile, PILEUP, geometry, ptThreshold, debug=False):

    trueTracks = ifile.Get("recoTrackPt_true_{0}".format(geometry)).Clone()
    fakeTracks = ifile.Get("recoTrackPt_fake_{0}".format(geometry)).Clone()

    totalTracks = fakeTracks.Clone("totalTracks")
    totalTracks.Add(trueTracks)

    errorTrue = Double(0.)
    errorFake = Double(0.)
    errorTotal = Double(0.)
    
    nTrueTracks  = trueTracks.IntegralAndError(  trueTracks.FindBin(ptThreshold), -1, errorTrue )
    nFakeTracks  = fakeTracks.IntegralAndError(  fakeTracks.FindBin(ptThreshold), -1, errorFake )
    nTotalTracks = totalTracks.IntegralAndError( totalTracks.FindBin(ptThreshold), -1, errorTotal )


    if debug:
    
        print 'ERROR DETECTED'
        can = TCanvas("can2", "can2", 500, 500)
        can.SetLogy()
        totalTracks.SetLineColor(4)
        totalTracks.GetXaxis().SetRangeUser(0, 50)
        totalTracks.Draw()
        trueTracks.SetLineColor(2)
        trueTracks.Draw("same")
        fakeTracks.SetLineColor(3)
        fakeTracks.Draw("same")
        can.SaveAs("test.pdf")

        print "calculateAverageFakeRate(pt>{0})".format(ptThreshold)
        print 'First bin above is: ', trueTracks.FindFirstBinAbove(ptThreshold)
        print "total tracks: {0}\t Total Fake tracks: {1}".format(nTotalTracks, nFakeTracks)
        print "fake integral: ", fakeTracks.Integral()
        averageFakeRate = nFakeTracks / nTotalTracks
        print "Average: {0}".format(averageFakeRate)
    averageFakeRate = nFakeTracks / nTotalTracks

    if(nFakeTracks != 0):
        error = calculateErrorDivision(nFakeTracks, errorFake, nTotalTracks, errorTotal)
    else:
        error = 0

    return [averageFakeRate, error]



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
def getEfficiencyTGraph(ifile, label, geometry, rebin=1):
    '''
    Return a reconstruction efficiency TGraph
    '''

    denominatorLabel = "nHits{0}_{1}".format(label,geometry)

    nHitsPt = ifile.Get(denominatorLabel).Clone()
    nHitsPt.Sumw2()

    numeratorLabel = "recoTrackHit{0}_true_{1}".format(label, geometry)
    recoTrackPt_true = ifile.Get(numeratorLabel).Clone()
    recoTrackPt_true.Sumw2() 

    binslist2 = [x/2.0 for x in range(0, 21*2)] # *2 since we want 0.5 bin width

    binslist2 += [22.0, 24.0, 26.0, 28.0, 30.0, 35.0, 40.0, 50.0, 60.0, 80.0, 100.0] 
    binsarray2 = array('d', binslist2)
    recoTrackPt_true = rebin_plot(recoTrackPt_true, binsarray2)
    nHitsPt = rebin_plot(nHitsPt, binsarray2)


    #recoTrackPt_true.Rebin(rebin)
    #nHitsPt.Rebin(rebin)

    recoEfficiency = TGraphAsymmErrors( recoTrackPt_true, nHitsPt )
    recoEfficiency.SetName( recoEfficiency.GetName() + rand_uuid() ) 
    return recoEfficiency

#______________________________________________________________________________
def efficiencyPerSpacing(path, geometry, pileups):
    '''
    Plot reconstruction efficiency for fixed triplet spacing, varying pileup
    '''

    can = TCanvas("can", "can", 500, 500)   
    # get the histograms 
    leg = prepareLegend('topRight')
    leg.SetHeader("ttbar + pileup")
    counter = 0
    theGraphs = {}
    for pu in pileups:
        fName = path + "hits_ttbar_pu{0}_multiGeometry.root".format(pu)
        ifile = TFile.Open(fName)

        recoEfficiency = getEfficiencyTGraph(ifile, "Pt", geometry, 1)
        recoEfficiency.SetTitle("")
        myText(0.2, 0.75, 'Triplet spacing: 30 mm', TEXT_SIZE)

        xaxis = recoEfficiency.GetXaxis()
        yaxis = recoEfficiency.GetYaxis()
        xaxis.SetRangeUser(0, 50)
        yaxis.SetRangeUser(0.9, 1.1)
        xaxis.SetTitle("Outer Hit (Track) p_{T} [GeV]") # hit pT of the track ... 
        yaxis.SetTitle("Reconstruction efficiency")
    
        # Add colours
        if counter == 0:
            icol = colours.blue
        elif counter == 1:
            icol = colours.orange
        elif counter == 2:
            icol =  colours.red
        recoEfficiency.SetMarkerColor(icol)
        recoEfficiency.SetLineColor(icol)
        theGraphs[pu] = recoEfficiency

        leg.AddEntry(recoEfficiency, '#LT#mu#GT = {0}'.format(pu), 'lp')

        if counter==0:
            recoEfficiency.Draw("APEl")
        else:
            recoEfficiency.Draw("PEl same")
        counter += 1
        recoEfficiency.GetHistogram().GetYaxis().SetTitleOffset(1.75)

    leg.Draw()
    can.SaveAs("reconstructionEfficiency{0}mm.pdf".format(geometry))



#______________________________________________________________________________
def calculateErrorDivision(numerator, numeratorError, denominator, denominatorError):
    '''
    Calculate propagated error on a = x/y
    '''

    x = numerator 
    sigma_x = numeratorError
    y = denominator
    sigma_y = denominatorError
    a = x/y

    sigma_a = math.sqrt( sigma_x**2 * (a/x)**2  + sigma_y**2 * (a/y)**2 )
    return sigma_a




#______________________________________________________________________________
if __name__ == "__main__":
    main()
