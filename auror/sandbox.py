import atexit
import logging
import subprocess
import time
from threading import Lock

_sandbox_name = f'auror-sandbox-{time.time()}'
_sandbox_startup_lock = Lock()

_logger = logging.getLogger(__name__)


class SandboxExecutionError(Exception):
    pass


def execute(bash_script: str, env: dict[str, str] = None, mounts: dict[str, str] = None):
    """
    Safely executes given script in a docker container and return its output
    :param env: environment variables which will be set with 'docker exec -e'
    :param mounts: Dict of file paths to file contents (these will be available similar to docker mounts)
    """
    with _sandbox_startup_lock:
        if not _is_sandbox_running():
            _start_sandbox()

    tmpdir_script = 'cd $(mktemp -d) && '
    mount_script = ''.join([f"cat <<'EOF' > {path}\n{content}\nEOF\n" for path, content in (mounts or {}).items()])
    script = tmpdir_script + mount_script + bash_script
    try:
        cmd = ['docker', 'exec']
        if env:
            cmd.append(''.join([f'--env={k}={v}' for k, v in env.items()]))
        cmd.extend([_sandbox_name, 'bash', '-c', script])
        output = subprocess.check_output(cmd, universal_newlines=True)
        return output.rstrip()
    except subprocess.CalledProcessError as e:
        raise SandboxExecutionError(e)


def _is_sandbox_running():
    running_container = subprocess.check_output(['docker', 'ps',
                                                 f'--filter=name={_sandbox_name}',
                                                 '--format={{.Names}}'],
                                                universal_newlines=True).strip()
    return running_container == _sandbox_name


def _start_sandbox():
    atexit.register(_stop_sandbox)
    subprocess.check_output(['docker', 'run', '-d', '--rm',
                             '--entrypoint', 'sleep', f'--name={_sandbox_name}',
                             'hnicke/auror:latest', 'infinity'])


def _stop_sandbox():
    subprocess.run(['docker', 'kill', _sandbox_name], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
