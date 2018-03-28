#!/usr/bin/python
'''
Script to make plots of data rate as a function of radial distance
'''

import json
from glob import glob




def main(verbose):

    fileNames = [
        'triplet1_50.json',
        'triplet2_50.json',
        'triplet3_50.json',
        'triplet4_50.json',
        'triplet5_50.json',
        ]

    superDict = {}

    # open json files, collate all data
    for fName in fileNames:
        jFileName = '/atlas/users/wfawcett/fcc/trackerSW/dataRate/'+fName
        layer = int(fName.split('_')[0][-1])
        with open(jFileName) as data_file:
            info = json.load(data_file)
        superDict[layer] = info

    # get the radii for the triplet layers
    makePlot(superDict, "Data rate per cm^2 - 40Mhz,spars [Gb/s/cm^2]</b")

def makePlot(superDict, variable):

    layers = sorted(superDict.keys())

    radii = []
    rates = []
    for layer in layers:
        radiiPositions     = [-1+layer, 0+layer, 1+layer]

        radiiList = superDict[layer]["Radius [mm]"]
        rateLits = superDict[layer][variabe]

        for pos in radiiPositions:
            radii.append(radiiList[pos])
            rates.append(rateLits[pos])

    xvals = radii
    yvals = rates

    # make a TGraph? 
    can = TCanvas("can", "can", 500, 500)

if __name__ == "__main__":

    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("-v", "--verbose", help="Turn on verbose messages", action="store_true", default=False)
    args = parser.parse_args()
    verbose = args.verbose

    main(verbose)


