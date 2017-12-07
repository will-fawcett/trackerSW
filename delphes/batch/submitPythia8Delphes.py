import time
import datetime
import os
import sys

# Detect location 
isGeneva = False
isLXplus = False
if os.environ['isLXplus'] == 'True':
    isLXplus = True
if os.environ['isGeneva'] == 'True':
    isGeneva = True

    
# Create directory structure in data 
if isLXplus:
    BASE_DIR = '/afs/cern.ch/work/w/wfawcett/private/geneva/delphes/'
    CODE_DIR = ''
if isGeneva:
    #BASE_DIR = '/beegfs/users/wfawcett/delphes/'
    BASE_DIR = '/atlas/data4/userdata/wfawcett/delphes/'
    CODE_DIR = '/atlas/users/wfawcett/fcc/delphes/'

JOB_DIR  = BASE_DIR+'batch/'
OUTPUT_DIR = BASE_DIR+'samples/'

unixTime = time.time()
CAMPAIGN = str(int(unixTime))
USER     = os.environ['USER']

#____________________________________________________________________________
def main():

    nEvents    = 1000
    randomSeed = 62
    pileup     = 200 # 0 | 200 | 1000
    pileup     = 0 # 0 | 200 | 1000

    process = 'pileup' # maybe don't need this? 
    process = 'MinBias' # MinBias | ttbar 
    process = 'ttbar' # MinBias | ttbar 

    if not process.lower() in ['ttbar', 'minbias']:
        print 'ERROR: process {0} not defined'.format(process)
        sys.exit()

    # estimate job time based on nevents 
    jobDemand = nEvents*(pileup+1)
    print 'Job demands: Nevents {0}\t pileup {1}\t demand\t{2}'.format(nEvents, pileup, jobDemand)

    # Identifier for this submission
    identifier = '{0}_mu{1}_s{2}_n{3}'.format(process, pileup, randomSeed, nEvents)

    # Create directory for all batch scripts
    jobDirName = JOB_DIR+'{0}_{1}/'.format(CAMPAIGN, identifier)
    checkDir(jobDirName)

    # Create Pythia8 card
    pythiaCardName = writePythia8Card(jobDirName, nEvents, randomSeed, process)

    # Write batch submission script 
    outputSampleDir = OUTPUT_DIR+'{0}/'.format(process)
    submission = open(jobDirName+'submit.sh', 'w')
    writeSubmissionScript(submission, outputSampleDir, identifier, pythiaCardName, pileup)

    # change to jobDir
    print 'cd', jobDirName
    os.chdir(jobDirName)
    
    # select job queue 
    if isLXplus:
        print 'LXplus environment detected'
        queue = '1nh'
        if jobDemand > 3000:
            queue = '8nh'
        if jobDemand > 25000: 
            queue = '1nd'
        if jobDemand > 10**6:
            queue == '2nd'
            print 'Greater than 1M events ... are you sure you want to do this?!'
            yesno = raw_input("y/n? ")
            if yesno != "y": 
                sys.exit("Exiting, try again with a new name")
    elif isGeneva:
        print 'Geneva environment detected'
        if jobDemand > 0 and  jobDemand < 30000:
            queue = 'veryshort' 
        elif jobDemand > 30000 and jobDemand < 100000:
            queue = 'short' 
        elif jobDemand > 100000 and jobDemand < 300000:
            queue = 'medium'
        elif jobDemand > 300000 and jobDemand < 10**7:
            queue = 'long'
        else:
            queue = 'production' 
        
    else:
        print 'Not using either Geneva or Lxplus cluster. Exit'
        sys.exit()

    # Create the submisson command
    batchName = 'py8_{0}'.format(identifier) 
    if isLXplus:
        command = 'bsub -q {0} -J {1} < submit.sh'.format(queue, batchName)
    if isGeneva:
        command = 'qsub -q {0} -N {1} -e {2} -o {3} submit.sh'.format(queue, batchName, jobDirName+batchName+'.err', jobDirName+batchName+'.out')
    
    # Add submit command to script
    submission.write('#Sumbitted with command: {0}\n'.format(command))
    submission.close()

    # Submit the batch job
    print command
    os.system(command)

    '''
    8nm (8 minutes)
    1nh (1 hour)
    8nh
    1nd (1day)
    2nd
    1nw (1 week)
    2nw
    '''


#____________________________________________________________________________
def writeSubmissionScript(submission, outputSampleDir, identifier, pythiaCardName, pileup):

    checkDir(outputSampleDir, False)
    outputSampleName = outputSampleDir + '{0}.root'.format(identifier)
    
    
    # tracking
    submission.write('hostname\n')
    submission.write('date\n')

    submission.write('cd '+CODE_DIR+'\n')
    submission.write('source '+CODE_DIR+'setup.sh\n')
    if pileup == 0:
        submission.write('./DelphesPythia8 cards/triplet/FCChh.tcl {0} {1}\n'.format(pythiaCardName, outputSampleName)) 
    elif pileup == 200:
        submission.write('./DelphesPythia8 cards/triplet/FCChh_PileUp.tcl {0} {1}\n'.format(pythiaCardName, outputSampleName)) 
    



#____________________________________________________________________________
def writePythia8Card(jobDirName, nEvents, seed, process):

    # Open file
    pythiaCardName = jobDirName+'generateFile.cmnd'
    ofile = open(pythiaCardName, 'w')

    lines = []
    lines.append('! File: generateFile.cmnd')
    lines.append('! Generated automatially: {0} = {1}'.format(CAMPAIGN, datetime.datetime.now() ) )
    lines.append('! User: {0}'.format(USER))
    lines.append('! Process {0}'.format(process))

    # nEvents
    lines.append('\n! 1) Settings that will be used in a main program.')
    lines.append('Main:numberOfEvents = {0}          ! number of events to generate'.format(nEvents))
    lines.append('Main:timesAllowErrors = 3          ! abort run after this many flawed events')

    lines.append('\n! 2) Settings related to output in init(), next() and stat().')
    lines.append('Init:showChangedSettings = on      ! list changed settings')
    lines.append('Init:showAllSettings = off         ! list all settings')
    lines.append('Init:showChangedParticleData = on  ! list changed particle data')
    lines.append('Init:showAllParticleData = off     ! list all particle data')
    lines.append('Next:numberCount = 1000            ! print message every n events')
    lines.append('Next:numberShowLHA = 1             ! print LHA information n times')
    lines.append('Next:numberShowInfo = 1            ! print event information n times')
    lines.append('Next:numberShowProcess = 1         ! print process record n times')
    lines.append('Next:numberShowEvent = 1           ! print event record n times')
    lines.append('Stat:showPartonLevel = on          ! additional statistics on MPI')

    # Random seed 
    lines.append('\nRandom:setSeed = on')
    lines.append('Random:setSeed = {0}'.format(seed))

    # Beam parameters
    lines.append('\n! 3) Beam parameter settings. Values below agree with default ones.')
    lines.append('Beams:idA = 2212                   ! first beam, p = 2212, pbar = -2212')
    lines.append('Beams:idB = 2212                   ! second beam, p = 2212, pbar = -2212')
    lines.append('Beams:eCM = 100000.                 ! CM energy of collision')

    # Process ! 
    if process.lower() == 'minbias':
        lines.append('\n! 4a) Pick processes and kinematics cuts.')
        lines.append('SoftQCD:all = on                   ! Allow total sigma = elastic/SD/DD/ND')
        lines.append('! 4b) Other settings. Can be expanded as desired.')
        lines.append('Tune:pp = 5                         ! use Tune 5')
    if process.lower() == 'ttbar':
        lines.append('! 4) Settings for the hard-process generation.')
        lines.append('Top:gg2ttbar = on                  ! g g -> t tbar')
        lines.append('Top:qqbar2ttbar = on               ! q qbar -> t tbar')

        lines.append('! 5) Switch on/off the key event generation steps.')
        lines.append('PartonLevel:MPI = on              ! no multiparton interactions')
        lines.append('PartonLevel:ISR = on              ! no initial-state radiation')
        lines.append('PartonLevel:FSR = on              ! no final-state radiation')
        lines.append('HadronLevel:Hadronize = on        ! no hadronization')
        lines.append('HadronLevel:Decay = on            ! no decays')

    for line in lines:
        ofile.write(line+'\n')

    return pythiaCardName


#____________________________________________________________________________
def checkDir(dir, CHECK=True):

    # if output directory does not exist, then create it
    if not os.path.isdir(dir):
        print 'Creating directory', dir
        os.mkdir(dir)
        os.system('chmod g+w '+dir)
    elif CHECK:
        print dir, "already exists... are you sure you want to overwrite it?",
        yesno             = raw_input("y/n? ")
        if yesno != "y": sys.exit("Exiting, try again with a new name")
    else:
        print dir, "already exists and will be overwritten"

#____________________________________________________________________________
if __name__ == "__main__":
    main()
