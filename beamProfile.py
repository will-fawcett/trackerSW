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
PILEUP = 1000 
PILEUP = 200 

def main():
    # gaussian parameters 
    mean = 0.0
    bunch_length = 75.0 # mm
    luminous_length = bunch_length / math.sqrt(2) 

    print 'Calculation for pileup of ', PILEUP
    print 'Bunch length: {0} mm'.format(bunch_length)
    print 'Luminous length: {0} mm'.format(luminous_length)

    mygaus = TF1("mygaus", "TMath::Gaus(x,0,"+str(luminous_length)+")",-luminous_length*5 , luminous_length*5)

    means = []
    pc95s = []

    for i in range(1000):
        [mean, pc95] = calculateMeanAnd95(mygaus)
        means.append(mean)
        pc95s.append(pc95)

    # calculate the mean of the mean
    mean95 = np.mean(pc95s)
    meanMeans = np.mean(means)

    print ''
    print 'Average mean distance: {0} um'.format(meanMeans*1000)
    print 'Average 95% distance:  {0} um'.format(mean95*1000)

def calculateMeanAnd95(mygaus):



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

    #print 'Distances. Mean {0} 95% {1}'.format( mean,  value95) 

    return [mean, value95]


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
