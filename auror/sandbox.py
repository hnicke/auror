import atexit
import subprocess
import time
from threading import Lock

_executor_name = f'auror-sandbox-{time.time()}'
_sandbox_startup_lock = Lock()


def execute(bash_script: str):
    """
    Safely executes given script in a docker container and return its output
    """
    with _sandbox_startup_lock:
        if not _is_executor_running():
            _start_executor()

    output = subprocess.check_output(['docker', 'exec', _executor_name,
                                      'bash', '-c', bash_script], universal_newlines=True)
    return output.rstrip()


def _is_executor_running():
    running_container = subprocess.check_output(['docker', 'ps',
                                                 f'--filter=name={_executor_name}',
                                                 '--format={{.Names}}'],
                                                universal_newlines=True).strip()
    return running_container == _executor_name


def _start_executor():
    atexit.register(_stop_executor)
    subprocess.check_output(['docker', 'run', '-it', '-d', '--rm', f'--name={_executor_name}', 'whynothugo/makepkg'])


def _stop_executor():
    subprocess.run(['docker', 'kill', _executor_name], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
