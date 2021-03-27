from pathlib import Path

import click

from auror import pkgbuild

CONTEXT_SETTINGS = dict(help_option_names=['-h', '--help'])


@click.command(context_settings=CONTEXT_SETTINGS)
def cli():
    # in order to build, we first need to find out the next available version!
    pkgbuild_path = Path('PKGBUILD')
    pkgbuild_content = pkgbuild_path.read_text()
    current_version = pkgbuild.current_version(pkgbuild_content)
    latest_version = pkgbuild.latest_version(pkgbuild_content)
    if current_version == latest_version:
        print("Nothing to do")
    else:
        print(f"Need update to {latest_version}")


if __name__ == '__main__':
    cli()
