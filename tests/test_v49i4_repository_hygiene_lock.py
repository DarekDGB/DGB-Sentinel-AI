from __future__ import annotations

import json
import re
import subprocess
import sys
import unicodedata
from pathlib import Path

import sentinel_ai_v2.cli as cli
import sentinel_ai_v2.server as server
from sentinel_ai_v2 import __version__
from sentinel_ai_v2.contracts.v3_2_lock import (
    COMPONENT_ID,
    CONTRACT_VERSION,
    PACKAGE_VERSION,
    build_manifest,
)

ALLOWED_ATTRIBUTION = "DarekDGB"
CURRENT_VERSION = "3.2.0"
LEGACY_DOCUMENTS = (
    "docs/legacy/ATTACK-SIMULATION-REPORT.md",
    "docs/legacy/whitepaper-sentinel-ai-v2.md",
)
ACTIVE_VERSION_SOURCES = (
    "src/sentinel_ai_v2/__init__.py",
    "src/sentinel_ai_v2/cli.py",
    "src/sentinel_ai_v2/server.py",
)

_GENERATED_DIRECTORY_NAMES = frozenset(
    {
        ".git",
        ".mypy_cache",
        ".pytest_cache",
        ".ruff_cache",
        ".tox",
        ".venv",
        "__pycache__",
        "build",
        "dist",
        "venv",
    }
)
_GENERATED_FILE_NAMES = frozenset({".coverage", "coverage.xml"})
_ATTRIBUTION_LINE = re.compile(
    r"^(?:author(?:s|\s+attribution)?|co-author|co-authored-by|"
    r"maintainer(?:s)?|attribution|"
    r"(?:ai|engineering)\s+assistant|created\s+by|developed\s+by|"
    r"written\s+by|engineered\s+by)"
    r"\s*:\s*(?P<value>.+?)\s*$",
    re.IGNORECASE,
)
_LEGACY_AI_ENGINEERING_LINE = re.compile(
    r"^engineering\s*:\s*(?P<value>.+?\(\s*AI\s+Assistant\s*\))\s*$",
    re.IGNORECASE,
)
_BYLINE = re.compile(
    r"^(?i:by)\s+(?P<value>@[A-Za-z0-9_][A-Za-z0-9_.-]*|"
    r"[^\W\d_][\w'.-]*(?:\s+[^\W\d_][\w'.-]*){0,3})\s*$"
)
_STRUCTURED_ATTRIBUTION_LINE = re.compile(
    r"""^["'](?:author|authors|author_attribution|maintainer|maintainers|"""
    r"""created_by|creator)["']\s*:\s*"""
    r"""["'](?P<value>[^"']+)["']\s*,?\s*$""",
    re.IGNORECASE,
)
_ASSIGNED_ATTRIBUTION_LINE = re.compile(
    r"^(?:__authors?__|authors?|author_attribution|maintainers?|creator)\s*=\s*"
    r"[\"'](?P<value>[^\"']+)[\"']\s*$",
    re.IGNORECASE,
)
_ATTRIBUTION_LIST_LINE = re.compile(
    r"^(?:[\"']?(?:authors|maintainers)[\"']?)\s*(?::|=)\s*"
    r"\[(?P<values>.*)\]\s*,?\s*$",
    re.IGNORECASE,
)
_INLINE_BYLINE = re.compile(
    r"\b(?i:architecture(?:\s*&\s*implementation)?|implementation|authored|"
    r"written|developed|created|engineered|maintained)\s+(?i:by)\s+"
    r"(?P<value>@[A-Za-z0-9_][A-Za-z0-9_.-]*|"
    r"[A-Z][A-Za-z0-9_.-]*(?:\s+[A-Z][A-Za-z0-9_.-]*)*)\b"
)
_ATTRIBUTION_HEADINGS = frozenset(
    {
        "author",
        "authors",
        "author attribution",
        "attribution",
        "maintainer",
        "maintainers",
    }
)
_COPYRIGHT_LINE = re.compile(
    r"^copyright\s+(?:\(c\)|\N{COPYRIGHT SIGN})\s+\d{4}(?:-\d{4})?"
    r"(?:\s+(?P<value>.+?))?\s*$",
    re.IGNORECASE,
)
_COPYRIGHT_SIGN_LINE = re.compile(
    r"^\N{COPYRIGHT SIGN}\s+\d{4}(?:-\d{4})?\s+(?P<value>.+?)\s*$"
)


def _repo_root() -> Path:
    current = Path(__file__).resolve()
    for candidate in current.parents:
        if (candidate / "pyproject.toml").is_file() and (
            candidate / "src" / "sentinel_ai_v2"
        ).is_dir():
            return candidate
    raise AssertionError("repository root not found")


def _is_generated(path: Path, root: Path) -> bool:
    relative = path.relative_to(root)
    return (
        _is_runtime_liboqs_checkout_path(path, root)
        or path.name in _GENERATED_FILE_NAMES
        or path.suffix in {".pyc", ".pyo"}
        or any(part in _GENERATED_DIRECTORY_NAMES for part in relative.parts)
        or any(part.endswith((".egg-info", ".dist-info")) for part in relative.parts)
    )


def _is_runtime_liboqs_checkout_path(path: Path, root: Path) -> bool:
    """Recognize only the workflow's real top-level liboqs checkout shape."""
    checkout = root / "liboqs"
    git_directory = checkout / ".git"
    if (
        checkout.is_symlink()
        or git_directory.is_symlink()
        or not checkout.is_dir()
        or not git_directory.is_dir()
    ):
        return False
    try:
        path.relative_to(checkout)
    except ValueError:
        return False
    return True


def _git_tracked_files(root: Path) -> list[Path] | None:
    git_marker = root / ".git"
    if not git_marker.exists() or git_marker.is_symlink():
        return None

    completed = subprocess.run(
        ("git", "-C", str(root), "ls-files", "-z"),
        check=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
    )
    relative_names = completed.stdout.decode("utf-8", errors="strict").split("\0")
    tracked: list[Path] = []
    for relative_name in relative_names:
        if not relative_name:
            continue
        candidate = root / relative_name
        try:
            candidate.relative_to(root)
        except ValueError as exc:
            raise AssertionError("git reported a path outside the repository") from exc
        if candidate.is_file():
            tracked.append(candidate)
    return sorted(tracked)


def _repository_files(root: Path | None = None) -> list[Path]:
    root = _repo_root() if root is None else root
    tracked = _git_tracked_files(root)
    if tracked is not None:
        return tracked
    return sorted(
        path for path in root.rglob("*") if path.is_file() and not _is_generated(path, root)
    )


def _display(path: Path) -> str:
    return path.relative_to(_repo_root()).as_posix()


def _text_files() -> list[tuple[Path, str]]:
    return [(path, path.read_bytes().decode("utf-8")) for path in _repository_files()]


def _known_mojibake_markers() -> tuple[str, ...]:
    codepoint_sequences = (
        (0x00C2,),
        (0x00C3,),
        (0x00E2, 0x0153),
        (0x00E2, 0x20AC),
        (0x00EF, 0x00BB, 0x00BF),
        (0x00F0, 0x0178),
    )
    return tuple(
        "".join(chr(codepoint) for codepoint in sequence) for sequence in codepoint_sequences
    )


def _plain_metadata_line(line: str) -> str:
    plain = line.strip().replace("*", "").replace("`", "")
    plain = plain.lstrip("#").strip()
    return re.sub(r"^(?:[-+>]\s+|\d+[.)]\s+)", "", plain).strip()


def _normalize_attribution(value: str) -> str:
    normalized = _plain_metadata_line(value).strip().strip("\"'")
    normalized = re.sub(r"\s+<[^<>]+>$", "", normalized).strip()
    if normalized.startswith("@"):
        normalized = normalized[1:]
    return normalized.strip()


def _attribution_declarations(text: str) -> list[tuple[int, str]]:
    """Return line-numbered values from explicit attribution declarations."""
    lines = text.splitlines()
    declarations: list[tuple[int, str]] = []

    for index, line in enumerate(lines):
        line_number = index + 1
        plain = _plain_metadata_line(line)

        if line.lstrip().startswith("#") and plain.casefold() in _ATTRIBUTION_HEADINGS:
            for value_index in range(index + 1, len(lines)):
                value_line = lines[value_index]
                if not value_line.strip():
                    continue
                declarations.append(
                    (value_index + 1, _normalize_attribution(value_line))
                )
                break
            continue

        match = _ATTRIBUTION_LINE.fullmatch(plain)
        if match is None:
            match = _LEGACY_AI_ENGINEERING_LINE.fullmatch(plain)
        if match is None:
            match = _BYLINE.fullmatch(plain)
        if match is None:
            match = _STRUCTURED_ATTRIBUTION_LINE.fullmatch(plain)
        if match is None:
            match = _ASSIGNED_ATTRIBUTION_LINE.fullmatch(plain)
        if match is not None:
            declarations.append(
                (line_number, _normalize_attribution(match.group("value")))
            )
            continue

        list_match = _ATTRIBUTION_LIST_LINE.fullmatch(plain)
        if list_match is not None:
            values = [
                value
                for value in re.findall(
                    r"[\"']([^\"']+)[\"']", list_match.group("values")
                )
                if value.casefold() != "name"
            ]
            if not values:
                declarations.append((line_number, ""))
            else:
                declarations.extend(
                    (line_number, _normalize_attribution(value)) for value in values
                )
            continue

        inline_match = _INLINE_BYLINE.search(plain)
        if inline_match is not None:
            declarations.append(
                (line_number, _normalize_attribution(inline_match.group("value")))
            )
            continue

        copyright_match = _COPYRIGHT_LINE.fullmatch(plain)
        if copyright_match is None:
            copyright_match = _COPYRIGHT_SIGN_LINE.fullmatch(plain)
        if copyright_match is not None and copyright_match.group("value") is not None:
            declarations.append(
                (
                    line_number,
                    _normalize_attribution(copyright_match.group("value")),
                )
            )

    return declarations


def _project_metadata_text() -> str:
    return (_repo_root() / "pyproject.toml").read_text(encoding="utf-8")


def _project_version() -> str:
    match = re.search(
        r'(?m)^version\s*=\s*"(?P<value>[^"]+)"\s*$',
        _project_metadata_text(),
    )
    assert match is not None, "pyproject.toml project version not found"
    return match.group("value")


def _project_authors() -> list[str]:
    match = re.search(
        r"(?m)^authors\s*=\s*\[\{\s*name\s*=\s*"
        r'"(?P<value>[^"]+)"\s*\}\]\s*$',
        _project_metadata_text(),
    )
    assert match is not None, "pyproject.toml project authors not found"
    return [match.group("value")]


def test_repository_text_is_strict_utf8_nfc_lf_and_mojibake_free() -> None:
    failures: list[str] = []
    markers = _known_mojibake_markers()

    for path in _repository_files():
        raw = path.read_bytes()
        relative = _display(path)
        if raw and not raw.endswith(b"\n"):
            failures.append(f"{relative}: missing terminal LF")
        if raw.startswith(bytes((0xEF, 0xBB, 0xBF))):
            failures.append(f"{relative}: UTF-8 BOM")
        if bytes((0,)) in raw:
            failures.append(f"{relative}: NUL byte")
        if bytes((13,)) in raw:
            failures.append(f"{relative}: CR byte")
        try:
            text = raw.decode("utf-8", errors="strict")
        except UnicodeDecodeError as exc:
            failures.append(f"{relative}: invalid UTF-8 at byte {exc.start}")
            continue
        if text != unicodedata.normalize("NFC", text):
            failures.append(f"{relative}: text is not NFC-normalized")
        if chr(0xFFFD) in text:
            failures.append(f"{relative}: replacement character")
        if any(0x80 <= ord(character) <= 0x9F for character in text):
            failures.append(f"{relative}: C1 control character")
        if any(marker in text for marker in markers):
            failures.append(f"{relative}: known mojibake marker")

    assert failures == [], "repository text hygiene failures:\n" + "\n".join(failures)


def test_repository_author_attribution_is_darekdgb_only() -> None:
    failures: list[str] = []
    declarations = 0

    for path, text in _text_files():
        for line_number, value in _attribution_declarations(text):
            declarations += 1
            if value != ALLOWED_ATTRIBUTION:
                failures.append(f"{_display(path)}:{line_number}: non-canonical attribution")

    package_authors = _project_authors()
    declarations += len(package_authors)
    if package_authors != [ALLOWED_ATTRIBUTION]:
        failures.append(
            "pyproject.toml: project authors must contain only the canonical attribution"
        )

    assert declarations >= 10, "expected repository attribution declarations were not found"
    assert failures == [], "author attribution lock failures:\n" + "\n".join(failures)


def test_active_version_identity_is_exactly_v3_2_0(capsys) -> None:
    manifest = build_manifest()

    assert __version__ == CURRENT_VERSION
    assert server.app.version == CURRENT_VERSION
    assert _project_version() == CURRENT_VERSION
    assert PACKAGE_VERSION == CURRENT_VERSION
    assert manifest["package_version"] == CURRENT_VERSION
    assert CONTRACT_VERSION == manifest["contract_version"] == 3
    assert COMPONENT_ID == manifest["component_id"] == "sentinel_ai"

    assert cli.main(["version"]) == 0
    output = json.loads(capsys.readouterr().out)
    assert output["sentinel_ai_v2"] == CURRENT_VERSION

    root = _repo_root()
    for relative in ACTIVE_VERSION_SOURCES:
        text = (root / relative).read_text(encoding="utf-8")
        assert '"3.1.0"' not in text
        assert f'"{CURRENT_VERSION}"' in text


def test_legacy_documents_are_historical_non_authoritative_and_darekdgb_only() -> None:
    root = _repo_root()

    for relative in LEGACY_DOCUMENTS:
        text = (root / relative).read_text(encoding="utf-8")
        normalized = " ".join(text.split())
        assert "Author attribution: DarekDGB" in text
        assert "Status: Historical and non-authoritative" in text
        assert "docs/CONTRACT.md" in text
        assert "docs/ARCHITECTURE.md" in text
        assert "docs/v4/CONTRACT.md" in text
        assert "transaction-signing" in normalized
        assert "broadcast" in normalized
        assert "DigiByte consensus" in normalized
        assert "AdamantineOS remains the final fail-closed policy and execution boundary" in normalized


def test_attack_scenario_is_locked_as_synthetic_not_executed_proof() -> None:
    text = (_repo_root() / LEGACY_DOCUMENTS[0]).read_text(encoding="utf-8")
    normalized = " ".join(text.split()).casefold()

    assert "synthetic scenario only" in normalized
    assert "were not executed" in normalized
    assert "does not prove" in normalized
    assert "testnet" in normalized
    assert "mainnet" in normalized
    assert "production system" in normalized
    assert "this proves the power" not in normalized


def test_hygiene_detectors_cover_transfer_damage_and_noncanonical_attribution() -> None:
    markers = _known_mojibake_markers()
    assert all(markers)
    assert any(0x80 <= ord(character) <= 0x9F for character in chr(0x80))
    assert unicodedata.normalize("NFC", "Cafe\N{COMBINING ACUTE ACCENT}") == "Caf\N{LATIN SMALL LETTER E WITH ACUTE}"

    other_author = "Other" + "Author"
    other_handle = "@" + "otherauthor"
    canonical_samples = (
        f"Author: {ALLOWED_ATTRIBUTION}",
        f"## Author\n\n{ALLOWED_ATTRIBUTION}",
        f"Architecture & Implementation by @{ALLOWED_ATTRIBUTION} - MIT",
        f"Written by {ALLOWED_ATTRIBUTION}",
        f'__author__ = "{ALLOWED_ATTRIBUTION}"',
        f'authors = ["{ALLOWED_ATTRIBUTION}"]',
        f'"author_attribution": "{ALLOWED_ATTRIBUTION}"',
        f"Copyright (c) 2026 {ALLOWED_ATTRIBUTION}",
        f"Co-authored-by: {ALLOWED_ATTRIBUTION} <author@example.invalid>",
    )
    noncanonical_samples = (
        f"Author: {other_author}",
        f"## Maintainer\n\n{other_author}",
        f"Implementation by @{other_author}",
        f"By {other_author}",
        f"By {other_handle}",
        "By " + "otherauthor",
        f"Written by {other_author}",
        f"Written by {other_handle}",
        f"Architecture & Implementation by {other_author}",
        f"Maintained by {other_author}",
        f'__author__ = "{other_author}"',
        f'__authors__ = "{other_author}"',
        f'authors = "{other_author}"',
        f'"authors": ["{other_author}"]',
        f'"author": "{other_author}"',
        f"Engineering: {other_author} (AI {'Assist' + 'ant'})",
        f"Co-authored-by: {other_author} <other@example.invalid>",
    )

    for sample in canonical_samples:
        assert [value for _, value in _attribution_declarations(sample)] == [
            ALLOWED_ATTRIBUTION
        ]
    for sample in noncanonical_samples:
        values = [value for _, value in _attribution_declarations(sample)]
        assert values and values != [ALLOWED_ATTRIBUTION]

    assert _attribution_declarations("Project office: Los Angeles\n") == []
    assert _attribution_declarations("Assistant: disabled\n") == []
    assert _attribution_declarations("Engineering: enabled\n") == []


def test_runtime_liboqs_checkout_exclusion_is_narrow(tmp_path: Path) -> None:
    ordinary_root = tmp_path / "ordinary"
    ordinary_file = ordinary_root / "liboqs" / "src" / "ordinary.c"
    ordinary_file.parent.mkdir(parents=True)
    ordinary_file.write_text("ordinary\n", encoding="utf-8")
    assert not _is_runtime_liboqs_checkout_path(ordinary_file, ordinary_root)

    checkout_root = tmp_path / "checkout"
    checkout_file = checkout_root / "liboqs" / "src" / "upstream.c"
    checkout_file.parent.mkdir(parents=True)
    (checkout_root / "liboqs" / ".git").mkdir()
    checkout_file.write_text("upstream\n", encoding="utf-8")
    assert _is_runtime_liboqs_checkout_path(checkout_file, checkout_root)
    assert _is_generated(checkout_file, checkout_root)

    file_marker_root = tmp_path / "file-marker"
    file_marker = file_marker_root / "liboqs" / ".git"
    file_marker.parent.mkdir(parents=True)
    file_marker.write_text("gitdir: elsewhere\n", encoding="utf-8")
    file_marker_child = file_marker_root / "liboqs" / "src.c"
    file_marker_child.write_text("source\n", encoding="utf-8")
    assert not _is_runtime_liboqs_checkout_path(file_marker_child, file_marker_root)

    nested_root = tmp_path / "nested"
    nested_file = nested_root / "docs" / "liboqs" / "src" / "nested.c"
    nested_file.parent.mkdir(parents=True)
    (nested_root / "docs" / "liboqs" / ".git").mkdir()
    nested_file.write_text("nested\n", encoding="utf-8")
    assert not _is_runtime_liboqs_checkout_path(nested_file, nested_root)

    symlink_root = tmp_path / "symlink"
    symlink_target = tmp_path / "symlink-target"
    (symlink_target / ".git").mkdir(parents=True)
    symlink_root.mkdir()
    (symlink_root / "liboqs").symlink_to(symlink_target, target_is_directory=True)
    assert not _is_runtime_liboqs_checkout_path(
        symlink_root / "liboqs" / "source.c", symlink_root
    )


def test_repository_inventory_prefers_tracked_files_and_has_safe_zip_fallback(
    tmp_path: Path, monkeypatch
) -> None:
    root = tmp_path / "repository"
    tracked_generated = root / "build" / "tracked.txt"
    tracked_generated.parent.mkdir(parents=True)
    tracked_generated.write_text("tracked\n", encoding="utf-8")
    ordinary = root / "src" / "ordinary.py"
    ordinary.parent.mkdir()
    ordinary.write_text("ordinary\n", encoding="utf-8")
    cache = root / "src" / "__pycache__" / "cache.pyc"
    cache.parent.mkdir()
    cache.write_bytes(b"cache")
    checkout = root / "liboqs"
    (checkout / ".git").mkdir(parents=True)
    upstream = checkout / "upstream.bin"
    upstream.write_bytes(b"upstream")

    module = sys.modules[__name__]
    monkeypatch.setattr(
        module, "_git_tracked_files", lambda selected_root: [tracked_generated]
    )
    assert _repository_files(root) == [tracked_generated]

    monkeypatch.setattr(module, "_git_tracked_files", lambda selected_root: None)
    assert _repository_files(root) == [ordinary]


def test_repaired_adaptive_bridge_comment_is_ascii_and_encoding_clean() -> None:
    path = _repo_root() / "tests/test_coverage_adaptive_core_bridge_and_hooks.py"
    raw = path.read_bytes()

    assert raw.isascii()
    assert b"# Force the available path." in raw
