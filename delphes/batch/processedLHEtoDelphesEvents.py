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
from generalProductionSubmit import DATA_DIR, OUTPUT_DIR, LHE_DIR, CMD_DIR, getSampleList, writeSubmissionHeader
import time

unixTime = time.time()
CAMPAIGN = str(int(unixTime))
USER     = os.environ['USER']

CAMPAIGN = "TEST"

def main(verbose):

    pileupScenarios = [0, 200, 1000]

    # get list of samples from LHE dir
    samples = getSampleList(LHE_DIR)

    # Create a new campaign dir for all of the samples that are needed from this campaign
    CAMPAIGN_DIR = "/atlas/data4/userdata/wfawcett/delphes/processedLHE/"+CAMPAIGN+"/"
    checkDir(CAMPAIGN_DIR)

    jobCounter = 0 

    for pu in pileupScenarios:

        for sample in samples: 

            # Create a directory for the all batch scripts and .sh files to go into 
            BATCH_SCRIPT_DIR = CAMPAIGN_DIR + sample + "_" + str(pu) + '/'
            print BATCH_SCRIPT_DIR

            checkDir(BATCH_SCRIPT_DIR)

            # Create a directory for all of the processed samples to go into 
            JOB_OUTPUT_DIR = CAMPAIGN_DIR + sample + "_" + str(pu) + '/'

            # find "finished" samples
            jFileName = BATCH_SCRIPT_DIR+sample+'.json'
            print 'Reading', jFileName
            with open(jFileName) as data_file:
                information = json.load(data_file)
            evts = information.keys()

            #JOB_BASE_DIR = BATCH_SCRIPT_DIR + sample + '/'

            # For each input file to process, write a .sh file inside BATCH_SCRIPT_DIR, and direct the output ROOT file to JOB_OUTPUT_DIR 
            for evt in evts:
                if information[evt]['finished'] == True:

                    # Select the right delphes card (specific to pileup)  
                    DELPHES_CARD = "cards/triplet/FCChh_HitsToTracks_PileUp{0}.tcl".format(pu)

                    # input file path
                    inputFile = information[evt]["FILE"]

                    # output file path
                    outputFile = JOB_OUTPUT_DIR + evt.replace('lhe', 'root')
                    

                    # Write jobFile
                    #JOB_DIR = JOB_BASE_DIR + evt.replace('.lhe','') + '/'
                    #JOB_FILE = JOB_DIR + evt.replace('lhe', 'sh')
                    JOB_FILE = BATCH_SCRIPT_DIR + "{0}".format(evt.replace('.lhe',''))
                    batchName = sample+"_"+str(jobCounter)
                    jobCounter += 1 
                    print JOB_FILE
                    writeSubmissionScript(JOB_FILE, batchName, DELPHES_CARD, inputFile, outputFile)


            #print 'For', sample, 'there are {0} finished evt files'.format(len(finishedSamples)) 


def writeSubmissionScript(JOB_FILE, batchName, DELPHES_CARD, inputName, outputName):
    ofile = open(JOB_FILE, 'w')

    # Write interpreter and slurm directives
    writeSubmissionHeader(ofile)

    ofile.write("./DelphesROOT {0} {1} {2}\n".format(tcl_card, outputName, inputName) )

    ofile.write("echo \"End.\"\n")
    ofile.write("date\n")
    ofile.close()



if __name__ == "__main__":

    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("-v", "--verbose", help="Turn on verbose messages", action="store_true", default=False)
    args = parser.parse_args()
    verbose = args.verbose

    main(verbose)


