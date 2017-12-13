from ROOT import * 
gROOT.SetBatch(1)

OUTPUT_DIR = 'plots/'

def main():

    ifile = TFile.Open('/Users/Will/Documents/fcc/trackerSW/delphes/output_ttbar_mu1000.root')

    truthTrackPt = ifile.Get('truthTrack100')
    #truthTrackPt = TH1D('tracks', '', 100, 0, 100)

    '''
    for bin in range(truthTrackPt_1000.GetNbinsX()):
        if bin > 100: continue
        truthTrackPt.SetBinContent(bin, truthTrackPt_1000.GetBinContent(bin))
    truthTrackPt_1000.GetXaxis().SetRangeUser(0,200)
    truthTrackPt_1000.Draw()
    truthTrackPt.SetLineColor(kGreen)
    truthTrackPt.Draw('same')
    can.SaveAs('test.pdf')
    '''
    can = TCanvas('can', 'can', 500, 500)

    tGraphs = {}

    for i in range(0, 6):
        ptCut = (i+1)*5
        hName = 'truthTrackPt{0}'.format(ptCut)
        print hName
        ptAfterCut = ifile.Get(hName)
        ptAfterCut.SetLineColor(kRed)

        can.SetLogy()
        truthTrackPt.Draw()
        ptAfterCut.Draw('same')
        can.SaveAs(OUTPUT_DIR+'tracksPt{0}.pdf'.format(ptCut))

        # to make turn on to TGraphAsymmErrors(numerator, denominator)
        ratio = TGraphAsymmErrors(ptAfterCut, truthTrackPt)

        can.SetLogy(0)
        ratio.Draw('AP')
        ratio.GetXaxis().SetRangeUser(0, ptCut*3)
        can.SaveAs(OUTPUT_DIR+'turnOnPt{0}.pdf'.format(ptCut))

        tGraphs[ptCut] = ratio
    

if __name__ == "__main__":
    main()
