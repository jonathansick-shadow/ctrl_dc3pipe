from lsst.pex.harness.Stage import Stage
from lsst.daf.persistence import LogicalLocation, DbStorage

class CcdMetadataStage(Stage):
    def preprocess(self):
        self.activeClipboard = self.inputQueue.getNextDataset()

        db = DbStorage()
        loc = LogicalLocation("%(dbUrl)")
        db.setPersistLocation(loc)
        db.startTransaction()
        db.executeSql("""
            INSERT INTO Raw_CCD_Exposure
            SELECT DISTINCT rawCCDExposureId, rawFPAExposureId
            FROM Raw_Amp_Exposure
        """)
        db.executeSql("""
            INSERT INTO Science_CCD_Exposure
            SELECT DISTINCT
                scienceCCDExposureId, scienceFPAExposureId, rawCCDExposureId
            FROM Science_Amp_Exposure
        """)
        db.executeSql("""
            INSERT INTO Science_FPA_Exposure
            SELECT DISTINCT scienceFPAExposureId
            FROM Science_Amp_Exposure
        """)
        db.endTransaction()

        # rely on default postprocess() to move self.activeClipboard to output queue
