from ROOT import * 
gROOT.SetBatch(1)


# Convenience function to check if an object is a TProfile
def is_profile(p):
    return isinstance(p, TProfile)

def printPrimitiveNames(tobject):

    primList = tobject.GetListOfPrimitives()
    print 'TObject of type: {0}, and name: {1}, has {2} primitives'.format(type(tobject), tobject.GetName(), len(primList))
    for x in primList:
        print '\t', x

# layer spacings
spacings = [10, 20, 25, 30, 25, 40, 50]

# barrel layers
barrels = [1, 2, 3]

RESULTS_PATH = '~/Documents/fcc/results-tkLayout'

def main():
    
    #########################
    # Setup
    multipleScattering = True
    region = 'triplet' # could be tracker, outer, inner
    plotEtaValues = [0, 1, 2, 2.5, 3] 
    #########################

    if multipleScattering:
        scattering = "withMS"
    else:
        scattering = "noMS"

    # variables from which to extract info from
    variables = [
            'z0res',
            'd0res'
            'logptres',
            'pres',
            'phi0res', # don't care so much about these
            'ctauRes', 
            'cotgThres',
            ]

    variables = ['z0res'] # testing
    layers = [1]
    spacings = [20]

    # First, extract all of the data and store it in a nice python dictionary 
    for variable in variables:

        for layer in layers:
            for spacing in spacings:

                # open root file and get plot 
                path = RESULTS_PATH + '/results_FCCtriplet_{0}barrel{1}mm/'.format(layer, spacing)
                fName = "{0}_{1}_{2}_Pt000".format(variable, region, scattering) # Note also can have P000 (for momentum)
                f = TFile.Open(path+fName+'.root') 
                can = f.Get(fName) 

                # Extract possible momentum values from list of primitives
                primList = can.GetListOfPrimitives()
                primNames = [x.GetName() for x in primList]
                momentumValues = [float(x.split('_')[-1]) for x in primNames if 'eta' in x]
                print momentumValues

                # Loop over primitives to extract all the info
                for prim in primList:
                    if is_profile(prim): 
                        momentum = float(prim.GetName().split('_')[-1])
                        print momentum

                        # get particular plot
                        plot = can.GetPrimitive(prim.GetName())

                        thisPlotInfo = extractPlotInfo(plot, plotEtaValues)                         
                        print thisPlotInfo

                


                        
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
        #print ibin, val, lowEdge, binWidth

        # only extract points from desired eta bins
        if lowEdge in xVals:
            info[lowEdge] = val
    return info
                



if __name__ == "__main__":
  main()

