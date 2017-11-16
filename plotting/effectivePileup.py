'''
Script to make effective pileup plots, based on distribution of pileup vertices
-- Not yet sure how to take into account timing
'''
from pprint import pprint
from ROOT import *
gROOT.SetBatch(1)
gStyle.SetPalette(kViridis)

RESULTS_PATH = '~/Documents/fcc/results-tkLayout'

from extract_coords import is_profile, prepareLegend

gStyle.SetGridStyle(3)
gStyle.SetGridColor(kGray)


Z_VERTEX_SPACING = 9.6 # um

def main():

    trackParameters = ['z0res'] # variableMap.keys() testing
    tripletSpacings = [20, 25, 30, 35, 40, 50] # Layer spacings to consider
    barrelLayers = [1, 2, 3, 4, 5] # Triplet in barrel layer?
    region = 'triplet' # could be tracker, outer, inner
    scattering = "withMS"

    # Make canvas and style
    newCan = TCanvas('can', 'can', 800, 600)
    newCan.cd()
    newCan.SetLogy()
    newCan.SetGrid()

    #barrelLayers = [1]
    #tripletSpacings = [50]

    # make plots for each tracker layout
    for variable in trackParameters:
        for layer in barrelLayers:
            for spacing in tripletSpacings:

                # open the ROOT File, get the canvas
                path = RESULTS_PATH + '/results_FCCtriplet_{0}barrel{1}mm/'.format(layer, spacing)
                fName = "{0}_{1}_{2}_Pt000".format(variable, region, scattering) # Note also can have P000 (for momentum)
                f = TFile.Open(path+fName+'.root')
                tempCan = f.Get(fName)

                # Extract possible momentum values from list of primitives
                primList = tempCan.GetListOfPrimitives()
                primNames = [x.GetName() for x in primList]
                momentumValues = [float(x.split('_')[-1]) for x in primNames if 'eta' in x]
                print momentumValues

                puGraphs = []
                fracGraphs = [] 

                leg = prepareLegend('topRight')
                leg.SetHeader('Track p_{T} [GeV]')

                for prim in primList:
                    if is_profile(prim):

                        # For each primitive (TProfile) make two new plots:
                        # One for effective pileup, and another for fraction of tracks unambiguously assigned to the PV
                        # TODO: incorporate timing resolution?

                        # Extract existing plot information
                        mColor = prim.GetMarkerColor()
                        mStyle = prim.GetMarkerStyle()
                        mSize  = prim.GetMarkerSize() / 2.0

                        graphData = extractBinInfo(prim)
                        pprint(graphData)

                        puGraphs.append(TGraphErrors())
                        puGraphs[-1].SetMarkerColor(mColor)
                        puGraphs[-1].SetMarkerStyle(mStyle)
                        puGraphs[-1].SetMarkerSize(mSize)
                        puGraphs[-1].SetLineColor(mColor)

                        fracGraphs.append(TGraphErrors())
                        fracGraphs[-1].SetMarkerColor(mColor)
                        fracGraphs[-1].SetMarkerStyle(mStyle)
                        fracGraphs[-1].SetMarkerSize(mSize)
                        fracGraphs[-1].SetLineColor(mColor)


                        trackPt = prim.GetName().split('_')[-1]
                        leg.AddEntry(puGraphs[-1], trackPt, 'lp')


                        counter = 0
                        for ibin in range(1, prim.GetNbinsX()+1):
                            resolution = graphData[ibin]['yvalue']
                            error      = graphData[ibin]['error']
                            eta        = graphData[ibin]['xvalue']

                            effPU = resolution / Z_VERTEX_SPACING
                            effPUerr = error / Z_VERTEX_SPACING


                            puGraphs[-1].SetPoint(ibin, eta, effPU)
                            puGraphs[-1].SetPointError(ibin, 0, effPUerr)


                            try:
                                fracTracks = 1.0 / effPU
                                fracTracksErr = effPUerr
                                fracGraphs[-1].SetPoint(counter, eta, fracTracks)
                                counter += 1
                                #fracGraphs[-1].SetPointError(ibin, 0, fracTracksErr)
                            except ZeroDivisionError:
                                continue # don't add point if 0 


                        puGraphs[-1].Draw('AP') # due to the mysteries of ROOTs drawing, one needs to do this first, for no reason
                        fracGraphs[-1].Draw('AP')

                        newCan.SaveAs(prim.GetName()+'.pdf')

                # declare multigraphs
                effectivePU    = TMultiGraph()
                fractionTracks = TMultiGraph()

                # Add graphs to multigraph
                for g in puGraphs:
                    effectivePU.Add(g, 'p')

                for g in fracGraphs:
                    fractionTracks.Add(g, 'lp')



                # Drawing for fraction of tracks plot 
                newCan.SetLogy(0)
                fractionTracks.SetTitle('Fracton of tracks being unambiguously assigned to the PV @95% CL: #sigma_{z}^{Gauss}=75 mm <#mu>=1000; #eta;Fraction')
                fractionTracks.Draw('a')
                leg.Draw()
                fractionTracks.GetHistogram().GetXaxis().SetRangeUser(0, 4) # won't be respected since no pointes here. Thanks ROOT
                newCan.SaveAs('plots/fracTracks_{0}barrel{1}mm.pdf'.format(layer, spacing))

                # Drawing for effective pileup plot 
                newCan.SetLogy(1)
                location = 'L={0}, S={1}'.format(layer, spacing)
                effectivePU.SetTitle('Effective pile-up@ 95% CL: #sigma_{z}^{Gauss}=75 mm <#mu>=1000 '+location+';#eta;Effective pile-up')
                effectivePU.Draw('a')
                newCan.Update()
                effectivePU.GetHistogram().GetXaxis().SetRangeUser(0, 4)
                effectivePU.Draw('a')
                leg.Draw()
                effectivePU.GetHistogram().GetXaxis().SetRangeUser(0, 4)
                newCan.SaveAs('plots/effPu_{0}barrel{1}mm.pdf'.format(layer, spacing))

                f.Close()

def extractBinInfo(plot):
    '''
    Returns a dict with x, y e of a TH1 derived object, indexed by bin number
    Args:
        plot: a TH1 derived class (e.g. TProfile)
        xVals: list of the x-values
    '''

    info={}

    # Extract info from plot
    nbinsx = plot.GetNbinsX()
    #print nbinsx
    for ibin in range(1, nbinsx+1): # start counting bins from 1, end at eta = 6
        lowEdge = plot.GetBinLowEdge(ibin)
        val = plot.GetBinContent(ibin)
        binWidth = plot.GetBinWidth(ibin)
        error = plot.GetBinError(ibin)
        center = plot.GetBinCenter(ibin)
        #print ibin, val, lowEdge, binWidth

        # only extract points from desired eta bins
        info[ibin] = {'xvalue' : center, 'yvalue' : val, 'error' : error}
    return info

if __name__ == "__main__":
    main()
