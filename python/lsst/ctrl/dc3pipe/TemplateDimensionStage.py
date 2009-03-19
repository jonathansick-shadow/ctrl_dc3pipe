from lsst.pex.harness.Stage import Stage
from lsst.pex.harness import Utils
from lsst.daf.persistence import LogicalLocation
import lsst.afw.image as afwImage

class TemplateDimensionStage(Stage):
    def process(self):
        self.activeClipboard = self.inputQueue.getNextDataset()

        additionalData = Utils.createAdditionalData(self,
                self._policy, clipboard)
        templateLocation = self._policy.get('templateLocation')
        templatePath = LogicalLocation(templateLocation,
                additionalData).locString()
        metadata = afwImage.readMetadata(templatePath)
        dims = afwImage.PointI(metadata.get("NAXIS1"), metadata.get("NAXIS2"))
        outputKey = self._policy.get('outputKey')
        self.activeClipboard.put(outputKey, dims)

        self.outputQueue.addDataset(self.activeClipboard)
