import copy

import pytest
from pydantic import ValidationError

from sask.schema import SCHEMA_VERSION, Evidence, Finding

BASE = {
    "id": "F-001",
    "title": "SQL injection in login",
    "cwe": "CWE-89",
    "severity": "high",
    "evidence": "scanner-only",
    "source": "semgrep",
    "location": {"file": "app.py", "line_start": 10, "line_end": 12},
    "description": "d",
    "impact": "i",
}
POC = {"path": "poc.py", "command": "python poc.py", "exit_code": 0, "log_path": "poc.log"}
PATCH = {"diff_path": "f.diff", "retest_passed": True, "tests_passed": True}


def make(**over):
    d = copy.deepcopy(BASE)
    d.update(over)
    return d


def test_valid_minimal_defaults():
    f = Finding.model_validate(BASE)
    assert f.schema_version == SCHEMA_VERSION
    assert f.status == "open" and f.poc is None and f.patch is None


def test_valid_reproduced_with_poc_and_patch():
    f = Finding.model_validate(
        make(evidence="reproduced", poc=POC, patch=PATCH, status="fixed-proposed")
    )
    assert f.evidence is Evidence.REPRODUCED


def test_json_roundtrip():
    f = Finding.model_validate(make(evidence="reproduced", poc=POC))
    assert Finding.model_validate_json(f.model_dump_json()) == f


def test_reproduced_without_poc_rejected():
    with pytest.raises(ValidationError, match="log_path"):
        Finding.model_validate(make(evidence="reproduced"))


@pytest.mark.parametrize("log", [None, ""])
def test_reproduced_without_log_rejected(log):
    with pytest.raises(ValidationError, match="log_path"):
        Finding.model_validate(make(evidence="reproduced", poc={**POC, "log_path": log}))


def test_fixed_status_requires_patch():
    with pytest.raises(ValidationError, match="requires a patch"):
        Finding.model_validate(make(status="applied"))


@pytest.mark.parametrize(
    "over",
    [
        {"cwe": "89"},
        {"severity": "urgent"},
        {"evidence": "proven"},
        {"status": "closed"},
        {"location": {"file": "a.py", "line_start": 5, "line_end": 2}},
        {"schema_version": "2"},
        {"extra": 1},
    ],
)
def test_invalid_rejected(over):
    with pytest.raises(ValidationError):
        Finding.model_validate(make(**over))
