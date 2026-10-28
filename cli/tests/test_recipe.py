import importlib.util
import sys
from pathlib import Path


def test_submission_recipe_uses_exact_release_archive(tmp_path, monkeypatch):
    script = Path(__file__).resolve().parents[1] / "tools" / "prepare_recipe.py"
    spec = importlib.util.spec_from_file_location("prepare_recipe", script)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    archive = tmp_path / "bileactome-1.0.1.tar.gz"
    archive.write_bytes(b"release bytes")
    output = tmp_path / "meta.yaml"
    url = "https://example.org/releases/cli-v1.0.1/bileactome-1.0.1.tar.gz"
    monkeypatch.setattr(sys, "argv", [str(script), "--archive", str(archive), "--url", url, "--output", str(output)])
    module.main()
    result = output.read_text(encoding="utf-8")
    import hashlib

    assert f"sha256: {hashlib.sha256(archive.read_bytes()).hexdigest()}" in result
    templated_url = "https://example.org/releases/cli-v{{ version }}/bileactome-{{ version }}.tar.gz"
    assert templated_url in result
    assert templated_url.replace("{{ version }}", "1.0.1") == url
    assert "path: ../.." not in result
    assert "BSD-3-Clause AND CC-BY-4.0" in result
    assert 'run_exports:\n    - {{ pin_subpackage(name, max_pin="x") }}' in result
