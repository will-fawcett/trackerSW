'''
Script to read histograms produced by trackParameters.C
And calculate the track parameters from fits to these histograms
'''
from ROOT import *
gROOT.SetBatch(1)
gStyle.SetGridStyle(3) 
gStyle.SetPadLeftMargin(0.15) # increase space for left margin
gStyle.SetGridColor(kGray)

resultsDir = '/afs/cern.ch/work/w/wfawcett/private/geneva/delphes/results/'

colours = [
    865, # blue
    801, # orange
    629, # red
    418,  # green
    15,  # grey
    618, # purple
    1, # black
]

def main():


    # open file 
    iFile = TFile.Open(resultsDir+'histograms_ttbar_mu0_s10_10k.root')


    # want to get z0 resolution 
    resPlot = iFile.Get('z0Res_pt_eta')

    ptRanges = [
            [0,2],
            [9, 11],
            [50, 101]
            ]
    etaRanges = [
            [0, 0.2],
            [0.2, 0.4],
            [0.4, 0.8],
            [0.8, 1.0],
            [1.0, 1.2],
            [1.2, 1.4],
            [1.4, 1.6],
            [1.6, 1.8],
            [1.8, 2.0]
            ]

    leg = prepareLegend('bottomRight')
    leg.SetHeader('Track p_{T} [GeV]')

    graphs = []
    for n, ptRange in enumerate(ptRanges):
        graphs.append(TGraphErrors())
        for i, etaRange in enumerate(etaRanges):

            xposition = (etaRange[0] + etaRange[1])/2.0
            fitResults = extractResolution(resPlot, ptRange, etaRange)
            graphs[n].SetPoint(i, xposition, fitResults['Sigma'][0])
            graphs[n].SetPointError(i, 0, fitResults['Sigma'][1])
            graphs[n].SetMarkerColor(colours[n])
            graphs[n].SetLineColor(colours[n])
        leg.AddEntry(graphs[n], '{0} < pT < {1}'.format(ptRange[0], ptRange[1]), 'lp')

    # Draw graphs 
    can = TCanvas('can', 'can', 500, 500)
    can.SetGrid()
    can.SetLogy()
    mg = TMultiGraph()
    for g in graphs:
        mg.Add(g, 'p')
    mg.SetTitle('z0 resolutions from Delphes; #eta;#deltaz_{0} [mm]')
    mg.Draw('a')
    leg.Draw()

    
    can.SaveAs('graphs.pdf')

def extractResolution(plot3D, ptRange, etaRange):
    # projection of a slice (resolution, pT, eta) 

    yaxis = plot3D.GetYaxis()
    zaxis = plot3D.GetZaxis()

    # find bins corresponding to pT range
    binLowPt  = yaxis.FindBin(ptRange[0])
    binHighPt = yaxis.FindBin(ptRange[1]) - 1 # want up-to ptRangeMax

    binLowEta  = zaxis.FindBin(etaRange[0])
    binHighEta = zaxis.FindBin(etaRange[1]) - 1 # want up-to etaRangeMax

    # use the SetRange function to pick out a slice in pT (SetRange uses bin numbers) 
    yaxis.SetRange(binLowPt, binHighPt)
    zaxis.SetRange(binLowEta, binHighEta)

    # project  
    res = plot3D.Project3D('x') # project onto the resolution axis

    # fit with gaussian 
    res.Fit("gaus", "MQO") # M: "improve fit", Q: "quiet" (no printing), O: "Don't draw fit or histo
    theFit = res.GetFunction("gaus")

    # Extract fit results
    fitResults = {}
    for i in range(0, 3):
        parName = theFit.GetParName(i)
        value = theFit.GetParameter(i)
        error = theFit.GetParError(i)
        fitResults[parName] = [value, error]

    sigma = fitResults['Sigma'][0]
    sigmaErr = fitResults['Sigma'][1]

    # save plot for diagnostic purposes
    name = '{0}pt{1}_{2}eta{3}'.format(ptRange[0], ptRange[1], int(etaRange[0]*10), int(etaRange[1]*10))
    res.SetTitle('{0} sigma = {1:.2f}#pm{2:.2f}'.format(name, sigma, sigmaErr))
    tempCan = TCanvas('tcan', 'can', 500, 500)
    res.GetXaxis().SetRangeUser(-sigma*4, sigma*4)

    res.Draw()
    tempCan.SaveAs('z0Res_{0}.pdf'.format(name))

    return fitResults


#___________________________________________________________________________
def prepareLegend(position):

    bottomLeft  = [0.15, 0.1, 0.35, 0.3]
    bottomRight = [0.7, 0.1, 0.9, 0.3]
    topRight    = [0.7, 0.7, 0.9, 0.9]
    topLeft     = [0.15, 0.7, 0.35, 0.9]

    if (position == "topLeft"):
        myPosition = topLeft
    if (position == "topRight"):
        myPosition = topRight
    if (position == "bottomLeft"):
        myPosition = bottomLeft
    if (position == "bottomRight"):
        myPosition = bottomRight

    return TLegend(myPosition[0], myPosition[1], myPosition[2], myPosition[3])


if __name__ == "__main__":
    main()
