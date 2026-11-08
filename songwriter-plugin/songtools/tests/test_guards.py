import importlib.metadata as md
import urllib.request

import pytest

from songtools.cli import main


def test_network_is_disabled_in_tests():
    with pytest.raises(RuntimeError, match="network disabled"):
        urllib.request.urlopen("https://example.com", timeout=2)


def test_no_gpl_family_licenses_installed():
    bad = []
    for d in md.distributions():
        meta = d.metadata
        # The License field sometimes holds a full license text (e.g. matplotlib
        # bundles third-party notices mentioning GPL); only short values are identifiers.
        short = meta.get("License")
        short = short if short and len(short) <= 200 else None
        lic = " ".join(
            filter(
                None,
                [meta.get("License-Expression"), short]
                + [c for c in meta.get_all("Classifier") or [] if c.startswith("License")],
            )
        )
        if "GPL" in lic.upper():
            bad.append(meta["Name"])
    assert bad == []


def test_version_subcommand(capsys):
    assert main(["version"]) == 0
    assert '"version"' in capsys.readouterr().out
