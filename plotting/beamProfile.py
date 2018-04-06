'''
Script to do some statistics for the beam profile in Z
'''


from ROOT import *
import math
from array import * 
import numpy as np
gROOT.SetBatch(1)

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
    h = TH1D("vertexDistribution", "", 100, -400, 400)
    vals = []
    for i in xrange(10000):
        val = mygaus.GetRandom()
        h.Fill(val)
        vals.append(val)
    h.DrawNormalized()
    can.SaveAs('vertexDistribution.pdf')

    can.SetLogy()
    #can.SetLogx()
    distances = calculateDistances(vals, 400)

    dist = TH1D("distanceDistribution", "", 100, 0, 1)
    for d in distances:
        dist.Fill(d)
    dist.DrawNormalized('E')
    can.SaveAs('distance.pdf')
    return


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
