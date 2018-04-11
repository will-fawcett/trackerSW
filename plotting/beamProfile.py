'''
Script to do some statistics for the beam profile in Z
'''
from utils import getReverseCumulativeHisto, myText
import math
from array import * 
import numpy as np

from ROOT import *
gROOT.SetBatch(1)
gStyle.SetPadBottomMargin(0.15)
gStyle.SetPadLeftMargin(0.13) # increase space for left margin
gStyle.SetPadTickX(1)
gStyle.SetPadTickY(1)
gStyle.SetOptStat(0)

# histogram styling
TEXT_SIZE = 0.04
gStyle.SetLabelSize(TEXT_SIZE, 'X')
gStyle.SetLabelSize(TEXT_SIZE, 'Y')
gStyle.SetTitleSize(TEXT_SIZE, 'X')
gStyle.SetTitleSize(TEXT_SIZE, 'Y')
gStyle.SetHistLineWidth(3)

# Set seed of random generator (default TRandom3)
gRandom.SetSeed(0)

MAX_Z = 400 # mm 
PILEUP = 200 
PILEUP = 1000 

def main():

    # gaussian parameters 
    mean = 0.0
    bunch_length = 75.0 # mm
    luminous_length = bunch_length / math.sqrt(2) 

    print 'Calculation for pileup of ', PILEUP
    print 'Bunch length: {0} mm'.format(bunch_length)
    print 'Luminous length: {0} mm'.format(luminous_length)

    mygaus = TF1("mygaus", "TMath::Gaus(x,0,"+str(luminous_length)+")",-luminous_length*5 , luminous_length*5)

    #########################################
    # make some plots to show results
    #########################################
    can = TCanvas('can', 'can', 500, 500)
    um = 1000  # units

    #____________________________________________
    # Distribution of vertices
    #____________________________________________
    vertices = TH1D("vertexDistribution", "", 100, -400*um, 400*um)
    vals = []
    nEvents = 1000
    weight = 1.0 / float(nEvents)
    for i in xrange(nEvents):
        val = mygaus.GetRandom()*um # um 
        vertices.Fill(val, weight)
        vals.append(val)

    xaxis = vertices.GetXaxis()
    yaxis = vertices.GetYaxis()
    xaxis.SetTitle('Vertex z position [#mum]')
    xaxis.SetRangeUser(-250*um, 250*um)
    yaxis.SetTitle('Fraction')
    yaxis.SetRangeUser(0.0, 0.1)
    vertices.Draw()
    vertices.Fit("gaus", "M") # M: "improve fit", Q: "quiet" (no printing), O: "Don't draw fit or histo
    myText(0.2, 0.80, '#LT#mu#GT = 1000', TEXT_SIZE)
    myText(0.2, 0.75, 'Luminous length = {0:.1f} mm'.format(luminous_length), TEXT_SIZE) 

    theFit = vertices.GetFunction("gaus")
    can.SaveAs('vertexDistribution.pdf')

    #____________________________________________
    # Distribution of distances between vertices
    #____________________________________________
    distances = calculateDistances(vals, MAX_Z*um)

    can.SetLogy(1)
    dist = TH1D("distanceDistribution", "", 1000, 0, 10*um)
    for d in distances:
        dist.Fill(d, weight)

    #distOriginal.GetXaxis().SetRangeUser(0, 1000)
    #dist = distOriginal.Clone('clone')
    xaxis = dist.GetXaxis()
    yaxis = dist.GetYaxis()
    meanDistance = dist.GetMean()
    print meanDistance
    xaxis.SetRangeUser(0, 100)
    yaxis.SetTitle('Fraction of vertices')
    xaxis.SetTitle('Distance between vertices, #deltaz [#mum]')

    dist.Rebin(2)
    dist.GetXaxis().SetRangeUser(0, 1000)
    dist.Draw('E')
    myText(0.45, 0.75, '#LT#mu#GT = 1000',TEXT_SIZE)
    myText(0.45, 0.8, 'Mean distance = 344 #mum', TEXT_SIZE)
    can.SaveAs('distance.pdf')

    #____________________________________________
    # Cumulative distribution of vertex distances 
    #____________________________________________
    can.SetLogy(0)
    #distPc = getReverseCumulativeHisto(dist)
    distPc = dist.GetCumulative()
    xaxis = distPc.GetXaxis()
    yaxis = distPc.GetYaxis()
    xaxis.SetTitle('Distance between vertices, #deltaz [#mum]')
    yaxis.SetTitle('Fraction of vertices #deltaz < X')
    xaxis.SetRangeUser(0, 1500)
    yaxis.SetRangeUser(0, 1)
    distPc.SetMarkerStyle(20)
    distPc.Draw('E')
    distPc.SetLineWidth(3)

    # find where 95% is
    for ibin in xrange(0,distPc.GetNbinsX()+1):
        yval =  distPc.GetBinContent(ibin)
        if yval > 0.95:
            pc95bin = ibin
            break
    print '95% of distances are smaller than:'
    print ibin, distPc.GetBinCenter(ibin), distPc.GetBinContent(ibin)
    avVertex95 = distPc.GetBinCenter(ibin)
    myText(0.4, 0.6, '#LT#mu#GT = 1000',TEXT_SIZE)
    myText(0.4, 0.5, '#LT#deltaz#GT_{Vertex}^{95%} #approx '+'{0} #mum'.format(avVertex95), TEXT_SIZE)
    myText(0.4, 0.4, 'Bunch length = {0} mm'.format(bunch_length) ,TEXT_SIZE)

    #can.SaveAs('cumulativeDistance.pdf')



    #########################################
    # More serious calculation
    #########################################

    means = []
    pc95s = []
    pc05s = []

    for i in xrange(1000):
        [mean, pc95, pc05] = calculateMeanAnd95(mygaus)
        means.append(mean)
        pc95s.append(pc95)
        pc05s.append(pc05)

    # calculate the mean of the mean
    mean95 = np.mean(pc95s)
    mean05 = np.mean(pc05s)
    meanMeans = np.mean(means)

    print ''
    print 'Average mean distance: {0} um'.format(meanMeans*1000)
    print 'Average 95% distance:  {0} um'.format(mean95*1000)
    print 'Average 05% distance:  {0} um'.format(mean05*1000)



def calculateMeanAnd95(mygaus):
    '''
    Take gaussian TF1, extract random numbers from that distribution
    Make a distribution of the "distance" between each number

    '''


    #h1 = TH1F("h1", "test", 50, -5 * luminous_length,  5 *luminous_length)
    #h2 = TH1F("h2", "distances; #Delta z [mm];", 1000, 0, 100)

    # Generate points according to gaussian 
    zRecord = []
    for i in range(PILEUP+1):
        #h1.Fill(mygaus.GetRandom())
        zValue = mygaus.GetRandom() 
        zRecord.append( mygaus.GetRandom() ) 

    # Calculate (distances between each vertex) 
    distances = calculateDistances(zRecord, MAX_Z)

    # Calculate average distance 
    mean = np.mean(distances)


    # What is the distance that 95% of verticies are seperated by (at least)
    # Calculate 95% of entries in list
    entry95 = int(len(distances) *.05)  # roun down, since counting starts at 0 
    value95 = distances[entry95]

    # What is the distance that 5% of vertices are separated by at least
    entry05 = int(len(distances) *.95)
    value05 = distances[entry05]

    #print 'Distances. Mean {0} 95% {1}'.format( mean,  value95) 

    return [mean, value95, value05]


    '''
    # some drawing 
    for d in distances:
        h2.Fill(d)
    can = TCanvas()
    h1.Fit("gaus")
    h1.Draw()
    h1.SetTitle(';z [mm]; Number of verticies')
    can.SaveAs('test.pdf')
    h2.Draw()
    can.SaveAs('test3.pdf')
    '''

def calculateDistances(zRecord, MAX_Z):

    # make sure it's sorted
    zRecord = sorted(zRecord)
    distances = []
    for i in range(len(zRecord)):

        # Remove any verticies with distance > MAX_Z from z0 
        if abs(zRecord[i]) > MAX_Z:
            print 'max z', zRecord[i]
            continue

        try:
            distance = abs( abs(zRecord[i]) - abs(zRecord[i+1]) ) 
            distances.append( distance ) 
        except IndexError:
            if i == len(zRecord):
                continue  
    return sorted(distances)



if __name__ == "__main__":
    main()
