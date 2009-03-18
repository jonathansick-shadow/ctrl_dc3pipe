#!/usr/bin/env python

import re

import lsst.afw.image as afwImage
import lsst.daf.base as dafBase

from lsst.pex.harness.Stage import Stage

def validateMetadata(metadata, metadataPolicy):
    paramNames = metadataPolicy.paramNames(1)
    for paramName in paramNames:
        if not metadata.exists(paramName):
            raise RuntimeError, 'Unable to find \'%s\' in metadata' % (paramName,)
        # TBD; VALIDATE AGAINST DICTIONARY FOR TYPE ETC
    return True

def transformMetadata(metadata, datatypePolicy, metadataPolicy, suffix):
    paramNames = metadataPolicy.paramNames(1)
    for paramName in paramNames:
        # If it already exists don't try and update it
        if metadata.exists(paramName):
            continue
        
        mappingKey = paramName + suffix
        if datatypePolicy.exists(mappingKey):
            keyword = datatypePolicy.getString(mappingKey)
            metadata.copy(paramName, metadata, keyword)
            metadata.copy(keyword + "_original", metadata, keyword)
            metadata.remove(keyword)
    
    # Any additional operations on the input data?
    if datatypePolicy.exists('convertDateobsToTai'):
        convertDateobsToTai = datatypePolicy.getBool('convertDateobsToTai')
        if convertDateobsToTai:
            dateObs  = metadata.getDouble('dateObs')
            dateTime = dafBase.DateTime(dateObs, dafBase.DateTime.UTC)
            dateObs  = dateTime.mjd(dafBase.DateTime.TAI)
            metadata.setDouble('dateObs', dateObs)

    if datatypePolicy.exists('convertDateobsToMidExposure'):
        convertDateobsToMidExposure = \
            datatypePolicy.getBool('convertDateobsToMidExposure')
        if convertDateobsToMidExposure:
            dateObs  = metadata.getDouble('dateObs')
            dateObs += metadata.getDouble('expTime') * 0.5 / 3600. / 24.
            metadata.setDouble('dateObs', dateObs)

    if datatypePolicy.exists('trimFilterName'):
        if datatypePolicy.getBool('trimFilterName'):
            filter = metadata.getString('filter')
            filter = re.sub(r'\..*', '', filter)
            metadata.setString('filter', filter)


class ValidateMetadataStage(Stage):

    """Validates that every field in metadataPolicy exists in the
    input metadata, before sending the event down the pipeline.  This
    will evolve as the pipeline evolves and the metadata requirements
    of each stage evolves.

    For the input of external (non-LSST) data these data's metadata
    should be generally be run through the TransformMetadata stage,
    with a survey-specific policy file specifying this mapping.
    """

    def process(self):
        self.activeClipboard = self.inputQueue.getNextDataset()
        metadataPolicy = self._policy.getPolicy("metadata")
        imageMetadataKey = self._policy.get("imageMetadataKey")
        metadata = self.activeClipboard.get(imageMetadataKey)
        validateMetadata(metadata, metadataPolicy)
        self.outputQueue.addDataset(self.activeClipboard)
    
class TransformMetadataStage(Stage):

    """This stage takes an input set of metadata and transforms this
    to the LSST standard.  It will be input-dataset specific, and the
    mapping is described in the datatypePolicy.  The standard is to
    have a string in the datatypePolicy named metadataKeyword that
    represents the location of LSST metadata in the particular data
    set."""

    def process(self):
        self.activeClipboard = self.inputQueue.getNextDataset()
        metadataPolicy = self._policy.getPolicy("metadata")
        datatypePolicy = self._policy.getPolicy("datatype")
        imageKey = self._policy.get("imageKey")
        metadataKey = self._policy.get("metadataKey")
        wcsKey = self._policy.get("wcsKey")
        decoratedImage = self.activeClipboard.get(imageKey)
        metadata = decoratedImage.getMetadata()

        if self._policy.exists("suffix"):
            suffix = self._policy.get("suffix")
        else:
            suffix = "Keyword"

        transformMetadata(metadata, datatypePolicy, metadataPolicy, suffix)

        self.activeClipboard.put(metadataKey, metadata)
        self.activeClipboard.put(imageKey, decoratedImage.getImage())
        if self._policy.getBool("computeWcsGuess"):
            self.activeClipboard.put(wcsKey, afwImage.Wcs(metadata))

        self.outputQueue.addDataset(self.activeClipboard)

class TransformExposureMetadataStage(Stage):

    """This stage takes alist of  input Exposures and transforms the metadata
    of each one to the LSST standard.  It will be input-dataset specific, and
    the mapping is described in the datatypePolicy.  The standard is to have a
    string in the datatypePolicy named metadataKeyword that represents the
    location of LSST metadata in the particular data set."""

    def process(self):
        self.activeClipboard = self.inputQueue.getNextDataset()
        metadataPolicy = self._policy.getPolicy("metadata")
        datatypePolicy = self._policy.getPolicy("datatype")
        exposureKeys = self._policy.getStringArray("exposureKey")

        if self._policy.exists("suffix"):
            suffix = self._policy.get("suffix")
        else:
            suffix = "Keyword"

        for exposureKey in exposureKeys:
            print exposureKey
            exposure = self.activeClipboard.get(exposureKey)
            metadata = exposure.getMetadata()
            transformMetadata(metadata, datatypePolicy, metadataPolicy, suffix)

        self.outputQueue.addDataset(self.activeClipboard)
