from ROOT import *
from colours import colours
from utils import prepareLegend
import os


gROOT.SetBatch(1)
gStyle.SetPadBottomMargin(0.15)
gStyle.SetPadLeftMargin(0.13) # increase space for left margin
gStyle.SetPadTickX(1)
gStyle.SetPadTickY(1)

if os.environ["isGeneva"]:
    path = "/atlas/users/wfawcett/fcc/delphes/results/hits/"
else:
    path = "/Users/Will/Desktop/hits/"


def main():

    can = TCanvas("can", "can", 500, 500)
    pileups = [0, 200]
    pileups = [0]
    for PILEUP in pileups:
    
        # filesystem 
        #fName = path+"hits_ttbar_pu{0}_result_AnnaAlgo.root".format(PILEUP) 
        fName = path+"hits_ttbar_pu{0}_simplestAlgo.root".format(PILEUP) 
        outputDir = "FakeRate/"
        ifile = TFile.Open(fName)

        # histograms
        nDelphesTracks = ifile.Get("nDelphesTracks")
        nDelphesTracks1GeV = ifile.Get("nDelphesTracks1GeV")
        nDelphesTracks10GeV = ifile.Get("nDelphesTracks10GeV")
        nRecoTracks = ifile.Get("nRecoTracks")
        nRecoTracksMatched = ifile.Get("nRecoTracksMatched")
        nDelphesHits = ifile.Get("nDelphesHits")

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
        print 'ymax:', baseHistogram.GetMaximum(), ymax2
        #yaxis.SetRangeUser(0, baseHistogram.GetMaximum()*1.3)
        baseHistogram.SetLineColor(colours.blue)
        baseHistogram.SetMarkerSize(0)
        baseHistogram.SetTitle("Pileup {0}".format(PILEUP))
        baseHistogram.Rebin(REBIN)

        if PILEUP == 0:
            xaxis.SetRangeUser(0, 500)
        if PILEUP == 200:
            xaxis.SetRangeUser(0, 1000)


        # Add legend and other plots
        leg = prepareLegend("topRight")
        #addLegendEntry(leg, nDelphesTracks1GeV, "True > 1 GeV") 
        addLegendEntry(leg, baseHistogram, "Hits")

        addPlot(nRecoTracks, colours.green, REBIN, leg, "Reco")
        addPlot(nRecoTracksMatched, colours.red, REBIN, leg, "Reco matched")
        #addPlot(nDelphesTracks10GeV, colours.red, REBIN, leg, "True > 10 GeV")
        #addPlot(nDelphesHits, colours.grey, REBIN, leg, "Hits")

        leg.Draw()

        can.SaveAs(outputDir+"trackComparrison_pu{0}.pdf".format(PILEUP))

def addLegendEntry(leg, hist, text):
    leg.AddEntry(hist, text, "l")
    leg.AddEntry(0, "mean : {0}".format(round(hist.GetMean())), "")
    #stdDevDelphesTracks = nDelphesTracks1GeV.GetStdDev() # standard deviation not used

def addPlot(histogram, colour, REBIN, legend, legendEntry):
    histogram.SetLineColor(colour)
    histogram.SetMarkerSize(0)
    histogram.Rebin(REBIN)
    histogram.Draw("same")
    addLegendEntry(legend, histogram, legendEntry)
    


if __name__ == "__main__":
    main()
