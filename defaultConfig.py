def addOuterTrackerHeader(ofile):
    '''
    Write to the file the default tracker parameters for the Outer tracker
    '''
    outerHeader='''
Tracker Outer {

    // Layout construction parameters
    zOverlap 0.75
    phiOverlap 0.5
    rOverlap 0.5
    barrelRotation 1.57079632679
    smallParity 1
    bigParity 1
    innerRadiusFixed true
    outerRadiusFixed true
    //useMinMaxRCorrect false
    plotColor 1

    // Detector constraints
    etaCut 6\n\n'''
    ofile.write(outerHeader)

def addNormalBarrelHeader(ofile, name, innerRadius, outerRadius, numLayers):
    toWrite = "    Barrel "+name+"  {\n"
    toWrite += "      innerRadius "+str(innerRadius)+"\n"
    toWrite += "      outerRadius "+str(outerRadius)+"\n"
    toWrite += "      numLayers "+str(numLayers)+"\n"
    toWrite += '''
      bigDelta 5
      smallDelta 2.5
      outerZ 2250
      startZMode modulecenter
      sameRods true
      physicalLength 102.4
      phiSegments 2

      trackingTags outer,tracker\n\n'''
    ofile.write(toWrite)

def addTripletHeader(ofile, name, innerRadius, outerRadius):
    toWrite = "    Barrel "+name+" {\n"
    toWrite += "      innerRadius "+str(innerRadius)+"\n"
    toWrite += "      outerRadius "+str(outerRadius)+"\n"
    toWrite += '''
      startZMode modulecenter
      bigDelta 5
      smallDelta 2.5
      numLayers 3
      outerZ 2250
      radiusMode fixed
      sameRods true
      physicalLength 102.4
      phiSegments 2
      moduleType strip
      plotColor 1

      trackingTags triplet,tracker\n\n'''
    ofile.write(toWrite)

def addNormalECHeader(ofile, ecName, innerZ, outerZ, numLayers, tag='outer'):
    toWrite = '    Endcap '+ecName+' {\n'
    toWrite += '      numDisks '+str(numLayers)+ '\n'
    toWrite += '      innerZ '+str(innerZ)+'\n'
    toWrite += '      outerZ '+str(outerZ)+'\n'

    toWrite +='''      phiSegments 4
      innerRadius 25
      outerRadius 1545
      //barrelGap 375 // Not reasonably defined if tilted barrel built
      alignEdges false
      bigDelta 5
      smallDelta 2.5
'''

    toWrite += '      trackingTags {0},tracker\n'.format(tag)

    ofile.write(toWrite)

def addTripletECRings(ofile):
    ofile.write('''
          Ring 1-6 {
           moduleShape wedge
           moduleType tripletPixel
           plotColor 12

           @include TripletPixel_module0.cfg
           @include TripletPixel_material.cfg
           resolutionLocalX  0.02 // Pitch 80um
           resolutionLocalY  0.02 // Pitch 80um
          }

          Ring 7-15 {
           moduleShape rectangular
           moduleType tripletPixel
           width 102.4
           length 102.4
           physicalLength 102.4
           plotColor 6

           @include TripletPixel_module0.cfg
           @include TripletPixel_material.cfg
           resolutionLocalX  0.02 // Pitch 80um
           resolutionLocalY  0.02 // Pitch 80um
          }
          Ring 16 {
           moduleShape rectangular
           width 102.4
           length 52.0
           physicalLength 52.0
           moduleType strip
           plotColor 6


           @include TripletPixel_module0.cfg
           @include TripletPixel_material.cfg
           resolutionLocalX  0.02 // Pitch 80um
           resolutionLocalY  0.02 // Pitch 80um
          }

          Ring 1 {
           waferDiameter 86.2
           additionalModules 0
          }
          Ring 2 {
           waferDiameter 113.0
           additionalModules 2
          }
          Ring 3 {
           waferDiameter 114.8
           additionalModules 3
          }
          Ring 4 {
           waferDiameter 112.6
           additionalModules 4
          }
          Ring 5 {
           waferDiameter 118.6
           additionalModules 5
          }
          Ring 6 {
           waferDiameter 113.7
           additionalModules 5
          }\n\n''')


def addDefaultECRings(ofile):
    ofile.write('''
          Ring 1 {
           moduleShape wedge
           moduleType pixel
           plotColor 11

           @include Pixel_OuterFwd_module0.cfg
           @include Pixel_material.cfg
           resolutionLocalX 0.0075 // Pitch ~25um
           resolutionLocalY 0.015  // Pitch ~50um
          }
          Ring 2 {
           moduleShape wedge
           moduleType pixel
           plotColor 5

           @include Pixel_OuterFwd_module1.cfg
           @include Pixel_material.cfg
           resolutionLocalX 0.0095 // Pitch ~100/3um
           resolutionLocalY 0.030  // Pitch ~100um
          }
          Ring 3 {
           moduleShape wedge
           moduleType macroPixel
           plotColor 7

           @include MacroPixel_OuterFwd_module0.cfg
           @include MacroPixel_material.cfg
           resolutionLocalX 0.0095 // Pitch ~100/3um
           resolutionLocalY 0.115  // Pitch ~400um
          }
          Ring 4 {
           moduleShape wedge
           moduleType macroPixel
           plotColor 7

           @include MacroPixel_OuterFwd_module1.cfg
           @include MacroPixel_material.cfg
           resolutionLocalX 0.0095 // Pitch ~100/3um
           resolutionLocalY 0.115  // Pitch ~400um
          }
          Ring 5 {
           moduleShape wedge
           moduleType macroPixel
           plotColor 7

           @include MacroPixel_OuterFwd_module2.cfg
           @include MacroPixel_material.cfg
           resolutionLocalX 0.0095 // Pitch ~100/3um
           resolutionLocalY 0.115  // Pitch ~400um
          }
          Ring 6 {
           moduleShape wedge
           moduleType macroPixel
           plotColor 7

           @include MacroPixel_OuterFwd_module3.cfg
           @include MacroPixel_material.cfg
           resolutionLocalX 0.0095 // Pitch ~100/3um
           resolutionLocalY 0.115  // Pitch ~400um
          }
          Ring 7-9 {
           moduleShape rectangular
           moduleType macroPixel
           width 102.4
           length 102.4
           physicalLength 102.4
           plotColor 7

           @include MacroPixel_module1.cfg
           @include MacroPixel_material.cfg
           resolutionLocalX 0.0095 // Pitch ~100/3um
           resolutionLocalY 0.115  // Pitch ~400um
          }
          Ring 10-15 {
           moduleShape rectangular
           moduleType strip
           width 102.4
           length 102.4
           physicalLength 102.4
           moduleType strip
           plotColor 1

           @include Strip_Fwd_module.cfg
           @include Strip_material_2.5.cfg
           resolutionLocalX 0.0095 // Pitch ~100/3um
           resolutionLocalY 2.887  // Strip = 10mm or r-phi pitch / rot. by angle 20mrad
          }
          Ring 16 {
           moduleShape rectangular
           width 102.4
           length 52.0
           physicalLength 52.0
           moduleType strip
           plotColor 1

           @include Strip_Fwd_half_module.cfg
           @include Strip_material_2.5.cfg
           resolutionLocalX 0.0095
           resolutionLocalY 2.887 // Strip = 10mm or r-phi pitch / rot. by angle 20mrad
          }

          Ring 1 {
           waferDiameter 86.2
           additionalModules 0
          }
          Ring 2 {
           waferDiameter 113.0
           additionalModules 2
          }
          Ring 3 {
           waferDiameter 114.8
           additionalModules 3
          }
          Ring 4 {
           waferDiameter 112.6
           additionalModules 4
          }
          Ring 5 {
           waferDiameter 118.6
           additionalModules 5
          }
          Ring 6 {
           waferDiameter 113.7
           additionalModules 5
          }\n\n''')


def addDefaultOuterEndcap(ofile):
    endcap = '''

    Endcap ECAP {
      //@includestd Conversions/flangeTEDD

      phiSegments 4
      numDisks 6
      innerRadius 25
      outerRadius 1545
      //barrelGap 375 // Not reasonably defined if tilted barrel built
      innerZ 2625     // Used instead of barrelGap
      outerZ 5000
      alignEdges false
      bigDelta 5
      smallDelta 2.5

      Ring 1 {
       moduleShape wedge
       moduleType pixel
       plotColor 11

       trackingTags inner,tracker
       @include Pixel_OuterFwd_module0.cfg
       @include Pixel_material.cfg
       resolutionLocalX 0.0075 // Pitch ~25um
       resolutionLocalY 0.015  // Pitch ~50um
      }
      Ring 2 {
       moduleShape wedge
       moduleType pixel
       plotColor 5

       trackingTags inner,tracker
       @include Pixel_OuterFwd_module1.cfg
       @include Pixel_material.cfg
       resolutionLocalX 0.0095 // Pitch ~100/3um
       resolutionLocalY 0.030  // Pitch ~100um
      }
      Ring 3 {
       moduleShape wedge
       moduleType macroPixel
       plotColor 7

       trackingTags inner,tracker
       @include MacroPixel_OuterFwd_module0.cfg
       @include MacroPixel_material.cfg
       resolutionLocalX 0.0095 // Pitch ~100/3um
       resolutionLocalY 0.115  // Pitch ~400um
      }
      Ring 4 {
       moduleShape wedge
       moduleType macroPixel
       plotColor 7

       trackingTags inner,tracker
       @include MacroPixel_OuterFwd_module1.cfg
       @include MacroPixel_material.cfg
       resolutionLocalX 0.0095 // Pitch ~100/3um
       resolutionLocalY 0.115  // Pitch ~400um
      }
      Ring 5 {
       moduleShape wedge
       moduleType macroPixel
       plotColor 7

       trackingTags inner,tracker
       @include MacroPixel_OuterFwd_module2.cfg
       @include MacroPixel_material.cfg
       resolutionLocalX 0.0095 // Pitch ~100/3um
       resolutionLocalY 0.115  // Pitch ~400um
      }
      Ring 6 {
       moduleShape wedge
       moduleType macroPixel
       plotColor 7

       trackingTags outer,tracker
       @include MacroPixel_OuterFwd_module3.cfg
       @include MacroPixel_material.cfg
       resolutionLocalX 0.0095 // Pitch ~100/3um
       resolutionLocalY 0.115  // Pitch ~400um
      }
      Ring 7-9 {
       moduleShape rectangular
       moduleType macroPixel
       width 102.4
       length 102.4
       physicalLength 102.4
       plotColor 7

       trackingTags outer,tracker
       @include MacroPixel_module1.cfg
       @include MacroPixel_material.cfg
       resolutionLocalX 0.0095 // Pitch ~100/3um
       resolutionLocalY 0.115  // Pitch ~400um
      }
      Ring 10-15 {
       moduleShape rectangular
       moduleType strip
       width 102.4
       length 102.4
       physicalLength 102.4
       moduleType strip
       plotColor 1

       trackingTags outer,tracker
       @include Strip_Fwd_module.cfg
       @include Strip_material_2.5.cfg
       resolutionLocalX 0.0095 // Pitch ~100/3um
       resolutionLocalY 2.887  // Strip = 10mm or r-phi pitch / rot. by angle 20mrad
      }
      Ring 16 {
       moduleShape rectangular
       width 102.4
       length 52.0
       physicalLength 52.0
       moduleType strip
       plotColor 1

       trackingTags outer,tracker
       @include Strip_Fwd_half_module.cfg
       @include Strip_material_2.5.cfg
       resolutionLocalX 0.0095
       resolutionLocalY 2.887 // Strip = 10mm or r-phi pitch / rot. by angle 20mrad
      }

      Ring 1 {
       waferDiameter 86.2
       additionalModules 0
      }
      Ring 2 {
       waferDiameter 113.0
       additionalModules 2
      }
      Ring 3 {
       waferDiameter 114.8
       additionalModules 3
      }
      Ring 4 {
       waferDiameter 112.6
       additionalModules 4
      }
      Ring 5 {
       waferDiameter 118.6
       additionalModules 5
      }
      Ring 6 {
       waferDiameter 113.7
       additionalModules 5
      }
    }

'''
    ofile.write(endcap)

def addBeampipe(ofile):
    bp='''
BeamPipe Pipe {

    radius         20.0   // mm
    thickness      0.8    // mm
    radLength      0.00227
    intLength      0.00190
}
'''
    ofile.write(bp)

def addInnerTracker(ofile):
    itrk='''
Tracker Inner {

    // Layout construction parameters
    bigDelta 5
    smallDelta 2.5
    zOverlap 0.0
    phiOverlap 0.0
    rOverlap 0.0
    barrelRotation 1.5707963268 // Starts building modules from X=0, Ymax
    smallParity -1
    bigParity 1
    innerRadiusFixed true
    outerRadiusFixed true
    //useMinMaxRCorrect false

    // Detector constraints
    etaCut 6

    trackingTags inner,tracker

    Barrel BRL_0 {

      numLayers 4
      radiusMode fixed
      //sameRods true

      Layer 1 {
       outerZ 685
       radius 25.0
       width 12.8
       length 68.5
       physicalLength 68.5
       bigDelta 1.0
       smallDelta 0.0
       zOverlap 0.0
       startZMode moduleedge
       moduleType pixel
       plotColor 2
       @include Pixel_BRL0_module0.cfg
       @include Pixel_material_innermost.cfg
       resolutionLocalX 0.0075 // Pitch ~25um
       resolutionLocalY 0.015  // Pitch ~50um
      }
      Layer 2 {
       outerZ 820
       radius 60.0
       width 25.6
       length 41.0
       physicalLength 41.0
       bigDelta 1.0
       smallDelta 0.0
       zOverlap 0.0
       moduleType pixel
       startZMode moduleedge
       plotColor 2
       @include Pixel_BRL0_module1.cfg
       @include Pixel_material_innermost.cfg
       resolutionLocalX 0.0075 // Pitch ~25um
       resolutionLocalY 0.015  // Pitch ~50um
      }
      Layer 3 {
       outerZ 820
       radius 100.0
       width 25.6
       length 41.0
       physicalLength 41.0
       bigDelta 1.0
       smallDelta 0.0
       zOverlap 0.0
       moduleType pixel
       startZMode moduleedge
       plotColor 2
       @include Pixel_BRL0_module1.cfg
       @include Pixel_material_innermost.cfg
       resolutionLocalX 0.0075 // Pitch ~25um
       resolutionLocalY 0.015  // Pitch ~50um
      }
      Layer 4 {
       outerZ 820
       radius 150.0
       width 25.6
       length 41.0
       physicalLength 41.0
       bigDelta 1.0
       smallDelta 0.0
       zOverlap 0.0
       moduleType pixel
       startZMode moduleedge
       plotColor 2
       @include Pixel_BRL0_module1.cfg
       @include Pixel_material_innermost.cfg
       resolutionLocalX 0.0075 // Pitch ~25um
       resolutionLocalY 0.015  // Pitch ~50um
      }

      innerRadius 23.5
      outerRadius 152.5
      phiSegments 2
    }

    Barrel BRL_1 {

      numLayers 2
      sameRods true
      radiusMode fixed
      //startZMode moduleedge

      Layer 1 {
       radius 270
      }

      Layer 2 {
       radius 400
      }

      Layer 1-2 {
       outerZ 820
       width 51.2
       length 102.4         // 51.2 + 51.2 together
       physicalLength 102.4
       moduleType macroPixel
       plotColor 7
       @include MacroPixel_module0.cfg
       @include MacroPixel_material.cfg
       resolutionLocalX 0.0095 // Pitch ~100/3um
       resolutionLocalY 0.115  // Pitch ~400um
      }
      innerRadius 197.0
      outerRadius 460.0
      phiSegments 2
    }
    Endcap ECAP {
      //@includestd Conversions/flangeTEDD

      phiSegments 4
      numDisks 5
      innerRadius 25
      outerRadius 400
      barrelGap 130 // Service channel between BRL & ECAP
      outerZ 2250
      alignEdges false
      moduleShape wedge
      moduleType pixel

      Disk 1-5 {
        Ring 1 {
          waferDiameter 86.2
          additionalModules 0
          moduleType pixel
          @include Pixel_InnerFwd_module0.cfg
          @include Pixel_material.cfg
          resolutionLocalX 0.0075 // Pitch ~25um
          resolutionLocalY 0.015  // Pitch ~50um
          plotColor 11
        }
        Ring 2 {
          waferDiameter 113.0
          additionalModules 2
          moduleType pixel
          @include Pixel_InnerFwd_module1.cfg
          @include Pixel_material.cfg
          resolutionLocalX 0.0095 // Pitch ~100/3um
          resolutionLocalY 0.030  // Pitch ~100um
          plotColor 5
        }
        Ring 3 {
          waferDiameter 114.8
          additionalModules 3
          moduleType macroPixel
          @include MacroPixel_InnerFwd_module0.cfg
          @include MacroPixel_material.cfg
          resolutionLocalX 0.0095 // Pitch ~100/3um
          resolutionLocalY 0.115  // Pitch ~400um
          plotColor 7
        }
        Ring 4 {
          waferDiameter 112.6
          additionalModules 4
          moduleType macroPixel
          @include MacroPixel_InnerFwd_module1.cfg
          @include MacroPixel_material.cfg
          resolutionLocalX 0.0095 // Pitch ~100/3um
          resolutionLocalY 0.115  // Pitch ~400um
          plotColor 7
        }
      }
    }
}'''
    ofile.write(itrk)
