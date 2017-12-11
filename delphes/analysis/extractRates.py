
from ROOT import * 
gROOT.SetBatch(1)
gROOT.SetBatch(1)
gStyle.SetGridStyle(3) 
gStyle.SetPadLeftMargin(0.15) # increase space for left margin
gStyle.SetPadBottomMargin(0.15) # increase space for left margin
gStyle.SetGridColor(kGray)
gStyle.SetPadTickX(1) # add tics on top x
gStyle.SetPadTickY(1) # add tics on right y

from extractTrackParameters import prepareLegend

colours = [
    865, # blue
    801, # orange
    629, # red
    418,  # green
    15,  # grey
    618, # purple
    1, # black
]

def main(inputFile, outputDir, text):
    outputDir = appendSlash(outputDir)

    can = TCanvas('can', 'can', 500, 500)
    ifile = TFile.Open(inputFile)

    
    for nJet in range(1,8):

    
        # extract jet pT histogram
        hName = 'jet{0}Pt'.format(nJet)
        print hName
        h = ifile.Get(hName)
        c = getReverseCumulativeHisto(h)

        # get associated jet pT histogram
        h2 = ifile.Get('associatedJet{0}Pt'.format(nJet))
        c2 = getReverseCumulativeHisto(h2)

        # draw jet pT histo     
        h.GetXaxis().SetRangeUser(0, 200)
        h.Draw()
        saveName =  outputDir+'jet{0}Pt{1}.pdf'.format(nJet, text)
        can.SaveAs(saveName)

        leg = prepareLegend('topRight')
        leg.SetHeader(text)
        leg.AddEntry(c, 'All jets', 'lp')
        leg.AddEntry(c2, 'Jets from PB', 'lp')
        
        # rate plots
        c.GetXaxis().SetRangeUser(0, 200)
        c.SetMarkerColor(865)
        c.SetLineColor(865)
        c.GetYaxis().SetTitle('Relative Rate')

        c2.SetMarkerColor(629)
        c2.SetLineColor(629)
        

        #c.DrawNormalized()
        c.Draw()
        c2.Draw('same')
        leg.Draw()
        saveName = outputDir+'jet{0}RateCumulativePt{1}.pdf'.format(nJet, text)
        can.SaveAs(saveName)


def appendSlash(path):
    if path[-1] != '/':
        return path+'/'
    else:
        return path

#____________________________________________________________________________
def getReverseCumulativeHisto(histo):
    '''
    Function to return the cumulative efficiency curve from a
    differential efficiency curve
    '''
    nbins = histo.GetNbinsX()
    error = Double()
    cumulHisto = histo.Clone()
    cumulHisto.Reset()
    for bin in range(1,nbins+1):
        integral = histo.IntegralAndError(bin,nbins,error)
        integralErr = error
        cumulHisto.SetBinContent(bin,integral)
        cumulHisto.SetBinError(bin,integralErr)
    return cumulHisto
    

if __name__ == "__main__":

    from optparse import OptionParser
    import sys

    parser = OptionParser()
    parser.add_option("-i", "--inputFile", action="store", type="string", help="Input ROOT file")
    parser.add_option("-o", "--outputDir", action="store", type="string",  default='./', help="Output directory for plots")
    parser.add_option("-t", "--text", action="store", type="string",  default="", help="text to add to plot names")

    if len(sys.argv) == 1:
        parser.print_help()
        sys.exit(0)

    options, args = parser.parse_args()
    option_dict = dict( (k, v) for k, v in vars(options).iteritems() if v is not None)
    main(**option_dict)