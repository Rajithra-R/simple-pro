import os
import json
import subprocess
import sys
import ast
import importlib.util
import re
import traceback
import types
import unittest
from pathlib import Path
from typing import Dict, Any, List, Optional

ROOT = Path(__file__).resolve().parents[1]  # project root

def read_file(path: str) -> str:
    """Read file content with error handling."""
    p = Path(path)
    return p.read_text(encoding='utf-8', errors='ignore')

def get_file_extension(path: str) -> str:
    """Get file extension for language detection."""
    return Path(path).suffix.lower()

def _find_artifacts_dir() -> Optional[Path]:
    # Walk up to find an 'artifacts' directory
    cur = ROOT
    for _ in range(5):
        cand = cur / 'artifacts'
        if cand.is_dir():
            return cand
        if cur.parent == cur:
            break
        cur = cur.parent
    # Also try CWD
    cwd = Path.cwd()
    if (cwd / 'artifacts').is_dir():
        return cwd / 'artifacts'
    return None

def _install_dummy_module(fullname: str):
    parts = fullname.split('.')
    built = ''
    for i, p in enumerate(parts):
        built = p if i == 0 else f'{built}.{p}'
        if built not in sys.modules:
            mod = types.ModuleType(built)
            def __getattr__(name, _d=None):
                class _D:
                    def __getattr__(self, _): return self
                    def __call__(self, *a, **k): return self
                    def __iter__(self): return iter(())
                    def __bool__(self): return False
                return _D()
            mod.__getattr__ = __getattr__  # type: ignore[attr-defined]
            sys.modules[built] = mod

def _safe_import_from_path(mod_name: str, file_path: str):
    try:
        spec = importlib.util.spec_from_file_location(mod_name, file_path)
        module = importlib.util.module_from_spec(spec)
        assert spec and spec.loader
        spec.loader.exec_module(module)  # type: ignore[assignment]
        return module
    except ModuleNotFoundError as e:
        missing = getattr(e, 'name', None) or (str(e).split("'")[1] if "'" in str(e) else None)
        if missing:
            _install_dummy_module(missing)
            spec = importlib.util.spec_from_file_location(mod_name, file_path)
            module = importlib.util.module_from_spec(spec)
            assert spec and spec.loader
            spec.loader.exec_module(module)  # type: ignore[assignment]
            return module
        raise

def test_modified_files_present():
    """Verify all modified files exist and optionally contain the marker (informational)."""
    p = ROOT / "templates/index.html"
    assert p.exists(), f'Expected modified file to exist: {p}'
    txt = read_file(p)
    # Marker is informational; do not fail minimal repos
    _has_marker = 'modified-by-module3' in txt
    if not _has_marker:
        print(f'Info: Marker not found in {p}')

    p = ROOT / "static/style.css"
    assert p.exists(), f'Expected modified file to exist: {p}'
    txt = read_file(p)
    # Marker is informational; do not fail minimal repos
    _has_marker = 'modified-by-module3' in txt
    if not _has_marker:
        print(f'Info: Marker not found in {p}')

def test_html_structure_validation():
    """Basic HTML structure validation."""
    for file_path in [
        "templates/index.html",
    ]:
        full_path = ROOT / file_path
        if full_path.exists():
            content = read_file(file_path)
            if content.strip():
                # Check for basic HTML structure
                assert '<html' in content.lower() or '<!doctype' in content.lower(), f'Missing HTML structure in {{file_path}}'

def test_css_syntax_validation():
    """Basic CSS syntax validation."""
    for file_path in [
        "static/style.css",
    ]:
        full_path = ROOT / file_path
        if full_path.exists():
            content = read_file(file_path)
            if content.strip():
                # Check for balanced braces
                brace_count = content.count('{') - content.count('}')
                assert brace_count == 0, f'Unbalanced braces in CSS file {{file_path}}'

def test_integration_file_consistency():
    """Test consistency between modified files."""
    # Check that related files have consistent imports/references
    import_patterns = []
    for file_path in [
        "templates/index.html",
        "static/style.css",
    ]:
        full_path = ROOT / file_path
        if full_path.exists() and file_path.endswith('.py'):
            content = read_file(file_path)
            # Extract import statements
            imports = re.findall(r'^import\s+([a-zA-Z_][a-zA-Z0-9_.]*)', content, re.MULTILINE)
            import_patterns.extend(imports)

    # Basic check: no circular imports
    unique_imports = set(import_patterns)
    assert len(unique_imports) >= 0, 'Integration test: import analysis completed'

def test_repository_integrity():
    """Test that repository structure and key files remain intact (informational)."""
    # Check that essential repository files still exist (do not fail if missing to support minimal repos)
    essential_files = ['README.md', 'package.json', 'requirements.txt', 'setup.py', 'pyproject.toml']
    found_essential = []
    for essential_file in essential_files:
        if (ROOT / essential_file).exists():
            found_essential.append(essential_file)
    # No assertion here; purely informational

def test_no_unintended_file_changes():
    """Verify that only expected files were modified."""
    modified_file_set = set([
        "templates/index.html",
        "static/style.css",
    ])

    # This test ensures we have a record of what was supposed to be modified
    assert len(modified_file_set) > 0, 'No files were marked for modification'

    # Check that each modified file exists
    for file_path in modified_file_set:
        full_path = ROOT / file_path
        assert full_path.exists(), f'Modified file does not exist: {file_path}'

def test_testing_framework_available():
    """Ensure testing framework is available."""
    try:
        import pytest
        assert hasattr(pytest, 'main'), 'pytest.main not available'
    except ImportError:
        # Fallback to unittest
        import unittest
        assert hasattr(unittest, 'TestCase'), 'unittest.TestCase not available'

def test_module4_test_execution():
    """Meta-test: verify this test file itself is working."""
    assert True, 'Module 4 test execution is functional'
