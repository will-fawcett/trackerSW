'''
Script to read json file with information on each hit, track (smeared), track (PB matched) and vertex
to make a plot of the verties, which tracks are there etc... 
'''

import numpy as np
import matplotlib.pyplot as plt
import json

def main():

    # open json file
    jFileName = '/Users/Will/Documents/fcc/trackerSW/hitTrackVertexPlotStore/testHitOutput.json'
    with open(jFileName) as data_file:
        data = json.load(data_file)

    # get keys
    keys = data.keys()
    print keys

    # read vertices into array
    numberOfPuVertices = len(data['pileupVertices'])
    print 'There are {0} pileup vertices'.format(numberOfPuVertices)
    vertexZ = np.array( data['pileupVertices'] ) 
    vertexR = np.zeros( (numberOfPuVertices, 1) )

    primaryVertexZ = np.array( [data['primaryVertex']] )
    primaryVertexR = np.array( [0] )
    
    plt.scatter(vertexZ, vertexR)
    plt.scatter(primaryVertexZ, primaryVertexR)
    plt.show()

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
