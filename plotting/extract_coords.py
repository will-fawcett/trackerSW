from ROOT import * 
import json
gROOT.SetBatch(1)
gStyle.SetPalette(kViridis)
gStyle.SetPadLeftMargin(0.15) # increase space for left margin

gStyle.SetGridStyle(3) 
gStyle.SetGridColor(kGray)

#____________________________________________________________________________
def checkDir(dir, CHECK=False):
    import os
    ''' Create a directory if it does not exist,
        overwrite it otherwise
    '''
    # if output directory does not exist, then create it
    if not os.path.isdir(dir):
        print 'Creating directory', dir
        os.mkdir(dir)
        os.system('chmod g+w '+dir)
    # If it already exists, check if one wants to overwrite
    elif CHECK:
        print dir, "already exists... are you sure you want to overwrite it?",
        yesno = raw_input("y/n? ")
        if yesno != "y": sys.exit("Exiting, try again with a new name")
    else:
        print dir, "already exists and will be overwritten"
        print 'Dir will be', dir

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
layoutType = 'triplet' # triplet|quartet|splitQuartet
layoutType = 'quartet' # triplet|quartet|splitQuartet
PLOT_DIR = 'plots_{0}/'.format(layoutType)
checkDir(PLOT_DIR)

# variables from which to extract info from
variableMap = {
        'z0res'     : {'units' : '[#mum]', 'title' : '#deltaz_{0}' },
        'd0res'     : {'units' : '[#mum]', 'title' : '#deltad_{0}' },
        'logptres'  : {'units' : '[%]' },
        'pres'      : {'units' : '[%]' },
        'phi0res'   : {'units' : '[deg]' }, # don't care so much about these
        'ctauRes'   : {}, 
        'cotgThres' : {},
        
        'barrelLayers' : {'units' : '' , 'title' : 'Barrel layer' },
        'tripletSpacings' : {'units' : '[mm]', 'title' : 'Triplet spacing' },
        'trackMomentum' : {'units' : '[GeV]', 'title' : 'Track p_{T}'}, # Note could also have track momentum 
        'trackEta' : {'units' : '', 'title' : 'Track #eta'},
        }

#___________________________________________________________________________
def main():
    
    #########################
    #####  Setup  ###########
    multipleScattering = True
    region = layoutType # could be tracker, outer, inner
    plotEtaValues = [0, 0.5, 1, 1.5] # eta values to be extracted
    tripletSpacings = [20, 25, 30, 35, 40, 50] # Layer spacings to consider
    barrelLayers = [1, 2, 3, 4] #, 5] # Triplet in barrel layer? 
    #########################

    if multipleScattering:
        scattering = "withMS"
    else:
        scattering = "noMS"

    # check layout type 
    if not layoutType in ['triplet', 'quartet', 'splitQuartet']:
        print 'ERROR: layout type must be triplet|quartet|splitQuartet' 
        sys.exit()
    else:
        print 'Will generate plots for layout type: ', layoutType


    trackParameters = ['z0res', 'd0res'] # variableMap.keys() testing
    #layers = [1]
    #spacings = [20]

    # Dictionary to store all of the information
    megaDict = {}

    # First, extract all of the data and store it in a nice python dictionary 
    for variable in trackParameters:
        megaDict[variable] = {}

        for layer in barrelLayers:
            megaDict[variable][layer] = {}

            for spacing in tripletSpacings:
                megaDict[variable][layer][spacing] = {}

                # open root file and get plot 
                path = RESULTS_PATH + '/results_FCC{0}_{1}barrel{2}mm/'.format(layoutType, layer, spacing)
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
    megaDict['metadata'] = {
            'barrelLayers' : barrelLayers,
            'tripletSpacings' : tripletSpacings, 
            'etaValues' : plotEtaValues, 
            'trackpT' : momentumValues,
            'layoutType': layoutType
            }


    # Store the json file
    outNameJson = 'infoStore{0}.json'.format(layoutType)
    with open(outNameJson, 'w') as fp:
        json.dump(megaDict, fp, sort_keys=True, indent=2)
    
    # now make some nice plots
    for variable in trackParameters:

        for pt in momentumValues:
            for eta in plotEtaValues:
                make2DPlot(variable, megaDict[variable], barrelLayers=[1,2,3], tripletSpacings=tripletSpacings, trackMomentum=pt, trackEta=eta)

        series = { "trackMomentum" : [1, 10, 100, 1000] }
        constants = { "trackEta" : 0 , 'tripletSpacing' : 20 } 
        xVar = 'barrelLayers' 
        makePlot(megaDict, xVar, variable, constants, series)

        '''
        series = { "trackEta" : plotEtaValues } 
        constants = { "trackMomentum" : 10, 'tripletSpacing' : 20 }
        xVar = 'barrelLayers' 
        makePlot(megaDict, xVar, variable, constants, series)
        '''

        series = { "trackMomentum" : [1, 10, 100, 1000] }
        constants = { "trackEta" : 0 , 'barrelLayer' : 1 } 
        xVar = 'tripletSpacings' 
        if variable == "z0res":
            legendPosition = "bottomLeft"
        if variable == "d0res": 
            legendPosition = "topRight"

        makePlot(megaDict, xVar, variable, constants, series, legendPosition)



#___________________________________________________________________________
def makePlot(plotInfo, xVar, yVar, constants, series, legendPosition="topLeft"): 
    '''
    plotInfo holds a multidimensional array of points, with values
    [barrel layer, triplet spacing, track pT, track eta, track parameter]
    This function will make a plot of one of these parameters versus another.
    Typically yVar will be a track parameter
    (the plot is a projection of this space onto a 2d plane)
    Args:
        plotInfo: dictionary with points in multidimensional space
        xVar: string with the x-variable name 
        yVar: string with the y-variable name 
        constants:
        series:
    '''

    print 'making plot for {0} vs {1}. {2} will be held constant. Data series {3} {4}'.format(xVar, yVar, constants, series.keys()[0], series[series.keys()[0]]) 
    plotTitle = '{0} vs {1} : '.format(variableMap[yVar]['title'], variableMap[xVar]['title'])
    for con in constants.keys():
        plotTitle += '{0}={1} '.format(con,constants[con])
    plotTitle += ' ('+layoutType+')'


    
    # extract xvalues  
    xValues = sorted(plotInfo['metadata'][xVar])

    # Data series 
    seriesType = series.keys()[0] # assume only one type of series?
    seriesValues = series[seriesType]

    # Some nice graph colours 
    colours = [
        865, # blue
        801, # orange
        629, # red
        418,  # green
        15,  # grey
        618, # purple
        1, # black
    ]

    # array of TGraphs
    graphArray = [] 

    leg = prepareLegend(legendPosition)
    leg.SetHeader('{0} {1}'.format(variableMap[seriesType]['title'], variableMap[seriesType]['units']))

    for iseries, dataSeries in enumerate(seriesValues):

        # define tgraph 
        graphArray.append(TGraphErrors()) 
        graphName = plotTitle+';{0} {1}; {2} {3}'.format(variableMap[xVar]['title'], variableMap[xVar]['units'], variableMap[yVar]['title'], variableMap[yVar]['units'] )
        
        graphArray[iseries].SetTitle(graphName)
        graphArray[iseries].SetMarkerColor(colours[iseries])
        graphArray[iseries].SetLineColor(colours[iseries])

        leg.AddEntry(graphArray[iseries], str(dataSeries), 'lp') 
       
        # Fill graph 
        smallestYval = 999999999
        for ipoint, xVal in enumerate(xValues):

            # find y-val (bit messy atm)  
            if xVar == 'barrelLayers':
                barrelLayer = xVal 
            else:
                barrelLayer = constants['barrelLayer']

            if xVar == 'tripletSpacings':
                tripletSpacing = xVal
            else:
                tripletSpacing = constants['tripletSpacing']

            if series.keys()[0] == 'trackMomentum':
                trackMomentum = dataSeries
            else:
                trackMomentum = constants['trackMomentum']

            if series.keys()[0] == 'trackEta':
                trackEta = dataSeries
            else:
                trackEta = constants['trackEta'] 

            trackParam = yVar

            yVal = plotInfo[trackParam][barrelLayer][tripletSpacing][trackMomentum][trackEta]['value']
            yErr = plotInfo[trackParam][barrelLayer][tripletSpacing][trackMomentum][trackEta]['error']

            graphArray[iseries].SetPoint(ipoint, xVal, yVal)
            graphArray[iseries].SetPointError(ipoint, 0, yErr) 

            if yVal < smallestYval:
                smallestYval = yVal


    # Now draw the plots     
    can = TCanvas('can', 'can', 800, 600)
    can.SetGrid()
    #can.SetLogy()
    mg = TMultiGraph() # takes (some) care of axis ranges
    for iseries in range(len(seriesValues)):
        mg.Add( graphArray[iseries], 'lp' ) 
    mg.SetTitle(graphName)
    mg.Draw('a') 
    leg.Draw()

    # Change the axis limits
    mgMin = mg.GetHistogram().GetYaxis().GetXmin()
    mgMax = mg.GetHistogram().GetYaxis().GetXmax()
    #print mgMin, mgMax
    mg.GetHistogram().GetYaxis().SetRangeUser(mgMin, mgMax*1.1) # make space for legend
        

    #gPad->Modified();
    #mg->GetXaxis()->SetLimits(1.5,7.5);
    #mg->SetMinimum(0.);
    #mg->SetMaximum(10.);




    saveName = '{0}_vs_{1}_{2}'.format(xVar, yVar, seriesType)
    for con in constants.keys():
        saveName += '_{0}{1}'.format(con, constants[con])
    can.SaveAs(PLOT_DIR+saveName +'.pdf')


    if int(mgMin) == 0: 
        print 'adding space'
        mg.GetHistogram().GetYaxis().SetRangeUser(smallestYval*0.5, mgMax*1.1) # needed for log plots, so much for TMultiGraph :/ 
    gPad.Modified()

    can.SetLogy()
    can.SaveAs(PLOT_DIR+'log_'+saveName+'.pdf')
    print '' 
        

            
#___________________________________________________________________________
def make2DPlot(variable, plotInfo, barrelLayers, tripletSpacings, trackMomentum, trackEta):
    
    can = TCanvas('can', 'can', 500, 500)
    maxSpacing = max(tripletSpacings) + 10
    nBinsx = maxSpacing *10 + 10 

    plotTitle = 'Track pT = {0} GeV,  track #eta = {1}'.format(trackMomentum, trackEta)
    zTitle = variableMap[variable]['title'] + variableMap[variable]['units']

    print 'plot properties', 'hist', variable+';Layer spacing [mm]; Barrel layer;'+zTitle, nBinsx, 0, maxSpacing, len(barrelLayers)+1, barrelLayers[0], barrelLayers[-1]+1
    h = TH2D('hist', '', nBinsx, 0, maxSpacing, len(barrelLayers)*10, 0, barrelLayers[-1]+1)
    xaxis = h.GetXaxis()
    yaxis = h.GetYaxis()

    g = TGraph2D()
    ipoint = 0

    f = TFile.Open('test.root', 'RECREATE')

    for layer in barrelLayers:
        for spacing in tripletSpacings:
            xbin = xaxis.FindBin(spacing)
            ybin = yaxis.FindBin(layer)
            #print ybin, layer

            z = plotInfo[layer][spacing][trackMomentum][trackEta]['value']
            e = plotInfo[layer][spacing][trackMomentum][trackEta]['error']

            h.SetBinContent(xbin,ybin,z)
            h.SetBinError(xbin,ybin,e)
            g.SetPoint(ipoint, spacing, layer, z) 
            ipoint += 1

    #h.Draw('surf')
    #h.Draw('cont3')
    #can.SaveAs(PLOT_DIR+'test.pdf')

    g.Draw('surf3')
    g.Draw('P0same')
    g.SetTitle(plotTitle+';Layer spacing [mm]; Barrel layer;'+zTitle)
    g.GetHistogram().GetXaxis().SetTitleOffset(2)
    g.GetHistogram().GetYaxis().SetTitleOffset(2)
    g.GetHistogram().GetYaxis().SetNdivisions( len(barrelLayers) ,5,0)
    g.GetHistogram().GetYaxis().SetTitleOffset(2)
    g.GetHistogram().GetZaxis().SetTitleOffset(2.2)
    saveName = '{0}_2D'.format(variable, 'barrelLayer', 'layerSpacing')
    saveName += '_tackMomenta{0}_trackEta{1}'.format(int(trackMomentum), int(trackEta*10)) 
    can.SaveAs(PLOT_DIR+saveName+'.pdf')
    g.Write()


    can.SetLogz()
    can.SaveAs(PLOT_DIR+'log_'+saveName+'.pdf')
    
    # try projecton
    proj = g.Project('xy')
    proj.Draw()
    can.SaveAs('projTest.pdf')

    
#___________________________________________________________________________
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



#___________________________________________________________________________
if __name__ == "__main__":
    main()
