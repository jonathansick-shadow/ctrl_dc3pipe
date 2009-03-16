from lsst.pex.harness.Stage import Stage
from lsst.daf.persistence import LogicalLocation
from lsst.daf.base import PropertySet, DateTime
import lsst.afw.image as afwImage

class VisitMetadataStage(Stage):
    def preprocess(self):
        self.activeClipboard = self.inputQueue.getNextDataset()

        eventName = self._policy.get("inputEvent")
        event = self.activeClipboard.get(eventName)
        visitId = event.get("visitId")
        exposureId = event.get("exposureId")

        ccdId = self.activeClipboard.get("ccdId")
        ampId = self.activeClipboard.get("ampId")

        fpaExposureId = long(visitId) << 1 + exposureId
        ccdExposureId = fpaExposureId << 8 + ccdId
        ampExposureId = ccdExposureId << 6 + ampId

        visit = PropertySet()
        visit.set("visitId", visitId)
        visit.set("exposureId", fpaExposureId)
        self.activeClipboard.put("visit" + str(exposureId), visit)

        rawFpaExposure = PropertySet()
        rawFpaExposure.set("fpaExposureId", fpaExposureId)
        rawFpaExposure.set("ra", event.get("ra"))
        rawFpaExposure.set("decl", event.get("decl"))
        rawFpaExposure.set("filterId",
                self.lookupFilterId(event.get("filter")))
        rawFpaExposure.set("equinox", event.get("equinox"))
        rawFpaExposure.set("dateObs", DateTime(event.get("dateObs")))
        rawFpaExposure.set("mjdObs", DateTime(event.get("dateObs")).mjd())
        rawFpaExposure.set("expTime", event.get("expTime"))
        rawFpaExposure.set("airmass", event.get("airmass"))
        self.activeClipboard.put("fpaExposure" + str(exposureId),
                rawFpaExposure)

        rawCcdExposure = PropertySet()
        rawCcdExposure.set("ccdExposureId", ccdExposureId)
        rawCcdExposure.set("fpaExposureId", fpaExposureId) 
        self.activeClipboard.put("ccdExposure" + str(exposureId),
                rawCcdExposure)

        # rely on default postprocess() to move clipboard to output queue

    def process(self):
        self.activeClipboard = self.inputQueue.getNextDataset()

        eventName = self._policy.get("inputEvent")
        event = self.activeClipboard.get(eventName)
        visitId = event.get("visitId")
        exposureId = event.get("exposureId")

        ccdId = self.activeClipboard.get("ccdId")
        ampId = self.activeClipboard.get("ampId")

        fpaExposureId = long(visitId) << 1 + exposureId
        ccdExposureId = fpaExposureId << 8 + ccdId
        ampExposureId = ccdExposureId << 6 + ampId

        self.activeClipboard.put("visitId", visitId)

        exposureMetadata = PropertySet()
        exposureMetadata.set("filterId",
                self.lookupFilterId(event.get("filter")))
        exposureMetadata.set("fpaExposureId", fpaExposureId)
        exposureMetadata.set("ccdExposureId", ccdExposureId)
        exposureMetadata.set("ampExposureId", ampExposureId)
        self.activeClipboard.put("exposureMetadata" + str(exposureId),
                exposureMetadata)

        self.outputQueue.addDataset(self.activeClipboard)

    def lookupFilterId(self, filterName):
        dbLocation = LogicalLocation("%(dbUrl)")
        filterDb = afwImage.Filter(dbLocation, filterName)
        filterId = filterDb.getId()
        return filterId
