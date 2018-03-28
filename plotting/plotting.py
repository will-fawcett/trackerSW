"""Provides minor abstractions on top of ROOT to faciliate somewhat more
elegant plotting.  As with anything that interfaces with ROOT, there are bound
to be... idiosyncrasies, though this module does its best to hide them.  It
provides several functions for manipulating histograms or collections thereof:

    - drawable_iterable
    - combined_histogram
    - maximum_value
    - ratio_histogram
    - histogram_stack

It also provides a class, 'Plot', which can be used to model a ROOT plot,
enabling the following features:

    - Stacked background histograms
    - Data histograms
    - Legend
    - Ratio histograms
    - Statistical error bars
    - Systematic error bars

For more documentation, please see the docstrings for the individual functions
and/or Plot methods.
"""


# System imports
from math import ceil, sqrt, log10
from uuid import uuid4
from itertools import chain

# Six imports
#from six import range

# ROOT imports
# HACK: We import and use SetOwnership because ROOT's memory management is so
# inconsistent and terrible that we have to stop Python from even touching ROOT
# graphical objects or ROOT will crash, often due to a double free or some
# other nonsense.
from ROOT import TCanvas, TPad, TH1, THStack, TGraph, TMath, TLegend, TLine, \
    TLatex, SetOwnership, TF1, TGraphErrors, TGraphAsymmErrors, kGray, kOrange, \
    TArrow, Double, TH1F


# Convenience function for generating random IDs
def _rand_uuid():
    return uuid4().hex


# Convenience function to check if an object is a TH1
def is_histo(h):
    return isinstance(h, TH1)


# Convenience function to check if an object is a THStack
def is_stack(h):
    return isinstance(h, THStack)


# Convenience function to check if an object is a TGraph
def is_graph(g):
    return isinstance(g, TGraph) or isinstance(g, TGraphErrors) or isinstance(g, TGraphAsymmErrors) 


# Convenience function to check if an object is a TLine
def is_line(l):
    return isinstance(l, TLine)


# Convenience function to check if an object is a TPad 
def is_pad(p):
    return isinstance(p, TPad)


def drawable_iterable(drawable, unpack_stacks = False, reverse_stacks = False):
    """Convenience method to get an iterable object from a drawable.

    Args:
        drawable: Some type of drawable object.  Existing iterables are passed
            through.
        unpack_stacks: By default, THStack objects are treated as a single
            histogram.  If you would like them to be treated as a collection of
            their constituent TH1 objects, set unpack_stacks = True.
        reverse_stacks: If unpacking stacks, they are typically iterated from
            bottom to top.  Specify True for reverse_stacks to iterate from top
            to bottom.

    Returns:
        An iterable of the histograms in the provided collection.
    """
    # Check if we are using a THStack
    if is_stack(drawable) and unpack_stacks:
        # Extract histograms from the stack
        result = list(drawable.GetHists())

        # Reverse if necessary
        if reverse_stacks:
            result.reverse()

        return result
    elif is_histo(drawable) or is_graph(drawable) or is_line(drawable):
        return (drawable,)

    # Already an iterable
    return drawable

#____________________________________________________________________________
def removeXerror(hist_or_graph):
    """Returns TGraphErrors with no X error
    Args:
        hist_or_graph: A TH1 histogram or a TGraphErrors 
    """

    # If histogram convert to graph
    if is_histo(hist_or_graph):
        gr = TGraphErrors(hist_or_graph)
    else:
        gr = hist_or_graph.Clone()

    # Maually set x error to 0 
    for iPoint in xrange(gr.GetN()):
        yErr = gr.GetErrorY(iPoint)
        gr.SetPointError(iPoint, 0, yErr)
    return gr 

#____________________________________________________________________________
def removeXasymErrors(gr):
    '''
    Removes the x errors from a TGraphAsymmErrors, manually
    '''
    for iPoint in xrange(gr.GetN()):
        gr.SetPointError(iPoint, 0, 0, gr.GetErrorYlow(iPoint), gr.GetErrorYhigh(iPoint) )
    return gr



#____________________________________________________________________________
def normalize(histogram):
    """Returns normalized histogram clone of input histogram

    Args:
        histogram: A TH1 histogram
    """
    nbins    = histogram.GetNbinsX()
    integral = histogram.Integral(1,nbins)
    newhist  = histogram.Clone()
    newhist.Reset()
    for bin in range(1,nbins+1):
        ibinY = histogram.GetBinContent(bin)
        newhist.SetBinContent(bin,ibinY/integral)
    return newhist

#____________________________________________________________________________
def rebin_plot(histogram, bins_array):
    """Will rebin the histogram 
    Draws a legend onto the plot with the specified histograms.

    Bin edges and overflow bins must be carefully considered, see the documentation
    https://root.cern.ch/doc/master/classTH1.html#aff6520fdae026334bf34fa1800946790
    Bin 0 contains the underflow
    Nbins+1 contains the overflow 

    The Rebin function is also a bit messy: 
    Double_t xbins[25] = {...} // array of low-edges (xbins[25] is the upper edge of last bin)
    h1->Rebin(24,"hnew",xbins);  //creates a new variable bin size histogram hnew

    Args:
        histogram: A single histogram 
        bins_array: an array containing the list of bin edges
    """
    newname = histogram.GetName()+'_rebinned'
    newplot = histogram.Rebin(len(bins_array)-1, newname, bins_array)
    newplot.SetDirectory(0)

    #print "found overflow for", newname, "of", overflow
    #newplot.SetBinContent(newplot.GetNbinsX(),newplot.GetBinContent(newplot.GetNbinsX())+newplot.GetBinContent(newplot.    GetNbinsX()+1))
    #newplot.SetBinError(newplot.GetNbinsX(),math.sqrt(newplot.GetBinError(newplot.GetNbinsX())**2 + newplot.               GetBinError(newplot.GetNbinsX()+1)**2 ) )
    #newplot.SetBinContent(newplot.GetNbinsX()+1,0) # Set overflow to 0

    return newplot


#____________________________________________________________________________
def rebin_THStack(stack, bins_array):
    '''
    THStack is just a collection of histograms, so call the re-binning on each histogram
    separately
    '''
    
    

    tempStack = THStack('Background stack rebinned','')
    #tempStack.SetDirectory(0)
    if is_stack(stack):
        histList = stack.GetHists()
        for hist in histList: 
            if type(bins_array) == int:
                tempHist = hist.Rebin(bins_array)
            else:
                tempHist = rebin_plot(hist, bins_array)
            tempHist.SetDirectory(0)
            tempStack.Add(tempHist)
    else:
        print 'ERROR, passed object is not a THStack'
        print element.GetName()
    return tempStack



#____________________________________________________________________________
def combined_histogram(histograms_or_stack):
    """Returns a combined TH1 object from a collection of histograms with bin
    errors calculated.

    Args:
        histograms_or_stack: A single histogram, a non-empty iterable of
            histograms, or a THStack object which represents the collection of
            histograms

    Returns:
        A single TH1 object which is a combination of the provided histograms
        and which has bin errors calculated.
    """
    # Convert the histograms to an iterable, always unpacking THStack objects
    histograms = drawable_iterable(histograms_or_stack, True)

    # Grab the first histogram, making sure bin errors are calculated before
    # adding the remaining histograms
    result = histograms[0].Clone(_rand_uuid())
    SetOwnership(result, False)
    if result.GetSumw2N() == 0:
        result.Sumw2()

    # Add the other histograms to the result
    map(result.Add, histograms[1:])

    return result

#____________________________________________________________________________
def minimum_value(drawbles):
    """Returns the minimum value of all bins of all histograms or graphs
    provided, including any errors.

    Args:
        drawables: An iterable of drawable objects, each of one of the
            following types:

            - A TH1 object
            - A THStack object
            - A tuple of the form (THStack, TGraph) where the latter
              represents error bars
            - A TGraph object

    Returns:
        The minimum value than any bin takes on in any of the provided
        drawables, as long as that minimum is larger than 0 
    """
    # Loop over histograms
    result = 10**20 
    for drawable in drawbles:
        # Unpack things if there is an error band
        if isinstance(drawable, tuple):
            drawable, error_band = drawable
        else:
            error_band = None

        if is_histo(drawable):
            MIN_VAL = 0.0 # found minimum must be larger than 0
            minimum = drawable.GetMinimum(MIN_VAL) 
        elif is_stack(drawable):
            minimum = drawable.GetMinimum("nostack")
        elif is_graph(drawable):
            minimum = TMath.MinElement(drawable.GetN(), drawable.GetY())
        elif is_line(drawable):
            minimum = min(drawable.GetY1(), drawable.GetY2()) # not tested
        else:
            print type(drawable)
            raise ValueError('unsupported drawable type')

        if minimum < 0.0: continue

        # Update the result
        result = min(result, minimum)

    return result


#____________________________________________________________________________
def maximum_value(drawables):
    """Returns the maximum value of all bins of all histograms or graphs
    provided, including any errors.

    Args:
        drawables: An iterable of drawable objects, each of one of the
            following types:

            - A TH1 object
            - A THStack object
            - A tuple of the form (THStack, TGraph) where the latter
              represents error bars
            - A TGraph object

    Returns:
        The maximum value than any bin takes on in any of the provided
        drawables.
    """
    # Create our initial maximum
    result = 0.0

    # Loop over histograms
    for drawable in drawables:
        # Unpack things if there is an error band
        if isinstance(drawable, tuple):
            drawable, error_band = drawable
        else:
            error_band = None

        # Compute the maximum for this drawable
        if is_histo(drawable) or is_stack(drawable):
            maximum = drawable.GetMaximum()
            #print 'histo max:', maximum
            #print 'min:' , drawable.GetMinimum(0)
        elif is_graph(drawable):
            # http://root.cern.ch/phpBB3/viewtopic.php?t=9070
            maximum = TMath.MaxElement(drawable.GetN(), drawable.GetY())
        elif is_line(drawable):
            maximum = max(drawable.GetY1(), drawable.GetY2())
        else:
            raise ValueError('unsupported drawable type')

        # NOTE: Clever math hack.  Since drawable may be a THStack, we can't
        # (easily) do a bin-wise pairing and compute (value + error-high) for
        # each bin when looking for a maximum.  However, the bin which has the
        # maximum value will also have the maximum statistical and systematic
        # normalization uncertainty, so we can assume that the value returned
        # by GetMaximum() corresponds to the bin with the greatest error, and
        # thus we can just scan for the largest error and adding that to the
        # GetMaximum() result gives the answer we would get from bin-wise
        # pairing.  Of course, even if we didn't get the exact answer here,
        # we'd still be at-or-above the true maximum value, which is all we
        # really care about for plotting purposes.
        # If there is no error band, we just add enough room for statistical
        # error.
        if error_band is not None:
            maximum_error = 0.0
            for i in xrange(error_band.GetN()):
                maximum_error = max(maximum_error, error_band.GetErrorYhigh(i))
            maximum += maximum_error
        else:
            # WJF: messes up plot when errors are small 
            #print maximum
            #maximum += sqrt(maximum)
            pass

        # Update the result
        result = max(result, maximum)

    return result


#____________________________________________________________________________
def ratio_histogram(numerator, denominator, y_title = 'Data / Background'):
    """Creates a ratio histogram by dividing a numerator histogram by a
    denominator histogram.  Errors are calculated under the assumption of error
    on the numerator histogram only. This method also provides some basic 
    styling of the ratio histogram, disabling statistics and title, and 
    setting markers appropriately.

    Args:
        numerator: A single histogram, an iterable of histograms, or a THStack
            object which represents the data to use in the numerator of the
            ratio division
        denominator: A single histogram, an iterable of histograms, or a
            THStack object which represents the data to use in the numerator of
            the ratio division.  This must have the same binning as numerator.
        y_title: The title for the y-axis

    Returns:
        A ROOT histogram representing the ratio of numerator/denominator.
    """
    # Create our result based off of the numerator (it will have bin errors
    # enabled)
    result = combined_histogram(numerator)

    # Create the denominator
    combined_denominator = combined_histogram(denominator)

    # Disable errors on the denominator (they should be handled in an
    # uncertainty band around unity)
    for bin in xrange(0, combined_denominator.GetNbinsX() + 2):
        combined_denominator.SetBinError(bin, 0.0)

    # Divide by the denominator
    result.Divide(combined_denominator)

    # Do some styling on the result
    result.SetTitle('')
    result.SetStats(0)
    result.SetMarkerStyle(20)
    #result.SetMarkerSize(1.5)

    # Set title
    result.GetYaxis().SetTitle(y_title)

    return result


#____________________________________________________________________________
def histogram_stack(*histograms):
    """Creates a THStack object with a unique identifier from the specified
    histograms.

    This method is useful due to THStack freaking out if a new THStack is
    created with the same name.

    Args:
        histograms: Each argument of this function after plot may be a single
            histogram, an iterable of histograms (each of which should be
            plotted), or even an existing THStack object whose component
            histograms should be included in the new stack.  The histograms
            should be specified from top-to-bottom.

    Returns:
        An initialized THStack object containing the specified histograms.
    """
    # Generate an iterable of all histograms provided
    histograms = chain(*(drawable_iterable(h, unpack_stacks = True)
                         for h
                         in histograms))

    # Create a new THStack object with a unique identifier
    stack = THStack(_rand_uuid(), '')
    SetOwnership(stack, False)

    # Add histograms
    map(stack.Add, histograms)

    return stack


#____________________________________________________________________________
class Plot(object):
    """Structural class for representing, accessing, and maintaining references
    to ROOT graphical elements forming a plot, potentially with a ratio
    subplot.
    """

    # Plotting 'constants' for the plot class.  Ideally, one would allow these
    # to be flexible, but unfortunately ROOT's coordinate system is extremely
    # inconsistent and fragile, so it is best to fix these values here.  You
    # can change them dynamically with Plot.Whatever = value, but it is
    # probably best to leave them alone.
    PLOT_WIDTH = 1280 # px
    PLOT_HEIGHT = 1024 # px # WJF changed to make square
    #PLOT_HEIGHT = PLOT_WIDTH
    print 'FOR THESIS PLOTS, ADJUSTED WITDH back to 1024'
    PLOT_MARGINS = (0.13, 0.05, 0.125, 0.1) # Left, Right, Bottom, Top
    PLOT_MARGINS_WITH_RATIO = (0.125, 0.05, 0.025, 0.1)
    PLOT_RATIO_MARGINS = (0.125, 0.05, 0.325, 0.05)
    PLOT_LEFT_MARGIN = 0.1
    PLOT_HEADER_HEIGHT = 400 # px
    PLOT_LEGEND_HEIGHT = 250 # px
    PLOT_LEGEND_LEFT = 0.55
    PLOT_LEGEND_RIGHT = 0.95
    PLOT_LEGEND_BOTTOM = 0.55 # expects that distribution will have fallen off somewhat, given that extra height isn't sufficient 
    PLOT_LEGEND_BOTTOM_WITH_RATIO = 0.5
    PLOT_LEGEND_TOP = 0.88
    PLOT_LEGEND_TOP_WITH_RATIO = 0.88
    PLOT_LEGEND_TEXT_SIZE = 0.05
    PLOT_LEGEND_TEXT_SIZE_WITH_RATIO = 0.04
    PLOT_LEGEND_N_COLUMNS = 1
    PLOT_RATIO_FRACTION = 0.3 # fraction of canvas height
    PLOT_X_AXIS_TITLE_SIZE = 0.05
    RATIO_TEXT_SIZE = 0.13
    #PLOT_X_AXIS_TITLE_SIZE_WITH_RATIO = 0.13
    PLOT_X_AXIS_TITLE_SIZE_WITH_RATIO = RATIO_TEXT_SIZE
    PLOT_X_AXIS_TITLE_OFFSET = 1.1
    PLOT_X_AXIS_TITLE_OFFSET_WITH_RATIO = 0.96
    PLOT_X_AXIS_LABEL_SIZE = PLOT_X_AXIS_TITLE_SIZE
    PLOT_X_AXIS_LABEL_SIZE_WITH_RATIO = RATIO_TEXT_SIZE
    PLOT_Y_AXIS_TITLE_SIZE = PLOT_X_AXIS_TITLE_SIZE
    PLOT_Y_AXIS_LABEL_SIZE = PLOT_X_AXIS_TITLE_SIZE
    PLOT_Y_AXIS_TITLE_SIZE_WITH_RATIO = 0.06
    PLOT_Y_AXIS_TITLE_OFFSET = 0.9
    PLOT_Y_AXIS_TITLE_OFSET_WITH_RATIO = 0.95
    PLOT_Y_AXIS_LABEL_SIZE_WITH_RATIO = 0.05
    #PLOT_RATIO_Y_AXIS_TITLE_SIZE = 0.09
    PLOT_RATIO_Y_AXIS_TITLE_SIZE = RATIO_TEXT_SIZE
    PLOT_RATIO_Y_AXIS_TITLE_OFFSET_RATIO = 0.425 # 0.575
    PLOT_RATIO_Y_AXIS_TITLE_OFFSET = 1.4
    PLOT_RATIO_Y_AXIS_LABEL_SIZE = 0.12
    PLOT_RATIO_Y_AXIS_MINIMUM = 0. # 0.6
    PLOT_RATIO_Y_AXIS_MAXIMUM = 2. # 1.4 
    PLOT_ERROR_BAND_FILL_STYLE = 3254 # Diagonal lines
    PLOT_ERROR_BAND_FILL_COLOR = 13 # Gray
    PLOT_ERROR_BAND_LINE_WIDTH = 0
    PLOT_ERROR_BAND_LINE_COLOR = 0
    PLOT_RATIO_ERROR_BAND_FILL_STYLE = 3254 # Diagonal lines
    PLOT_RATIO_ERROR_BAND_FILL_COLOR = 807 # Orange
    PLOT_RATIO_ERROR_BAND_LINE_WIDTH = 0
    PLOT_RATIO_ERROR_BAND_LINE_COLOR = 0

    ##########################
    # Label text
    ##########################
    # ATLAS stamp should be at the top, all other labels should be the same text size
    # and have the same left alignment. Separated vertically by the same amount of space 
    PLOT_ATLAS_STAMP_LEFT = 0.18
    PLOT_ATLAS_STAMP_TEXT_FONT = 42 # Normal helvetica 
    PLOT_ATLAS_STAMP_ATLAS_TEXT_FONT = 72 # Bold slanted 
    PLOT_ATLAS_STAMP_TITLE_SIZE = 0.04
    PLOT_ATLAS_STAMP_TITLE_SIZE_WITH_RATIO = PLOT_LEGEND_TEXT_SIZE_WITH_RATIO
    PLOT_ATLAS_STAMP_TEXT_COLOR = 1
    PLOT_ATLAS_STAMP_ATLAS_TOP_WITH_RATIO = 0.83
    PLOT_ATLAS_STAMP_ATLAS_TOP = 0.84
    # Space between "ATLAS" and e.g. "Internal"
    PLOT_ATLAS_STAMP_LABEL_LEFT_ADDITION = 0.105
    PLOT_ATLAS_STAMP_LABEL_LEFT_ADDITION_WITH_RATIO = 0.1
    # L_int and sqrt(s) 
    PLOT_ATLAS_STAMP_LUMINOSITY_SIZE = 0.035
    PLOT_ATLAS_STAMP_LUMINOSITY_SIZE_WITH_RATIO = PLOT_LEGEND_TEXT_SIZE_WITH_RATIO
    PLOT_ATLAS_STAMP_LUMINOSITY_LEFT = PLOT_ATLAS_STAMP_LEFT
    PLOT_ATLAS_STAMP_LUMINOSITY_TOP = 0.78
    PLOT_ATLAS_STAMP_LUMINOSITY_TOP_WITH_RATIO = PLOT_ATLAS_STAMP_ATLAS_TOP_WITH_RATIO-0.05
    # Additional text
    PLOT_ATLAS_STAMP_ADDITIONAL_TOP_WITH_RATIO = PLOT_ATLAS_STAMP_ATLAS_TOP_WITH_RATIO-0.1
    PLOT_ATLAS_STAMP_ADDITIONAL_TOP = 0.72
    
    #######################
    # Arrows for ratio plot
    #######################
    ARROW_SIZE   = 0.02
    ARROW_COLOUR = 100


    def __init__(self,
                 title         = '',
                 x_title       = None,
                 y_title       = None,
                 plot_header   = True,
                 ratio         = False,
                 x_range       = None,
                 y_max         = None,
                 y_min         = None,
                 legendColumns = 1):
        """Initializes a new instance of the Plot class.

        Args:
            title: The title to set for the histogram
            plot_header: Whether or not to include whitespace at the top of the
                plot for the ATLAS label and legend
            ratio: Whether or not to include a ratio plot
            x_range: A tuple of (x_min, x_max)
            y_max: The maximum Y axis value
            y_min: The minumum Y axis value
        """
        # Store the title
        self._title = title
        self._x_title, self._y_title = x_title, y_title

        # Store whether or not the user wants to create a plot header
        self._plot_header = plot_header

        # Calculate a unique name for the plot components
        name = _rand_uuid()

        # Default logy if off
        self._logy = False

        # Default off for integer x-ticks 
        self._x_integer_ticks = False 

        # store n columns for legend
        self.PLOT_LEGEND_N_COLUMNS = legendColumns 

        # Create a canvas
        self._canvas = TCanvas(name + '_canvas',
                               name,
                               int(self.PLOT_WIDTH),
                               int(self.PLOT_HEIGHT))
        SetOwnership(self._canvas, False)



        # Create the main plot and draw it
        self._plot = TPad(
            'upperPad',
            'upperPad',
            #name + '_plot', # WJF: don't need upper pad to have unique name 
            #name,
            0.0,
            (self.PLOT_RATIO_FRACTION
             if ratio
             else 0.0),
            1.0,
            1.0
        )
        SetOwnership(self._plot, False)
        self._plot.SetMargin(*(self.PLOT_MARGINS_WITH_RATIO
                               if ratio
                               else self.PLOT_MARGINS))
        self._plot.Draw()

        # Store ranges
        self._x_range = x_range
        if y_max is not None:
            self._set_maximum_value(y_max)
        if y_min is not None:
            self._set_minimum_value(y_min)

        # Switch back to the context of the canvas
        self._canvas.cd()


        # Create a ratio plot and draw it if requested
        if ratio:
            self._ratio_plot = TPad(
                'lowerPad', # WJF, don't need lower pad to have unique name
                'lowerPad',
                0.0,
                0.0,
                1.0,
                self.PLOT_RATIO_FRACTION
            )
            SetOwnership(self._ratio_plot, False)
            self._ratio_plot.SetMargin(*self.PLOT_RATIO_MARGINS)
            self._ratio_plot.SetGridy(True)
            self._ratio_plot.Draw()
        else:
            self._ratio_plot = None
            # increase canvas margins
            #self._canvas.SetBottomMargin(1)
            #self._plot.SetMargin
            #self._canvas.SetLeftMargin(

        # Track whether or not we've already drawn to the main pad
        self._drawn = False

        # Track whether or not we've already drawn to the ratio pad
        self._ratio_drawn = False

        # Track that object which sets up the axes in the main plot
        self._axes_object = None

        # Track whether or not we've already added the atlas label to the main pad
        self._atlas_label_drawn = False

        # Create a structure to track any histograms we generate internally
        # which need to be added to any legends created
        self._legend_extras = []
    
        # Flag if y-axis has been set to a log scale 
        self._logy = False 

    def getCanvas(self):
        """Returns the canvas
        """
        # Force an update of the canvas
        self._canvas.Update()
        return self._canvas

    def write(self):
        self._canvas.Write()

    def Print(self, printName, ex):
        """Prints this plot 

        Args:
            printName: filename
            ex: file extension (e.g. .pdf)
        """

        # Force an update of the canvas
        self._canvas.Update()
        self._canvas.Print(printName, ex)

    def save(self, path):
        """Saves this plot to file.

        Args:
            path: The path where the plot should be saved.
        """
        # Force an update of the canvas
        self._canvas.Update()

        # Save to file
        self._canvas.SaveAs(path)


    def _get_minimum_value(self):
        """Returns the currently set maximum value (possibly None).
        """
        if hasattr(self, '_minimum_value'):
            return self._minimum_value
        return None

    def _set_minimum_value(self, value):
        """Sets the current minimum value
        """
        # Check if the current value is not None, and if so, throw an error
        # because this property should not be set twice
        if self._get_minimum_value() is not None:
            raise RuntimeError('maximum value should not be set twice')

        # If the value is None, ignore it
        if value is None:
            return

        # Set the value
        self._minimum_value = value

    def _get_maximum_value(self):
        """Returns the currently set maximum value (possibly None).
        """
        if hasattr(self, '_maximum_value'):
            return self._maximum_value
        return None

    def _set_maximum_value(self, value):
        """Sets the current maximum value, possibly including room for a plot
        header. Adjusts accordinly if logY is set

        Args:
            value: The value to set
        """
        # Check if the current value is not None, and if so, throw an error
        # because this property should not be set twice
        if self._get_maximum_value() is not None:
            raise RuntimeError('maximum value should not be set twice')

        # If the value is None, ignore it
        if value is None:
            return

        # If the user wants a plot header, then add space for one
        if self._plot_header:

            if self._logy:
                # ensure y-axis is scaled by 30% for log-plot
                try:
                    nDecades = (log10(value) - log10(self._minimum_value))
                    if True:
                        #print 'min decade:', log10(self._minimum_value)
                        #print 'max decade:', log10(value)
                        #print 'No. decades:', nDecades
                        pass
                    # increase the number of decades by 30 % 
                    nDecades *= 1.3 
                    value = self._minimum_value * 10**nDecades
                    #print 'new max decade', log10(value)
                except ValueError:
                    value *= 10**3 # of min value is 0, default to an extra 3 decades

            else:
                # Grab the plot pad height (in pixels)
                plot_height = (
                    self.PLOT_HEIGHT * (self._plot.GetY2() - self._plot.GetY1())
                )
                
                # Adjust the height
                value *= (plot_height + self.PLOT_HEADER_HEIGHT) / plot_height
                value *= 1.1
            

        # Set the value
        self._maximum_value = value

    #____________________________________________________________________________
    def set_integer_xticks(self, set_ticks = False):
        """Set integer tick marks only on X axis for this plot."""
        self._x_integer_ticks = True


    #____________________________________________________________________________
    def set_log_scale(self, log_scale = True):
        """Set log scale on the Y axis for this plot."""
        self._plot.SetLogy(int(log_scale))
        self._logy = True 

    #____________________________________________________________________________
    def draw(self, *drawables_options):
        """Plots a collection of plottables to the main plot pad.  All TH1
        objects are drawn with error bars.  THStack elements are only drawn
        with an error band if one is provided.

        This method may only be called once

        Args:
            drawables_options: Each argument of this function must be of the
                form (object, options), where object is one of the following:

                - A TH1 object
                - A THStack object
                - A tuple of the form (THStack, TGraph) where the latter
                  represents error bars
                - A TGraph object
                - A TLine object

                and options is a string which will be used for the options
                argument of the object's Draw method.  Plottables will be
                rendered in the order provided.  Axes drawing options (e.g.
                'a' or 'same' should not be provided and will be set
                automatically).  A TLine may not be the first drawable element.
        """
        # Make sure there are drawables
        if len(drawables_options) == 0:
            raise ValueError('must provide at least one plottable')

        # Check if we've already drawn
        if self._drawn:
            raise RuntimeError('cannot draw twice to a plot')
        self._drawn = True

        # Extract drawables
        drawables, _ = zip(*drawables_options)

        # Check if there is a minimum value set, and if not, set it
        if self._get_minimum_value() is None:
            self._set_minimum_value(minimum_value(drawables))

        # Check if there is a maximum value set, and if not, set it
        if self._get_maximum_value() is None:
            self._set_maximum_value(maximum_value(drawables))

        # Move to the context of the plot pad
        self._plot.cd()

        # Iterate through and draw drawables based on type
        first = True
        for drawable, option in drawables_options:
            # Check if this a tuple of histogram, error_band
            if isinstance(drawable, tuple):
                drawable, error_band = drawable
            else:
                error_band = None

            # Make a clone of the drawable so we don't modify it
            drawable = drawable.Clone(drawable.GetName()+'_clone') #_rand_uuid())
            SetOwnership(drawable, False)

            # Set the maximum value of the drawable if supported
            # HACK: I wish this could go into _handle_axes, but apparently it
            # can't because ROOT sucks and this has to be set on EVERY
            # drawable, not just the one with the axes.
            if not is_line(drawable):
                drawable.SetMaximum(self._get_maximum_value())

            #if not is_line(drawable):
            #drawable.SetMinimum(self._get_minimum_value())
            #drawable.SetMinimum(10**(-2))
            

            # Include axes if we need
            if first:
                if is_line(drawable):
                    raise ValueError('TLine may not be first drawable')
                if is_graph(drawable):
                    option += 'a'
            else:
                option += 'same'
            first = False

            # Draw the histogram
            drawable.Draw(option)

            # Handle axes
            if not is_line(drawable):
                self._handle_axes(drawable, option)

            # If there is an error band, draw it
            if error_band is not None:
                self._draw_error_band(error_band)

        # HACK: Need to force a redraw of plot axes due to issue with ROOT:
        # http://root.cern.ch/phpBB3/viewtopic.php?f=3&t=14034
        self._plot.RedrawAxis()

    def _handle_axes(self, drawable, option):
        """If there is no object currently registered as the owner of the axes
        drawn on the main plot, then this will set it.

        Args:
            drawable: The graph, histogram or stack whose axes were ALREADY
                drawn
            option: The option with which to draw the axes
        """
        # If we already have an axes object, ignore this one
        if self._axes_object is not None:
            return

        # Grab the histogram used for axes style/range manipulation
        if is_stack(drawable) or is_graph(drawable):
            axes_histogram = drawable.GetHistogram()
        else:
            axes_histogram = drawable

        # Grab the histogram used for title manipulation
        if is_stack(drawable):
            title_histogram = drawable.GetHists()[0]
        else:
            title_histogram = drawable

        # Set the plot title
        title_histogram.SetTitle(self._title)

        # Grab axes
        x_axis, y_axis = axes_histogram.GetXaxis(), axes_histogram.GetYaxis()

        # Grab titles from first histogram if not set explicitly
        if self._x_title is None:
            self._x_title = title_histogram.GetXaxis().GetTitle()
        if self._y_title is None:
            self._y_title = title_histogram.GetYaxis().GetTitle()

        # Style x-axis, or hide it if this plot has a ratio plot
        if self._x_range is not None:
            x_axis.SetRangeUser(*self._x_range)
        if self._ratio_plot:
            x_axis.SetLabelOffset(999)
            x_axis.SetTitleOffset(999)
        else:
            x_axis.SetTitle(self._x_title)
            x_axis.SetTitleSize(self.PLOT_X_AXIS_TITLE_SIZE)
            x_axis.SetTitleOffset(self.PLOT_X_AXIS_TITLE_OFFSET)
            x_axis.SetLabelSize(self.PLOT_X_AXIS_LABEL_SIZE)
        if self._x_integer_ticks:
            x_axis.SetNdivisions(11) # hack for integer ticks 

        # Style y-axis
        y_axis.SetTitle(self._y_title)
        y_axis.SetLabelFont(self.PLOT_ATLAS_STAMP_TEXT_FONT)
        y_axis.SetTitleSize(
            (self.PLOT_Y_AXIS_TITLE_SIZE_WITH_RATIO
             if self._ratio_plot
             else self.PLOT_Y_AXIS_TITLE_SIZE)
        )
        y_axis.SetTitleOffset(
            (self.PLOT_Y_AXIS_TITLE_OFSET_WITH_RATIO
             if self._ratio_plot
             else self.PLOT_Y_AXIS_TITLE_OFFSET)
        )
        y_axis.SetNdivisions(5,5,0)
        
        # set axis text sizes 
        if self._ratio_plot:
            y_axis.SetLabelSize(self.PLOT_Y_AXIS_LABEL_SIZE_WITH_RATIO)
        else:
            y_axis.SetLabelSize(self.PLOT_Y_AXIS_LABEL_SIZE) 
            y_axis.SetTitleSize(self.PLOT_Y_AXIS_TITLE_SIZE)
            y_axis.SetTitleOffset(self.PLOT_RATIO_Y_AXIS_TITLE_OFFSET)

        # Redraw the drawable with the new style
        drawable.Draw(option)

    def _draw_error_band(self, error_band):
        """Draws an error band on top of histogram objects.

        Args:
            error_band: The error band to draw (a TGraphAsymmErrors)
        """
        # Style it
        # HACK: Setting the marker style to 0 specifies this should be filled
        # in the legend
        error_band.SetMarkerStyle(0)
        error_band.SetMarkerSize(0)
        error_band.SetFillStyle(self.PLOT_ERROR_BAND_FILL_STYLE)
        error_band.SetFillColor(self.PLOT_ERROR_BAND_FILL_COLOR)
        error_band.SetLineWidth(self.PLOT_ERROR_BAND_LINE_WIDTH)
        error_band.SetLineColor(self.PLOT_ERROR_BAND_LINE_COLOR)

        # axis style
        if self._x_integer_ticks:
            error_band.GetAxis().SetNdivisions(11)

        # Draw it
        error_band.Draw('e2same')

        # Add it to the list of things we need to add to the legend
        self._legend_extras.append(error_band)

    def draw_ratio_histogram(self,
                             drawableOption,
                             error_band = None,
                             draw_unity = True,
                             error_band2 = None):
        """Draws a ratio histogram to the ratio pad.

        Args:
            histogramOption: Tuple containing: 1 the ratio histogram to draw (use ratio_histogram), 2 the option to remove X error bars 
            draw_unity: Whether or not to draw a line at 1
            error_band: An error band to draw under the ratio histogram

        The histogram X axis title is set by draw_histogram if not set
        explicitly. draw_ratio_histogram should therefore be called after
        draw_histogram.

        Note that all the Draw function for the drawable objects is called at the end 
        of the function, as it can be messy as to what needs to be drawn first depending 
        on the type of drawable (thanks ROOT) 
        """


        # Check if we've already drawn a ratio
        ratio_draw_option = '' 
        if self._ratio_drawn:
            #raise RuntimeError('cannot draw twice to a plot')
            print 'WARNING: Drawing two ratios'
            ratio_draw_option = 'same'

        # Extract drawable and option from tuple
        drawable      = drawableOption[0] # could be a TGraph or a TH1
        noXerror      = drawableOption[1]
        RATIO_Y_TITLE = drawableOption[2]

        # Switch to the context of the ratio pad
        self._ratio_plot.cd()


        #################################################################
        # Extract histogram object from graph, used for the unity line and arrows
        # This acts as a frame in the case of TGraph 
        #################################################################
        if is_graph(drawable):
            histogram = drawable.GetHistogram() 
            print 'ratio histogram was a TGraph'
        else: 
            histogram = drawable.Clone()
        histogram.SetMarkerSize(0)


        
        #################################################################
        # Create an empty frame, very handy for axis ranges (!!!)
        frame = TH1F('lowerFrame', '', 100, self._x_range[0], self._x_range[1]) 
        frame.Fill(1)
        #frame.SetMarkerSize(0)
        frame.SetStats(0)
        #################################################################




        #################################################################
        # Style objects like error band, unity line. They are drawn later
        #################################################################
        if not self._ratio_drawn:

            # If an error band was provided, draw it and add it to our legend elements
            # Note the error_band can also be a TGraph if it is asymmetric 
            if error_band:
                # Keep ownership of the error band
                SetOwnership(error_band, False)
                
                # Style it (styling can only correspond to drawable type)
                error_band.GetXaxis().SetRangeUser(*self._x_range)
                error_band.SetMarkerSize(0)
                error_band.SetTitle("")
                if is_histo(error_band):
                    error_band.SetStats(0)

            # Style or unity line 
            if draw_unity:

                # Calculate the line coordinates
                line_min = histogram.GetBinLowEdge(1)
                max_bin  = histogram.GetNbinsX()
                line_max = (histogram.GetBinLowEdge(max_bin) + histogram.GetBinWidth(max_bin))

                # Create and draw the line (don't use TLine) 
                unit_line = TF1("unityLine", "1", line_min, line_max) 
                SetOwnership(unit_line, False)
                unit_line.SetLineColor(2) # Red
                unit_line.SetLineWidth(2)
                unit_line.SetLineStyle(2)

            # Styling for second error band (if needed)  
            if error_band2:
                print 'Adding second error band'
                SetOwnership(error_band2, False)

        #################################################################
        # Style the frame
        #################################################################

        #x_axis = frame.GetXaxis()
        #y_axis = frame.GetYaxis()

        x_axis = histogram.GetXaxis()
        y_axis = histogram.GetYaxis()

        x_axis.SetTitle(self._x_title)
        x_axis.SetTitleSize(self.PLOT_X_AXIS_TITLE_SIZE_WITH_RATIO)
        #x_axis.SetTitleOffset(self.PLOT_X_AXIS_TITLE_OFFSET_WITH_RATIO)
        x_axis.SetLabelSize(self.PLOT_X_AXIS_LABEL_SIZE_WITH_RATIO)
        x_axis.SetLabelColor(1) # black 
        x_axis.SetLabelFont(self.PLOT_ATLAS_STAMP_TEXT_FONT)

        if self._x_integer_ticks:
            x_axis.SetNdivisions(11) # hack for integer ticks 
        if self._x_range:
            x_axis.SetRangeUser(*self._x_range)
        
        y_axis.SetTitle(RATIO_Y_TITLE)
        y_axis.SetTitleSize(self.PLOT_RATIO_Y_AXIS_TITLE_SIZE)
        y_axis.CenterTitle()
        y_axis.SetTitleOffset(self.PLOT_RATIO_Y_AXIS_TITLE_OFFSET_RATIO)
        y_axis.SetLabelSize(self.PLOT_RATIO_Y_AXIS_LABEL_SIZE)
        #y_axis.SetLabelSize(30)
        y_axis.SetLabelFont(self.PLOT_ATLAS_STAMP_TEXT_FONT)

        y_axis.SetRangeUser(self.PLOT_RATIO_Y_AXIS_MINIMUM,
                            self.PLOT_RATIO_Y_AXIS_MAXIMUM)
        y_axis.SetNdivisions(504, False)



        x_axis_drawable = drawable.GetXaxis()
        y_axis_drawable = drawable.GetYaxis()
        x_axis_drawable.SetTitle(self._x_title)
        x_axis_drawable.SetTitleSize(self.PLOT_X_AXIS_TITLE_SIZE_WITH_RATIO*100)
        x_axis_drawable.SetLabelSize(self.PLOT_X_AXIS_LABEL_SIZE_WITH_RATIO*100)
        x_axis_drawable.SetLabelColor(1) # black 
        x_axis_drawable.SetLabelFont(self.PLOT_ATLAS_STAMP_TEXT_FONT)
        if self._x_integer_ticks:
            x_axis_drawable.SetNdivisions(11) # hack for integer ticks 
        if self._x_range:
            x_axis_drawable.SetRangeUser(*self._x_range)
        y_axis_drawable.SetTitle(RATIO_Y_TITLE)
        y_axis_drawable.SetTitleSize(self.PLOT_RATIO_Y_AXIS_TITLE_SIZE)
        y_axis_drawable.CenterTitle()
        y_axis_drawable.SetTitleOffset(self.PLOT_RATIO_Y_AXIS_TITLE_OFFSET_RATIO)
        y_axis_drawable.SetLabelSize(self.PLOT_RATIO_Y_AXIS_LABEL_SIZE)
        y_axis_drawable.SetLabelFont(self.PLOT_ATLAS_STAMP_TEXT_FONT)
        y_axis_drawable.SetRangeUser(self.PLOT_RATIO_Y_AXIS_MINIMUM,
                            self.PLOT_RATIO_Y_AXIS_MAXIMUM)
        y_axis_drawable.SetNdivisions(504, False)


        if error_band:
            x_axis_error_band = error_band.GetXaxis()
            y_axis_error_band = error_band.GetYaxis()
            x_axis_error_band.SetTitle(self._x_title)
            x_axis_error_band.SetTitleSize(self.PLOT_X_AXIS_TITLE_SIZE_WITH_RATIO*100)
            x_axis_error_band.SetLabelSize(self.PLOT_X_AXIS_LABEL_SIZE_WITH_RATIO*100)
            x_axis_error_band.SetLabelColor(1) # black 
            x_axis_error_band.SetLabelFont(self.PLOT_ATLAS_STAMP_TEXT_FONT)
            if self._x_integer_ticks:
                x_axis_error_band.SetNdivisions(11) # hack for integer ticks 
            if self._x_range:
                x_axis_error_band.SetRangeUser(*self._x_range)
            y_axis_error_band.SetTitle(RATIO_Y_TITLE)
            y_axis_error_band.SetTitleSize(self.PLOT_RATIO_Y_AXIS_TITLE_SIZE)
            y_axis_error_band.CenterTitle()
            y_axis_error_band.SetTitleOffset(self.PLOT_RATIO_Y_AXIS_TITLE_OFFSET_RATIO)
            y_axis_error_band.SetLabelSize(self.PLOT_RATIO_Y_AXIS_LABEL_SIZE)
            y_axis_error_band.SetLabelFont(self.PLOT_ATLAS_STAMP_TEXT_FONT)
            y_axis_error_band.SetRangeUser(self.PLOT_RATIO_Y_AXIS_MINIMUM,
                                self.PLOT_RATIO_Y_AXIS_MAXIMUM)
            y_axis_error_band.SetNdivisions(504, False)

        ##################################################
        # Drawing
        ##################################################

        print 'DRAWING FRAME'
        #frame.Draw('axis')
        histogram.Draw()

        # NOTE: Have to specify E0 or points out of the vertical range won't have
        # their error bars drawn: https://root.cern.ch/phpBB3/viewtopic.php?f=3&t=13329
        if is_histo(drawable):
            if noXerror:
                #drawable.Draw('e0px0'+ratio_draw_option)
                drawable.Draw('e0px0same')
            else:
                #drawable.Draw('e0p'+ratio_draw_option)
                drawable.Draw('e0psame')
        elif is_graph(drawable):
            #drawable.Draw('APEZ0') # default no x-error bars 
            #drawable.Draw('PEZ0same') # default no x-error bars 
            pass
            # There are problems with drawing the TGraph first

        # Draw 2
        if not self._ratio_drawn:
            if error_band:
                error_band.Draw('e2same')

            if draw_unity:
                unit_line.Draw('same')

                # Draw error band again to make sure it's on top
                if error_band: 
                    error_band.Draw('e2same')

            if error_band2:
                error_band2.Draw('e2same')

            # Now, if we've drawn unity or an error band, redraw our ratio
            # histogram so that its point lie on top of the unity line or error
            # band, but use 'same' so that the axes/ticks don't cover the red line
            if draw_unity or error_band:
                if is_histo(drawable):
                    if noXerror:
                        drawable.Draw('e0px0same')
                    else:
                        drawable.Draw('e0psame')
                elif is_graph(drawable):
                    drawable.Draw('PEZ0 same') # O option for error bars outside Y range



        if not self._ratio_drawn:
            # Finally, draw nice little arrows if a data-point extends beyond 
            # the axis range. Add a line just for taste :)
            arrow = TArrow()
            line_arrow = TLine()
            line_arrow.SetLineColor(self.ARROW_COLOUR)
            line_arrow.SetLineWidth(2)
            arrow.SetLineColor(self.ARROW_COLOUR)
            arrow.SetFillColor(self.ARROW_COLOUR)

            # different access functions for the points 
            if is_histo(drawable):
                for mybin in xrange( histogram.GetXaxis().GetNbins()+1 ):
                    yval  = histogram.GetBinContent(mybin)
                    xval  = histogram.GetBinCenter(mybin)
                    elow  = histogram.GetBinErrorLow(mybin)
                    error = histogram.GetBinError(mybin)
                    actualErrorLowValue = yval - error
                    print xval, yval, elow, error
                    if actualErrorLowValue > 2: # only draw arrow if error does not extend into ratio plot
                        #print xval, Rdat, elow, error
                        arrow.DrawArrow(xval, 1.7, xval, 1.9, self.ARROW_SIZE, '|>' )
                        line_arrow.DrawLine(xval, 1.5, xval, 1.8)
            elif is_graph(drawable):
                for iPoint in xrange( drawable.GetN()+1 ): 
                    xval = Double(0.0)
                    yval = Double(0.0)
                    point = drawable.GetPoint(iPoint, xval, yval) 
                    errorLow = drawable.GetErrorYlow(iPoint)
                    actualErrorLowValue = yval - errorLow
                    if actualErrorLowValue > 2: # only draw arrow if error does not extend into ratio plot
                        #print xval, Rdat, elow, error
                        arrow.DrawArrow(xval, 1.7, xval, 1.9, self.ARROW_SIZE, '|>' )
                        line_arrow.DrawLine(xval, 1.5, xval, 1.8)


                    
        # re-set the x-range
        self._ratio_plot.Update()
        #if self._x_range:
        #x_axis.SetRangeUser(*self._x_range)









        x_axis.SetTitle(self._x_title)
        x_axis.SetTitleSize(self.PLOT_X_AXIS_TITLE_SIZE_WITH_RATIO*100)
        #x_axis.SetTitleOffset(self.PLOT_X_AXIS_TITLE_OFFSET_WITH_RATIO)
        x_axis.SetLabelSize(self.PLOT_X_AXIS_LABEL_SIZE_WITH_RATIO*100)
        x_axis.SetLabelColor(1) # black 
        x_axis.SetLabelFont(self.PLOT_ATLAS_STAMP_TEXT_FONT)

        if self._x_integer_ticks:
            x_axis.SetNdivisions(11) # hack for integer ticks 
        if self._x_range:
            x_axis.SetRangeUser(*self._x_range)
        
        y_axis.SetTitle(RATIO_Y_TITLE)
        y_axis.SetTitleSize(self.PLOT_RATIO_Y_AXIS_TITLE_SIZE)
        y_axis.CenterTitle()
        y_axis.SetTitleOffset(self.PLOT_RATIO_Y_AXIS_TITLE_OFFSET_RATIO)
        y_axis.SetLabelSize(self.PLOT_RATIO_Y_AXIS_LABEL_SIZE)
        #y_axis.SetLabelSize(30)
        y_axis.SetLabelFont(self.PLOT_ATLAS_STAMP_TEXT_FONT)

        y_axis.SetRangeUser(self.PLOT_RATIO_Y_AXIS_MINIMUM,
                            self.PLOT_RATIO_Y_AXIS_MAXIMUM)
        y_axis.SetNdivisions(504, False)


















        # Re-draw axis at the end         
        self._ratio_plot.RedrawAxis()

        # Set to true 
        self._ratio_drawn = True


    def draw_atlas_label(self,
                         luminosity,
                         atlas_label = None,
                         custom_label = None,
                         #ks_test = None,
                         sqrt_s = 13):
        """Draws an ATLAS stamp on the plot, with an optional categorization
        label.

        It is recommended that you construct the Plot with plot_header = True
        in order to make space for the label.

        Args:
            luminosity: The integrated luminosity, in pb^-1
            label:      The label to put after 'ATLAS', None to exclude the 'ATLAS'
                        categorization entirely
            custom_label: Additional text to put on the plot  
            sqrt_s:     The center of mass energy, in TeV
        """
        # Change context to the plot pad
        self._plot.cd()

        # Create the latex object
        stamp = TLatex()

        # Style it
        stamp.SetTextColor(self.PLOT_ATLAS_STAMP_TEXT_COLOR)
        stamp.SetTextFont(self.PLOT_ATLAS_STAMP_TEXT_FONT)
        stamp.SetNDC()

        # Draw the luminosity and COM
        stamp.SetTextSize((self.PLOT_ATLAS_STAMP_LUMINOSITY_SIZE_WITH_RATIO
                           if self._ratio_plot
                           else self.PLOT_ATLAS_STAMP_LUMINOSITY_SIZE))
        text = '#sqrt{s} = 13 TeV'+', {0:.1f} fb^{{#minus1}}'.format(luminosity / 1000.0)
        #text = 'L_{int} ='+' {0:.1f} fb^{{#minus1}}, 13 TeV'.format(luminosity / 1000.0)
        stamp.DrawLatex(
            self.PLOT_ATLAS_STAMP_LUMINOSITY_LEFT,
            (self.PLOT_ATLAS_STAMP_LUMINOSITY_TOP_WITH_RATIO
             if self._ratio_plot
             else self.PLOT_ATLAS_STAMP_LUMINOSITY_TOP),
            text
        )


        # If requested, draw the custom label or the 'ATLAS' label,
        # preferring the former
        #print 'Custom label:',custom_label
        if custom_label is not None:
            # Draw the label
            stamp.DrawLatex(
                self.PLOT_ATLAS_STAMP_LEFT,
                (self.PLOT_ATLAS_STAMP_ADDITIONAL_TOP_WITH_RATIO
                 if self._ratio_plot
                 else self.PLOT_ATLAS_STAMP_ADDITIONAL_TOP),
                custom_label
            )

        # Draw "ATLAS" label with e.g. "Internal"
        if atlas_label is not None:
            # Draw the "Internal" part 
            stamp.SetTextSize((self.PLOT_ATLAS_STAMP_TITLE_SIZE_WITH_RATIO
                               if self._ratio_plot
                               else self.PLOT_ATLAS_STAMP_TITLE_SIZE))
            stamp.DrawLatex(
                self.PLOT_ATLAS_STAMP_LEFT + (
                    self.PLOT_ATLAS_STAMP_LABEL_LEFT_ADDITION_WITH_RATIO
                    if self._ratio_plot
                    else self.PLOT_ATLAS_STAMP_LABEL_LEFT_ADDITION
                ),
                (self.PLOT_ATLAS_STAMP_ATLAS_TOP_WITH_RATIO
                 if self._ratio_plot
                 else self.PLOT_ATLAS_STAMP_ATLAS_TOP),
                atlas_label
            )

            # Draw the 'ATLAS' part 
            stamp.SetTextFont(self.PLOT_ATLAS_STAMP_ATLAS_TEXT_FONT)
            stamp.DrawLatex(
                self.PLOT_ATLAS_STAMP_LEFT,
                (self.PLOT_ATLAS_STAMP_ATLAS_TOP_WITH_RATIO
                 if self._ratio_plot
                 else self.PLOT_ATLAS_STAMP_ATLAS_TOP),
                'ATLAS'
            )

        '''
        # Draw the result of the KS-test, if requested
        if ks_test is not None:
            text = ', KS = {0:.2f}'.format(ks_test)
            stamp.DrawLatex(
                self.PLOT_ATLAS_STAMP_LEFT,
                (self.PLOT_ATLAS_STAMP_SQRT_S_TOP_WITH_RATIO
                 if self._ratio_plot
                 else self.PLOT_ATLAS_STAMP_SQRT_S_TOP),
                text
            )
        '''

        self._atlas_label_drawn = True

    def draw_legend(self, *drawables):
        """Draws a legend onto the plot with the specified histograms.

        It is recommended that you construct the Plot with plot_header = True
        in order to make space for the legend.

        Args:
            drawables: The elements to include in the legend (via AddEntry)
        """
        # Check if we already have a legend
        if hasattr(self, '_legend'):
            raise RuntimeError('legend already exists on this plot')

        # Switch to the context of the main plot
        self._plot.cd()

        # Create the legend
        if self._atlas_label_drawn:
            self._legend = TLegend(self.PLOT_LEGEND_LEFT,
                                   (self.PLOT_LEGEND_BOTTOM_WITH_RATIO
                                    if self._ratio_plot
                                    else self.PLOT_LEGEND_BOTTOM),
                                   self.PLOT_LEGEND_RIGHT,
                                   (self.PLOT_LEGEND_TOP_WITH_RATIO
                                    if self._ratio_plot
                                    else self.PLOT_LEGEND_TOP))
        else:
            # WJF may need customisation with ratio
            self._legend = TLegend(0.15, 0.7, 0.5, 0.88)

        SetOwnership(self._legend, False)

        # Style it
        self._legend.SetTextSize((
            self.PLOT_LEGEND_TEXT_SIZE_WITH_RATIO
            if self._ratio_plot
            else self.PLOT_LEGEND_TEXT_SIZE
        ))
        self._legend.SetBorderSize(0)
        self._legend.SetFillStyle(0) # transparent
        self._legend.SetNColumns(self.PLOT_LEGEND_N_COLUMNS)

        # Create a chained list of all drawables.  We decompose THStack
        # objects in reverse order, i.e. top-to-bottom.
        drawables = \
            list(chain(*(drawable_iterable(h, True, True)
                         for h
                         in drawables)))

        # Add anything to this list that we created internally
        drawables.extend(self._legend_extras)

        # Because ROOT draws legend entries from left-to-right across rows and
        # not top-to-bottom along columns, we need to do a bit of a pivot on
        # the list so that the histograms appear in the vertical order of the
        # stack
        n_entries = len(drawables)
        n_col = self.PLOT_LEGEND_N_COLUMNS
        n_row = int(ceil(float(n_entries) / n_col))
        legend_order = []
        for r in xrange(0, n_row):
            for c in xrange(0, n_col):
                if (r * n_col + c) == n_entries:
                    # Don't need an outer break, this would only happen on the
                    # last row if n_row * n_col != n_entries
                    break
                legend_order.append(drawables[r + c * n_row])

        # Add the drawables
        for drawable in legend_order:
            SetOwnership(drawable, False)
            title = drawable.GetTitle()
            # HACK: Convention: legend for drawables with a non-default
            # marker style (data) to be drawn as point, and with
            # empty fill (signal) to be drawn as line
            #print 'Adding plottable {0} to legend. Has MarkerStyle {1} and fill colour {2}'.format(drawable.GetName(), drawable.GetMarkerStyle(), drawable.GetFillColor())
            #self._legend.AddEntry(drawable, title, 'f')
            this_marker = drawable.GetMarkerStyle()
            if this_marker == 20:
                self._legend.AddEntry(drawable, title, 'p')
                #self._legend.AddEntry(drawable, title, 'l')
            elif drawable.GetTitle() == 'Total Background' or drawable.GetTitle() == 'Total background':
                self._legend.AddEntry(drawable, title, 'lf')
            elif drawable.GetFillColor() == 0:
                self._legend.AddEntry(drawable, title, 'l')
            elif this_marker == 21 or this_marker == 3 or this_marker == 22:
                self._legend.AddEntry(drawable, title, 'lp')
            else:
                self._legend.AddEntry(drawable, title, 'f')

        # Draw the legend
        self._legend.Draw()


