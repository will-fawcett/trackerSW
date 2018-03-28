#!/usr/bin/python
'''
Script to submit jobs to generate en-mass .pileup files (with many, 5000? pu events each) 
'''

from generalProductionSubmit import writeSubmissionHeader
import os
import time

# base dir
BASE_DIR = '/atlas/data4/userdata/wfawcett/delphes/pileup/'

# directory to store .pileup files
OUPUT_DIR = BASE_DIR + 'pileup/'

# directory to store .root files (and batch jobs and cmd files inside subdirectories)
PROCESS_DIR = BASE_DIR + 'production/'

# directory to store .sh files and .out files 
JOB_DIR = PROCESS_DIR + "jobs/"

# directory to store CMD files 
CMD_DIR = PROCESS_DIR + "cmd/"



#____________________________________________________________________________
def main(verbose):

    for seed in xrange(0, 1001):
        jobNumStr = '{0:04d}'.format(seed)
        jobName = 'pileup_'+jobNumStr
        #print jobName

        # write the cmd file
        cmdFile = CMD_DIR + jobName + '.cmd' 
        writeCMDfile(seed, cmdFile)

        # write a batch script 
        scriptFile = JOB_DIR + jobName+'.sh'
        writeSubmissionScript(scriptFile, jobName, cmdFile)

        # submit the job
        os.chdir(JOB_DIR)
        command = 'sbatch -p rhel6-veryshort {0}'.format(scriptFile)
        print command
        os.system(command)
        time.sleep(1)


#____________________________________________________________________________
def writeSubmissionScript(scriptFile, jobName, cmdFile):

    print 'SH file:', scriptFile
    ofile = open(scriptFile, 'w')
    writeSubmissionHeader(ofile, jobName, JOB_DIR) 

    # generate the minbias ROOT file
    outputFilePath = PROCESS_DIR+jobName+'.root'
    ofile.write('./build/readers/DelphesPythia8 cards/converter_card.tcl {0} {1}\n'.format(cmdFile, outputFilePath))

    ofile.write('\necho "Should have created ROOT file {0}"\n'.format(outputFilePath))
    ofile.write('echo "End of generate pileup with DelphesPythia8"\n')

    # convert to a binary file for faster access
    outputPileupPath = OUPUT_DIR + jobName+'.pileup'
    ofile.write('./build/converters/root2pileup {0} {1}\n'.format(outputPileupPath, outputFilePath)) 

    ofile.write('echo "Should have created PIULEUP file {0}"\n'.format(outputPileupPath))

    ofile.write("echo \"End.\"\n")
    ofile.write("date\n")
    ofile.close()



#____________________________________________________________________________
def writeCMDfile(seed, fileName):

    print 'CMD file:', fileName
    cmdFile = open(fileName, 'w')

    cmdFile.write('''! File: generatePileUp.cmnd
! This file contains commands to be read in for a Pythia8 run.
! Lines not beginning with a letter or digit are comments.
! Names are case-insensitive  -  but spellings-sensitive!
! The changes here are illustrative, not always physics-motivated.

! 1) Settings that will be used in a main program.
Main:numberOfEvents = 10000          ! number of events to generate
Main:timesAllowErrors = 3          ! abort run after this many flawed events

! 2) Settings related to output in init(), next() and stat().
Init:showChangedSettings = on      ! list changed settings
Init:showAllSettings = off         ! list all settings
Init:showChangedParticleData = on  ! list changed particle data
Init:showAllParticleData = off     ! list all particle data
Next:numberCount = 100            ! print message every n events
Next:numberShowLHA = 1             ! print LHA information n times
Next:numberShowInfo = 1            ! print event information n times
Next:numberShowProcess = 1         ! print process record n times
Next:numberShowEvent = 1           ! print event record n times
Stat:showPartonLevel = on          ! additional statistics on MPI
Random:setSeed = on
Random:setSeed = {0}

! 3) Beam parameter settings. Values below agree with default ones.
Beams:idA = 2212                   ! first beam, p = 2212, pbar = -2212
Beams:idB = 2212                   ! second beam, p = 2212, pbar = -2212
Beams:eCM = 100000.                 ! CM energy of collision

! 4a) Pick processes and kinematics cuts.
SoftQCD:all = on                   ! Allow total sigma = elastic/SD/DD/ND

! 4b) Other settings. Can be expanded as desired.
Tune:pp = 5                         ! use Tune 5'''.format(seed))


if __name__ == "__main__":

    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("-v", "--verbose", help="Turn on verbose messages", action="store_true", default=False)
    args = parser.parse_args()
    verbose = args.verbose

    main(verbose)


