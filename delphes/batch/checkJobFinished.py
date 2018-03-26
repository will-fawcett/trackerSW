#!/usr/bin/python
import json
import ROOT
import os


def main(verbose):


    DATA_DIR = "/atlas/data4/userdata/wfawcett/delphes/"
    BATCH_SCRIPT_DIR = DATA_DIR + "particleProductionBatch/"
    LHE_DIR = DATA_DIR + "lhe/"

    # get list of samples from LHE dir
    samples = [x[0].split('/')[-1] for x in os.walk(LHE_DIR)] # [ "mg_pp_hh",  "mg_pp_tth",  "mg_pp_tt_nlo" ] 
    samples = [x for x in samples if x != '']

    for sample in samples:

        # open json with submit information
        jFileName = BATCH_SCRIPT_DIR+sample+'.json'
        print 'Reading', jFileName
        with open(jFileName) as data_file:
            information = json.load(data_file)

        evts = information.keys()
        for evt in evts:
            status = information[evt]
            if status["submitted"] == True and status['finished'] == False:

                oFilePath = status['outputFile']
                print 'checking file', oFilePath

                tFile = ROOT.TFile.Open(oFilePath, "READ")
                tree = tFile.Get("Delphes")
                nEvents = tree.GetEntriesFast()

                print 'has', nEvents, 'events'

                if nEvents == 1000 or sample == 'mg_pp_tt_nlo':
                    print 'therefore finished'
                    information[evt]['finished'] = True

        # Update log of jobs
        with open(jFileName, 'w') as fp:
            json.dump(information, fp, sort_keys=True, indent=4)


                

if __name__ == "__main__":

    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("-v", "--verbose", help="Turn on verbose messages", action="store_true", default=False)
    args = parser.parse_args()
    verbose = args.verbose

    main(verbose)


