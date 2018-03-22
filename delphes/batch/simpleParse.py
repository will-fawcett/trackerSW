#!/usr/bin/python

from submitPythia8Delphes import checkDir 

import time
import datetime
import os
import sys

BATCH_DIR = "/atlas/data4/userdata/wfawcett/delphes/batch/"
CODE_DIR  = "/atlas/users/wfawcett/fcc/delphes/"

unixTime = time.time()
CAMPAIGN = str(int(unixTime))
USER     = os.environ['USER']

def main(command, name):

    print 'Command to be submitted', command
    jobName = 'cmdParse'

    # create a directory for the batch command
    jobDir = BATCH_DIR + '{0}_{1}_{2}/'.format(CAMPAIGN, jobName, name)
    checkDir(jobDir)

    # create a submit script 
    writeSubmissionScript(command, jobDir, CAMPAIGN, name) 

    # change to job dir 
    print 'cd', jobDir
    os.chdir(jobDir)

    # submit the job to the batch 
    queue = "rhel6-medium" 
    command = 'sbatch -p {0} submit.sh'.format(queue)
    print command
    os.system(command)

def writeSubmissionScript(command, jobDir, CAMPAIGN, name):

    ofile = open(jobDir+'submit.sh','w')
    ofile.write("#!/bin/bash\n") # interpereter directive  

    batchName = '{0}_cmdParse_{1}'.format(name, CAMPAIGN) 

    # SLURM directives
    ofile.write('#SBATCH --job-name="{0}"\n'.format(batchName))
    ofile.write('#SBATCH --partition=rhel6-medium\n')
    ofile.write('#SBATCH --workdir="{0}"\n'.format(jobDir)) # default to PWD from where the job was submitted
    ofile.write('#SBATCH --output={0}%j.o\n'.format(batchName))
    ofile.write('#SBATCH --error={0}%j.o\n'.format(batchName))

    # setup 
    ofile.write("hostname\n")
    ofile.write("date\n")
    ofile.write("cd /atlas/users/wfawcett/fcc/delphes\n")
    ofile.write("source setup.sh\n")

    # the command to submit
    ofile.write(command+'\n')
    ofile.write("echo \"End.\"\n")
    ofile.write("date\n")
    ofile.close()
    
if __name__ == "__main__":

    from optparse import OptionParser
    parser = OptionParser()
    parser.add_option("-c", "--command", action="store", type="string", help="The command to submit to the batch script")
    parser.add_option("-n", "--name", action="store", type="string", help="The name of the job, something to id it")
    if len(sys.argv) == 1:
        parser.print_help()
        sys.exit(0)

    options, args = parser.parse_args()
    option_dict = dict( (k, v) for k, v in vars(options).iteritems() if v is not None)
    main(**option_dict)
