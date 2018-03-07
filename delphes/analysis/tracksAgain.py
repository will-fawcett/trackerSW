#!/usr/bin/python

from ROOT import * 

def addTrack(aDict, cut):

    try:
        aDict[cut] += 1
    except KeyError:
        aDict[cut] = 1


def main(verbose):

    resultsDir = "/atlas/data4/userdata/wfawcett/delphes/results/"
    baseDir = resultsDir+"hits_phiEtaSeg_tolerance05mm_phi2GeV_curvature0005_nVertexSigma4/"
    ifile = TFile.Open(baseDir+"hits_ttbar_pu0_multiGeometry_tracks.root", "READ")

    # get relevant tree
    tree = ifile.Get("Tracks10")

    numberOfHits = tree.GetEntries()
    print 'There are {0} entries'.format(numberOfHits)

    nFakesOriginal = 0.0

    kappaCuts = [0.0050, 0.0045, 0.0040, 0.0035, 0.0030, 0.0025]

    nTracksSurviveKappaCut = {}
    nFakesSurviveKappaCut = {}

    # high pT fake rate
    nFakesPt50 = 0.0
    nFakesSurviveKappaCutPt50 = {}
    nTracksSurviveKappaCutPt50 = {}

    # Loop over all events in tree
    for event in tree:
            
        if event.isFake:
            nFakesOriginal += 1 
            if event.hit3pT > 50:
                nFakesPt50 += 1

        deltaKappa = abs(event.kappa_123 - event.kappa_013)

        for cut in kappaCuts:
            if deltaKappa < cut: 
                addTrack(nTracksSurviveKappaCut, cut)

                if event.hit3pT > 50:
                    addTrack(nTracksSurviveKappaCutPt50, cut)

                if event.isFake:
                    addTrack(nFakesSurviveKappaCut, cut)

                    if event.hit3pT > 50:
                        addTrack(nFakesSurviveKappaCutPt50, cut) 


            

    print 'Original number of fakes', nFakesOriginal
    print 'Original fake rate', nFakesOriginal/float(numberOfHits)

    for cut in kappaCuts:

        overallTracksRemoved = numberOfHits - nTracksSurviveKappaCut[cut]
        fakesRemoved         = nFakesOriginal - nFakesSurviveKappaCut[cut]

        fakesRemaining       = nFakesOriginal - fakesRemoved
        trueTracksRemoved    = overallTracksRemoved - fakesRemoved

        newFakeRate          = fakesRemaining / nTracksSurviveKappaCut[cut]

        efficiency           = nTracksSurviveKappaCut[cut] / float(numberOfHits)

        print 'Kappa cut: ', cut
        print '\tTotal number of tracks removed by cut: {0}'.format(overallTracksRemoved)
        print '\tNumber of fakes removed: {0}'.format(fakesRemoved)
        print '\tNumber of fakes remaining: {0}'.format(fakesRemaining)
        print '\tNumber of true tracks removed: {0}'.format(trueTracksRemoved)
        print '\tEfficiency: {0:.2f}, efficiency loss {1:.2f}'.format(efficiency*100, (1-efficiency)*100)
        print '\tNew fake rate: {0}'.format(newFakeRate)
        print ''


if __name__ == "__main__":

    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("-v", "--verbose", help="Turn on verbose messages", action="store_true", default=False)
    args = parser.parse_args()
    verbose = args.verbose

    main(verbose)
