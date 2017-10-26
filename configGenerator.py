#!/usr/bin/env python

'''
Script to generate config files for tkLayout, but including a triplet layer at a variable location in the outer tracker.
Variables include
    - Layer of triplet in barrel
    - Spacing of triplet layer in barrel
    - Position of triplet in end-cap
    - Spacing of triplet in end-cap
'''
from defaultConfig import addBeampipe, addInnerTracker, addOuterTrackerHeader, addTripletHeader, addNormalBarrelHeader, addDefaultOuterEndcap
from Layer import Layer

# Mapping of barrel layers to radii [mm]
radiiMap = {1: 522.0, 2:727.56, 3:932.67, 4:1137.78, 5:1342.89, 6:1548.0}

# Mapping of end-cap layers to z-distance [mm]
ecMap = {}

# allowance within the triplet region for extra space (+ and - of the required space) [mm]
TRIPLET_TOLERANCE = 10

debug = True # development

def main(tripletLayer, layerSpacing):
    print 'hello world'
    print 'tripletLayer: {0}, {1}'.format(type(tripletLayer), tripletLayer)
    print 'layerSpacing: {0}, {1}'.format(type(layerSpacing), layerSpacing)
    print 'TRIPLET_TOLERANCE', TRIPLET_TOLERANCE

    # Create new config file
    ofile = open("layout.cfg", "w")

    # Write default/unmodified information
    ofile.write("@include SimParms\n") # important first line
    addBeampipe(ofile)
    addInnerTracker(ofile)

    # Now create outer tracker, with triplet
    addOuterTrackerHeader(ofile)
    if (tripletLayer==1):
        genRegTriplet(ofile, tripletLayer, layerSpacing)
        genRegNormal(ofile, [2,3,4,5,6], 1)
    elif (tripletLayer==6):
        genRegNormal(ofile, [1,2,3,4,5], 0)
        genRegTriplet(ofile, tripletLayer, layerSpacing)
    else:
        genRegNormal(ofile, range(1, tripletLayer), 0)
        genRegTriplet(ofile, tripletLayer, layerSpacing)
        genRegNormal(ofile, range(tripletLayer+1, 7), 2)

    # Now add end-caps
    addDefaultOuterEndcap(ofile)

    # End the outer-tracker
    ofile.write('}\n')


def genRegNormal(ofile, layerRange, barrelAreaID):
    '''
    Adds normal barrel regions withing the given layer range.
    Automatically detects if "multilayer" functionailty can be used
    Args:
        ofile: the file to be written to
        layerRange: the range of barrel layers to be included
    '''

    barrelName = "BRL_"+str(barrelAreaID)+"_outer"

    # Calcualte length of barrel
    if len(layerRange) == 1 and layerRange[0] != 6:
        innerRadius = radiiMap[layerRange[0]]
        outerRadius = radiiMap[layerRange[0]] + 10
    elif len(layerRange) == 1 and layerRange[0] == 6:
        innerRadius = radiiMap[layerRange[0]] - 10
        outerRadius = radiiMap[layerRange[0]]
    else:
        innerRadius = radiiMap[layerRange[0]]
        outerRadius = radiiMap[layerRange[-1]]

    if debug:
        print 'Generating normal region for', barrelName
        print '\tinnerRadius' , innerRadius
        print '\touterRadius' , outerRadius

    addNormalBarrelHeader(ofile, barrelName, innerRadius, outerRadius)

    # Add layers to barrel, first add macroPixel layers
    if layerRange[0] == 1:
        if len(layerRange)==1:
            # one layer of macroPixel
            l1 = Layer(radius=-1, color=7, moduleType="macroPixel", layerNumber=1)
        elif len(layerRange) >= 2:
            # double layer of macroPixel
            l1 = Layer(radius=-1, color=7, moduleType="macroPixel", layerNumber="1-2")
        l1.addLayer(ofile)
    elif layerRange[0] == 2:
        # one layer of macroPixel
        l1 = Layer(radius=-1, color=7, moduleType="macroPixel", layerNumber=2)
        l1.addLayer(ofile)

    # remove layers 1 and 2 if in list
    if 1 in layerRange:
        layerRange.remove(1)
    if 2 in layerRange:
        layerRange.remove(2)

    # N layers of strips, in with N repeated layers, excluding layers 1 and 2
    if len(layerRange) > 1:
        layerNumbering = "{0}-{1}".format(layerRange[0], layerRange[1])
    elif len(layerRange) == 1:
        layerNumbering = layerRange[0]
    else:
        return # No remaining layers to draw

    l2 = Layer(radius=-1, color=1, moduleType="strip", layerNumber=layerNumbering)
    l2.addLayer(ofile)

    # Add end of barrel region
    ofile.write('    }\n')






def genRegTriplet(ofile, position, spacing):
    '''
    Adds the triplet information based on the requested barrel layer Position
    Args:
        ofile: the file to be written to
        position: requested position of the barrel layer
        spacing: requested spacing between the triplet layers [mm]
    '''

    if position == 1:
        barrelName = "BRL_0_triplet"
    else:
        barrelName = "BRL_1_triplet"

    # Calculate inner and outer radius based on requested position and layer spacing
    # Allow for triplet to be at the top and bottom of barrel region
    tripletCentroid = radiiMap[position]
    if position == 1:
        tripletCentroid += (TRIPLET_TOLERANCE+spacing)
    if position == 6:
        tripletCentroid -= (TRIPLET_TOLERANCE+spacing)

    innerRadius = tripletCentroid - (TRIPLET_TOLERANCE+spacing)
    outerRadius = tripletCentroid + (TRIPLET_TOLERANCE+spacing)

    if debug:
        print 'Triplet in layer {0}, spacing {1}'.format(position, spacing)
        print 'Nominal centroid: {0}, Calculated centroid {1}'.format(radiiMap[position], tripletCentroid)

    # add triplet sub-region header
    addTripletHeader(ofile, barrelName, innerRadius, outerRadius)

    # Calculate radii of triplet layers (maybe put this into a function?)
    radius1 = tripletCentroid-spacing
    radius2 = tripletCentroid
    radius3 = tripletCentroid+spacing
    l1 = Layer(radius=radius1, color=7, moduleType="macroPixel", layerNumber=1)
    l2 = Layer(radius=radius2, color=6, moduleType="macroPixel", layerNumber=2)
    l3 = Layer(radius=radius3, color=5, moduleType="macroPixel", layerNumber=3)

    l1.addLayer(ofile)
    l2.addLayer(ofile)
    l3.addLayer(ofile)
    ofile.write('    }\n') # close brace after barrel area




from optparse import OptionParser
import sys
if __name__ == "__main__":
  parser = OptionParser()
  #parser.add_option("-j", "--jsonFile", action="store", type="string", help="Input JSON file")
  #parser.add_option("-o", "--outputDir", action="store", type="string", default=os.getcwd(), help="Output directory for plots")
  parser.add_option("-l", "--tripletLayer", action="store", type="int", help="Triplet layer in barrel, choose 1--6")
  parser.add_option("-s", "--layerSpacing", action="store", type="int", help="Spacing of triplet layers in mm")
  #parser.add_option("-W", "--chartWidth", action="store", type="int", default = 300, help="width of each chart plot")
  #parser.add_option("-H", "--chartHeight", action="store", type="int", default = 300, help="height of each chart plot")
  #parser.add_option("-l", "--labelFormat", action="store", type="string", default="%perc", help="label format: %val for numbers, %perc for percentages")
  if len(sys.argv) == 1:
    parser.print_help()
    sys.exit(0)

  options, args = parser.parse_args()
  option_dict = dict( (k, v) for k, v in vars(options).iteritems() if v is not None)
  main(**option_dict)
