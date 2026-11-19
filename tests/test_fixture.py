import json
import re
from pathlib import Path

FIXTURES = Path(__file__).parent / "fixtures"


def test_expected_matches_seeded_markers():
    expected = json.loads((FIXTURES / "expected.json").read_text())["findings"]
    assert len(expected) == 5
    src = (FIXTURES / "vulnerable-app" / "app.py").read_text()
    seeded = re.findall(r"SEEDED VULN \d+ \((CWE-\d+)\)", src)
    assert sorted(seeded) == sorted(e["cwe"] for e in expected)
    for e in expected:
        assert (FIXTURES / "vulnerable-app" / e["file"]).is_file()
