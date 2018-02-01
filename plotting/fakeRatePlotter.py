from ROOT import *
from colours import colours
from utils import prepareLegend
import os


gROOT.SetBatch(1)
gStyle.SetPadBottomMargin(0.15)
gStyle.SetPadLeftMargin(0.12) # increase space for left margin
gStyle.SetPadTickX(1)
gStyle.SetPadTickY(1)

if os.environ["isGeneva"]:
    path = "/atlas/users/wfawcett/fcc/delphes/results/hits/"
else:
    path = "/Users/Will/Desktop/hits/"


def main():

    can = TCanvas("can", "can", 500, 500)
    for PILEUP in [0, 200]:
    
        # filesystem 
        fName = path+"hits_ttbar_pu{0}_result.root".format(PILEUP) 
        outputDir = "FakeRate/"
        ifile = TFile.Open(fName)

        # histograms
        nDelphesTracks = ifile.Get("nDelphesTracks")
        nDelphesTracks1GeV = ifile.Get("nDelphesTracks1GeV")
        nRecoTracks = ifile.Get("nRecoTracks")

        # stats
        meanDelphesTracks = nDelphesTracks1GeV.GetMean()
        stdDevDelphesTracks = nDelphesTracks.GetStdDev()

        meanRecoTracks = nRecoTracks.GetMean()
        stdDevDelphesTracks = nRecoTracks.GetStdDev()


        # styling
        REBIN = 4
        nDelphesTracks1GeV.Draw()
        nDelphesTracks1GeV.SetTitle("Pileup {0}".format(PILEUP))
        xaxis = nDelphesTracks1GeV.GetXaxis()
        xaxis.SetNdivisions(5, 5, 0)
        nDelphesTracks1GeV.SetLineColor(colours.blue)
        nDelphesTracks1GeV.Rebin(REBIN)

        if PILEUP == 0:
            xaxis.SetRangeUser(0, 500)

        nRecoTracks.SetLineColor(colours.green)
        nRecoTracks.Rebin(REBIN)
        nRecoTracks.Draw("same")

        # Legend
        leg = prepareLegend("topRight")
        leg.AddEntry(nDelphesTracks1GeV, "True", "l")     
        leg.AddEntry(0, "mean : {0}".format(round(meanDelphesTracks)), "")
        leg.AddEntry(nRecoTracks, "Reco", "l")
        leg.AddEntry(0, "mean : {0}".format(round(meanRecoTracks)), "")
        leg.Draw()

        can.SaveAs(outputDir+"trackComparrison_pu{0}.pdf".format(PILEUP))

if __name__ == "__main__":
    main()
