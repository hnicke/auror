import atexit
import logging
import subprocess
import time
from threading import Lock

_executor_name = f'auror-sandbox-{time.time()}'
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
        if not _is_executor_running():
            _start_executor()

    tmpdir_script = 'cd $(mktemp -d) && '
    mount_script = ''.join([f"cat <<'EOF' > {path}\n{content}\nEOF\n" for path, content in (mounts or {}).items()])
    script = tmpdir_script + mount_script + bash_script
    try:
        env_option = ''.join([f'-e {k}={v}' for k, v in (env or {}).items()])
        output = subprocess.check_output(['docker', 'exec', env_option,
                                          _executor_name,
                                          'bash', '-c', script], universal_newlines=True)
        return output.rstrip()
    except subprocess.CalledProcessError as e:
        raise SandboxExecutionError(e)


def _is_executor_running():
    running_container = subprocess.check_output(['docker', 'ps',
                                                 f'--filter=name={_executor_name}',
                                                 '--format={{.Names}}'],
                                                universal_newlines=True).strip()
    return running_container == _executor_name


def _start_executor():
    atexit.register(_stop_executor)
    subprocess.check_output(['docker', 'run', '-d', '--rm',
                             '--entrypoint', 'sleep', f'--name={_executor_name}',
                             'whynothugo/makepkg', 'infinity'])


def _stop_executor():
    subprocess.run(['docker', 'kill', _executor_name], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
