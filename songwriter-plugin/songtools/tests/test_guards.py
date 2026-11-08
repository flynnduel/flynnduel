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


def test_songtools_error_exit_code_and_stderr_format(monkeypatch, capsys):
    import json
    import sys
    import types

    from songtools import cli

    def handler(args):
        raise cli.SongtoolsError("a.txt", 3, "bad")

    mod = types.ModuleType("fake_boom")
    mod.register = lambda sub: sub.add_parser("boom").set_defaults(handler=handler)
    monkeypatch.setitem(sys.modules, "fake_boom", mod)
    monkeypatch.setattr(cli, "MODULES", ("fake_boom",))
    assert cli.main(["boom"]) == 2
    assert json.loads(capsys.readouterr().err) == {"error": "a.txt:3: bad"}
