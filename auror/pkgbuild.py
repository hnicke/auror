import re
import subprocess
from enum import Enum
from functools import cache

import requests
from semantic_version import Version

from auror import sandbox


class PkgBuildKey(Enum):
    pkgver = 'pkgver'
    source = 'source'
    sha256sums = 'sha256sums'


def eval_value(pkgbuild_content: str, key: PkgBuildKey) -> str:
    """Source PKGBUILD in an isolated docker container and print value of given key"""
    return sandbox.execute(f'CARCH=x86_64 source <(cat <<\'EOF\'\n{pkgbuild_content}\nEOF\n) && echo "${key.value}"')


def set_value(pkgbuild_content: str, key: PkgBuildKey, value: object) -> str:
    return '\n'.join(
        [re.sub(rf'^{key.value}=.*', f'{key.value}={str(value)}', x) for x in pkgbuild_content.splitlines()]
    )


@cache
def sources(pkgbuild_content: str) -> list[str]:
    return eval_value(pkgbuild_content, PkgBuildKey.source).split(' ')


def _source_exists(source: str) -> bool:
    return requests.head(source).status_code < 300


@cache
def latest_version(pkgbuild_content: str) -> Version:
    # this is the most generic way to figure out the new release.
    # another more specific way would be to use github api (query for latest release) - this is faster
    current = current_version(pkgbuild_content)
    for next_version in [current.next_major(), current.next_minor(), current.next_patch()]:
        next_pkgbuild_content = set_value(pkgbuild_content, PkgBuildKey.pkgver, next_version)
        if all([_source_exists(x) for x in sources(next_pkgbuild_content)]):
            return latest_version(set_value(pkgbuild_content, PkgBuildKey.pkgver, next_version))
    return current


@cache
def current_version(pkgbuild_content: str) -> Version:
    version_string = eval_value(pkgbuild_content, PkgBuildKey.pkgver)
    return Version(version_string)
