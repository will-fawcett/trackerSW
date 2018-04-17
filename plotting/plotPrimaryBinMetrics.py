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
            'distancePB_PV' :  { 'xtitle' :'Distance from PB centre to PV', 'xrange' : [-300, 300]},
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
            'allHits' : {'colour' : colours.grey, 'legend' : 'All'}, 
            'matchedHits' : {'colour' : colours.blue, 'legend' : 'Matched to PB'},
            'unmatchedHits' : {'colour' : colours.red, 'legend' : 'Not matched to PB'}
            }

    can = TCanvas('can', 'can', 500, 500)
    for plot in plots.keys():
        print 'making', plot
        leg = TLegend(0.52, 0.7, 0.9, 0.9)
        leg.SetTextSize(TEXT_SIZE-0.005)
        for t in types:
            histName = t+'_'+plot
            #print 'getting plot', histName
            h = ifile.Get(histName)


            xaxis = h.GetXaxis()
            yaxis = h.GetYaxis()
            xaxis.SetTitle(plots[plot]['xtitle'])
            xRange =  plots[plot]['xrange'] 
            print xRange
            xaxis.SetRangeUser(xRange[0], xRange[1])

            if plot != 'nVerticesPB':
                h.Rebin(10)


            h.SetLineColor(typeInfo[t]['colour'])
            leg.AddEntry(h, typeInfo[t]['legend'], 'l')

            if t == types[0]:
                h.Draw()
                can.Update()
                yMax = gPad.GetUymax()
                yaxis.SetRangeUser(0, 1.2*yMax)
                if plot == 'distancePB_PV':
                    yaxis.SetRangeUser(0, 100)
                xaxis.SetRangeUser(xRange[0], xRange[1])
                h.Draw()
            else:
                h.Draw('same')

        can.Update()
        yMax = gPad.GetUymax()
        print yMax
        yaxis.SetRangeUser(0, 1.2*yMax)
        can.Update()
        yMax = gPad.GetUymax()
        leg.Draw()
        can.SaveAs(SAVE_DIR+plot+'.eps')
        #break
        






if __name__ == "__main__":
    main()

