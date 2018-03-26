#!/usr/bin/python
from glob import glob
import json
import os
'''
One-use script (in principle) (or at least, one use per set of LHE files)
to generate json file to store information on the processing of LHE -> particles
'''

def main(verbose):

    DATA_DIR = "/atlas/data4/userdata/wfawcett/delphes/"
    BATCH_SCRIPT_DIR = DATA_DIR + "particleProductionBatch/"
    OUTPUT_DIR = DATA_DIR + "particleProductionResults/"
    LHE_DIR = DATA_DIR + "lhe/"
    CMD_DIR = DATA_DIR + "pythiaControl/"

    # get list of samples from LHE dir
    samples = [x[0].split('/')[-1] for x in os.walk(LHE_DIR)] # [ "mg_pp_hh",  "mg_pp_tth",  "mg_pp_tt_nlo" ] 
    samples = [x for x in samples if x != '']
    print samples

    for sample in samples:
        lheFiles = glob(LHE_DIR+sample+"/*.lhe")
        store = {} 
        for evt in lheFiles:
            name = evt.split('/')[-1]
            
            store[name] = {
                    "submitted" : False, 
                    "lhePath" : evt, 
                    "cmdPath" : CMD_DIR+sample+'/'+name.replace('lhe','cmd'),
                    "timeSubmitted" : 0,
                    "batchJobFile" : "",
                    "finished" : False,
                    "outputFile" : ""
                    }

        storeName = BATCH_SCRIPT_DIR + sample + '.json'
        print 'writing', storeName
        with open(storeName, 'w') as fp:
            json.dump(store, fp, sort_keys=True, indent=4)


if __name__ == "__main__":

    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("-v", "--verbose", help="Turn on verbose messages", action="store_true", default=False)
    args = parser.parse_args()
    verbose = args.verbose

    main(verbose)


