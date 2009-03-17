#!/usr/bin/env python

import os, sys, re
import glob
import imp
import time
import eups
import lsst.afw.image as afwImage
import lsst.afw.math as afwMath
import lsst.pex.policy as pexPolicy
import lsst.pex.logging as pexLog
import lsst.daf.base as dafBase
import lsst.ctrl.events as ctrlEvents
from lsst.ctrl.dc3pipe.MetadataStages import transformMetadata, validateMetadata

import lsst.pex.logging as logging

# Import EventFromInputfile from eventFromFitsfile.py so that we do not have to
# re-write that one. We do not use the imputil modules since it is deprecated as
# of Python 2.6 and removed in Python 3.0.
# From http://docs.python.org/3.0/library/imp.html
# Fast path: see if the module has already been imported.
if('eventFromFitsfile' in sys.modules):
    import eventFromFitsfile
else:
    thisDir = this_dir = os.path.dirname(os.path.realpath(__file__))
    fp, pathname, description = imp.find_module('eventFromFitsfile', [thisDir,])
try:
    eventFromFitsfile = imp.load_module('eventFromFitsfile', fp, pathname, 
                                        description)
finally:
    # Since we may exit via an exception, close fp explicitly.
    if fp:
        fp.close()



# Constants
EXP_TIME = 15.
SLEW_TIME = 5.
ROOT_DIR = '/lsst/images/repository/raw'
SUBSETS = ['ALL', 'D1', 'D2', 'D3', 'D4']




# Verbosity/logging.
Verbosity = 4
logging.Trace_setVerbosity('dc3pipe', Verbosity)



def EventFromInputSubsets(subsets, 
                          datatypePolicy, 
                          expTime=15,
                          slweTime=5,
                          rootTopicName='triggerImageprocEvent', 
                          hostName='lsst8.ncsa.uiuc.edu'):
    """
    Generate events for the IPSD (and MOPS) pipeline by extracting the relevant 
    information from the FITS files in the standard DC3 CFHT subdirectories.

    Users specify whether they want events generated for all fields or only for 
    a subset. In the latter case, they can specify the name of the subset: D1 
    through D4. Multiple subset can be specified as a space separated list in 
    quotes (e.g. "D1 D3"). 'ALL' is shorthand for ['D1', 'D2', 'D3', 'D4'].

    A second required parameter is the path to the data policy file for the 
    input FITS files.

    The two optional parameters are the exposure time of each exposure in a 
    visit (assumed constant) and the average slew time of the telescope. Both 
    are in seconds. The default to 15 seconds and 5 seconds respecively.

    The script sends one event for the first visit exposure, waits <exp time> 
    sec and then sends an event for the second exposure. At that point, it waits
    (<exp time> + <slew time>) sec before passing to the next visit.
    
    @param subsets: list of subset names (e.g. ['D1', 'D2']). 'ALL' is shorthand
           for ['D1', 'D2', 'D3', 'D4'].
    @param datatypePolicy: Policy file for the input data.
    @param expTime: assume each exposure in a visit is expTime long (defualts to
           15 seconds for DC3). expTime is in seconds.
    @param slewTime: assume an average slew time of slewTime seconds (defualts 
           to 5 seconds for DC3). slewTime is in seconds.
    @param rootTopicName: root name for the event's topic. The final topic will 
           be rootTopicName+'0' or rootTopicName+'1' depending on whether the
           event refers to the first or second image of the visit.
    hostName: hostname of the event broker.
    
    @return None
    """
    # Create a metadata policy object.
    dc3pipeDir = eups.productDir('ctrl_dc3pipe')
    metadataPolicy = pexPolicy.Policy.createPolicy(os.path.join(dc3pipeDir, 
                        'pipeline', 'dc3MetadataPolicy.paf'))
    
    # Covenience function.
    def sendEvent(f):
        return(eventFromFitsfile.EventFromInputfile(f, 
                                                    datatypePolicy, 
                                                    metadataPolicy,
                                                    rootTopicName, 
                                                    hostName))
    
    if('ALL' in subsets):
        subsets = ['D1', 'D2', 'D3', 'D4']
    
    for subset in subsets:
        dirName = os.path.join(ROOT_DIR, subset)
        
        # Get the list of amp FITS files in each dir.
        fileList0 = glob.glob(os.path.join(dirName, '*', '0', '*.fits'))
        fileList1 = glob.glob(os.path.join(dirName, '*', '1', '*.fits'))
        
        # Simple sanity check.
        if(len(fileList0) != len(fileList1)):
            pexLog.Trace('dc3pipe.eventfrominputfilelist', 1, 
                         'Skipping %s: wrong file count in 0 and 1' \
                         %(os.path.dirname(fileList0)))
            continue
        
        # Now we just trust that the i-th file in 0 corresponds to the i-th file
        # in 1... Fortunately, we only need to send one event per image 
        # directory, since all images there are one MEF split into individual 
        # amps.
        sendEvent(fileList0[0])
        # Sleep some.
        time.sleep(expTime)
        # Next event.
        sendEvent(fileList1[0])
        # Sleep expTime + slewTime.
        time.sleep(expTime + slewTime)
    return
    



if __name__ == "__main__":
    import sets
    
    USAGE = '''
usage: eventGeneratorForDC3.py <D1|D2|D3|D4|ALL> <policy_file> [<exp time>] [<slew time>]
    
Generate events for the IPSD (and MOPS) pipeline by extracting the relevant 
information from the FITS files in the standard DC3 CFHT subdirectories.

Users specify whether they want events generated for all fields or only for a
subset. In the latter case, they can specify the name of the subset: D1 through
D4. Multiple subset can be specified as a space separated list in quotes (e.g.
"D1 D3"). 'ALL' is shorthand for ['D1', 'D2', 'D3', 'D4'].

A second required parameter is the path to the data policy file for the input
FITS files.

The two optional parameters are the exposure time of each exposure in a visit
(assumed constant) and the average slew time of the telescope. Both are in 
seconds. The default to 15 seconds and 5 seconds respecively.

The script sends one event for the first visit exposure, waits <exp time> sec 
and then sends an event for the second exposure. At that point, it waits 
(<exp time> + <slew time>) sec before passing to the next visit.
'''
    
    if(len(sys.argv) not in (3, 4, 5)):
        sys.stderr.write(USAGE)
        sys.exit(1)
    
    subsets = [x.upper() for x in sys.argv[1].split()]
    # Make sure thet the subsets make sense.
    if(not sets.Set(subsets).issubset(sets.Set(SUBSETS))):
        sys.stderr.write('subsets must be a combination of %s\n' \
                         %(', '.join(SUBSETS)))
        sys.stderr.write(USAGE)
        sys.exit(2)
    
    datatypePolicy = pexPolicy.Policy.createPolicy(sys.argv[2])
    expTime = EXP_TIME
    slewTime = SLEW_TIME
    if(len(sys.argv) == 4):
        try:
            expTime = int(sys.argv[4])
        except:
            pass
    if(len(sys.argv) == 5):
        try:
            slewTime = int(sys.argv[4])
        except:
            pass
    
    # Extract broker info etc.
    pipelinePolicy = dafBase.PropertySet()
    if pipelinePolicy.exists('hostName'):
        hostName  = pipelinePolicy.getString('hostName')
    else:
        hostName = 'lsst8.ncsa.uiuc.edu'
    if pipelinePolicy.exists('topicName'):
        topicName = pipelinePolicy.getString('topicName')
    else:
        topicName = 'triggerImageprocEvent'
    
    EventFromInputSubsets(subsets, datatypePolicy, expTime, 
                          slewTime, topicName, hostName)
        
