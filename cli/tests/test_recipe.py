import importlib.util
import sys
from pathlib import Path


def test_submission_recipe_uses_exact_release_archive(tmp_path, monkeypatch):
    script = Path(__file__).resolve().parents[1] / "tools" / "prepare_recipe.py"
    spec = importlib.util.spec_from_file_location("prepare_recipe", script)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    archive = tmp_path / "bileactome-1.0.0.tar.gz"
    archive.write_bytes(b"release bytes")
    output = tmp_path / "meta.yaml"
    url = "https://example.org/releases/cli-v1.0.0/bileactome-1.0.0.tar.gz"
    monkeypatch.setattr(sys, "argv", [str(script), "--archive", str(archive), "--url", url, "--output", str(output)])
    module.main()
    result = output.read_text(encoding="utf-8")
    import hashlib

    assert f"sha256: {hashlib.sha256(archive.read_bytes()).hexdigest()}" in result
    assert url in result
    assert "path: ../.." not in result
    assert "LicenseRef-BileActome-Research-Commercial AND CC-BY-4.0" in result
