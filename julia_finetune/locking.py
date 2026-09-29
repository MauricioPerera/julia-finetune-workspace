"""Kernel-held lock: automatically released even if the owner is killed."""
import os


class RunLock:
    def __init__(self, path):
        self.stream = open(path, "a+b")
        try:
            if os.fstat(self.stream.fileno()).st_size == 0:
                self.stream.write(b"0")
                self.stream.flush()
            self.stream.seek(0)
            if os.name == "nt":
                import msvcrt
                msvcrt.locking(self.stream.fileno(), msvcrt.LK_NBLCK, 1)
            else:
                import fcntl
                fcntl.flock(self.stream.fileno(), fcntl.LOCK_EX | fcntl.LOCK_NB)
        except OSError:
            self.stream.close()
            raise ValueError("Otra ejecución mantiene bloqueada esta carpeta") from None

    def close(self):
        # Keep the inode/path stable: deleting a lock file permits concurrent owners.
        self.stream.close()
