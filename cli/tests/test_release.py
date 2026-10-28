import json
import pytest

from bileactome.cli import main
from bileactome.selftest import locate_fixture, locate_mag_fixture


def test_selftest_data_available_outside_source_tree(tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    fixture = locate_fixture()
    assert "data/toy" in fixture.as_posix()
    assert (fixture / "gene_catalog" / "toy_unigenes.protein.fa").is_file()
    assert len(list((fixture / "clean_reads").glob("*.fastq.gz"))) == 4
    assert (locate_mag_fixture(fixture) / "toy_genome.fna").is_file()


def test_banner_does_not_corrupt_json(capsys):
    with pytest.raises(SystemExit) as exc:
        main(["--banner", "db", "verify"])
    assert exc.value.code == 0
    captured = capsys.readouterr()
    assert json.loads(captured.out)["passed"] == 27
    assert "BileActome CLI" in captured.err


def test_no_args_help_exits_successfully(capsys):
    with pytest.raises(SystemExit) as exc:
        main(["--no-banner"])
    assert exc.value.code == 0
    assert "usage: bileactome" in capsys.readouterr().out


def test_version_is_one_line(capsys):
    with pytest.raises(SystemExit) as exc:
        main(["--version"])
    assert exc.value.code == 0
    captured = capsys.readouterr()
    assert captured.out == "BileActome 1.0.1\n"
    assert captured.err == ""


def test_license_summary_marks_cc_exception(capsys):
    with pytest.raises(SystemExit) as exc:
        main(["license", "--no-banner"])
    assert exc.value.code == 0
    text = capsys.readouterr().out
    assert "China Agricultural University" in text
    assert "BSD-3-Clause" in text
    assert "prior written authorization required" not in text
    assert "commercial reuse permitted" in text
    assert "Bing Wang: wangb@cau.edu.cn" in text
    assert "Boyan Zhang: 1362996609zby@gmail.com" in text
    assert not any("\u4e00" <= character <= "\u9fff" for character in text)


def test_workflow_logs_stay_off_json_stdout(tmp_path, capsys):
    from bileactome.utils import setup_logging

    logger = setup_logging(tmp_path / "run.log")
    logger.info("workflow progress")
    print(json.dumps({"ok": True}))
    captured = capsys.readouterr()
    assert json.loads(captured.out) == {"ok": True}
    assert "workflow progress" in captured.err
    for handler in list(logger.handlers):
        handler.close()
        logger.removeHandler(handler)
