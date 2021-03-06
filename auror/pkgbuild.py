import re
from enum import Enum
from functools import cache
from typing import Union

import requests
from semantic_version import Version

from auror import sandbox


class PkgBuildKey(Enum):
    pkgver = 'pkgver'
    source = 'source'


def eval_value(pkgbuild_content: str, key: PkgBuildKey) -> str:
    """Source PKGBUILD in an isolated docker container and print value of given key"""
    value = sandbox.execute(f"source PKGBUILD && echo \"${key.value}\"",
                            env=dict(CARCH='x86_64'), mounts={'PKGBUILD': pkgbuild_content})
    assert value is not None
    return value


def set_value(pkgbuild_content: str, key: Union[PkgBuildKey, str], value: object) -> str:
    if isinstance(key, PkgBuildKey):
        key = key.value
    return '\n'.join(
        [re.sub(rf'^{key}=.*', f'{key}={str(value)}', x) for x in pkgbuild_content.splitlines()]
    ) + '\n'


@cache
def sources(pkgbuild_content: str) -> list[str]:
    return [x.split("::", maxsplit=1)[-1] for x in eval_value(pkgbuild_content, PkgBuildKey.source).split(' ')]


@cache
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


@cache
def update(pkgbuild_content: str, target_version: Version) -> str:
    pkgbuild_content_updated = set_value(pkgbuild_content, PkgBuildKey.pkgver, target_version)
    pkgbuild_content_updated = sandbox.execute('updpkgsums > /dev/null && cat PKGBUILD',
                                               mounts={'PKGBUILD': pkgbuild_content_updated}) + '\n'
    return pkgbuild_content_updated


@cache
def source_info(pkgbuild_content: str) -> str:
    return sandbox.execute(f"makepkg --printsrcinfo", mounts={'PKGBUILD': pkgbuild_content}) + '\n'
