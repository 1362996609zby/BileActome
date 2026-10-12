from bileactome.database import verify_database


def test_packaged_database_has_27_verified_profiles():
    report = verify_database()
    assert report["ok"], report["errors"]
    assert report["passed"] == 27

