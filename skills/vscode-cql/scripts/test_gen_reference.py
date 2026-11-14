"""Offline tests for gen_reference.py, with a small package.json fixture."""
from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import gen_reference as G  # noqa: E402

PKG = {
    "name": "cql", "publisher": "cqframework", "version": "9.9.9",
    "engines": {"vscode": "^1.90.0"},
    "activationEvents": ["workspaceContains:**/*.cql"],
    "javaDependencies": {"cql-language-server": {"groupId": "g", "artifactId": "a", "version": "5.0.0"}},
    "contributes": {
        "commands": [
            {"command": "cql.run", "title": "Execute CQL", "category": "CQL"},
            {"command": "cql.tree.do", "title": "Do | Thing", "category": "CQL Explorer"},
            {"command": "cql.hidden", "title": "Hidden"},
        ],
        "menus": {
            "commandPalette": [{"command": "cql.tree.do", "when": "false"}, {"command": "cql.hidden", "when": "false"}],
            "editor/context": [{"command": "cql.run"}],
            "view/item/context": [{"command": "cql.tree.do", "when": "view == cql-libraries && viewItem == x"}],
        },
        "views": {"explorer": [{"id": "cql-libraries", "name": "CQL Explorer"}],
                  "debug": [{"id": "cql.debug.ast", "name": "CQL AST", "when": "cql.debug.active"}]},
        "debuggers": [{"type": "cql", "configurationAttributes": {"launch": {
            "required": ["libraryUri"],
            "properties": {"libraryUri": {"type": "string"},
                           "stepGranularity": {"type": "string", "enum": ["cql", "ast"], "default": "cql"}}}}}],
        "jsonValidation": [{"fileMatch": "**/input/tests/config.jsonc", "url": "./schemas/x.json"}],
        "configurationDefaults": {"debug.openExplorerOnEnd": True},
        "languages": [{"id": "cql", "extensions": [".cql"], "aliases": ["CQL"]}],
    },
}


def test_where():
    c = PKG["contributes"]
    assert G.where("cql.run", c) == (True, ["editor right-click"])
    assert G.where("cql.tree.do", c) == (False, ["CQL Explorer tree item"])
    assert G.where("cql.hidden", c) == (False, [])


def test_render():
    text = G.render(PKG)
    assert "| CQL: Execute CQL | `cql.run` | yes | editor right-click |" in text
    assert "| CQL Explorer: Do \\| Thing | `cql.tree.do` | no | CQL Explorer tree item |" in text
    assert "| Hidden | `cql.hidden` | no | no menu |" in text
    assert "| `libraryUri` | string | yes |  |  |" in text
    assert "| `stepGranularity` | string (cql / ast) | no | `cql` |" in text
    assert "| VS Code settings contributed | none |" in text
    assert "| `debug.openExplorerOnEnd` | `true` |" in text
    assert "`g:a:5.0.0`" in text
    assert "| CQL AST | `cql.debug.ast` | debug | `cql.debug.active` |" in text


def test_committed_page_is_for_the_pinned_tag():
    text = G.OUT.read_text(encoding="utf-8")
    assert f"from `package.json` at `{G.REF}`" in text
    assert f"Baseline: vscode-cql {G.REF.lstrip('v')}." in text
