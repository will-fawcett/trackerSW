#!/usr/bin/python
'''
Script to make plots of data rate as a function of radial distance
'''

import json
from glob import glob

import numpy as np
import matplotlib.pyplot as plt

import os


def main(verbose):
    
    # get directory where info is stored
    STORE_DIR = os.path.dirname(os.path.realpath(__file__)) + "/../dataRate/"

    # files to investigate
    fileNames = [
        'triplet1_50.json',
        'triplet2_50.json',
        'triplet3_50.json',
        'triplet4_50.json',
        'triplet5_50.json',
        ]

    # things to plot
    variables = {
        'Data rate per cm^2 - 40Mhz,spars [Gb/s/cm^2]' : {'ytitle' : 'Data rate', 'units' : '[Gb/s/cm$^2$]', 'title' :  'Data rate for minimum bias @ 40 MHz (PU=1000)', 'save' : 'perArea'},
        'Data rate per layer - 40MHz,spars [Tb/s]' :     {'ytitle' : 'Data rate per layer', 'units' : '[Tb/s]', 'title' : 'Data rate for minimum bias @ 40 MHz (PU=1000)', 'save' : 'perLayer'},
        'Module avg occupancy (max[sen1,sen2])[%]' :     {'ytitle' : 'Module average occupancy', 'units' : '', 'title' : '', 'save' : 'moduleAverageOccupancy'},
        'Module max occupancy (max[sen1,sen2])[%]' :     {'ytitle' : 'Module maximum occupancy', 'units' : '', 'title' : '', 'save' : 'moduleMaxOccupancy'},

        #'Max flux in Z [particles/cm^2]'              :

        #'Data rate per module - 40Mhz : spars [Gb/s]' :  
        #'Module max occupancy (max[sen1 : sen2])[%]'  :  

        #'Data rate per module -  1Mhz : spars [Gb/s]' :  
        #'Max cell area (1% occupancy) [mm^2]'         :  
        #'Module bandwidth/(addr+clsWidth=2b[b]'       :  
        #'Data rate per layer -  1MHz : spars [Tb/s]'  :  
        #'Min flux in Z [particles/cm^2]'              :  
        #'Data rate per cm^2 -  1Mhz : spars [Gb/s/cm^2]</b' :  
        #'Z position [mm] related to max flux'         :  
        #'Data rate per ladder - 40Mhz : spars [Gb/s]' :  
        #'Data rate per ladder -  1Mhz : spars [Gb/s]' : 
        #'Mod. bandwidth(#chnls*(addr+clsWidth)[kb]'   :  
        #'Mod. bandwidth (matrix*1b/channel) [kb]'     :  
    }


    superDict = {}

    # open json files, collate all data
    for fName in fileNames:
        jFileName = STORE_DIR+fName
        layer = int(fName.split('_')[0][-1])
        with open(jFileName) as data_file:
            info = json.load(data_file)
        superDict[layer] = info

    print superDict[1].keys()

    for variable in variables.keys():
        [xvals, yvals] = getXYVals(superDict, variable)
        makePlot(xvals, yvals, variables[variable])



def makePlot(xvals, yvals, settings):
    '''
    makes a matplotlib plot 
    given xvals and yvals
    '''
    title = settings['title'] 
    name = settings['save']

    #plt.ioff()
    plt.figure(name)
    plt.plot(xvals, yvals, 'o-')
    plt.title(title)
    plt.ylabel('{0} {1}'.format(settings['ytitle'], settings['units']))
    plt.xlabel('Radius [mm]')
    #plt.show()
    fig = plt.figure(name)
    plt.savefig('dataRate/{0}.pdf'.format(name),  bbox_inches='tight')
    #plt.close()


def getXYVals(superDict, variable):
    '''
    Returns two lists of the same size with the x and y values to plot
    '''


    layers = sorted(superDict.keys())
    radii = []
    rates = []
    for layer in layers:
        radiiPositions     = [-1+layer, 0+layer, 1+layer]

        radiiList = superDict[layer]["Total [TB/s]</th </tr<tr<tdRadius [mm]"] # radius 
        rateLits = superDict[layer][u"{0}".format(variable)]


        for pos in radiiPositions:
            radii.append(radiiList[pos])
            rates.append(rateLits[pos])

    xvals = radii
    yvals = rates
    return [xvals, yvals]

if __name__ == "__main__":

    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("-v", "--verbose", help="Turn on verbose messages", action="store_true", default=False)
    args = parser.parse_args()
    verbose = args.verbose

    main(verbose)
