# quick script to make plots for minbias a bit nicer

from ROOT import * 

gROOT.SetBatch(1)
gStyle.SetPadLeftMargin(0.12) # increase space for left margin


def main():


    can = TCanvas('can', 'can', 500, 500)

    filename = 'minbias/minbiasPT.root'
    ptHist = getHistogram(filename)
    ptHist.SetTitle('Minbias + pileup 1000')
    ptHist.SetStats(0)
    xaxis = ptHist.GetXaxis()
    yaxis = ptHist.GetYaxis()
    xaxis.SetTitle('Particle p_{T} [GeV]')
    yaxis.SetTitle('A. U.')

    can.cd()
    ptHist.DrawNormalized()
    can.SaveAs('minbiasPT.pdf')

    filename = 'minbias/minbiasEta.root'
    etaHist = getHistogram(filename)
    etaHist.SetTitle('Minbias + pileup 1000')
    etaHist.SetStats(0)
    xaxis = etaHist.GetXaxis()
    yaxis = etaHist.GetYaxis()
    xaxis.SetTitle('Particle #eta')
    yaxis.SetTitle('A. U.')

    can.cd()
    etaHist.DrawNormalized()
    can.SaveAs('minbiasEta.pdf')


    filename = 'minbias/minbiasNtracks.root'
    ntracks = getHistogram(filename)
    ntracks.Rebin(4)
    ntracks.SetTitle('Minbias + pileup 1000. |#eta| < 2.0 & p_{T} > 1 GeV')
    ntracks.SetStats(0)
    xaxis = ntracks.GetXaxis()
    yaxis = ntracks.GetYaxis()
    xaxis.SetTitle('Track multiplicity')
    yaxis.SetTitle('A. U.')

    can.cd()
    ntracks.DrawNormalized()
    can.SaveAs('minbiasNtracks.pdf')




def getHistogram(filename):

    f = TFile.Open(filename)
    hpt = f.Get('Canvas_1')
    hist = hpt.GetPrimitive('htemp')
    hist.SetLineWidth(2)
    f.Close()
    return hist

def printPrimitiveNames(tobject):
    primList = tobject.GetListOfPrimitives()
    print 'TObject of type: {0}, and name: {1}, has {2} primitives'.format(type(tobject), tobject.GetName(), len(primList))
    for x in primList:
        print '\t', x

if __name__ == "__main__":
    main()

