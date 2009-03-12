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
        ccdFormat = self._policy.get("ccdIdStringFormat")
        ampFormat = self._policy.get("ampIdStringFormat")

        ccdId = eval(ccdFormula)
        ampId = eval(ampFormula)
        ccdIdString = ccdFormat % (ccdId)
        ampIdString = ampFormat % (ampId)

        self.outputQueue.addDataset(self.activeClipboard)
