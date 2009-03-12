#!/usr/bin/env python

import sys, re
import lsst.afw.image as afwImage
import lsst.afw.math as afwMath
import lsst.pex.policy as pexPolicy
import lsst.daf.base as dafBase
import lsst.ctrl.events as ctrlEvents

def EventFromInputfile(inputfile, datatypePolicy, pipelinePolicy=dafBase.PropertySet()):
    # For DC3a, inputfile is a .fits file on disk
    metadata = afwImage.readMetadata(inputfile)

    # Policy contains the mapping from inputfile metadata (for DC3a
    # persisted in the .fits header, into required Event keywords.
    #
    #
    # Everything we expect to get from the Camera, and is needed later
    # on in the pipeline, should be extracted here.
    visitIdKeyword       = datatypePolicy.getString('visitIdKeyword')
    exposureIdKeyword    = datatypePolicy.getString('exposureIdKeyword')
    ccdIdKeyword         = datatypePolicy.getString('ccdIdKeyword')
    ampIdKeyword         = datatypePolicy.getString('ampIdKeyword')
    dateObsKeyword       = datatypePolicy.getString('dateObsKeyword')
    filterIdKeyword      = datatypePolicy.getString('filterIdKeyword')
    exptimeKeyword       = datatypePolicy.getString('exptimeKeyword')
    boresightRaKeyword   = datatypePolicy.getString('boresightRaKeyword')
    boresightDeclKeyword = datatypePolicy.getString('boresightDeclKeyword')
    equinoxKeyword       = datatypePolicy.getString('equinoxKeyword')
    airmassKeyword       = datatypePolicy.getString('airmassKeyword')
    dataSetIdKeyword     = datatypePolicy.getString('dataSetIdKeyword')

    # Any operations on the input data?
    if datatypePolicy.exists('convertDateObstoTai'):
        convertDateObstoTai = datatypePolicy.getBool('convertDateObstoTai')
    else:
        convertDateObstoTai = False

    if datatypePolicy.exists('convertDateObstoMidExposure'):
        convertDateObstoMidExposure = datatypePolicy.getBool('convertDateObstoMidExposure')
    else:
        convertDateObstoMidExposure = False
    
    # Create event policy, using defaults from input metadata
    event = dafBase.PropertySet()
    event.copy('visitId',     metadata, visitIdKeyword)
    event.copy('ccdId',       metadata, ccdIdKeyword)
    event.copy('ampId',       metadata, ampIdKeyword)
    event.copy('exposureId',  metadata, exposureIdKeyword)
    event.copy('datasetId',   metadata, dataSetIdKeyword)
    
    event.copy('filter',      metadata, filterIdKeyword)
    event.copy('exptime',     metadata, exptimeKeyword)
    event.copy('ra',          metadata, boresightRaKeyword)
    event.copy('decl',        metadata, boresightDeclKeyword)
    event.copy('equinox',     metadata, equinoxKeyword)
    event.copy('airmass',     metadata, airmassKeyword)

    # Operations on the input metadata
    if convertDateObstoTai or convertDateObstoMidExposure:
        dateobs = metadata.getDouble(dateObsKeyword)

        if convertDateObstoTai:
            dateTime = dafBase.DateTime(dateobs, dafBase.DateTime.UTC)
            dateobs  = dateTime.mjd(dafBase.DateTime.TAI)

        if convertDateObstoMidExposure:
            dateobs += metadata.getDouble(exptimeKeyword) * 0.5

        event.setDouble('dateobs', dateobs)
        
    else:
        event.copy('dateobs', metadata, dateObsKeyword)

    
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
        
