from lsst.pex.harness.Stage import Stage
from lsst.daf.persistence import LogicalLocation
from lsst.daf.base import PropertySet, DateTime
from lsst.pex.policy import Policy
import lsst.afw.image as afwImage

class VisitMetadataStage(Stage):
    def __init__(self, stageId=-1, stagePolicy=None):
        Stage.__init__(self, stageId, stagePolicy)
        self.ampBBoxDb = Policy(self._policy.get("ampBBoxDbPath"))

    def preprocess(self):
        clipboard = self.inputQueue.getNextDataset()

        eventName = self._policy.get("inputEvent")
        event = clipboard.get(eventName)
        visitId = event.get("visitId")
        exposureId = event.get("exposureId")

        fpaExposureId = long(visitId) << 1 + exposureId

        visit = PropertySet()
        visit.setInt("visitId", visitId)
        visit.setLongLong("exposureId", fpaExposureId)
        clipboard.put("visit" + str(exposureId), visit)

        rawFpaExposure = PropertySet()
        rawFpaExposure.setLongLong("rawFPAExposureId", fpaExposureId)
        rawFpaExposure.set("ra", event.get("ra"))
        rawFpaExposure.set("decl", event.get("decl"))
        rawFpaExposure.set("filterId",
                self.lookupFilterId(event.get("filter")))
        rawFpaExposure.set("equinox", event.get("equinox"))
        rawFpaExposure.set("dateObs", DateTime(event.get("dateObs")))
        rawFpaExposure.set("mjdObs", DateTime(event.get("dateObs")).mjd())
        rawFpaExposure.set("expTime", event.get("expTime"))
        rawFpaExposure.set("airmass", event.get("airmass"))
        clipboard.put("fpaExposure" + str(exposureId), rawFpaExposure)

        # rely on default postprocess() to move clipboard to output queue

    def process(self):
        clipboard = self.inputQueue.getNextDataset()

        eventName = self._policy.get("inputEvent")
        event = clipboard.get(eventName)
        visitId = event.get("visitId")
        exposureId = event.get("exposureId")

        ccdId = clipboard.get("ccdId")
        ampId = clipboard.get("ampId")

        fpaExposureId = long(visitId) << 1 + exposureId
        ccdExposureId = fpaExposureId << 8 + ccdId
        ampExposureId = ccdExposureId << 6 + ampId

        clipboard.put("visitId", visitId)

        exposureMetadata = PropertySet()
        exposureMetadata.setInt("filterId",
                self.lookupFilterId(event.get("filter")))
        exposureMetadata.setLongLong("fpaExposureId", fpaExposureId)
        exposureMetadata.setLongLong("ccdExposureId", ccdExposureId)
        exposureMetadata.setLongLong("ampExposureId", ampExposureId)
        clipboard.put("exposureMetadata" + str(exposureId), exposureMetadata)

        clipboard.put("ampBBox", self.lookupAmpBBox(ampId, ccdId))

        self.outputQueue.addDataset(clipboard)

    def lookupFilterId(self, filterName):
        dbLocation = LogicalLocation("%(dbUrl)")
        filterDb = afwImage.Filter(dbLocation, filterName)
        filterId = filterDb.getId()
        return filterId

    def lookupAmpBBox(self, ampId, ccdId):
        key = "CcdBBox.Amp%d" % ampId
        p = self.ampBBoxDb.get(key)
        return afwImage.BBox(
                afwImage.PointI(p.get("x0"), p.get("y0")),
                p.get("width"), p.get("height"))
