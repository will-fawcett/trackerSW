'''
Script to make effective pileup plots, based on distribution of pileup vertices
-- Not yet sure how to take into account timing
'''
from pprint import pprint
from ROOT import *
gROOT.SetBatch(1)
gStyle.SetPalette(kViridis)

RESULTS_PATH = '~/Documents/fcc/results-tkLayout'

from extract_coords import is_profile

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
    newCan.SetLogy()
    newCan.SetGrid()

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

                # declare multigraphs
                effectivePU    = TMultiGraph()
                fractionTracks = TMultiGraph()

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

                        pu = TGraphErrors()
                        for ibin in range(1, prim.GetNbinsX()+1):
                            resolution = graphData[ibin]['yvalue']
                            error      = graphData[ibin]['error']
                            eta        = graphData[ibin]['xvalue']

                            effPU = resolution / Z_VERTEX_SPACING
                            effPUerr = error / Z_VERTEX_SPACING

                            fracTracks = 1 - effPU
                            fracTracksErr = effPUerr

                            pu.SetPoint(ibin, eta, effPU)
                            pu.SetPointError(ibin, 0, effPUerr)

                        pu.SetMarkerColor(mColor)
                        pu.SetMarkerStyle(mStyle)
                        pu.SetMarkerSize(mSize)
                        pu.SetLineColor(mColor)

                        effectivePU.Add(pu, 'p')

                effectivePU.Draw('a')
                #effectivePU.SetTitle('Effective pile-up;#eta;Effective pile-up')
                #effectivePU.GetHistogram().GetXaxis().SetRangeUser(0, 4) # make space for legend
                newCan.SaveAs('effPu.pdf')
                sys.exit()

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
