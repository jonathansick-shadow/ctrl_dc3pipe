#!/usr/bin/env python

import sys, re
import lsst.afw.image as afwImage
import lsst.afw.math as afwMath
import lsst.pex.policy as pexPolicy
import lsst.daf.base as dafBase
import lsst.ctrl.events as ctrlEvents
from ValidateMetadata import *

import lsst.pex.logging as logging
Verbosity = 4
logging.Trace_setVerbosity('dc3pipe', Verbosity)

def EventFromInputfile(inputfile, datatypePolicy, pipelinePolicy=dafBase.PropertySet()):
    # For DC3a, inputfile is a .fits file on disk
    metadata = afwImage.readMetadata(inputfile)

    # First, transform the input metdata
    TransformMetadata(metadata, datatypePolicy)

    # To be consistent...
    print ValidateMetadata(metadata)

    # Create event policy, using defaults from input metadata
    event = dafBase.PropertySet()
    event.copy('visitId',     metadata, 'visitId')
    event.copy('ccdId',       metadata, 'ccdId')
    event.copy('ampId',       metadata, 'ampId')
    event.copy('exposureId',  metadata, 'exposureId')
    event.copy('datasetId',   metadata, 'datasetId')
    event.copy('filter',      metadata, 'filter')
    event.copy('exptime',     metadata, 'exptime')
    event.copy('ra',          metadata, 'ra')
    event.copy('decl',        metadata, 'decl')
    event.copy('equinox',     metadata, 'equinox')
    event.copy('airmass',     metadata, 'airmass')
    event.copy('dateobs',     metadata, 'dateobs')

    # Policy for the event transmission
    if pipelinePolicy.exists('hostName'):
        hostName  = pipelinePolicy.getString('hostName')
    else:
        hostName = 'lsst8.ncsa.uiuc.edu'
    if pipelinePolicy.exists('topicName'):
        topicName = pipelinePolicy.getString('topicName')
    else:
        topicName = 'triggerImageprocEvent'

    if event.getInt('exposureId') == 0:
        eventTransmitter = ctrlEvents.EventTransmitter(hostName, topicName+'0')
    elif event.getInt('exposureId') == 1:
        eventTransmitter = ctrlEvents.EventTransmitter(hostName, topicName+'1')
        
    eventTransmitter.publish(event)


if __name__ == "__main__":
    inputfile      = sys.argv[1]
    datatypePolicy = pexPolicy.Policy.createPolicy(sys.argv[2])
    
    EventFromInputfile(inputfile, datatypePolicy)
        
