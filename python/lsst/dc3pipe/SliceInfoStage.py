#! /usr/bin/env python

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
        nCcds = self._policy.get("ccdsPerFocalPlane")
        nAmps = self._policy.get("ampsPerCcd")
        assert nAmps * nCcds == getUniverseSize()
        self.activeClipboard["ampId"] = sliceId % nAmps
        self.activeClipboard["ccdId"] = sliceId / nAmps
        self.outputQueue.addDataset(self.activeClipboard)
