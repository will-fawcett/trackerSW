from ROOT import * 
import json
gROOT.SetBatch(1)
#gROOT.SetPalette(kViridis)
gStyle.SetPalette(kViridis)
gStyle.SetPadLeftMargin(0.15) # increase space for left margin


# Convenience function to check if an object is a TProfile
def is_profile(p):
    return isinstance(p, TProfile)

# Convenience function to print list of primitives associated with a TObject 
def printPrimitiveNames(tobject):
    primList = tobject.GetListOfPrimitives()
    print 'TObject of type: {0}, and name: {1}, has {2} primitives'.format(type(tobject), tobject.GetName(), len(primList))
    for x in primList:
        print '\t', x


RESULTS_PATH = '~/Documents/fcc/results-tkLayout'

# variables from which to extract info from
variableMap = {
        'z0res'     : {'units' : '[#mu m]', 'title' : '#delta z_{0}' },
        'd0res'     : {'units' : '[#mu m]', 'title' : '#delta d_{0}' },
        'logptres'  : {'units' : '[%]' },
        'pres'      : {'units' : '[%]' },
        'phi0res'   : {'units' : '[deg]' }, # don't care so much about these
        'ctauRes'   : {}, 
        'cotgThres' : {},
        }

def main():
    
    #########################
    #####  Setup  ###########
    multipleScattering = True
    region = 'triplet' # could be tracker, outer, inner
    plotEtaValues = [0, 1, 2, 2.5, 3] # eta values to be extracted
    #spacings = [10, 20, 25, 30, 25, 40, 50] # Layer spacings to consider
    spacings = [20, 25, 30, 25, 40, 50] # Layer spacings to consider
    barrelLayers = [1, 2, 3] # Triplet in barrel layer? 
    #########################

    if multipleScattering:
        scattering = "withMS"
    else:
        scattering = "noMS"


    variables = ['z0res', 'd0res'] # variableMap.keys() testing
    #layers = [1]
    #spacings = [20]

    # Dictionary to store all of the information
    megaDict = {}

    # First, extract all of the data and store it in a nice python dictionary 
    for variable in variables:
        megaDict[variable] = {}

        for layer in barrelLayers:
            megaDict[variable][layer] = {}

            for spacing in spacings:
                megaDict[variable][layer][spacing] = {}

                # open root file and get plot 
                path = RESULTS_PATH + '/results_FCCtriplet_{0}barrel{1}mm/'.format(layer, spacing)
                fName = "{0}_{1}_{2}_Pt000".format(variable, region, scattering) # Note also can have P000 (for momentum)
                f = TFile.Open(path+fName+'.root') 
                tempCan = f.Get(fName) 

                # Extract possible momentum values from list of primitives
                primList = tempCan.GetListOfPrimitives()
                primNames = [x.GetName() for x in primList]
                momentumValues = [float(x.split('_')[-1]) for x in primNames if 'eta' in x]
                #print momentumValues

                # Loop over primitives to extract all the info
                for prim in primList:
                    if is_profile(prim): 
                        momentum = float(prim.GetName().split('_')[-1])
                        #print momentum

                        # get particular plot
                        plot = tempCan.GetPrimitive(prim.GetName())

                        thisPlotInfo = extractPlotInfo(plot, plotEtaValues)                         
                        megaDict[variable][layer][spacing][momentum] = thisPlotInfo

                f.Close() 

    megaDict['info'] = '{variable name -> barrel layer -> triplet spacing -> track momentum -> eta -> {value : variable value, error : variable error}'

    # Store the json file
    outNameJson = 'plotInfoStore.json'
    with open(outNameJson, 'w') as fp:
        json.dump(megaDict, fp, sort_keys=True, indent=2)
    
    # now make some nice plots
    for variable in variables:
        #makePlot(variable, megaDict[variable], barrelLayers)
        make2DPlot(variable, megaDict[variable], barrelLayers, spacings)


def make2DPlot(variable, plotInfo, barrelLayers, spacings):
    
    can = TCanvas('can', 'can', 500, 500)
    maxSpacing = max(spacings) + 10
    nBinsx = maxSpacing *10 + 10 

    zTitle = variableMap[variable]['title'] + variableMap[variable]['units']

    print 'plot properties', 'hist', variable+';Layer spacing [mm]; Barrel layer;'+zTitle, nBinsx, 0, maxSpacing, len(barrelLayers)+1, barrelLayers[0], barrelLayers[-1]+1
    h = TH2D('hist', '', nBinsx, 0, maxSpacing, len(barrelLayers)*10, 0, barrelLayers[-1]+1)
    xaxis = h.GetXaxis()
    yaxis = h.GetYaxis()

    g = TGraph2D()
    ipoint = 0

    f = TFile.Open('test.root', 'RECREATE')

    for layer in barrelLayers:
        for spacing in spacings:
            xbin = xaxis.FindBin(spacing)
            ybin = yaxis.FindBin(layer)
            #print ybin, layer

            z = plotInfo[layer][spacing][10][0]['value']
            e = plotInfo[layer][spacing][10][0]['error']

            #print ipoint, spacing, layer, z

            h.SetBinContent(xbin,ybin,z)
            h.SetBinError(xbin,ybin,e)
            g.SetPoint(ipoint, spacing, layer, z) 
            #g.SetPoint(ipoint, layer, spacing, z) 
            ipoint += 1

    #h.Draw('surf')
    h.Draw('cont3')
    can.SaveAs('test.pdf')

    print 'offset is', g.GetXaxis().GetTitleOffset()
    g.Draw('surf3')
    #g.Draw('tri1')
    g.Draw('P0same')
    g.SetTitle(variable+';Layer spacing [mm]; Barrel layer;'+zTitle)
    g.GetXaxis().SetTitleOffset(20)
    print 'offset is', g.GetXaxis().GetTitleOffset()
    can.SaveAs('graphTest.pdf')
    g.Write()

    
    # try projecton
    proj = g.Project('xy')
    proj.Draw()
    can.SaveAs('projTest.pdf')

    

    pass 

def makePlot(variable, plotInfo, spacings):

    print 'making plot for', variable
    #print plotInfo

    can = TCanvas('can', 'can', 500, 500)

    p = TGraphErrors()
    for i, layer in enumerate(barrelLayers):
        


        p.SetPoint(i, x, y)


                        
def extractPlotInfo(plot, xVals):
    '''
    Extracts the y-values from a plot, from a set of x-values given in etaBins.
    Assumes that the x-values in etaBins are the low-edges of the bin in the plot
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
        #print ibin, val, lowEdge, binWidth

        # only extract points from desired eta bins
        if lowEdge in xVals:
            info[lowEdge] = {'value' :val, 'error' : error}
    return info
                



if __name__ == "__main__":
  main()

'''
if      (colorIndex==0) return 865; // blue
else if (colorIndex==1) return 801; // orange
else if (colorIndex==2) return 629; // red
else if (colorIndex==3) return 418; // green
else if (colorIndex==4) return  15; // grey
else if (colorIndex==5) return 618; // purple
else if (colorIndex==6) return 432; // turquoise (sorry projectors)
else                    return kBlack;

'''
