# class for tracker layers

class Layer():
    def __init__(self, radius):
        self._radius = radius

        # Default attributes that a layer may have
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


    def printLayer():
        return 'layerinfo'
