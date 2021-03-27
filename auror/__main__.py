import subprocess
from pathlib import Path

import click

from auror import pkgbuild

CONTEXT_SETTINGS = dict(help_option_names=['-h', '--help'])


@click.command(context_settings=CONTEXT_SETTINGS)
def cli():
    # in order to build, we first need to find out the next available version!
    pkgbuild_path = Path('PKGBUILD')
    srcinfo_path = Path('.SRCINFO')
    pkgbuild_content = pkgbuild_path.read_text()
    current_version = pkgbuild.current_version(pkgbuild_content)
    latest_version = pkgbuild.latest_version(pkgbuild_content)
    if current_version == latest_version:
        print("Nothing to do")
    else:
        print(f"Need update to {latest_version}")
        updated_pkgbuild = pkgbuild.update(pkgbuild_content, latest_version)
        pkgbuild_path.write_text(updated_pkgbuild)
        srcinfo_path.write_text(pkgbuild.source_info(updated_pkgbuild))
        subprocess.check_call([
            'git', 'commit',
            '-i', pkgbuild_path, '-i', srcinfo_path,
            '-m', f'Update to version {latest_version}'
        ])


if __name__ == '__main__':
    cli()
