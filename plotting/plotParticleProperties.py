'''
Script to make basic plots of particle properties
'''

from ROOT import *
from utils import prepareLegend, myText

from colours import colours

STORE = "/Users/Will/Documents/fcc/trackerSW/particleProperties/"

gROOT.SetBatch(1)
gStyle.SetPadTickX(1)
gStyle.SetPadTickY(1)
gStyle.SetPadBottomMargin(0.15)
gStyle.SetPadLeftMargin(0.13) # increase space for left margin

def main():

    
    pileup = ["py8_pp_minbias_pu0.root"]
    signals = [
            "mg_pp_thh_pu0.root",
            #"mg_pp_tt_nlo_pu0.root",
            "mg_pp_hh_pu0.root",
            ]

    toPlot = {
            #"allTrackEta": {'xrange' : [-10, 10], 'xtitle' : 'Truth Track #eta', 'logy' : 1},
            "track1Eta": {'xrange'  : [-6, 6], 'xtitle' : 'Truth Track 1 #eta', 'logy' : 1},
            #"allTrackPt": {'xrange' : [0, 100], 'xtitle' : 'Truth Track p_{T} [GeV]', 'logy' : 1},
            "track1Pt": {'xrange' :  [0, 150], 'xtitle' : 'Truth Track 1 p_{T} [GeV]', 'logy' : 1}
            }

    colz = {
            "py8_pp_minbias_pu0.root" : {'col' : colours.blue, 'leg' : 'Minbias'},
            "mg_pp_thh_pu0.root"      : {'col' : colours.orange, 'leg' : 'ttH'},
            "mg_pp_tt_nlo_pu0.root"   : {'col' : colours.purple, 'leg' : 'ttbar'},
            "mg_pp_hh_pu0.root"       : {'col' : colours.red, 'leg' : 'HH'}
            }
    

    # open fucking files
    files = {}
    for f in signals+pileup: 
        files[f] = TFile.Open(STORE+f)

    can = TCanvas("can", "can", 500, 500)
    for plot in toPlot.keys():

        storedPlots = {}
        counter = 0
        leg = prepareLegend('topRight')
        for sig in pileup+signals:

            style = colz[sig]
            
            fName = STORE+sig
            #print 'opening', fName
            #print 'getting plot', plot
            h = files[sig].Get("TruthTrack_"+plot)
            h.Rebin(2)
            '''
            if sig == 'py8_pp_minbias_pu0.root':
                h.Rebin(10)
            else:
                h.Rebin(2)
            '''
            storedPlots[sig] = h
            h.SetMarkerColor(style['col'])
            h.SetLineColor(style['col'])
            xaxis = h.GetXaxis()
            yaxis = h.GetYaxis()
            xaxis.SetRangeUser(*toPlot[plot]['xrange'])
            xaxis.SetTitle(toPlot[plot]['xtitle'])
            yaxis.SetTitle('Frequency')
            print yaxis.GetXmin(), h.GetMinimum()
            #yaxis.SetRangeUser(yaxis.GetXmin(), yaxis.GetXmax()*1.1)  # increase y range by 10%
            h.SetMaximum(h.GetMaximum()*4)
            h.SetMinimum(1e-3)
            leg.AddEntry(h, style['leg'], 'lp')

            myText(0.2, 0.8, '#sqrt{s}=100 TeV' )




            can.SetLogy( toPlot[plot]['logy'] )

            if counter == 0:
                h.Draw('hist e2')
            else:
                h.Draw('hist e2 same')
            counter += 1
        leg.Draw()
        can.SaveAs("particleProperties/"+plot+'.pdf')
        can.SaveAs("particleProperties/"+plot+'.eps')

        '''
        counter = 0
        for sig in signals:
            print type(storedPlots[sig])
            if counter == 0:
                storedPlots[sig].Draw()
            else:
                storedPlots[sig].Draw('same')
        '''
                
            

            
    print ''


if __name__ == "__main__":
    main()
