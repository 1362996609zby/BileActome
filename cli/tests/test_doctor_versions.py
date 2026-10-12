import pytest

from bileactome.doctor import supported_tool_version


@pytest.mark.parametrize("name,version,supported", [
    ("hmmsearch", "HMMER 3.4 (Aug 2023)", True),
    ("hmmscan", "HMMER 3.3.2", False),
    ("prodigal", "Prodigal V2.6.3: February, 2016", True),
    ("bowtie2", "/prefix/bin/bowtie2-align-s version 2.5.4", True),
    ("bowtie2", "bowtie2 version 2.6.0", False),
    ("bash", "GNU bash, version 5.2.21(1)-release", True),
    ("bash", "GNU bash, version 3.2.57(1)-release", False),
    ("hmmscan", "version unavailable", None),
])
def test_tool_version_compatibility(name, version, supported):
    assert supported_tool_version(name, version) is supported
