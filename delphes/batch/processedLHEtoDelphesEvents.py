#!/usr/bin/python
'''
Principally the "last step" in generating events 

Script to turn the procssed events (from LHE->delphes root) and put them through the detector simulation
essentially runs this command:
    ./DelphesROOT cards/delphes_card_CMS.tcl CMS_output.root events.root

- finds the samples that are "finished"
- creats a batch file to run the above command

- repeats for each pileup scenario (the hope is that there will be many jobs in the queue, so that the same file won't be being read by mor than one job -- not sure if this is a problem but don't know anyway)
'''

import json
from generalProductionSubmit import DATA_DIR, OUTPUT_DIR, LHE_DIR, CMD_DIR, getSampleList, writeSubmissionHeader
from submitPythia8Delphes import checkDir
import time
import os

unixTime = time.time()
CAMPAIGN = str(int(unixTime))
USER     = os.environ['USER']


#CAMPAIGN = "TEST"


JSON_DIR = DATA_DIR + "particleProductionBatch/"

def main(verbose):

    pileupScenarios = [200]
    pileupScenarios = [1000]
    pileupScenarios = [0, 200, 1000]

    # get list of samples from LHE dir
    samples = getSampleList(LHE_DIR) 
    samples += ['py8_pp_minbias']
    samples.remove('mg_pp_tt_nlo') # remove this sample, for pT(top) > 2.5 TeV (quite a lot :p)
    #samples = ['mg_pp_hh']
    #CAMPAIGN = "1522403805"
    #CAMPAIGN = "1522404983"

    # Create a new campaign dir for all of the samples that are needed from this campaign
    CAMPAIGN_DIR = "/atlas/data4/userdata/wfawcett/delphes/processedLHE/"+CAMPAIGN+"/"
    checkDir(CAMPAIGN_DIR)

    jobCounter = 0 

    for pu in pileupScenarios:
        for sample in samples: 

            # Create a directory for all of the processed samples to go into 
            JOB_OUTPUT_DIR = CAMPAIGN_DIR + sample + "_pu" + str(pu) + '/'
            checkDir(JOB_OUTPUT_DIR, False)

            # Create a directory for the all batch scripts and .sh files to go into 
            BATCH_SCRIPT_DIR = CAMPAIGN_DIR + sample + "_pu" + str(pu) + '/jobs/'
            checkDir(BATCH_SCRIPT_DIR, False)
            print BATCH_SCRIPT_DIR

            # copy the resolution .tcl to the BATCH_SCRIPT_DIR
            copyer = 'cp /atlas/users/wfawcett/fcc/trackerSW/delphes/cards/tripletFCCresolutions_*0mm.tcl {0}'.format(BATCH_SCRIPT_DIR)
            print copyer
            os.system(copyer)

            # find "finished" samples
            jFileName = JSON_DIR+sample+'.json'
            print 'Reading', jFileName
            with open(jFileName) as data_file:
                information = json.load(data_file)
            evts = information.keys()
            evts = sorted(evts)

            #JOB_BASE_DIR = BATCH_SCRIPT_DIR + sample + '/'

            # For each input file to process, write a .sh file inside BATCH_SCRIPT_DIR, and direct the output ROOT file to JOB_OUTPUT_DIR 
            sampleCounter = -1
            for evt in evts:
                if information[evt]['finished'] == True:

                    if sampleCounter > 50 and sample == 'py8_pp_minbias':
                        continue
                    sampleCounter +=1
                    print 'submitting for', evt

                    # Select the right delphes card (specific to pileup)  
                    BASE_DELPHES_CARD = "cards/triplet/FCChh_HitsToTracks_PileUp{0}.tcl".format(pu)

                    # input file path
                    inputFile = information[evt]["outputFile"]

                    # output file path
                    outputFile = JOB_OUTPUT_DIR + evt.replace('.lhe', '_pu{0}.root'.format(pu))
                    
                    # Directory in which the job will run, and where to store the custom delphes card
                    JOB_DIR = BATCH_SCRIPT_DIR
                    jobNumber = int(evt.split('_')[-1].split('.')[0])
                    DELPHES_CARD = copyDelphesCard(BASE_DELPHES_CARD, JOB_DIR, jobNumber)

                    # Write jobFile
                    JOB_FILE = JOB_DIR + "{0}".format(evt.replace('.lhe','.sh'))
                    batchName = sample+"_"+str(jobCounter)
                    jobCounter += 1 
                    print '\tWriting batch job script', JOB_FILE
                    writeSubmissionScript(JOB_FILE, batchName, DELPHES_CARD, inputFile, outputFile, BATCH_SCRIPT_DIR)
                    
                    # select queue
                    queue = 'veryshort'
                    if pu == 200:
                        queue = 'short'
                    elif pu == 1000:
                        queue = 'medium'

                    # submit job
                    os.chdir(JOB_DIR)
                    command = 'sbatch -p rhel6-{0} {1}'.format(queue, JOB_FILE)
                    print command
                    os.system(command)
                    time.sleep(1)
                    print ''


def copyDelphesCard(inputCard, outputDir, jobNumber):
    '''
    Copy an input delphes card, but modify the pileup file used inside (so a unique pileup file is used each time)
    '''

    # read in the input card
    baseFileName = '/atlas/users/wfawcett/fcc/delphes/'+inputCard
    #print 'reading', baseFileName
    lines = [l for l in open(baseFileName, 'r').readlines()]

    # check pileupfile exists
    newFile = '/atlas/data4/userdata/wfawcett/delphes/pileup/pileup/pileup_{0:04d}.pileup'.format(jobNumber)
    #print newFile
    if not os.path.exists(newFile):
        print 'WARNING: file {0} does not exist, EXIT.'
        print newFile
        sys.exit()

    # create the new delphes card
    oFileName = outputDir + inputCard.split('/')[-1].replace('.tcl','_{0:04d}.tcl'.format(jobNumber))
    print '\tWriting delphes card: ', oFileName
    ofile = open(oFileName, 'w')
    for line in lines:
        if 'PileUpFile' in line:
            line = '  set PileUpFile {0}\n'.format(newFile) 
        ofile.write(line)
    ofile.close()

    return oFileName




def writeSubmissionScript(JOB_FILE, batchName, DELPHES_CARD, inputName, outputName, BATCH_SCRIPT_DIR):
    ofile = open(JOB_FILE, 'w')

    
    # Write interpreter and slurm directives
    writeSubmissionHeader(ofile, batchName, BATCH_SCRIPT_DIR)

    ofile.write("./build/readers/DelphesROOT {0} {1} {2}\n".format(DELPHES_CARD, outputName, inputName) )

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


