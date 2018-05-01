'''
Script to make plots analysing the PB finding algorithm
'''

from colours import colours
from utils import prepareLegend 

from ROOT import *
gROOT.SetBatch(1)
gStyle.SetPadTickX(1)
gStyle.SetPadTickY(1)
gStyle.SetPadBottomMargin(0.15)
gStyle.SetPadLeftMargin(0.13) # increase space for left margin

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

SAVE_DIR = '/Users/Will/Documents/fcc/note/TripletTracker_Note/figures/'

def main():

    ifile = TFile.Open('/Users/Will/Documents/fcc/trackerSW/hitTrackVertexPlotStore/PB_mg_pp_hh_pu1000.root')

    plots = {
            'nVerticesPB' :  { 'xtitle' :'Number of vertices in the PB', 'xrange' : [0, 35]},
            #'nVerticesPV' :  { 'xtitle' :'Number of vertices within #pm0.5 mm of the PV'},
            'distancePB_PV' :  { 'xtitle' :'Distance from PB centre to PV [mm]', 'xrange' : [-300, 300]},
            'PBlocation' :  { 'xtitle' :'Location of the PB centre [mm]', 'xrange' : [-200, 200]},
            'PVlocation' :  { 'xtitle' :'Location of the PV [mm]', 'xrange' : [-200, 200]},
            'sumPtPB' :  { 'xtitle' :'Sum p_{T} of tracks matched to the PB [GeV]', 'xrange' : [0, 1000] }
            }

    types = [
            'allHits',
            'matchedHits',
            'unmatchedHits',
            ]

    typeInfo = {
            'allHits' : {'colour' : colours.grey, 'legend' : 'All', 'marker' : 20}, 
            'matchedHits' : {'colour' : colours.blue, 'legend' : 'Matched to PB', 'marker' : 22 },
            'unmatchedHits' : {'colour' : colours.red, 'legend' : 'Not matched to PB', 'marker' : 33 }
            }

    can = TCanvas('can', 'can', 500, 500)
    for plot in plots.keys():
        print 'making', plot
        leg = TLegend(0.15, 0.7, 0.4, 0.85)
        leg.SetTextSize(TEXT_SIZE-0.01)
        for t in types:
            histName = t+'_'+plot
            #print 'getting plot', histName
            h = ifile.Get(histName)

            if t == 'allHits':
                scaleFactor = 1.0/h.Integral()

            # normalise the histogram
            h.Scale(scaleFactor)


            xaxis = h.GetXaxis()
            yaxis = h.GetYaxis()
            xaxis.SetTitle(plots[plot]['xtitle'])
            yaxis.SetTitle('Frequency')
            xRange =  plots[plot]['xrange'] 
            xaxis.SetRangeUser(xRange[0], xRange[1])

            if plot != 'nVerticesPB':
                h.Rebin(10)

            # print kurtosis (measure of tailness)
            print histName, 'kurtosis', h.GetKurtosis()
            kurtosis =  h.GetKurtosis()

            h.SetLineColor(typeInfo[t]['colour'])
            h.SetMarkerColor(typeInfo[t]['colour'])
            h.SetMarkerStyle(typeInfo[t]['marker'])
            leg.AddEntry(h, '{0}, kurtosis = {1:.2f}'.format(typeInfo[t]['legend'], kurtosis), 'lp')

            if t == types[0]:
                h.Draw()
                can.Update()
                yMax = gPad.GetUymax()
                yaxis.SetRangeUser(0, 1.3*yMax)
                if plot == 'distancePB_PV':
                    yaxis.SetRangeUser(0, 0.035)
                xaxis.SetRangeUser(xRange[0], xRange[1])
                h.Draw()
                h.Draw('p same')
            else:
                h.Draw('p same')
                h.Draw('same')

        can.Update()
        yMax = gPad.GetUymax()
        yaxis.SetRangeUser(0, 1.2*yMax)
        can.Update()
        yMax = gPad.GetUymax()
        leg.Draw()
        can.SaveAs(SAVE_DIR+plot+'.eps')
        #break
        






if __name__ == "__main__":
    main()

