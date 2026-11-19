"""Finding schema (SPEC sections 6 and 7). Versioned via SCHEMA_VERSION."""

from __future__ import annotations

from enum import StrEnum
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field, model_validator

SCHEMA_VERSION = "1"


class Severity(StrEnum):
    INFO = "info"
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


class Evidence(StrEnum):
    REPRODUCED = "reproduced"
    PLAUSIBLE = "plausible"
    SCANNER_ONLY = "scanner-only"
    REFUTED = "refuted"


class Status(StrEnum):
    OPEN = "open"
    FIXED_PROPOSED = "fixed-proposed"
    APPLIED = "applied"
    DISMISSED = "dismissed"


class _Model(BaseModel):
    model_config = ConfigDict(extra="forbid")


class Location(_Model):
    file: str = Field(min_length=1)
    line_start: int = Field(ge=1)
    line_end: int = Field(ge=1)

    @model_validator(mode="after")
    def _ordered(self) -> Location:
        if self.line_end < self.line_start:
            raise ValueError("line_end must be >= line_start")
        return self


class Poc(_Model):
    path: str = Field(min_length=1)
    command: str = Field(min_length=1)
    exit_code: int
    log_path: str | None = None


class Patch(_Model):
    diff_path: str = Field(min_length=1)
    retest_passed: bool
    # None: repo has no detected tests, so none were run.
    tests_passed: bool | None = None


class Finding(_Model):
    schema_version: Literal["1"] = SCHEMA_VERSION
    id: str = Field(min_length=1)
    title: str = Field(min_length=1)
    cwe: str = Field(pattern=r"^CWE-\d+$")
    severity: Severity
    evidence: Evidence
    source: str = Field(min_length=1)  # scanner name or "agent"
    location: Location
    description: str
    impact: str
    reachability_notes: str = ""
    poc: Poc | None = None
    patch: Patch | None = None
    status: Status = Status.OPEN

    @model_validator(mode="after")
    def _rules(self) -> Finding:
        # SPEC section 6: never `reproduced` without a saved PoC and log.
        if self.evidence is Evidence.REPRODUCED and (self.poc is None or not self.poc.log_path):
            raise ValueError("evidence 'reproduced' requires a poc with a log_path")
        if self.status in (Status.FIXED_PROPOSED, Status.APPLIED) and self.patch is None:
            raise ValueError(f"status '{self.status.value}' requires a patch")
        return self
