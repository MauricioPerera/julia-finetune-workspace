import subprocess
import sys
import tempfile
import unittest
from pathlib import Path
from julia_finetune.locking import RunLock


class LockTests(unittest.TestCase):
    def test_exclusion_and_release_after_process_kill(self):
        with tempfile.TemporaryDirectory() as root:
            path = str(Path(root) / "RUNNING.lock")
            code = "from julia_finetune.locking import RunLock; import sys,time; lock=RunLock(sys.argv[1]); print('LOCKED',flush=True); time.sleep(60)"
            process = subprocess.Popen([sys.executable, "-c", code, path], stdout=subprocess.PIPE, text=True)
            try:
                self.assertEqual(process.stdout.readline().strip(), "LOCKED")
                with self.assertRaisesRegex(ValueError, "bloqueada"):
                    RunLock(path)
            finally:
                process.kill()
                process.wait(timeout=10)
                process.stdout.close()
            lock = RunLock(path)
            lock.close()
            self.assertTrue(Path(path).is_file())
