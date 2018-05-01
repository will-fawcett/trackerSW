'''
Script to read json file with information on each hit, track (smeared), track (PB matched) and vertex
to make a plot of the verties, which tracks are there etc... 
'''

import numpy as np
import matplotlib.pyplot as plt
import json
import math

RMAX = 100.0 # mm 
M_PI = 3.14159265
SAVE_PATH = '/Users/Will/Documents/fcc/note/TripletTracker_Note/figures'


#_____________________________________________________________________________
def getTrackEndPoint(z0, eta):
    
    # convert eta to theta
    theta = 2 * math.atan( math.exp( -1* eta) ) # return eta in radians 
    #print eta, theta/M_PI, 'pi'

    shift = RMAX / math.tan(theta) 
    endZ = z0+shift
    return (endZ, RMAX)


#_____________________________________________________________________________
class track():
    def __init__(self, eta, z0, isPU):
        self.eta = eta
        self.isPU = isPU

        # start coordinates
        self.z0 = z0
        self.r0 = 0.0

        # calculate end coordinates of track
        endCoordinates = getTrackEndPoint(self.z0, self.eta)
        self.z1 = endCoordinates[0]
        self.r1 = endCoordinates[1]
    
    def Print(self):
        print '({0}, {1}) --> ({2}, {3})'.format(self.z0, self.r0, self.z1, self.r1)
        print 'eta: ', self.eta
        print 'isPU: ', self.isPU

    def start(self):
        return [self.z0, self.r0]
    def end(self):
        return [self.z1, self.r1]

    def xVar(self):
        return [self.z0, self.z1]
    def yVar(self):
        return [self.r0, self.r1]



#_____________________________________________________________________________
def main():

    # open json file
    jFileName = '/Users/Will/Documents/fcc/trackerSW/hitTrackVertexPlotStore/testHitOutput.json'
    with open(jFileName) as data_file:
        data = json.load(data_file)

    # get keys
    keys = data.keys()
    print keys

    #################################
    # Extract info from json
    #################################

    # read vertices into array
    numberOfPuVertices = len(data['pileupVertices'])
    print 'There are {0} pileup vertices'.format(numberOfPuVertices)
    vertexZ = np.array( data['pileupVertices'] ) 
    vertexR = np.zeros( (numberOfPuVertices, 1) )
    primaryVertexZ = np.array( [data['primaryVertex']] )
    primaryVertexR = np.array( [0] )

    # get smeared tracks 
    smearedTrackEta  = data['smearedTrackEta']
    smearedTrackIsPU = data['smearedTrackIsPU']
    smearedTrackZ0   = data['smearedTrackZ0']

    # get primary bin
    PB = data['primaryBin']
    binMin = PB - 0.5
    binMax = PB + 0.5

    # get matched tracks 
    matchedTrackEta  = data['matchedTrackEta']
    matchedTrackIsPU = data['matchedTrackIsPU']
    matchedTrackZ0   = data['matchedTrackZ0']


    plotMatched = True
    plotMatched = False
    addPB = True
    #################################
    # plot! 
    #################################


    # select set of tracks 
    if plotMatched:
        trackInfo = zip(matchedTrackEta, matchedTrackZ0, matchedTrackIsPU)
    else:
        trackInfo = zip(smearedTrackEta, smearedTrackZ0, smearedTrackIsPU)

    # Draw pileup tracks first
    for eta, z0, pu in trackInfo:
        aTrack = track(eta, z0, pu)
        if aTrack.isPU:
            plt.plot(aTrack.xVar(), aTrack.yVar(), color='grey', linestyle='-', linewidth=1)

    # draw hard scatter tracks second
    for eta, z0, pu in trackInfo:
        aTrack = track(eta, z0, pu)
        if not aTrack.isPU:
            plt.plot(aTrack.xVar(), aTrack.yVar(), color='red', linestyle='-', linewidth=2)

    # plot vertices 
    if not plotMatched:
        plt.scatter(vertexZ, vertexR, c='dodgerblue')
    plt.scatter(primaryVertexZ, primaryVertexR, c='orange')

    # Draw primary bin
    if addPB: 
        plt.plot( [binMin, binMax], [-0.05, -0.05], color='green', linestyle='-', linewidth=3)

    # Add axis labels
    plt.ylabel('r [mm]')
    plt.xlabel('z [mm]')

    if not plotMatched:
        plt.savefig(SAVE_PATH+'/trackDisplayFull.eps', bbox_inches='tight' )


    xmin = 35
    xmax = 60
    ymin = -0.1
    ymax = 1.0
    axes = plt.gca()
    axes.set_xlim([xmin,xmax])
    axes.set_ylim([ymin,ymax])

    if plotMatched:
        plt.savefig(SAVE_PATH+'/trackDisplayMatched_zoom.eps', bbox_inches='tight' )
    else: 
        plt.savefig(SAVE_PATH+'/trackDisplayFull_zoom.eps', bbox_inches='tight' )


    return

    # Fixing random state for reproducibility
    np.random.seed(19680801)

    N = 50
    x = np.random.rand(N)
    y = np.random.rand(N)
    colors = np.random.rand(N)
    area = (30 * np.random.rand(N))**2  # 0 to 15 point radii

    plt.scatter(x, y, s=area, c=colors, alpha=0.5)
    plt.show()




if __name__ == "__main__":
    main()
