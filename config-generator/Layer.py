# class for tracker layers

class Layer():
    def __init__(self, radius, color, moduleType, layerNumber):

        # Read in parameters
        self._radius = radius
        self._color = color
        self._moduleType = moduleType
        self._layerNumber = layerNumber

        # Default attributes
        self.plotColor = 7
        self.width = 102.4
        self.modleShape = "rectangular"

        # module material includes



    def addModule(self, lstring):
        lstring += "        moduleType "+self._moduleType+"\n"
        if self._moduleType == "macroPixel":
            lstring += "        @include MacroPixel_module1.cfg\n"
            lstring += "        @include MacroPixel_material.cfg\n"
            lstring += "        resolutionLocalX 0.0095 // Pitch ~100/3um\n"
            lstring += "        resolutionLocalY 0.115  // Macro-pixels ~ 400um\n"
        if self._moduleType == "strip":
            lstring += "        @include Strip_Outer_module.cfg\n"
            lstring += "        @include Strip_material_2.5.cfg\n"
            lstring += "        resolutionLocalX 0.0095\n"
            lstring += "        resolutionLocalY 14.434 // Strip = 50mm\n"
        if self._moduleType == "tripletPixel":
            lstring += "        @include TripletPixel_module0.cfg\n"
            lstring += "        @include TripletPixel_material.cfg\n"
            lstring += "        resolutionLocalX  0.01 // Pitch 40um \n"
            lstring += "        resolutionLocalY  0.01 // Pitch 40um \n"

        return lstring

    def addLayer(self, ofile):
        lstring = "      Layer "+str(self._layerNumber)+" {\n"
        # Allow auto-placement of layer within barrel if not specified
        if self._radius != -1:
            lstring += "        radius "+str(self._radius)+"\n"
        lstring += "        plotColor "+str(self._color)+"\n"
        lstring = self.addModule(lstring)
        lstring += '''        // Layer generic properties (same for all layers)
        width 102.4
        length 102.4            // 256pxls x 0.4mm
        moduleShape rectangular
      }\n'''
        ofile.write(lstring)
