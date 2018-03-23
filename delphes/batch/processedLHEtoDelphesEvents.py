#!/usr/bin/python
'''
Script to turn the procssed events (from LHE->delphes root) and put them through the detector simulation
essentially runs this command:
    ./DelphesROOT cards/delphes_card_CMS.tcl CMS_output.root events.root

- finds the samples that are "finished"
- creats a batch file to run the above command

- repeats for each pileup scenario (the hope is that there will be many jobs in the queue, so that the same file won't be being read by mor than one job -- not sure if this is a problem but don't know anyway)
'''

import json
from generalProductionSubmit import DATA_DIR, BATCH_SCRIPT_DIR, OUTPUT_DIR, LHE_DIR, CMD_DIR, getSampleList, writeSubmissionHeader


def main(verbose):

    pileupScenarios = [0, 200, 1000]

    # get list of samples from LHE dir
    samples = getSampleList(LHE_DIR)

    for pu in pileupScenarios:

        for sample in samples: 

            # find "finished" samples
            jFileName = BATCH_SCRIPT_DIR+sample+'.json'
            print 'Reading', jFileName
            with open(jFileName) as data_file:
                information = json.load(data_file)
            evts = information.keys()

            JOB_BASE_DIR = BATCH_SCRIPT_DIR + sample + '/'

            for evt in evts:
                if information[evt]['finished'] == True:

                    # Write jobFile
                    JOB_DIR = JOB_BASE_DIR + evt.replace('.lhe','') + '/'
                    JOB_FILE = JOB_DIR + evt.replace('lhe', 'sh')
                    #batchName = sample+"_"+str(jobCounter)
                    #jobCounter += 1 
                    print JOB_FILE
                    #writeSubmissionScript(JOB_FILE, batchName, cmdFile, outputName, JOB_DIR)


            print 'For', sample, 'there are {0} finished evt files'.format(len(finishedSamples)) 


def writeSubmissionScript():
    #ofile = open()
    pass

if __name__ == "__main__":

    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("-v", "--verbose", help="Turn on verbose messages", action="store_true", default=False)
    args = parser.parse_args()
    verbose = args.verbose

    main(verbose)


