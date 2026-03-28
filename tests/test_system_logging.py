import unittest
import os
import sqlite3
from orchestrator.orchestrator import PipelineOrchestrator
from utils.logger import JsonLogger

class TestSystemLogging(unittest.TestCase):
    
    def setUp(self):
        self.db_file = "logs/test_system_logs.db"
        self.log_file = "logs/test_system.log"
        if os.path.exists(self.db_file):
            os.remove(self.db_file)
        if os.path.exists(self.log_file):
            os.remove(self.log_file)
        self.logger = JsonLogger(log_file=self.log_file, db_file=self.db_file)
        
    def test_log_persistence_and_query(self):
        """ Verify that logs are written to SQLite and retrievable via Orchestrator. """
        # 1. Log various levels
        self.logger.debug("Debug event")
        self.logger.info("Info event")
        self.logger.warning("Warning event")
        self.logger.error("Error event")
        self.logger.critical("Critical event")
        
        # 2. Inject this logger into Orchestrator
        orch = PipelineOrchestrator()
        orch.logger = self.logger
        
        # 3. Test Command Parser
        # a) All logs
        report_all = orch.handle_log_system_command("/log-system")
        self.assertIn("ALL", report_all.upper())
        self.assertIn("CRI", report_all.upper())
        self.assertIn("ERR", report_all.upper())
        self.assertIn("INF", report_all.upper())
        
        # b) Error specific
        report_err = orch.handle_log_system_command("/log-system error")
        self.assertIn("ERROR", report_err.upper())
        self.assertIn("ERR", report_err.upper())
        self.assertNotIn("INF", report_err.upper())
        
        # c) Limit test
        report_limit = orch.handle_log_system_command("/log-system 2")
        # Header + Separator + 2 logs = 4 lines starting with `
        lines = [l for l in report_limit.split("\n") if l.strip().startswith("`")]
        self.assertEqual(len(lines), 4)

if __name__ == '__main__':
    unittest.main()
