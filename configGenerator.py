#!/usr/bin/env python

'''
Script to generate config files for tkLayout, but including a triplet layer at a variable location in the outer tracker.
Variables include
    - Layer of triplet in barrel
    - Spacing of triplet layer in barrel
    - Position of triplet in end-cap
    - Spacing of triplet in end-cap
'''
from defaultConfig import addBeampipe, addInnerTracker, addOuterTrackerHeader, addTripletHeader

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
    if (tripletLayer==1):
        addOuterTrackerHeader(ofile)
        genRegTriplet(ofile, tripletLayer, layerSpacing)
    elif (tripletLayer==6):
        genRegTriplet(6)
    else:
        pass

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
    '''
      Barrel BRL_1_triplet {
      bigDelta 5
      smallDelta 2.5
      numLayers 3
      outerZ 2250
      radiusMode fixed
      startZMode modulecenter
      innerRadius 677.60 // layer spacing, 4cm (+1cm tolerence either side)
      outerRadius 777.60
      sameRods true
      physicalLength 102.4
      phiSegments 2
      moduleType strip
      plotColor 1

      trackingTags triplet,tracker

      Layer 1 {
        // radius 517.45
        radius 687.60
        plotColor 7
        // Layer generic properties (same for all layers)
        width 102.4
        // length 2250            // 256pxls x 0.4mm
        length 102.4            // 256pxls x 0.4mm
        moduleType macroPixel
        moduleShape rectangular
        @include MacroPixel_module1.cfg
        @include MacroPixel_material.cfg
        resolutionLocalX 0.0095 // Pitch ~100/3um
        resolutionLocalY 0.115  // Macro-pixels ~ 400um
      }
      Layer 2 {
        // radius 542.45
        radius 727.60
        plotColor 6
        // Layer generic properties (same for all layers)
        width 102.4
        // length 2250            // 256pxls x 0.4mm
        length 102.4            // 256pxls x 0.4mm
        moduleType macroPixel
        moduleShape rectangular
        @include MacroPixel_module1.cfg
        @include MacroPixel_material.cfg
        resolutionLocalX 0.0095 // Pitch ~100/3um
        resolutionLocalY 0.115  // Macro-pixels ~ 400um
      }
      Layer 3 {
        // radius 562.45
        radius 767.60
        plotColor 5
        // Layer generic properties (same for all layers)
        width 102.4
        // length 2250            // 256pxls x 0.4mm
        length 102.4            // 256pxls x 0.4mm
        moduleType macroPixel
        moduleShape rectangular
        @include MacroPixel_module1.cfg
        @include MacroPixel_material.cfg
        resolutionLocalX 0.0095 // Pitch ~100/3um
        resolutionLocalY 0.115  // Macro-pixels ~ 400um
      }
    }
    '''









def genRegInner():
    pass





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
