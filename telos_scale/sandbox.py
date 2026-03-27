"""
Docker Sandbox for safe code execution.
"""

import docker
import tarfile
import io
import os
import time
from typing import Tuple, Optional
import logging

logger = logging.getLogger(__name__)


class DockerSandbox:
    """Safe code execution environment using Docker."""

    def __init__(
        self,
        image: str = "python:3.11-slim",
        memory_limit: str = "512m",
        timeout: int = 300,
        workdir: str = "/workspace",
    ):
        self.image = image
        self.memory_limit = memory_limit
        self.timeout = timeout
        self.workdir = workdir
        self.client = docker.from_env()
        self.container = None

    def start(self):
        """Start a Docker container."""
        if self.container is not None:
            logger.warning("Container already running, restarting.")
            self.stop(cleanup=True)

        try:
            self.container = self.client.containers.run(
                self.image,
                command=["sleep", "infinity"],
                detach=True,
                mem_limit=self.memory_limit,
                working_dir=self.workdir,
                tty=True,
                stdin_open=True,
                # Mount a temporary volume for workspace? For simplicity, use container's filesystem.
                # We'll copy files via exec.
            )
            logger.info(f"Started container {self.container.short_id}")
            # Wait a bit for container to be ready
            time.sleep(1)
        except Exception as e:
            logger.error(f"Failed to start container: {e}")
            raise

    def execute_command(self, cmd: str, workdir: Optional[str] = None) -> Tuple[int, str]:
        """Execute a command inside the container and return exit code and output."""
        if self.container is None:
            self.start()

        exec_cmd = ["sh", "-c", cmd]
        try:
            exec_result = self.container.exec_run(
                exec_cmd,
                workdir=workdir or self.workdir,
                demux=True,  # returns (stdout, stderr)
            )
            exit_code = exec_result.exit_code
            stdout = exec_result.output[0] or b""
            stderr = exec_result.output[1] or b""
            output = stdout.decode("utf-8", errors="replace") + stderr.decode("utf-8", errors="replace")
            return exit_code, output
        except Exception as e:
            logger.error(f"Command execution failed: {e}")
            return 1, f"Execution error: {str(e)}"

    def read_file(self, path: str) -> str:
        """Read a file from container."""
        if self.container is None:
            self.start()
        try:
            # Use docker copy
            stream, stat = self.container.get_archive(path)
            # stream is a generator yielding bytes
            # For simplicity, we'll just execute cat
            exit_code, output = self.execute_command(f"cat {path}")
            if exit_code == 0:
                return output
            else:
                raise FileNotFoundError(f"File {path} not found or cannot read")
        except Exception as e:
            logger.error(f"Failed to read file {path}: {e}")
            raise

    def write_file(self, path: str, content: str):
        """Write a file into container."""
        if self.container is None:
            self.start()
        # Create a tar archive in memory
        tar_buffer = io.BytesIO()
        with tarfile.open(fileobj=tar_buffer, mode="w") as tar:
            data = content.encode("utf-8")
            tarinfo = tarfile.TarInfo(name=os.path.basename(path))
            tarinfo.size = len(data)
            tarinfo.mode = 0o644
            tar.addfile(tarinfo, io.BytesIO(data))
        tar_buffer.seek(0)
        # Upload to container
        self.container.put_archive(os.path.dirname(path) or "/", tar_buffer.read())

    def stop(self, cleanup: bool = False):
        """Stop the container, optionally remove it."""
        if self.container is not None:
            try:
                self.container.stop()
                if cleanup:
                    self.container.remove()
                    logger.info(f"Removed container {self.container.short_id}")
                else:
                    logger.info(f"Stopped container {self.container.short_id}")
            except Exception as e:
                logger.error(f"Error stopping container: {e}")
            finally:
                self.container = None

    def __del__(self):
        """Cleanup on deletion."""
        if hasattr(self, 'container') and self.container is not None:
            try:
                self.stop(cleanup=True)
            except:
                pass


if __name__ == "__main__":
    # Simple test
    sandbox = DockerSandbox()
    try:
        sandbox.start()
        exit_code, output = sandbox.execute_command("echo 'Hello, World!'")
        print(f"Exit code: {exit_code}, Output: {output}")
        sandbox.write_file("/workspace/test.txt", "Hello from sandbox")
        content = sandbox.read_file("/workspace/test.txt")
        print(f"Read content: {content}")
    finally:
        sandbox.stop(cleanup=True)