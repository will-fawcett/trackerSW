#!/usr/bin/python
'''
Script to submit production of particles using LHE files as a starting point
'''

from submitPythia8Delphes import checkDir 
from glob import glob
import json 
import os
import time

DATA_DIR = "/atlas/data4/userdata/wfawcett/delphes/"
BATCH_SCRIPT_DIR = DATA_DIR + "particleProductionBatch/"
OUTPUT_DIR = DATA_DIR + "particleProductionResults/"
LHE_DIR = DATA_DIR + "lhe/"
CMD_DIR = DATA_DIR + "pythiaControl/"

#____________________________________________________________________________
def getSampleList(path):

    samples = [x[0].split('/')[-1] for x in os.walk(path)] # [ "mg_pp_hh",  "mg_pp_tth",  "mg_pp_tt_nlo" ] 
    samples = [x for x in samples if x != '']
    return samples

#____________________________________________________________________________
def main(verbose):

    NJOBS_PER_SAMPLE = 100


    # get list of samples from LHE dir
    samples = getSampleList(LHE_DIR)


    for sample in samples:

        print 'Processing sample', sample
    
        # open json with submit information
        jFileName = BATCH_SCRIPT_DIR+sample+'.json'
        print 'Reading', jFileName
        with open(jFileName) as data_file:
            information = json.load(data_file)


        # Select NJOBS_PER_SAMPLE that haven't already been submitted 
        evtFiles = sorted(information.keys())
        evtsToProcess = []
        counter = 0
        for f in evtFiles:
            if information[f]['submitted'] == False:
                evtsToProcess.append(f)
                if(len(evtsToProcess) >= NJOBS_PER_SAMPLE): break
        sorted(evtsToProcess)
        print 'selected {0} files to process'.format(len(evtsToProcess))

        # write batch script
        JOB_BASE_DIR = BATCH_SCRIPT_DIR + sample + '/'
        jobCounter = 0
        for evt in evtsToProcess:

            # Create subdir to store the .sh file, as well as the text output 
            JOB_DIR = JOB_BASE_DIR + evt.replace('.lhe','') + '/'
            checkDir(JOB_DIR, False)


            # extact relevant job info
            cmdFile = information[evt]["cmdPath"]
            outputName = OUTPUT_DIR+sample+ '/'+evt.replace('lhe', 'root')

            # Write the job file
            JOB_FILE = JOB_DIR + evt.replace('lhe', 'sh')
            batchName = sample+"_"+str(jobCounter)
            jobCounter += 1 
            writeSubmissionScript(JOB_FILE, batchName, cmdFile, outputName, JOB_DIR)

            # submit job
            os.chdir(JOB_DIR)
            command = 'sbatch -p rhel6-short {0}'.format(JOB_FILE)
            print command
            os.system(command)
            time.sleep(1)

            # update the dictionary
            unixTime = str(int(time.time()))
            tempInfo = information[evt]
            information[evt] = {
                    "submitted" : True,
                    "lhePath" : tempInfo["lhePath"],
                    "cmdPath" : tempInfo["cmdPath"],
                    "timeSubmitted" : unixTime,
                    "batchJobFile" : JOB_FILE,
                    "finished" : False,
                    "outputFile" : outputName
                    }

    
        # Update log of jobs
        with open(jFileName, 'w') as fp:
            json.dump(information, fp, sort_keys=True, indent=4)

#____________________________________________________________________________
def writeSubmissionScript(scriptName, batchName, cmdFile, outputName, jobDir):

    print 'Writing submission script', scriptName
    ofile = open(scriptName, "w") 

    writeSubmissionHeader(ofile, batchName, jobDir)

    ofile.write("./build/readers/DelphesPythia8 cards/gen_card.tcl {0} {1}\n".format(cmdFile, outputName)) 
    ofile.write("echo \"End.\"\n")
    ofile.write("date\n")
    ofile.close()
#____________________________________________________________________________
def writeSubmissionHeader(ofile, batchName, jobDir):

    ofile.write("#!/bin/bash\n") # interpereter directive  

    # SLURM directives
    ofile.write('#SBATCH --job-name="{0}"\n'.format(batchName))
    #ofile.write('#SBATCH --partition=rhel6-short\n')
    ofile.write('#SBATCH --workdir="{0}"\n'.format(jobDir)) # default to PWD from where the job was submitted
    ofile.write('#SBATCH --output={0}%j.o\n'.format(batchName))
    ofile.write('#SBATCH --error={0}%j.o\n'.format(batchName))
    ofile.write('#SBATCH --mem=6GB\n')

    ofile.write("hostname\n")
    ofile.write("date\n")

    ofile.write("cd /atlas/users/wfawcett/fcc/delphes\n")
    ofile.write("source setup.sh\n")

#____________________________________________________________________________
if __name__ == "__main__":

    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("-v", "--verbose", help="Turn on verbose messages", action="store_true", default=False)
    args = parser.parse_args()
    verbose = args.verbose

    main(verbose)
