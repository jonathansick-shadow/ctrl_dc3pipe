#!/usr/bin/env python

import sys, re, os
import eups
import lsst.afw.image as afwImage
import lsst.afw.math as afwMath
import lsst.pex.policy as pexPolicy
import lsst.daf.base as dafBase
import lsst.ctrl.events as ctrlEvents
import lsst.pex.logging as pexLog

def ValidateMetadata(metadata, metadataPolicy=None):

    """Validates that every field in metadataPolicy exists in the
    input metadata, before sending the event down the pipeline.  This
    will evolve as the pipeline evolves and the metadata requirements
    of each stage evolves.

    For the input of external (non-LSST) data these data's metadata
    should be generally be run through the TransformMetadata stage,
    with a survey-specific policy file specifying this mapping.
    """

    if metadataPolicy == None:
        # Use the default for DC3a
        dc3pipeDir     = eups.productDir('ctrl_dc3pipe')
        dc3PolicyPath  = os.path.join(dc3pipeDir, 'pipeline', 'dc3MetadataPolicy.paf')
        metadataPolicy = pexPolicy.Policy.createPolicy(dc3PolicyPath)

    paramNames = metadataPolicy.paramNames(1)
    for paramName in paramNames:
        if not metadata.exists(paramName):
            pexLog.Trace('dc3pipe.validatemetadata', 1, 'Unable to find \'%s\' in metadata' % (paramName))
            return False
        # TBD; VALIDATE AGAINST DICTIONARY FOR TYPE ETC

    return True
    

def WcsFromMetadata(metadata):
    # put on clipboad as initialWcs
    return afwImage.Wcs(metadata)

def TransformMetadata(metadata, datatypePolicy, metadataPolicy=None, suffix='Keyword'):
    """This stage takes an input set of metadata and transforms this
    to the LSST standard.  It will be input-dataset specific, and the
    mapping is described in the datatypePolicy.  The standard is to
    have a string in the datatypePolicy named metadataKeyword that
    represents the location of LSST metadata in the particular data
    set."""

    if metadataPolicy == None:
        # Use the default for DC3a
        dc3pipeDir     = eups.productDir('ctrl_dc3pipe')
        dc3PolicyPath  = os.path.join(dc3pipeDir, 'pipeline', 'dc3MetadataPolicy.paf')
        metadataPolicy = pexPolicy.Policy.createPolicy(dc3PolicyPath)

    paramNames = metadataPolicy.paramNames(1)
    for paramName in paramNames:
        # If it already exists don't try and update it
        if metadata.exists(paramName):
            continue
        
        mappingKey = paramName+suffix
        if datatypePolicy.exists(mappingKey):
            keyword = datatypePolicy.getString(mappingKey)
            metadata.copy(paramName, metadata, keyword)
    
    # Any additional operations on the input data?
    if datatypePolicy.exists('convertDateobsToTai'):
        convertDateobsToTai = datatypePolicy.getBool('convertDateobsToTai')
        if convertDateobsToTai:
            dateobs  = metadata.getDouble('dateobs')
            dateTime = dafBase.DateTime(dateobs, dafBase.DateTime.UTC)
            dateobs  = dateTime.mjd(dafBase.DateTime.TAI)
            metadata.setDouble('dateobs', dateobs)

    if datatypePolicy.exists('convertDateobsToMidExposure'):
        convertDateobsToMidExposure = datatypePolicy.getBool('convertDateobsToMidExposure')
        if convertDateobsToMidExposure:
            dateobs  = metadata.getDouble('dateobs')
            dateobs += metadata.getDouble('exptime') * 0.5 / 3600. / 24.
            metadata.setDouble('dateobs', dateobs)
    
