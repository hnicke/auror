import logging
import subprocess
import sys
from pathlib import Path

import click

from auror import pkgbuild

CONTEXT_SETTINGS = dict(help_option_names=['-h', '--help'])

root_logger = logging.getLogger()
handler = logging.StreamHandler(sys.stdout)
handler.setFormatter(logging.Formatter(f'%(asctime)s %(levelname)-5s > %(message)s'))
root_logger.addHandler(handler)
_logger = logging.getLogger('auror')
_logger.setLevel(logging.DEBUG)


@click.group(context_settings=CONTEXT_SETTINGS)
def cli():
    pass


@cli.command()
def update():
    """Automatically update package to latest version"""
    # in order to build, we first need to find out the next available version!
    pkgbuild_path = Path('PKGBUILD')
    srcinfo_path = Path('.SRCINFO')
    pkgbuild_content = pkgbuild_path.read_text()
    current_version = pkgbuild.current_version(pkgbuild_content)
    latest_version = pkgbuild.latest_version(pkgbuild_content)
    if current_version == latest_version:
        _logger.info("Package is up to date")
    else:
        _logger.info(f"Need update to {latest_version}")
        updated_pkgbuild = pkgbuild.update(pkgbuild_content, latest_version)
        pkgbuild_path.write_text(updated_pkgbuild)
        srcinfo_path.write_text(pkgbuild.source_info(updated_pkgbuild))
        subprocess.check_call([
            'git', 'commit',
            '-i', pkgbuild_path, '-i', srcinfo_path,
            '-m', f'Update to version {latest_version}'
        ])
        _logger.info(f"Updated package ({current_version} -> {latest_version})")
        _logger.info("Don't forget to push.")


if __name__ == '__main__':
    cli()
