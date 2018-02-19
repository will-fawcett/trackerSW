#!/usr/bin/python

# Quick script to plot hit multiplicity average in the outer layer
from ROOT import * 
gROOT.SetBatch(1)

gROOT.SetBatch(1)
#gStyle.SetPalette(kViridis)
gStyle.SetGridStyle(3) 
gStyle.SetGridColor(kGray)

#gStyle.SetPadBottomMargin(0.15)
gStyle.SetPadLeftMargin(0.13) # increase space for left margin
gStyle.SetPadTickX(1)
gStyle.SetPadTickY(1)

def main(verbose):

    can = TCanvas("can", "can", 500, 500)
    gr = TGraph()
    counter =0
    pileups = [0]
    pileups = [0, 100, 200, 300, 400, 500, 600, 700, 800,  1000]
    '''
    for pu in pileups:
        ifile = TFile.Open("/atlas/data4/userdata/wfawcett/delphes/samples/hits/hits_ttbar_pu{0}_multiGeometry.root".format(pu))
        tree = ifile.Get("Delphes")
        nEvents = tree.GetEntries() 
        print nEvents

        tree.Draw("sqrt(Hits20.X*Hits20.X+Hits20.Y*Hits20.Y):Hits20.Z", "sqrt(Hits20.X*Hits20.X+Hits20.Y*Hits20.Y)>585", "goff")
        theHist = tree.GetHistogram()
        print theHist.GetEntries()

        hitAverage = theHist.GetEntries()/float(nEvents)
        print hitAverage

        gr.SetPoint(counter, pu, hitAverage)
        counter += 1
    '''

    hitMulti = {
    0: 109.1635,
    100: 974.6075,
    200: 1861.971,
    300: 2737.454,
    400: 3632.144,
    500: 4507.611,
    600: 5390.7695,
    700: 6256.5285,
    800: 7152.472,
    1000: 8921.9545,
    }

    for pu in pileups:
        gr.SetPoint(counter, pu, hitMulti[pu])
        print counter, pu, hitMulti[pu] 
        counter += 1
    gr.SetMarkerStyle(20)
    gr.Draw("AP")
    xaxis = gr.GetXaxis()
    yaxis = gr.GetYaxis()
    yaxis.SetTitleOffset(1.75)
    xaxis.SetTitle("Pileup")
    yaxis.SetTitle("Average number of hits")

    can.SaveAs("pileup_hits.pdf")







if __name__ == "__main__":

    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("-v", "--verbose", help="Turn on verbose messages", action="store_true", default=False)
    args = parser.parse_args()
    verbose = args.verbose

    main(verbose)


