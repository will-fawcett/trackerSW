#!/usr/bin/env python

'''
Script to generate config files for tkLayout, but including a triplet layer at a variable location in the outer tracker.
Variables include
    - Layer of triplet in barrel
    - Spacing of triplet layer in barrel
    - Position of triplet in end-cap
    - Spacing of triplet in end-cap
'''
from defaultConfig import * 
from Layer import Layer

# Mapping of barrel layers to radii [mm]
radiiMap = {1: 522.0, 2:727.56, 3:932.67, 4:1137.78, 5:1342.89, 6:1548.0}

# Mapping of end-cap layers to z position [mm]
zMap = {1: 2622.5, 2: 2986.1, 3: 3396.8, 4:3864.0, 5: 4395.4, 6: 5000.0}

# Mapping of end-cap layers to z-distance [mm]
ecMap = {}

# allowance within the triplet region for extra space (+ and - of the required space) [mm]
TRIPLET_TOLERANCE = 10

# Overlaps of modules 
BIG_DELTA = 0 
SMALL_DELTA = 0 

#____________________________________________________________________________
def main(tripletLayer, layerSpacing, addECtriplet, ecTripletLayer, ecTripletSpacing, path, debug):
    print 'barrel tripletLayer: {0}, {1}'.format(type(tripletLayer), tripletLayer)
    print 'barrel layerSpacing: {0}, {1}'.format(type(layerSpacing), layerSpacing)
    print 'TRIPLET_TOLERANCE', TRIPLET_TOLERANCE
    print 'bigDelta: {0} \t\t smallDelta {1}'.format(BIG_DELTA, SMALL_DELTA)
    print 'Add endcap triplet?', addECtriplet
    if addECtriplet:
        print 'endcap triplet layer: {0} {1}'.format(type(ecTripletLayer), ecTripletLayer)
        print 'endcap triplet spacing: {0} {1}'.format(type(ecTripletSpacing), ecTripletSpacing)


    # Create new config file
    fName = path + "FCCtriplet_{0}barrel{1}mm".format(tripletLayer, layerSpacing)
    if addECtriplet:
        fName += "_{0}EC{1}mm".format(ecTripletLayer, ecTripletSpacing)
    fName += ".cfg"
    print 'Writing to file', fName
    ofile = open(fName, "w")

    # Write default/unmodified information
    ofile.write("@include SimParms\n") # important first line
    addBeampipe(ofile)
    addInnerTracker(ofile)

    # Now create outer tracker, with triplet
    addOuterTrackerHeader(ofile)
    if (tripletLayer==1):
        genRegTriplet(ofile, tripletLayer, layerSpacing, debug)
        genRegNormal(ofile, [2,3,4,5,6], 1, debug)
    elif (tripletLayer==6):
        genRegNormal(ofile, [1,2,3,4,5], 0, debug)
        genRegTriplet(ofile, tripletLayer, layerSpacing, debug)
    else:
        genRegNormal(ofile, range(1, tripletLayer), 0, debug)
        genRegTriplet(ofile, tripletLayer, layerSpacing, debug)
        genRegNormal(ofile, range(tripletLayer+1, 7), 2, debug)

    # Now add end-caps (optional)
    if addECtriplet:
        # addECHeader(ofile)
        # addDefaultECRings(ofile)
        if (ecTripletLayer == 1):
            genRegECTriplet(ofile, ecTripletLayer, ecTripletSpacing, debug)
            genRegECNormal(ofile, range(2,7), 1, debug)
        elif (ecTripletLayer == 6):
            genRegECNormal(ofile, range(1,6), 0, debug)
            genRegECTriplet(ofile, ecTripletLayer, ecTripletSpacing, debug)
        else:
            genRegECNormal(ofile, range(1, ecTripletLayer), 0, debug)
            genRegECTriplet(ofile, ecTripletLayer, ecTripletSpacing, debug)
            genRegECNormal(ofile, range(ecTripletLayer+1, 7), 2, debug)
    else:
        addDefaultOuterEndcap(ofile)

    # End the outer-tracker
    ofile.write('}\n')

#____________________________________________________________
def genRegECNormal(ofile, layerRange, ecAreaID, debug):
    '''
    Adds normal end-cap regions within the given layer range.
    Args:
        ofile: the file to be written to
        layerRange: the range of barrel layers to be included
        ecAreaID: the ID of the end-cap sub region
    '''

    ecName = "ECAP_"+str(ecAreaID)+"_outer"


    # Calculate length of sub-region
    if len(layerRange) == 1 and layerRange[0] != 6:
        innerZ = zMap[layerRange[0]]
        outerZ = zMap[layerRange[0]] + 10
    elif len(layerRange) == 1 and layerRange[0] == 6:
        innerZ = zMap[layerRange[0]] - 10
        outerZ = zMap[layerRange[0]]
    else:
        innerZ = zMap[layerRange[0]]
        outerZ = zMap[layerRange[-1]]

    if debug:
        print '\nGenerating normal region for', ecName
        print '\tinnerZ' , innerZ
        print '\touterZ' , outerZ


    addNormalECHeader(ofile, ecName, innerZ, outerZ, numLayers=len(layerRange))

    # add Disks
    if len(layerRange) == 1:
        diskRange = 'Disk 1'
    else:
        diskRange = 'Disk {0}-{1}'.format(1, len(layerRange))

    # Open disk environment
    #ofile.write('      '+diskRange + '{\n')

    # Add rings
    addDefaultECRings(ofile)

    # Close the disk environment
    #ofile.write('      }\n')

    # close the end-cap environment
    ofile.write('    }\n\n')


#____________________________________________________________
def genRegECTriplet(ofile, ecTripletLayer, ecSpacing, debug):
    '''
    Add a triplet layer to the end-cap
    Args:
        ofile: the file to be written to
        ecTripletLayer: layer in which the triplet will be inserted
        ecSpacing: spacing between the layers
    '''

    #zmin 2615.706
    #zmax 5009.294

    if ecTripletLayer == 1:
        ecName = "ECAP_0_triplet"
    else:
        ecName = "ECAP_1_triplet"

    if debug:
        print '\nGenerating end-cap triplet "{2}" in layer {0} with spacing {1} mm'.format(ecTripletLayer, ecSpacing, ecName)


    # Calculate inner and outer Z based on requested position and layer spacing
    # Allow for triplet to be at the left and right edges of the endcap region
    tripletCentroid = zMap[ecTripletLayer]
    if ecTripletLayer == 1:
        tripletCentroid += (TRIPLET_TOLERANCE+ecSpacing)
    if ecTripletLayer == 6:
        tripletCentroid -= (TRIPLET_TOLERANCE+ecSpacing)

    innerZ = tripletCentroid - (TRIPLET_TOLERANCE+ecSpacing)
    outerZ = tripletCentroid + (TRIPLET_TOLERANCE+ecSpacing)

    # Add endcap region header
    addNormalECHeader(ofile, ecName, innerZ, outerZ, 3, 'triplet')

    #ofile.write('      Disk 1-3 {\n')

    # Add rings
    #addTripletECRings(ofile)
    addTripletECRings_allwedges(ofile)
    #addDefaultECRings(ofile)

    # Close the disk environment
    #ofile.write('      }\n')

    # close the end-cap environment
    ofile.write('    }\n\n')


#____________________________________________________________
def genRegNormal(ofile, layerRange, barrelAreaID, debug):
    '''
    Adds normal barrel regions withing the given layer range.
    Automatically detects if "multilayer" functionailty can be used
    Args:
        ofile: the file to be written to
        layerRange: the range of barrel layers to be included
        barrelAreaID: the ID of the barrel sub-region
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
        print '\nGenerating normal region for', barrelName
        print '\tinnerRadius' , innerRadius
        print '\touterRadius' , outerRadius

    addNormalBarrelHeader(ofile, barrelName, innerRadius, outerRadius, numLayers=len(layerRange))

    usedLayerCounter = 0

    # Add layers to barrel, first add macroPixel layers
    if layerRange[0] == 1:
        if len(layerRange)==1:
            # one layer of macroPixel
            l1 = Layer(radius=-1, color=7, moduleType="macroPixel", layerNumber=1)
            usedLayerCounter = 1
        elif len(layerRange) >= 2:
            # double layer of macroPixel
            l1 = Layer(radius=-1, color=7, moduleType="macroPixel", layerNumber="1-2")
            usedLayerCounter = 2
        l1.addLayer(ofile)
    elif layerRange[0] == 2:
        # one layer of macroPixel
        l1 = Layer(radius=-1, color=7, moduleType="macroPixel", layerNumber=1)
        l1.addLayer(ofile)
        usedLayerCounter = 1


    # remove layers 1 and 2 if in list
    if 1 in layerRange:
        layerRange.remove(1)
    if 2 in layerRange:
        layerRange.remove(2)

    if len(layerRange) == 0:
        ofile.write('    }\n')
        return # No remaining layers to draw


    # N layers of strips, in with N repeated layers, excluding layers 1 and 2
    if 6 in layerRange:
        if len(layerRange) > 1:
            layerNumbering = "{0}-{1}".format(1+usedLayerCounter, len(layerRange)+usedLayerCounter)
        elif len(layerRange) == 1:
            layerNumbering = 1+usedLayerCounter
    else:
        if len(layerRange) > 1:
            layerNumbering = "{0}-{1}".format(layerRange[0], layerRange[-1])
        elif len(layerRange) == 1:
            layerNumbering = layerRange[0]




    l2 = Layer(radius=-1, color=1, moduleType="strip", layerNumber=layerNumbering)
    l2.addLayer(ofile)

    # Add end of barrel region
    ofile.write('    }\n')




#____________________________________________________________
def genRegTriplet(ofile, position, spacing, debug):
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

    if debug:
        print '\nGenerating triplet "{2}" in layer {0} with spacing {1} mm'.format(position, spacing, barrelName)

    # Calculate inner and outer radius based on requested position and layer spacing
    # Allow for triplet to be at the top and bottom of barrel region
    tripletCentroid = radiiMap[position]
    if position == 1:
        tripletCentroid += (TRIPLET_TOLERANCE+spacing)
    if position == 6:
        tripletCentroid -= (TRIPLET_TOLERANCE+spacing)

    innerRadius = tripletCentroid - (TRIPLET_TOLERANCE+spacing)
    outerRadius = tripletCentroid + (TRIPLET_TOLERANCE+spacing)

    # add triplet sub-region header
    addTripletHeader(ofile, barrelName, innerRadius, outerRadius, BIG_DELTA, SMALL_DELTA)

    # Calculate radii of triplet layers (maybe put this into a function?)
    radius1 = tripletCentroid-spacing
    radius2 = tripletCentroid
    radius3 = tripletCentroid+spacing
    tripletModuleType = "tripletPixel"
    l1 = Layer(radius=radius1, color=6, moduleType=tripletModuleType, layerNumber=1)
    l2 = Layer(radius=radius2, color=6, moduleType=tripletModuleType, layerNumber=2)
    l3 = Layer(radius=radius3, color=6, moduleType=tripletModuleType, layerNumber=3)

    l1.addLayer(ofile)
    l2.addLayer(ofile)
    l3.addLayer(ofile)
    ofile.write('    }\n') # close brace after barrel area

    if debug:
        print '\tinnerRadius', innerRadius
        print '\ttripletCentroid', tripletCentroid
        print '\touterRadius', outerRadius
        print '\t(r1, r2, r3) : ({0}, {1}, {2})'.format(radius1, radius2, radius3 )



from optparse import OptionParser
import sys

#____________________________________________________________
if __name__ == "__main__":
  parser = OptionParser()
  parser.add_option("-l", "--tripletLayer", action="store", type="int", help="Triplet layer in barrel, choose 1--6")
  parser.add_option("-s", "--layerSpacing", action="store", type="int", help="Spacing of triplet layers in barrel in mm")

  parser.add_option("-e", "--addECtriplet", action="store", type="int", default=0, help="Output directory for plots")
  parser.add_option("-c", "--ecTripletLayer",      action="store", type="int", default=-1, help="Location of triplet in endcap, choose 1--6")
  parser.add_option("-p", "--ecTripletSpacing",    action="store", type="int", default=-1, help="Spacing of triplet in endcap in mm")
  parser.add_option("-o", "--path", action="store", type="string", default="./", help="Define output path")
  parser.add_option("-d", "--debug", action="store", type="int", default=0, help="Turn on debug mode (helpful messages)")
  if len(sys.argv) == 1:
    parser.print_help()
    sys.exit(0)

  options, args = parser.parse_args()
  option_dict = dict( (k, v) for k, v in vars(options).iteritems() if v is not None)
  main(**option_dict)
