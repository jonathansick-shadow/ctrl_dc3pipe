#! /usr/bin/env python

from lsst.pex.harness import Stage

class SliceInfoStage(Stage):
    '''Compute per-slice information.'''

    def preprocess(self): 
        self.process()

    def process(self): 
        """
        Compute the ampId and ccdId corresponding to this slice.
        """
        self.activeClipboard = self.inputQueue.getNextDataset()

        sliceId = self.getRank()

        nAmps = self._policy.get("nAmps")
        nCcds = self._policy.get("nCcds")

        ccdFormula = self._policy.get("ccdIdFormula")
        ampFormula = self._policy.get("ampIdFormula")

        ccdId = eval(ccdFormula)
        ampId = eval(ampFormula)

        self.activeClipboard["ccdId"] = ccdId
        self.activeClipboard["ampId"] = ampId

        self.outputQueue.addDataset(self.activeClipboard)
