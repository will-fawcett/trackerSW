'''
Quick script to plot the ratio of the track parameters between quartet and triplet layouts
'''

import json 
from glob import glob 
from extract_coords import prepareLegend

from ROOT import * 
gROOT.SetBatch(1)
gStyle.SetPalette(kViridis)
gStyle.SetPadLeftMargin(0.12) # increase space for left margin
gStyle.SetGridStyle(3) 
gStyle.SetGridColor(kGray)

RESULTS_PATH = '~/Documents/fcc/results-tkLayout'

def main():


    trackParameters = {
            'z0res': { 'title': '#deltaz_{0}', 'id' : 'z0'},
            'd0res': { 'title': '#deltad_{0}', 'id' : 'd0'},
            
            'logptres' : {'title' : 'ratio #deltap_{T}/p_{T}', 'id' : 'pT'},
            'pres'     : {'title' : 'ratio #deltap/p', 'id' : 'p'},
            'phi0res'  : {'title' : 'ratio #phi_{0}', 'id' : 'phi0'},
            'ctauRes'  : {'title' : 'ratio c#tau', 'id' : 'ctau'},
            'cotgThres': {'title' : 'ratio cot(#theta)', 'id' : 'cotgTh'},

                    }

    
    # open json files for quartet and triplet
    with open('infoStoretriplet.json') as data_file:
        tripletInfo = json.load(data_file)
    with open('infoStorequartet.json') as data_file:
        quartetInfo = json.load(data_file)

    # Check if available metadata is the same 
    metaTrip = tripletInfo['metadata']
    metaQuart = quartetInfo['metadata']

    for key in metaTrip.keys():
        if (metaTrip[key] != metaQuart[key]) and not key == "layoutType":
            print 'WARNING: mismatch between triplet and quartet info for key', key

    # extract useful info from metadata (assumes it's recent) 
    barrelLayers = metaTrip['barrelLayers']
    trackpT = metaTrip['trackpT']
    tripletSpacings = metaTrip['tripletSpacings']

    #barrelLayers = [1]
    #tripletSpacings = [20]
    #trackParameters = {'z0res':'z0'}


    # Now read ROOT files and TCanvases 
    for parameter in trackParameters.keys(): 
        for layer in barrelLayers:
            for spacing in tripletSpacings:
            
                # extract triplet canvas
                tfName = RESULTS_PATH+'/results_FCCtriplet_{0}barrel{1}mm/{2}_triplet_withMS_Pt000.root'.format(layer, spacing, parameter)
                thName = '{0}_triplet_withMS_Pt000'.format(parameter)
                tf = TFile.Open(tfName)
                if tf.IsOpen():
                    tc = tf.Get(thName)

                # extract quartet canvas
                qfName = RESULTS_PATH+'/results_FCCquartet_{0}barrel{1}mm/{2}_quartet_withMS_Pt000.root'.format(layer, spacing, parameter)
                qhName = '{0}_quartet_withMS_Pt000'.format(parameter)
                qf = TFile.Open(qfName)
                if qf.IsOpen():
                    qc = qf.Get(qhName)


                # get list of primitives from triplet file
                primList = tc.GetListOfPrimitives()
                primNames = [x.GetName() for x in primList]
                momentumValues = [float(x.split('_')[-1]) for x in primNames if 'eta' in x]

                # Extract TProfile
                ratioPlots = []
                for pt in trackpT:
                    primName = '{0}_vs_eta_{1}'.format(trackParameters[parameter]['id'], int(pt))
                    tripPlot = tc.GetPrimitive(primName)
                    quartPlot = qc.GetPrimitive(primName)
                    ratio = quartPlot.Clone()
                    ratio.Divide(tripPlot)
                    ratioPlots.append(ratio)
                makePlot(ratioPlots, 
                        'ratio_{0}_{1}barrel{2}mm'.format(parameter, layer, spacing),
                        trackParameters[parameter]['title']
                        )

                    
def makePlot(ratios, saveName, yTile):
    newCan = TCanvas('can', 'can', 500, 500)
    newCan.SetGrid()

    leg = prepareLegend('topRight')
    leg.SetHeader('Track p_{T} [GeV]')

    for i, plot in enumerate(ratios):
        plot.SetMinimum(0)
        plot.SetMaximum(1.5)
        if i==0:
            plot.Draw('Phist')
        else:
            plot.Draw('Psame hist')

        plot.GetYaxis().SetTitleOffset(1.4)
        plot.GetYaxis().SetTitle('Ratio '+yTile)
        plot.GetXaxis().SetRangeUser(0, 4)
        leg.AddEntry(plot, plot.GetName().split('_')[-1], 'lp')

    leg.Draw()
    newCan.SaveAs('ratios/'+saveName+'.pdf')


if __name__ == "__main__":
    main()
