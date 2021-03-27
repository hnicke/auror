from pathlib import Path

from pytest import fixture

from auror import pkgbuild

resources = Path(__file__).parent / 'resources'


def test_sources(pulumi_pkgbuild: str):
    result = pkgbuild.sources(pulumi_pkgbuild)
    expected = ["https://get.pulumi.com/releases/sdk/pulumi-v2.23.2-linux-x64.tar.gz"]
    assert result == expected


@fixture
def pulumi_pkgbuild() -> str:
    return (resources / 'pulumi.PKGBUILD').read_text()
