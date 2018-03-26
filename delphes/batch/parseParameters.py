#!/usr/bin/python

from submitPythia8Delphes import writePythia8Card, checkDir 

import time
import datetime
import os
import sys

BATCH_DIR = "/atlas/data4/userdata/wfawcett/delphes/batch/"
CODE_DIR  = "/atlas/users/wfawcett/fcc/delphes/"

unixTime = time.time()
CAMPAIGN = str(int(unixTime))
USER     = os.environ['USER']

def main(inputDelphesCard, outputFileName, configFile):

    # Some defaults
    nEvents = 1000 
    process = 'ttbar'  
    randomSeed = 20 

    # Print input configuration 
    print 'Input delphes card:', inputDelphesCard
    print 'Output filename:', outputFileName 
    print 'config file:', configFile

    # Parse specific input
    jobName = inputDelphesCard.split('/')[-1].split('.')[0]

    # Create a directory for the specific batch job 
    jobDir = BATCH_DIR + '{0}_{1}/'.format(CAMPAIGN, jobName)
    checkDir(jobDir)

    # Create pythia8 card
    pythiaCardName = writePythia8Card(jobDir, nEvents, randomSeed, process)

    # Write batch submission script 
    batchName = "py8_"+jobName 
    writeSubmissionScript(jobDir, inputDelphesCard, pythiaCardName, outputFileName, batchName)

    # change to job dir 
    print 'cd', jobDir
    os.chdir(jobDir)

    # Select a job queue (based on time estimate)
    queue = "short" 
    queue = "rhel6-short"
    queue = "rhel6-medium" 

    # Submit the batch job 
    #command = 'qsub -q {0} -N {1} -e {2} -o {3} submit.sh'.format(queue, batchName, jobDir+batchName+'.err', jobDir+batchName+'.out')
    command = 'sbatch -p {0} submit.sh'.format(queue)
    print command
    os.system(command)



def writeSubmissionScript(jobDir, inputDelphesCard, pythiaCardName, outputFileName, batchName):

    scriptName = jobDir + "submit.sh"
    print 'Writing submission script', scriptName
    ofile = open(scriptName, "w") 
    ofile.write("#!/bin/bash\n") # interpereter directive  

    # SLURM directives
    ofile.write('#SBATCH --job-name="{0}"\n'.format(batchName))
    ofile.write('#SBATCH --partition=rhel6-short\n')
    ofile.write('#SBATCH --workdir="{0}"\n'.format(jobDir)) # default to PWD from where the job was submitted
    ofile.write('#SBATCH --output={0}%j.o\n'.format(batchName))
    ofile.write('#SBATCH --error={0}%j.o\n'.format(batchName))
    ofile.write('#SBATCH --mem=6GB\n')

    ofile.write("hostname\n")
    ofile.write("date\n")

    ofile.write("cd /atlas/users/wfawcett/fcc/delphes\n")
    ofile.write("source setup.sh\n")

    # remove output file
    ofile.write("rm {0}\n".format(outputFileName))

    ofile.write("./build/readers/DelphesPythia8 {0} {1} {2}\n".format(inputDelphesCard, pythiaCardName, outputFileName)) 
    ofile.write("echo \"End.\"\n")
    ofile.write("date\n")
    ofile.close()



if __name__ == "__main__":

    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("-i", "--inputCard", help="Input Delphes card")
    parser.add_argument("-o", "--outputFileName", help="Output file name") 
    parser.add_argument("-c", "--configFile", help="Pythia8 config file") 

    #parser.add_argument("-v", "--verbose", help="Turn on verbose messages", action="store_true", default=False)
    args = parser.parse_args()
    #verbose = args.verbose
    inputCard = args.inputCard
    configFile = args.configFile
    outputFileName = args.outputFileName

    main(inputCard, outputFileName, configFile)
