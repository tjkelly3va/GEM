#!/usr/bin/env python3
"""
gem_audit.py — GEM canonical-files drift audit and autofix tool.

Purpose
-------
Detect and (where mechanical) repair drift across the GEM project's canonical
files. Designed to be run at every session boundary so that human session time
is spent on features, not on hand-cataloguing drift.

Usage
-----
    gem_audit.py [--files-dir DIR] [--output-dir DIR] [--handoff PATH] [--autofix] [--json]

    --files-dir DIR    Directory containing the canonical files (default: .).
                       May be read-only; the script reads but never writes here
                       unless --output-dir is omitted.
    --output-dir DIR   Where to write autofix-modified files. Defaults to
                       --files-dir (in-place). Use this when --files-dir is
                       read-only — e.g., --files-dir /mnt/user-data/uploads/
                       --output-dir /mnt/user-data/outputs/. Only files that
                       autofix actually modifies are written; unchanged files
                       are not copied.
    --handoff PATH     Handoff document for §1 hash table (default: auto-find
                       latest GEM_Policy-Extraction_Handoff_*.md in --files-dir)
    --autofix          Apply mechanical-only fixes; never touches anything
                       requiring judgment.
    --json             Emit findings as JSON instead of pretty output.

Exit codes
----------
    0 — all GREEN
    1 — YELLOW findings present (drift, but nothing contradictory)
    2 — at least one RED finding (contradiction; halt)

Design principles
-----------------
1. The graph is the truth. When the graph and documentation disagree,
   documentation is wrong (unless the disagreement is itself the finding).
2. Autofix is for mechanical substitutions only. Anything requiring
   judgment surfaces as a YELLOW finding for human resolution.
3. The audit is fast (parses are cached, no PDF reading) — sub-second over
   the canonical-file set.
4. Findings carry enough context for the human reader to act without
   re-doing the audit's work.
"""

from __future__ import annotations

import argparse
import dataclasses
import hashlib
import json
import re
import sys
from collections import Counter, defaultdict
from pathlib import Path
from typing import Callable, Optional

try:
    import rdflib
    from rdflib import Namespace, URIRef
except ImportError:
    sys.stderr.write("ERROR: gem_audit.py requires rdflib. Install with:\n")
    sys.stderr.write("    pip install rdflib --break-system-packages\n")
    sys.exit(2)


# --- Constants ---------------------------------------------------------------

CANONICAL_FILES = [
    "GEM_ontology.ttl",
    "GEM_policy_instances.ttl",
    "GEM_code_group_instances.ttl",
    "cpt.ttl",  # S88: CPT fixture, hash-tracked source artifact. NOT in TTL_FILES (decoupled cpt: source, LF-authored, no gem: reference; never parsed into the audit graph).
    "SKILL.md",
    "gem_reference.md",
    "gem_rule_categories.md",
    "gem_edit_log.md",  # S255: chronological corpus edit log, split out of gem_rule_categories.md (was a mid-file `## Edit log` H2).
    "gem_structured_rule_guide.md",
    "gem_turtle_style_guide.md",
    "manifest_format.md",
    "policy_worklist.json",
    "gem_llm_annotations.json",  # S140: external mirror of individual-level gem:llm* annotations on controlled-vocab individuals. Hash-tracked; NOT in TTL_FILES/MARKDOWN_FILES (JSON, never parsed into the audit graph). Content parity to the graph is guarded by check_llm_annotation_drift.
    "worklist_schema.md",
    "gem_audit.py",  # Self-tracked: the audit script's own hash is verified at every session
]

TTL_FILES = {"GEM_ontology.ttl", "GEM_policy_instances.ttl", "GEM_code_group_instances.ttl"}
MARKDOWN_FILES = {
    "SKILL.md",
    "gem_reference.md",
    "gem_rule_categories.md",
    "gem_edit_log.md",
    "gem_structured_rule_guide.md",
    "gem_turtle_style_guide.md",
    "manifest_format.md",
    "worklist_schema.md",
}

# GEM / GEMI are the data namespace the audit keys every graph query off.
# They are RUNTIME-DETECTED from the audited ontology's own `@prefix gem:` /
# `@prefix gemi:` declarations (see detect_gem_namespace + audit_files_dict), so
# a version bump of the namespace (e.g. .../2026/07/GEM/ -> .../2026/08/GEM/)
# needs NO edit here. The literals below are only a fallback used when the
# ontology cannot be read for detection; keep them at the most recent known
# namespace so a detection miss still degrades to a working default.
GEM = Namespace("http://www.cms.hhs.gov/ontology/2026/08/GEM/")
GEMI = Namespace("http://www.cms.hhs.gov/ontology/2026/08/GEM/instances/")
DC = Namespace("http://purl.org/dc/elements/1.1/")

# Frozen namespace used by the embedded self-test fixtures (see the --self-test
# region below, where the fixture TTL literals declare it). It is a fixed,
# arbitrary test namespace and is deliberately INDEPENDENT of the detected
# GEM/GEMI: check_selftest_harness_integrity temporarily binds GEM/GEMI to it
# while running the fixture suite, so the suite exercises the (namespace-
# parametric) check logic against fixtures at a stable namespace regardless of
# which namespace the real audited files use.
_SELFTEST_GEM = Namespace("http://www.cms.hhs.gov/ontology/2026/07/GEM/")
_SELFTEST_GEMI = Namespace("http://www.cms.hhs.gov/ontology/2026/07/GEM/instances/")


def detect_gem_namespace(files: dict[str, bytes]) -> tuple[Namespace, Namespace]:
    """Read the GEM / GEMI base IRIs from the audited files' own @prefix
    declarations so the audit follows a namespace version bump without a code
    edit. Authority order: GEM_ontology.ttl, then GEM_policy_instances.ttl,
    then GEM_code_group_instances.ttl. The `gem:` prefix is read directly; the
    `gemi:` prefix is read directly when present, else derived as gem +
    "instances/". Falls back to the module-level GEM/GEMI literals if no
    declaration is found (e.g. an unreadable/absent ontology)."""
    gem_re = re.compile(rb'@prefix\s+gem:\s*<([^>]+)>')
    gemi_re = re.compile(rb'@prefix\s+gemi:\s*<([^>]+)>')
    gem_uri = None
    gemi_uri = None
    for name in ("GEM_ontology.ttl", "GEM_policy_instances.ttl",
                 "GEM_code_group_instances.ttl"):
        data = files.get(name)
        if not data:
            continue
        if gem_uri is None:
            m = gem_re.search(data)
            if m:
                gem_uri = m.group(1).decode("utf-8")
        if gemi_uri is None:
            m = gemi_re.search(data)
            if m:
                gemi_uri = m.group(1).decode("utf-8")
        if gem_uri is not None:
            break
    if gem_uri is None:
        return GEM, GEMI  # fallback: module defaults
    if gemi_uri is None:
        gemi_uri = gem_uri + "instances/"
    return Namespace(gem_uri), Namespace(gemi_uri)

# gem_reference.md §5.3: the URI suffix marking a transmittal-retired policy.
# Single source of truth — read by check_proposal_b (Category B) and
# check_deleted_twin_collision (S146).
_DELETED_SUFFIX = "_DELETED"


# --- Finding type ------------------------------------------------------------

@dataclasses.dataclass
class Finding:
    """A single audit observation."""

    tier: str               # 'RED' | 'YELLOW' | 'GREEN'
    category: str           # short category name, e.g. 'hash_verify'
    message: str            # human-readable description
    file: Optional[str] = None
    location: Optional[str] = None     # e.g. "line 125", URI, etc.
    autofixable: bool = False
    autofix_fn: Optional[Callable] = None  # closure that applies the fix
    autofix_description: Optional[str] = None  # human-readable summary of fix

    def to_dict(self) -> dict:
        return {
            "tier": self.tier,
            "category": self.category,
            "message": self.message,
            "file": self.file,
            "location": self.location,
            "autofixable": self.autofixable,
            "autofix_description": self.autofix_description,
        }


# --- Helpers -----------------------------------------------------------------

def load_canonical_files(files_dir: Path) -> dict[str, bytes]:
    """Read all canonical files as raw bytes (preserves CRLF for TTL)."""
    out = {}
    for name in CANONICAL_FILES:
        p = files_dir / name
        if not p.exists():
            out[name] = None  # missing — will be flagged by hash check
        else:
            out[name] = p.read_bytes()
    return out


_HANDOFF_GLOB = "GEM_Policy-Extraction_Handoff_*.md"
_HANDOFF_SUBDIR = "handoffs"
_HANDOFF_SESSION_RE = re.compile(r"_session(\d+)\.md$", re.IGNORECASE)


def _handoff_sort_key(name: str) -> tuple[int, int, str]:
    """Sort key for handoff filenames (S260).

    Primary key is the parsed session integer, so selection is width-independent
    and immune to date/session inversion. Accepts any digit width: the corpus
    carries legacy 3-digit names (`_session259.md`) and S260+ writes 5-digit
    (`_session00260.md`), and the two must coexist in `handoffs/` without the
    older name winning. Names carrying no parseable session number sort below
    every name that does, tie-breaking lexicographically (pre-S260 behaviour).
    """
    m = _HANDOFF_SESSION_RE.search(name)
    return (1, int(m.group(1)), name) if m else (0, 0, name)


def _select_latest_handoff(names: list[str]) -> Optional[str]:
    """Pure selector — filesystem-free so the in-memory self-test can reach it."""
    return max(names, key=_handoff_sort_key) if names else None


def _handoff_resolution_findings(sub: list[str], flat: list[str]) -> list[Finding]:
    """Pure ambiguity guard. Both locations populated is unresolvable by rule."""
    if sub and flat:
        return [Finding(
            tier="YELLOW", category="handoff_resolution", file=_HANDOFF_SUBDIR,
            message=(f"Handoffs in both {_HANDOFF_SUBDIR}/ ({len(sub)}) and the "
                     f"canonical directory ({len(flat)}). Resolving to "
                     f"{_HANDOFF_SUBDIR}/; move the flat copies or delete them."),
        )]
    return []


def find_latest_handoff(files_dir: Path) -> Optional[Path]:
    """Locate the newest handoff. `handoffs/` wins when populated; the flat
    files-dir is the fallback, preserving pre-S260 layout and letting the
    unmodified-layout case keep working."""
    sub_dir = files_dir / _HANDOFF_SUBDIR
    sub = [p.name for p in sub_dir.glob(_HANDOFF_GLOB)] if sub_dir.is_dir() else []
    if sub:
        return sub_dir / _select_latest_handoff(sub)
    flat = [p.name for p in files_dir.glob(_HANDOFF_GLOB)]
    return files_dir / _select_latest_handoff(flat) if flat else None


def parse_handoff_table(handoff_path: Path) -> dict[str, tuple[str, int]]:
    """Extract the §1 canonical-file table from a handoff document.

    Returns dict {filename: (md5_hex, size_bytes)}.
    """
    text = handoff_path.read_text(encoding="utf-8")
    rows: dict[str, tuple[str, int]] = {}

    # Match §1 table rows in all four supported formats:
    #   Pre-S54 (5-col, leading index, backticked filename):
    #     | 1 | `GEM_ontology.ttl` | `a2ab6723...` | 127,495 | ... |
    #   S54+    (4-col, no index, bare filename, single numeric Bytes column):
    #     | GEM_ontology.ttl       | `389670e2...` | 127,493 | no  |
    #   S57-S63 (4-col, no index, two numeric columns: Lines then Bytes):
    #     | `GEM_ontology.ttl`     | `56ce801b...` | 1,810   | 127,806 |
    #   S64+    (4-col, no index, two numeric columns: Bytes then Lines):
    #     | `GEM_ontology.ttl`     | `122c7237...` | 135,295 | 1,842   |
    # The backticked 32-char-hex MD5 is the strong anchor; the leading
    # numeric column and filename backticks are both optional.
    #
    # Column-role identification: when two numeric columns are present,
    # the §1 header row names them (Bytes / Lines, in either order).
    # Read the header to identify which position is Bytes; do not assume
    # position. If header detection fails (older templates, malformed
    # header), fall back to the legacy heuristic "second column is Bytes"
    # so pre-S64 handoffs continue to parse identically.
    bytes_col = None  # 1 or 2, indicating which numeric column holds bytes
    header_re = re.compile(
        r"^\|\s*File\s*\|\s*MD5\s*\|\s*(\w+)\s*\|(?:\s*(\w+)\s*\|)?",
        re.MULTILINE | re.IGNORECASE,
    )
    m_hdr = header_re.search(text)
    if m_hdr:
        h1 = (m_hdr.group(1) or "").lower()
        h2 = (m_hdr.group(2) or "").lower()
        if h1 == "bytes":
            bytes_col = 1
        elif h2 == "bytes":
            bytes_col = 2

    pattern = re.compile(
        r"^\|\s*(?:\d+\s*\|\s*)?`?([\w.\-]+\.\w+)`?\s*\|\s*`([0-9a-f]{32})`"
        r"\s*\|\s*([\d,]+)\s*\|(?:\s*([\d,]+)\s*\|)?",
        re.MULTILINE,
    )
    for m in pattern.finditer(text):
        fname, md5, first_num, second_num = (
            m.group(1), m.group(2), m.group(3), m.group(4)
        )
        if bytes_col == 1:
            size_str = first_num
        elif bytes_col == 2 and second_num is not None:
            size_str = second_num
        else:
            # Legacy fallback: second column is Bytes when present,
            # otherwise the single numeric column is Bytes.
            size_str = second_num if second_num is not None else first_num
        rows[fname] = (md5, int(size_str.replace(",", "")))
    return rows


def parse_graph(files: dict[str, bytes]) -> Optional[rdflib.Graph]:
    """Parse ontology + instances into a single in-memory graph."""
    g = rdflib.Graph()
    parsed_any = False
    for name in ("GEM_ontology.ttl", "GEM_policy_instances.ttl", "GEM_code_group_instances.ttl"):
        if files.get(name):
            g.parse(data=files[name], format="turtle")
            parsed_any = True
    return g if parsed_any else None


def parse_instances_only(files: dict[str, bytes]) -> Optional[rdflib.Graph]:
    """Parse just the instances file (for counts of asserted triples)."""
    g = rdflib.Graph()
    if files.get("GEM_policy_instances.ttl"):
        g.parse(data=files["GEM_policy_instances.ttl"], format="turtle")
        return g
    return None


# --- Checks ------------------------------------------------------------------

def check_hashes(
    files: dict[str, bytes],
    expected: dict[str, tuple[str, int]],
) -> list[Finding]:
    findings: list[Finding] = []
    for name in CANONICAL_FILES:
        data = files.get(name)
        if data is None:
            findings.append(Finding(
                tier="RED", category="hash_verify",
                file=name,
                message=f"Canonical file missing from files-dir.",
            ))
            continue
        if name not in expected:
            findings.append(Finding(
                tier="YELLOW", category="hash_verify",
                file=name,
                message=f"File present but not listed in handoff §1 table.",
            ))
            continue
        exp_md5, exp_size = expected[name]
        act_md5 = hashlib.md5(data).hexdigest()
        act_size = len(data)
        if act_md5 != exp_md5 or act_size != exp_size:
            findings.append(Finding(
                tier="RED", category="hash_verify",
                file=name,
                message=(
                    f"Hash/size mismatch with handoff §1 table. "
                    f"actual md5={act_md5} size={act_size}; "
                    f"expected md5={exp_md5} size={exp_size}."
                ),
            ))
    return findings


def detect_handoff_session(handoff_text: Optional[str]) -> Optional[int]:
    """Return the session number declared by a handoff's title (H1) line.

    Two title forms are accepted, because the corpus uses the first and the
    original implementation assumed the second:

        # GEM Policy-Extraction Handoff — Session 143 (2026-07-14)   <- corpus
        # GEM Policy-Extraction Session 143 Handoff                  <- legacy

    Rather than enumerate forms, this anchors to the document's first H1 line
    and pulls "Session <N>" out of it. Anchoring matters: an unanchored search
    would match "Session 143" anywhere in the body (§2/§3 headings, prose), so
    the title's authority would be lost to whichever mention came first.

    Returns None when there is no H1 line or the H1 carries no session number.
    Callers must treat None as a *detection failure worth reporting*, not as a
    benign default — see the S144 defect below.

    S144 defect (handoff §4 item 2, opened S143): the original regex required
    the legacy form verbatim and therefore never matched a real handoff, so
    check_empirical_counts' session marker silently never advanced. The
    self-test fixtures synthesized the legacy form, so the suite stayed green
    while the code was inert. Fixtures are now built from the corpus form
    (V18/V19/V41) with the legacy form retained as an explicit case (V42).
    """
    if not handoff_text:
        return None
    m_h1 = re.search(r"^#[ \t]+\S.*$", handoff_text, re.MULTILINE)
    if not m_h1:
        return None
    m_s = re.search(r"\bSession\s+(\d+)\b", m_h1.group(0))
    return int(m_s.group(1)) if m_s else None


def check_empirical_counts(
    files: dict[str, bytes], graph: rdflib.Graph,
    handoff_text: Optional[str] = None,
) -> list[Finding]:
    """SKILL.md's empirical-counts sentence must match the graph.

    The sentence has shape:
        "as of S<N>, <X> `gem:revisesPolicy` ... <Y> `gem:revisedByPolicy`
         ... <Z> `gem:referencesPolicy` ..."

    Autofix updates both the session marker AND the three counts to current
    values. Rationale: the "as of S<N>" marker is an empirical-verification
    timestamp, not a rule-codification timestamp (rule codification is
    separately annotated by "Rule codified ..., Session ..."). Each
    re-verification of the counts is a new verification at a new timestamp,
    so the marker should advance whenever counts are re-checked.

    Target session is read from the handoff_text's title line; falls back
    to the claimed session in the sentence if the handoff is unavailable.
    """
    findings: list[Finding] = []
    skill = files.get("SKILL.md")
    if not skill:
        return findings
    text = skill.decode("utf-8")

    # Compute actual counts from the instances file (asserted triples only)
    instances = parse_instances_only(files)
    if instances is None:
        return findings
    rev_actual = sum(1 for _ in instances.triples((None, GEM.revisesPolicy, None)))
    revby_actual = sum(1 for _ in instances.triples((None, GEM.revisedByPolicy, None)))
    ref_actual = sum(1 for _ in instances.triples((None, GEM.referencesPolicy, None)))

    # Determine current session from the handoff document's title (H1) line.
    # See detect_handoff_session for the accepted forms and the S144 defect.
    current_session: Optional[int] = detect_handoff_session(handoff_text)

    # Regex with explicit in-between-text capture groups. The autofix
    # constructs the replacement by substituting only the numbers
    # (groups 2, 4, 6, 8) while preserving every literal in-between
    # span (groups 1, 3, 5, 7, 9). This avoids the property-name
    # duplication that arose from earlier slice-based reconstruction.
    pattern = re.compile(
        r"(as of S)(\d+)(,\s*)"
        r"(\d+)(\s*`gem:revisesPolicy`[^.]*?,\s*)"
        r"(\d+)(\s*`gem:revisedByPolicy`[^.]*?,\s*and\s*)"
        r"(\d+)(\s*`gem:referencesPolicy`)"
    )
    m = pattern.search(text)
    if not m:
        findings.append(Finding(
            tier="YELLOW", category="empirical_counts",
            file="SKILL.md",
            message=(
                "Empirical-counts sentence (pattern 'as of S<N>, <X> revisesPolicy, "
                "<Y> revisedByPolicy, <Z> referencesPolicy') not found. "
                "Skipping count cross-check."
            ),
        ))
        return findings

    claimed_session = int(m.group(2))
    claimed_rev = int(m.group(4))
    claimed_revby = int(m.group(6))
    claimed_ref = int(m.group(8))

    # S144 inert-precondition guard. A handoff that is present but whose title
    # yields no session number is a silent no-op: target_session falls back to
    # the claimed session, the equality test passes, and the marker never
    # advances while every message still reads as though it had. Absence of a
    # handoff is benign (nothing to advance to); an unreadable one is not.
    if handoff_text is not None and current_session is None:
        findings.append(Finding(
            tier="YELLOW", category="empirical_counts",
            file="SKILL.md",
            location="handoff title (H1)",
            message=(
                "Handoff present but its title line declares no session number "
                "(expected an H1 containing 'Session <N>'). The empirical-counts "
                "session marker cannot advance and will silently keep its current "
                "value. Retitle the handoff or extend detect_handoff_session."
            ),
        ))

    # Target session: prefer the current session from the handoff; fall back
    # to the claimed session (no advance) if the handoff isn't available.
    target_session = current_session if current_session is not None else claimed_session

    if (claimed_session, claimed_rev, claimed_revby, claimed_ref) == (
        target_session, rev_actual, revby_actual, ref_actual
    ):
        return findings  # all green

    def repl(mm: re.Match) -> str:
        return (
            mm.group(1) + str(target_session) + mm.group(3)
            + str(rev_actual) + mm.group(5)
            + str(revby_actual) + mm.group(7)
            + str(ref_actual) + mm.group(9)
        )

    def fix_skill_counts(files_inner):
        original = files_inner["SKILL.md"].decode("utf-8")
        updated = pattern.sub(repl, original, count=1)
        files_inner["SKILL.md"] = updated.encode("utf-8")

    marker_change = ""
    if target_session != claimed_session:
        marker_change = f" and session marker S{claimed_session}→S{target_session}"

    findings.append(Finding(
        tier="YELLOW", category="empirical_counts",
        file="SKILL.md",
        location="line ~127 (empirical-counts sentence)",
        message=(
            f"Counts claimed in SKILL.md disagree with actual graph state. "
            f"Claimed (S{claimed_session}): revisesPolicy={claimed_rev}, "
            f"revisedByPolicy={claimed_revby}, referencesPolicy={claimed_ref}. "
            f"Actual: revisesPolicy={rev_actual}, revisedByPolicy={revby_actual}, "
            f"referencesPolicy={ref_actual}."
            + (f" Current session (from handoff): S{current_session}."
               if current_session is not None else
               " Current session not detected; marker will not advance.")
        ),
        autofixable=True,
        autofix_fn=fix_skill_counts,
        autofix_description=(
            f"Rewrite the empirical-counts sentence in SKILL.md: counts "
            f"→ {rev_actual}/{revby_actual}/{ref_actual}{marker_change}."
        ),
    ))
    return findings


def check_processed_list(
    files: dict[str, bytes], graph: rdflib.Graph,
) -> list[Finding]:
    """The TTL header '# Policies processed:' list, the worklist's
    `policies_processed` counter, and the graph's count of `planDone`
    individuals must agree.
    """
    findings: list[Finding] = []

    ttl = files.get("GEM_policy_instances.ttl")
    worklist_raw = files.get("policy_worklist.json")
    if not ttl or not worklist_raw:
        return findings

    # Extract header list
    text = ttl.decode("latin-1")
    hdr_match = re.search(r"^#\s+Policies processed:\s*(.+?)$", text, re.MULTILINE)
    if not hdr_match:
        findings.append(Finding(
            tier="YELLOW", category="processed_list",
            file="GEM_policy_instances.ttl",
            message="No '# Policies processed:' header line found.",
        ))
        return findings
    header_list = [s.strip() for s in hdr_match.group(1).split(",") if s.strip()]
    header_count = len(header_list)

    # Worklist counter
    worklist = json.loads(worklist_raw.decode("utf-8"))
    wl_count = worklist.get("metadata", {}).get("policies_processed", -1)

    # Graph count of planDone individuals
    if graph is None:
        graph_count = None
    else:
        plan_done = URIRef(str(GEM) + "planDone")
        graph_count = sum(
            1 for _ in graph.triples((None, GEM.nextPlannedStep, plan_done))
        )

    counts = {
        "TTL header list length": header_count,
        "worklist policies_processed": wl_count,
        "graph planDone individuals": graph_count,
    }

    distinct = set(v for v in counts.values() if v is not None)
    if len(distinct) <= 1:
        return findings  # all green

    # Disagreement — flag YELLOW
    findings.append(Finding(
        tier="YELLOW", category="processed_list",
        file="GEM_policy_instances.ttl, policy_worklist.json",
        message=(
            "Processed-policy counts disagree across sources: "
            + "; ".join(f"{k}={v}" for k, v in counts.items())
            + ". The graph's planDone count is the source of truth; "
            + "the TTL header and worklist counter should match it."
        ),
        # Autofix is conservative: only sync the TTL header list IF the worklist
        # counter agrees with the graph (i.e., the TTL header is the only outlier).
        # Worklist edits are out of scope (worklist is humanedited per protocol).
    ))
    return findings


def check_uri_scheme_consistency(
    files: dict[str, bytes], graph: rdflib.Graph,
) -> list[Finding]:
    """Detect documentation that references URI forms not actually used in the
    graph. Today's canonical example: gem_reference.md saying `gemi:article<id>`
    when actual practice (verified in the graph) is `gemi:a<id>`.
    """
    findings: list[Finding] = []
    if graph is None:
        return findings

    # Determine the actual Article-URI scheme used in the graph.
    # Article identifiers begin 'A' followed by digits; URI forms could be
    # 'gemi:article<digits>' or 'gemi:a<digits>'.
    article_uris = set()
    for s in set(graph.subjects()):
        ln = str(s).split("/")[-1]
        if re.match(r"^a\d+(_group\d+)?$", ln):
            article_uris.add("a_form")
        if re.match(r"^article\d+$", ln):
            article_uris.add("article_form")

    if len(article_uris) > 1:
        findings.append(Finding(
            tier="RED", category="uri_scheme",
            message=(
                f"Article URIs present in graph use both forms: "
                f"{sorted(article_uris)}. Pick one and migrate."
            ),
        ))

    actual_form = next(iter(article_uris), None)
    # S149: this used to `return findings` when actual_form != "a_form", which would
    # skip every scheme branch added below it on any graph without Articles. The
    # Article check is now a guard, not an exit.
    check_article_drift = (len(article_uris) == 1 and actual_form == "a_form")

    # Check documentation files for stale `gemi:article<digits>` references
    drift_files = {
        "gem_reference.md": files.get("gem_reference.md"),
        "gem_turtle_style_guide.md": files.get("gem_turtle_style_guide.md"),
        "worklist_schema.md": files.get("worklist_schema.md"),
        "SKILL.md": files.get("SKILL.md"),
        "manifest_format.md": files.get("manifest_format.md"),
    }

    for fname, data in drift_files.items():
        if not check_article_drift or not data:
            continue
        text = data.decode("utf-8")
        # Find any literal `gemi:article<digits>` or `gemi:article<id>` references
        bad_refs = re.findall(r"gemi:article(?:\d+|<[^>]+>)", text)
        if bad_refs:
            counter = Counter(bad_refs)
            # Build autofix: rewrite gemi:article<...> → gemi:a<...>
            def make_fix(fn=fname):
                def apply(files_inner):
                    t = files_inner[fn].decode("utf-8")
                    t2 = re.sub(
                        r"gemi:article(\d+|<[^>]+>)",
                        lambda m: f"gemi:a{m.group(1)}",
                        t,
                    )
                    files_inner[fn] = t2.encode("utf-8")
                return apply

            findings.append(Finding(
                tier="YELLOW", category="uri_scheme",
                file=fname,
                message=(
                    f"Found `gemi:article*` references in documentation but graph uses "
                    f"`gemi:a*`. Occurrences: {dict(counter)}."
                ),
                autofixable=True,
                autofix_fn=make_fix(),
                autofix_description=(
                    f"Substitute `gemi:article<X>` → `gemi:a<X>` in {fname} ({sum(counter.values())} occurrences)."
                ),
            ))

    # --- NCA branch (S149) -------------------------------------------------
    # Same defect shape as the Article case above, found four sessions later:
    # gem_reference.md mandated `gemi:ncaCAG<NNNNN>` while the graph carried 39
    # `gemi:cag<id>` individuals and gem_turtle_style_guide.md documented the
    # `cag` form correctly. Two canonical files, two schemes, and nothing
    # executed either claim. This branch reads the graph's actual form and
    # flags documentation that names the other one.
    nca_forms = set()
    for s in set(graph.subjects(rdflib.RDF.type, GEM.NCAdocument)):
        ln = str(s).split("/")[-1]
        if re.match(r"^cag\d+[A-Za-z]*\d*$", ln):
            nca_forms.add("cag_form")
        elif re.match(r"^ncaCAG\d+[A-Za-z]*\d*$", ln):
            nca_forms.add("ncaCAG_form")

    if len(nca_forms) > 1:
        findings.append(Finding(
            tier="RED", category="uri_scheme",
            message=(f"NCA URIs present in graph use both forms: {sorted(nca_forms)}. "
                     f"Pick one and migrate."),
        ))
    elif nca_forms == {"cag_form"}:
        for fname, data in drift_files.items():
            if not data:
                continue
            text = data.decode("utf-8")
            bad_refs = re.findall(r"gemi:ncaCAG(?:\w+|<[^>]+>)", text)
            if bad_refs:
                counter = Counter(bad_refs)

                def make_nca_fix(fn=fname):
                    def apply(files_inner):
                        tx = files_inner[fn].decode("utf-8")
                        tx2 = re.sub(r"gemi:ncaCAG(\w+|<[^>]+>)",
                                     lambda m: f"gemi:cag{m.group(1)}", tx)
                        files_inner[fn] = tx2.encode("utf-8")
                    return apply

                findings.append(Finding(
                    tier="YELLOW", category="uri_scheme", file=fname,
                    location="ncaCAG -> cag",
                    message=(f"Found `gemi:ncaCAG*` references in documentation but graph uses "
                             f"`gemi:cag*` ({len(set(graph.subjects(rdflib.RDF.type, GEM.NCAdocument)))} "
                             f"individuals). Occurrences: {dict(counter)}."),
                    autofixable=True,
                    autofix_fn=make_nca_fix(),
                    autofix_description=(
                        f"Substitute `gemi:ncaCAG<X>` → `gemi:cag<X>` in {fname} "
                        f"({sum(counter.values())} occurrences)."),
                ))
    return findings


# --- S149: transmittal manual token, NCA URI derivation, doc URI examples -----

MANUAL_TOKEN_PUB = {"CIM": "6", "BP": "100-02", "NCD": "100-03", "CP": "100-04", "OTN": "100-20", "MHM": "10", "HHA": "11", "MIM": "13", "MCM": "14"}
CIM_MAX_TN = 169   # the Coverage Issues Manual ran TN 1-169, ending early 2003 (R169CIM verified by Tom, S247 -- the 04/2003 crystallization-boundary transmittal; prior ceiling 168 per S177, 167 before that)


def check_transmittal_manual_token(
    files: dict[str, bytes], graph: rdflib.Graph,
) -> list[Finding]:
    """S149 (gem_reference.md §5.2, the manual-token rule).

    A transmittal number is unique only *within* one CMS manual, so every
    gem:TransmittalPolicy URI must carry a manual token, and that token must
    agree with the individual's own gem:publicationNumber. The token and the
    publicationNumber are one fact recorded twice; this check is what stops
    them drifting apart.

    Why it exists: gem_reference.md has said "the suffix is therefore always
    present on transmittal URIs" since long before S149, and 61 of 85
    transmittals were bare anyway. A rule nothing executes is not a rule. The
    S148/S149 defects (tn78, tn144, tn36) were all "right number, wrong
    manual" and all survived because no code read the claim.

    Rules enforced:
      1. local name matches tn<digits><TOKEN>?  (TOKEN in MANUAL_TOKEN_PUB)
      2. token present  -> gem:publicationNumber == MANUAL_TOKEN_PUB[token]
      3. token absent   -> no gem:publicationNumber, AND gem:description
                           declares "Manual undetermined" (the bare form is a
                           declared-unknown, never a resting state)
      4. CIM token      -> transmittal number <= 169 (the CIM's extent).
                           The era half of the gate (dates) is not machine-
                           readable from the graph and stays a methodology rule.
    """
    findings: list[Finding] = []
    if graph is None:
        return findings

    for s in sorted(set(graph.subjects(rdflib.RDF.type, GEM.TransmittalPolicy)), key=str):
        ln = str(s).split("/")[-1]
        m = re.match(r"^tn(\d+)([A-Za-z]*)$", ln)
        if not m:
            findings.append(Finding(
                tier="RED", category="transmittal_manual_token", location=ln,
                message=(f"Transmittal URI `gemi:{ln}` does not match the "
                         f"`tn<NN><MANUAL>` scheme (gem_reference.md §5 naming table)."),
            ))
            continue
        num, token = int(m.group(1)), m.group(2)
        pubs = sorted(str(o) for o in graph.objects(s, GEM.publicationNumber))
        desc = " ".join(str(o) for o in graph.objects(s, GEM.description))

        if token:
            if token not in MANUAL_TOKEN_PUB:
                findings.append(Finding(
                    tier="RED", category="transmittal_manual_token", location=ln,
                    message=(f"`gemi:{ln}` carries manual token {token!r}, which is not in the "
                             f"controlled vocabulary {sorted(MANUAL_TOKEN_PUB)} "
                             f"(gem_reference.md §5.2). A new token is introduced only for a "
                             f"genuinely new CMS manual, and enters that table with its "
                             f"publication number in the same edit."),
                ))
                continue
            want = MANUAL_TOKEN_PUB[token]
            if pubs != [want]:
                findings.append(Finding(
                    tier="RED", category="transmittal_manual_token", location=ln,
                    message=(f"`gemi:{ln}`: manual token {token!r} requires "
                             f"gem:publicationNumber \"{want}\"; found {pubs or 'none'}. "
                             f"The token and the publication number are one fact recorded twice."),
                ))
            if token == "CIM" and num > CIM_MAX_TN:
                findings.append(Finding(
                    tier="RED", category="transmittal_manual_token", location=ln,
                    message=(f"`gemi:{ln}` carries the CIM token but TN {num} exceeds the "
                             f"Coverage Issues Manual's extent (TN 1-{CIM_MAX_TN}, ended early 2003). "
                             f"Era gate, gem_reference.md §5.2."),
                ))
        else:
            if pubs:
                findings.append(Finding(
                    tier="RED", category="transmittal_manual_token", location=ln,
                    message=(f"`gemi:{ln}` is bare but asserts gem:publicationNumber {pubs}. "
                             f"The manual is determined, so the URI must carry its token "
                             f"({', '.join(k for k, v in MANUAL_TOKEN_PUB.items() if v in pubs) or '?'})."),
                ))
            elif "Manual undetermined" not in desc:
                findings.append(Finding(
                    tier="RED", category="transmittal_manual_token", location=ln,
                    message=(f"`gemi:{ln}` is bare and does not declare it. A bare transmittal "
                             f"URI means *unresolved*, never *fine*: it must carry no "
                             f"gem:publicationNumber and its gem:description must say "
                             f"\"Manual undetermined\" (gem_reference.md §5.2)."),
                ))
    return findings


def check_nca_uri_derivation(
    files: dict[str, bytes], graph: rdflib.Graph,
) -> list[Finding]:
    """S149: an NCA's URI is a function of its own gem:identifier.

    local name == "cag" + gem:identifier with "CAG-" removed. Derived from the
    individual rather than from a hand-maintained roster, so the rule cannot
    decay as the corpus grows and it catches revision-letter case drift by
    construction (the S149 defects: cag00313r/cag00313r2/cag00405n/cag00426n,
    each carrying an UPPERCASE identifier).

    Deliberately NOT autofixable: the fix is a URI rename, which is an identity
    change and a Generate-turn decision (and if an identifier were itself wrong,
    an autofix would propagate the error rather than surface it).
    """
    findings: list[Finding] = []
    if graph is None:
        return findings
    for s in sorted(set(graph.subjects(rdflib.RDF.type, GEM.NCAdocument)), key=str):
        ln = str(s).split("/")[-1]
        ids = sorted(str(o) for o in graph.objects(s, GEM.identifier))
        if len(ids) != 1:
            findings.append(Finding(
                tier="RED", category="nca_uri_derivation", location=ln,
                message=(f"`gemi:{ln}` carries {len(ids)} gem:identifier values ({ids}); "
                         f"exactly one is required to derive the URI."),
            ))
            continue
        expected = "cag" + ids[0].replace("CAG-", "")
        if expected != ln:
            findings.append(Finding(
                tier="RED", category="nca_uri_derivation", location=ln,
                message=(f"`gemi:{ln}` does not match its own gem:identifier {ids[0]!r}: "
                         f"expected `gemi:{expected}` (cag + identifier minus 'CAG-', source "
                         f"casing preserved). gem_reference.md §5 naming table."),
            ))
    return findings


def check_doc_uri_examples(
    files: dict[str, bytes], graph: rdflib.Graph,
) -> list[Finding]:
    """S149: every concrete `gemi:` example in gem_reference.md's URI-naming
    table must name an individual that exists in the graph.

    The table's job is to show what the corpus actually does, so an example
    that names nothing is a false claim about the graph — the S148 class. At
    S149 seven of twenty-one examples failed: `tn44NCD` and `tn96NCD` (never
    existed; the graph had bare `tn96`), three `ncaCAG*` forms (wrong scheme
    entirely), `dl33797` (no draft LCDs), and `conceptArterialPO2` (the graph
    has `conceptPO2`). Two of those had been wrong for the whole life of the
    convention they illustrate.

    Placeholders (`gemi:tn<NN>`) are skipped; a row whose Examples cell is
    italicised *reserved* is a deliberate no-instances scheme and is skipped
    too — that escape hatch is explicit so it cannot be used silently.
    """
    findings: list[Finding] = []
    if graph is None:
        return findings
    data = files.get("gem_reference.md")
    if not data:
        return findings
    text = data.decode("utf-8")
    start = text.find("### Instance URI naming schemes")
    if start < 0:
        findings.append(Finding(
            tier="YELLOW", category="doc_uri_examples", file="gem_reference.md",
            message=("The `### Instance URI naming schemes` heading is gone; the URI-naming "
                     "table can no longer be located, so its examples are unchecked."),
        ))
        return findings
    end = text.find("\n### ", start + 1)
    table = text[start:end if end > 0 else len(text)]

    present = {str(s).split("/")[-1] for s in set(graph.subjects())}
    missing: dict[str, str] = {}
    for line in table.split("\n"):
        if not line.startswith("|"):
            continue
        cells = [c.strip() for c in line.strip("|").split("|")]
        if len(cells) < 3 or cells[1].strip("- ") == "" or "Scheme" in cells[1]:
            continue
        examples = cells[-1]
        if "*reserved" in examples:
            continue
        for m in re.finditer(r"`gemi:([A-Za-z][A-Za-z0-9_.]*)`", examples):
            ln = m.group(1)
            if ln not in present:
                missing[ln] = cells[0]
    for ln, kind in sorted(missing.items()):
        findings.append(Finding(
            tier="YELLOW", category="doc_uri_examples", file="gem_reference.md",
            location=ln,
            message=(f"§5 URI-naming-table example `gemi:{ln}` ({kind} row) names nothing in "
                     f"the graph. The table documents what the corpus does — replace it with "
                     f"a real individual, or mark the row *reserved* if the scheme has no "
                     f"instances by design."),
        ))
    return findings


def check_proposal_b(
    files: dict[str, bytes], graph: rdflib.Graph,
) -> list[Finding]:
    """Proposal B (S50, SKILL.md §Policy-to-Policy / Linking direction):
    `revisesPolicy` is asserted on the revising side, `referencesPolicy` on
    the citing side. Where both apply, both must be asserted on opposite
    sides.

    The audit classifies each `revisesPolicy` triple's missing citing-side
    counterpart into five categories:
      A. transmittal-chain (successor revises predecessor) — NOT a bug
      B. _DELETED stub (deleted policy has no current text) — NOT a bug
      C. unextracted stub (planPromote) — DEFERRED, not a bug at extraction layer
      D. fully-extracted target (planDone) — REAL EXTRACTION GAP (RED)
      E. superseded revision (planDone target carries a DIFFERENT, reciprocated
         current transmittal) — NOT a bug. The flagged transmittal revised an
         earlier version now superseded; per the three-contexts rule, a
         Revision-History transmittal earns no citing-side `referencesPolicy`,
         so the missing reciprocal is correct, not a gap. (S107; precedent:
         tn48 → ncd20.29, superseded by tn203 which ncd20.29 reciprocates.)
    """
    findings: list[Finding] = []
    if graph is None:
        return findings

    # Restrict to instance-file triples (the schema declares the property
    # but never asserts an instance-level triple).
    instances = parse_instances_only(files)
    if instances is None:
        return findings

    def workflow_state(uri):
        for o in instances.objects(uri, GEM.nextPlannedStep):
            return str(o).split("/")[-1]
        return None

    transmittal_class = GEM.TransmittalPolicy
    pm_class = GEM.ProgramMemorandumPolicy

    real_gaps = []
    for trans, _, revised in instances.triples((None, GEM.revisesPolicy, None)):
        if (revised, GEM.referencesPolicy, trans) in instances:
            continue  # both directions asserted — green

        # Categorize the gap
        revised_ln = str(revised).split("/")[-1]
        revised_types = set(str(t).split("/")[-1] for t in instances.objects(revised, rdflib.RDF.type))
        is_transmittal_target = any("Transmittal" in t or "ProgramMemorandum" in t for t in revised_types)
        is_deleted = revised_ln.endswith(_DELETED_SUFFIX)

        if is_transmittal_target:
            continue  # Category A: chain link
        if is_deleted:
            continue  # Category B: deleted

        state = workflow_state(revised)
        if state == "planDone":
            # Category E: superseded revision. The target is fully extracted and
            # lacks the reciprocal for THIS transmittal, but it carries a
            # DIFFERENT, reciprocated revising transmittal (its current
            # Transmittal Information field). That marks this revises link as a
            # superseded historical revision, which — per the three-contexts
            # rule (Revision History is excluded from citing-side references) —
            # earns no `referencesPolicy`. Not an extraction gap. A lone
            # unreciprocated revises link with no current transmittal still
            # falls through to Category D (RED), so genuine gaps are not masked.
            superseded = any(
                other != trans
                and (revised, GEM.referencesPolicy, other) in instances
                for other in instances.subjects(GEM.revisesPolicy, revised)
            )
            if superseded:
                continue  # Category E: superseded-revision — not a gap
            # Category D: real gap
            real_gaps.append((str(trans).split("/")[-1], revised_ln))
        # else: Category C, deferred

    for rev_ln, target_ln in real_gaps:
        findings.append(Finding(
            tier="RED", category="proposal_b",
            file="GEM_policy_instances.ttl",
            location=f"gemi:{target_ln} (POLICY INSTANCE block)",
            message=(
                f"gemi:{rev_ln} `gem:revisesPolicy` gemi:{target_ln}, "
                f"but gemi:{target_ln} (planDone) does not assert "
                f"`gem:referencesPolicy gemi:{rev_ln}`. "
                f"Per Proposal B (SKILL.md §Policy-to-Policy / Linking direction), "
                f"when a transmittal revises a fully-extracted policy AND the policy's "
                f"current text cites the transmittal, both directions must be asserted. "
                f"This is a Category D gap requiring source-text verification before backfill."
            ),
        ))

    return findings


def check_workflow_state_coverage(
    files: dict[str, bytes], graph: rdflib.Graph,
) -> list[Finding]:
    """S45 rule: every `gem:CMSpolicy` individual carries `gem:nextPlannedStep`
    and `gem:isInEffect`.
    """
    findings: list[Finding] = []
    if graph is None:
        return findings
    instances = parse_instances_only(files)
    if instances is None:
        return findings

    # Build subclass closure of gem:CMSpolicy in the full graph (which includes the schema)
    cms_classes = {GEM.CMSpolicy}
    for sub in graph.subjects(rdflib.RDFS.subClassOf, GEM.CMSpolicy):
        cms_classes.add(sub)

    missing = []
    for cls in cms_classes:
        for ind in instances.subjects(rdflib.RDF.type, cls):
            has_step = any(True for _ in instances.objects(ind, GEM.nextPlannedStep))
            has_eff = any(True for _ in instances.objects(ind, GEM.isInEffect))
            if not (has_step and has_eff):
                missing.append((str(ind).split("/")[-1], has_step, has_eff))

    if missing:
        for ln, has_step, has_eff in missing:
            absent = []
            if not has_step:
                absent.append("nextPlannedStep")
            if not has_eff:
                absent.append("isInEffect")
            findings.append(Finding(
                tier="RED", category="workflow_state",
                file="GEM_policy_instances.ttl",
                location=f"gemi:{ln}",
                message=(
                    f"gemi:{ln} is a gem:CMSpolicy individual but is missing: {absent}. "
                    f"Per S45 §2k (gem_reference.md), every CMSpolicy must carry both "
                    f"nextPlannedStep and isInEffect (typically in the Retroactive Assignment section)."
                ),
            ))
    return findings


def check_uri_collisions(
    files: dict[str, bytes], graph: rdflib.Graph,
) -> list[Finding]:
    """Per Proposal A (S50): at-most-one `gem:prefLabel` and at-most-one
    `gem:description` per URI; `dc:source` may be legitimately multi-valued.
    """
    findings: list[Finding] = []
    if graph is None:
        return findings
    instances = parse_instances_only(files)
    if instances is None:
        return findings

    label_counts = defaultdict(int)
    desc_counts = defaultdict(int)
    for s, _, _ in instances.triples((None, GEM.prefLabel, None)):
        label_counts[str(s)] += 1
    for s, _, _ in instances.triples((None, GEM.description, None)):
        desc_counts[str(s)] += 1

    for uri, n in label_counts.items():
        if n > 1:
            ln = uri.split("/")[-1]
            findings.append(Finding(
                tier="YELLOW", category="uri_collision",
                file="GEM_policy_instances.ttl",
                location=f"gemi:{ln}",
                message=(
                    f"gemi:{ln} has {n} `gem:prefLabel` triples (expected 1). "
                    f"Per Proposal A cardinality conventions, retain one canonical and "
                    f"demote the others to `skos:altLabel`."
                ),
            ))
    for uri, n in desc_counts.items():
        if n > 1:
            ln = uri.split("/")[-1]
            findings.append(Finding(
                tier="YELLOW", category="uri_collision",
                file="GEM_policy_instances.ttl",
                location=f"gemi:{ln}",
                message=(
                    f"gemi:{ln} has {n} `gem:description` triples (expected 1). "
                    f"Per Proposal A, merge into one coherent prose description; SME review required."
                ),
            ))
    return findings


def check_deleted_twin_collision(
    files: dict[str, bytes], graph: rdflib.Graph,
) -> list[Finding]:
    """S146: flag any `gemi:<x>` / `gemi:<x>_DELETED` pair that are both minted.

    `gem_reference.md` §5.3 mints a transmittal-deleted policy at
    `gemi:ncd<section>_DELETED` and deliberately leaves the standard URI
    `gemi:ncd<section>` unreserved, so that a *different* future policy CMS
    assigns to the same section identifier has somewhere clean to land (the
    §20.8.3 motivation). A bare URI existing alongside its retiree therefore
    means one of exactly two things, and a human must say which:

      (a) DUPLICATE MINT — the bare URI holds the *same* policy as the
          retiree, minted a second time from a stale cross-reference in some
          citing policy. This is a breach: the reservation has been consumed
          by the very policy it was not for, and the graph now asserts one
          real-world document is two entities. Fix: retarget inbound links to
          the retiree, fold any findings into its description, delete the bare
          stub. Canonical instance: `gemi:ncd150.4` / `gemi:ncd160.3`, minted
          at S114 from NCD 160.13's 1988-era cross-references and consolidated
          at S146 (breach latent S114–S146).

      (b) IDENTIFIER REUSE — the bare URI holds a *genuinely different* policy
          CMS later assigned to the same section number. This is §5.3 working
          as designed and the pair is correct.

    NO DISCRIMINATOR, deliberately. The obvious automatic tell for (a)-vs-(b)
    is label similarity, and it is the wrong one: it would have missed
    `gemi:ncd160.3`, the very case that motivated this check, whose bare
    prefLabel ("TENS for Chronic Intractable Pain", reconstructed from citing
    context) does not resemble its retiree's TN-48-grounded title ("Assessing
    Patients Suitability for Electrical Nerve Stimulation"). The check reports
    the pair and lets a human read it.

    Consequence, recorded so it is not rediscovered as a surprise: the FIRST
    genuine (b) will fire YELLOW permanently and break the fully-GREEN
    bootstrap invariant. It needs an allowlist at that point, not before —
    there are zero (b) instances today, and a suppression mechanism built for
    a hypothetical shape is the failure this project already has a name for.
    See `gem_reference.md` §5.3.

    YELLOW, no autofix: neither disposition has a mechanical fix. Scope is
    *minted subjects* — a URI is counted only if it carries an `rdf:type`
    triple, so a dangling reference to a nonexistent bare URI is a different
    defect (`uri_scheme` / typo territory), not a duplicate mint.
    """
    findings: list[Finding] = []
    if graph is None:
        return findings
    instances = parse_instances_only(files)
    if instances is None:
        return findings

    minted = set()
    for s, _, _ in instances.triples((None, rdflib.RDF.type, None)):
        uri = str(s)
        if uri.startswith(str(GEMI)):
            minted.add(uri[len(str(GEMI)):])

    for ln in sorted(minted):
        if not ln.endswith(_DELETED_SUFFIX):
            continue
        bare = ln[: -len(_DELETED_SUFFIX)]
        if bare not in minted:
            continue
        findings.append(Finding(
            tier="YELLOW", category="deleted_twin_collision",
            file="GEM_policy_instances.ttl",
            location=f"gemi:{bare}",
            message=(
                f"gemi:{bare} and gemi:{ln} are both minted. Per gem_reference.md "
                f"§5.3 the bare URI is deliberately left unreserved for a future CMS "
                f"reuse of the identifier, so this pair is either (a) a duplicate mint "
                f"of the SAME policy — consolidate into gemi:{ln}, retarget inbound "
                f"links, delete gemi:{bare} — or (b) a genuine identifier reuse by CMS, "
                f"in which case the pair is correct and this finding needs an allowlist. "
                f"No automatic discriminator: label similarity would have missed the "
                f"S114 gemi:ncd160.3 case. Human decision required."
            ),
        ))
    return findings


def check_predicate_ordering(files: dict[str, bytes]) -> list[Finding]:
    """gem:memberOfOntology is second-to-last, dc:source is last.
    Only checks instance definitions, not full ontology terms (which follow
    a different ordering convention).
    """
    findings: list[Finding] = []
    ttl = files.get("GEM_policy_instances.ttl")
    if not ttl:
        return findings
    text = ttl.decode("latin-1")

    # Find each subject's block: subject line followed by indented predicate lines,
    # terminated by a line ending with ' .' (with possible whitespace).
    # Then check the order of memberOfOntology and dc:source.
    # We scan blocks one at a time.
    block_pat = re.compile(
        r"(?P<head>^(gemi:|<)[^\s]+\s+a\s+[^;]+;\s*\r?\n)"  # subject + first type line
        r"(?P<body>(?:[ \t]+[^\r\n]+\r?\n)+)"
        r"(?P<term>[ \t]+[^\r\n]+\s+\.\s*\r?\n)",
        re.MULTILINE,
    )

    bad_blocks = []
    for m in block_pat.finditer(text):
        body = m.group("body") + m.group("term")
        lines = [L for L in body.splitlines() if L.strip()]
        # locate predicates of interest
        moo_idx = None
        dcs_idx = None
        for i, L in enumerate(lines):
            if "gem:memberOfOntology" in L:
                moo_idx = i
            if re.search(r"\bdc:source\b", L):
                dcs_idx = i
        n = len(lines)
        # If both present, memberOfOntology should be at n-2 and dc:source at n-1
        # (or memberOfOntology at n-1 if no dc:source)
        if moo_idx is not None and dcs_idx is not None:
            if not (moo_idx == n - 2 and dcs_idx == n - 1):
                head_ident = m.group("head").split()[0]
                bad_blocks.append((head_ident, moo_idx, dcs_idx, n))
        elif moo_idx is not None and dcs_idx is None:
            if moo_idx != n - 1:
                head_ident = m.group("head").split()[0]
                bad_blocks.append((head_ident, moo_idx, dcs_idx, n))

    if bad_blocks:
        # report aggregate, with the first few as examples
        sample = bad_blocks[:5]
        findings.append(Finding(
            tier="YELLOW", category="predicate_ordering",
            file="GEM_policy_instances.ttl",
            message=(
                f"{len(bad_blocks)} blocks have non-standard predicate ordering: "
                f"`gem:memberOfOntology` should be second-to-last, `dc:source` last. "
                f"Examples (subject; memberOfOntology idx; dc:source idx; n): "
                + "; ".join(f"{s} ({mo}, {ds} of {nn})" for s, mo, ds, nn in sample)
            ),
        ))
    return findings


def check_formatting_integrity(files: dict[str, bytes]) -> list[Finding]:
    """TTL: CRLF only, no tabs, ends with `.\\r\\n`.
       Markdown: LF only.
    """
    findings: list[Finding] = []
    for name, data in files.items():
        if data is None:
            continue
        if name in TTL_FILES:
            crlf = data.count(b"\r\n")
            total_lf = data.count(b"\n")
            lone_lf = total_lf - crlf
            tabs = data.count(b"\t")
            if lone_lf > 0:
                findings.append(Finding(
                    tier="RED", category="formatting",
                    file=name,
                    message=f"{lone_lf} lone-LF line endings (TTL requires CRLF only).",
                ))
            if tabs > 0:
                findings.append(Finding(
                    tier="RED", category="formatting",
                    file=name,
                    message=f"{tabs} tab characters present (TTL forbids tabs).",
                ))
            # File ending: should end with `.\r\n` (no trailing blank lines).
            if not data.endswith(b".\r\n"):
                # Distinguish trailing-blank-line case from missing-period case
                if data.endswith(b".\r\n\r\n") or data.endswith(b".\r\n\r\n\r\n"):
                    # Build autofix: iteratively trim trailing \r\n pairs until
                    # the file ends with exactly one (terminator after final `.`).
                    # The while-loop handles arbitrary trailing-CRLF counts
                    # independent of the detection's narrow endswith matchers.
                    def make_fix(fn=name):
                        def apply(files_inner):
                            d = files_inner[fn]
                            while d.endswith(b"\r\n\r\n"):
                                d = d[:-2]
                            files_inner[fn] = d
                        return apply

                    findings.append(Finding(
                        tier="YELLOW", category="formatting",
                        file=name,
                        message=(
                            "File ends with `.\\r\\n\\r\\n` (trailing blank line(s)) "
                            "rather than `.\\r\\n`. Per SKILL.md §Verification Checkpoint "
                            "item 6, TTL files should end with `.\\r\\n` only."
                        ),
                        autofixable=True,
                        autofix_fn=make_fix(),
                        autofix_description=(
                            f"Strip trailing blank line(s) from {name} so the file "
                            f"ends with `.\\r\\n` only."
                        ),
                    ))
                else:
                    findings.append(Finding(
                        tier="RED", category="formatting",
                        file=name,
                        message=f"File does not end with `.\\r\\n` (ends with {data[-10:]!r}).",
                    ))
        elif name in MARKDOWN_FILES:
            crlf = data.count(b"\r\n")
            if crlf > 0:
                findings.append(Finding(
                    tier="YELLOW", category="formatting",
                    file=name,
                    message=f"{crlf} CRLF line endings (markdown should be LF only).",
                ))
    return findings


def check_ruledescription_domain_conformance(
    files: dict[str, bytes], graph: rdflib.Graph,
) -> list[Finding]:
    """Post-Phase-4 domain invariant: gem:ruleDescription attaches EXCLUSIVELY to
    gem:PolicyRule subjects.

    As of S86 (2026-06-24) gem:ruleDescription's rdfs:domain was narrowed from
    union(gem:CMSpolicy, gem:AnchoredCodingScope, gem:PolicyRule) to gem:PolicyRule
    alone, completing the Phase 4 schema closeout. Every gem:ruleDescription triple
    must therefore have a subject asserted rdf:type gem:PolicyRule (or a subclass).
    A subject carrying gem:ruleDescription that is not a gem:PolicyRule is a domain
    violation -- e.g. a stray legacy string re-added to a gem:CMSpolicy or
    gem:AnchoredCodingScope subject, or a mid-migration regression.

    Runs on the ASSERTED graph: with RDFS inference enabled in the production
    triplestore, a stray gem:ruleDescription on a non-PolicyRule subject would be
    masked by inferring that subject into gem:PolicyRule via the (now narrowed)
    domain. Validating the asserted triples catches the error at source.

    Supersedes the retired Phase-3 'three-state invariant' (NotMigrated / Migrated /
    NoRules on gem:CMSpolicy subjects): once gem:ruleDescription is illegal on any
    non-PolicyRule subject, the BOTH-state corruption that check guarded against is
    strictly subsumed by this domain check, which additionally covers
    gem:AnchoredCodingScope and any other subject. Finding category is
    "ruledescription_domain".
    """
    findings: list[Finding] = []
    instances = parse_instances_only(files)
    if instances is None:
        return findings

    # Subclass closure of gem:PolicyRule (none today; future-proof, mirrors the
    # closure idiom in check_policyrule_provenance_reciprocity).
    pr_classes = {GEM.PolicyRule}
    if graph is not None:
        for sub in graph.subjects(rdflib.RDFS.subClassOf, GEM.PolicyRule):
            pr_classes.add(sub)

    def is_policyrule(node: URIRef) -> bool:
        return any((node, rdflib.RDF.type, c) in instances for c in pr_classes)

    for s, o in instances.subject_objects(GEM.ruleDescription):
        if not isinstance(s, URIRef):
            continue
        if is_policyrule(s):
            continue
        local = str(s).split("/")[-1]
        subj_types = [
            f"gem:{str(t).split('/')[-1]}"
            for t in instances.objects(s, rdflib.RDF.type)
        ]
        type_str = ", ".join(subj_types) if subj_types else "(untyped)"
        findings.append(Finding(
            tier="RED",
            category="ruledescription_domain",
            file="GEM_policy_instances.ttl",
            location=f"gemi:{local}",
            message=(
                f"gemi:{local} carries gem:ruleDescription but is not a "
                f"gem:PolicyRule (asserted type(s): {type_str}). As of S86, "
                f"gem:ruleDescription's domain is gem:PolicyRule exclusively; "
                f"rule strings must live on gem:PolicyRule individuals linked "
                f"from policy / anchor-scope subjects via gem:hasPolicyRule, not "
                f"directly on those subjects."
            ),
        ))
    return findings



_INVERSE_CLAIM_MARKERS = (
    "materialized both ways",
    "materialized inverse of",
    "both directions are present in the data",
    "both present in data",
    "are both asserted",
    "both are asserted",
    "traverse either direction without inference",
    "traverse in either direction without inference",
)
_INVERSE_BOTH_MARKERS = (
    "both ways",
    "both directions",
    "both present",
    "both asserted",
    "are both",
    "either direction",
)
_INVERSE_DENIAL_MARKERS = (
    "no materialized inverse",
    "no inverse is materialized",
)


def check_inverse_note_conformance(
    files: dict[str, bytes], graph: rdflib.Graph,
) -> list[Finding]:
    """A gem:llmInverseNote must describe the canonical .ttl files truthfully.

    Two predicates in GEM declare owl:inverseOf partners (gem:revisesPolicy /
    gem:revisedByPolicy and gem:transmitsChangeRequest /
    gem:changeRequestTransmittedBy). Before S197 all four terms carried a
    gem:llmInverseNote asserting the inverse was "materialized" and could be
    traversed "without inference" -- and neither inverse had a single triple in
    the instances files. The claim was true only of a triplestore running the
    OWL reasoner, and a consumer parsing the files got nothing. Nothing fired:
    the notes are prose, so parse, SHACL, mass conservation and the whole
    self-test suite were all blind to them. This is the S159 shape -- a claim
    that answers differently depending on which graph you are standing in.

    Two directions, both YELLOW with no autofix (repairing prose is a human
    call: materialize the inverse, or reword the note):
      (a) the note claims materialization and the declared inverse carries
          ZERO assertions in the instances files;
      (b) the note denies materialization ("no materialized inverse") and the
          declared inverse carries assertions after all.
    A note claiming materialization with no owl:inverseOf declared at all is
    also (a) -- there is no inverse to be materialized.

    Per the S144 inert-precondition rule the check distinguishes "nothing to
    check" from "found nothing to check with": an ontology carrying no
    gem:llmInverseNote at all returns YELLOW rather than a silent pass.
    Finding category is "inverse_note_conformance".
    """
    findings: list[Finding] = []
    if graph is None:
        return findings
    instances = parse_instances_only(files)
    if instances is None:
        return findings

    notes = list(graph.subject_objects(GEM.llmInverseNote))
    if not notes:
        findings.append(Finding(
            tier="YELLOW",
            category="inverse_note_conformance",
            file="GEM_ontology.ttl",
            location="(ontology)",
            message=(
                "No gem:llmInverseNote assertion found anywhere in the "
                "ontology, so this check had nothing to check with. The "
                "corpus carries these notes on the inverse-bearing and "
                "traversal-relevant object properties; their total absence "
                "means either the annotation was dropped or the ontology did "
                "not parse as expected. Inert-precondition rule (S144): a "
                "benign default is reported, not returned silently."
            ),
        ))
        return findings

    for subj, note in notes:
        if not isinstance(subj, URIRef):
            continue
        text = str(note).lower()
        local = str(subj).split("/")[-1]
        denied = any(m in text for m in _INVERSE_DENIAL_MARKERS)
        claimed = (not denied) and any(m in text for m in _INVERSE_CLAIM_MARKERS)
        inverses = [o for o in graph.objects(subj, rdflib.OWL.inverseOf)
                    if isinstance(o, URIRef)]
        inverses += [sj for sj in graph.subjects(rdflib.OWL.inverseOf, subj)
                     if isinstance(sj, URIRef)]
        inverses = sorted({str(i) for i in inverses})

        if claimed and any(m in text for m in _INVERSE_BOTH_MARKERS):
            own = sum(1 for _ in instances.triples((None, subj, None)))
            if own == 0:
                findings.append(Finding(
                    tier="YELLOW",
                    category="inverse_note_conformance",
                    file="GEM_ontology.ttl",
                    location=f"gem:{local}",
                    message=(
                        f"gem:{local}'s gem:llmInverseNote claims both directions "
                        f"are present in the data, but gem:{local} itself carries "
                        f"ZERO assertions in the instances files. A both-ways "
                        f"claim has to hold for the predicate it is written on, "
                        f"not only for its partner."
                    ),
                ))

        if claimed:
            if not inverses:
                findings.append(Finding(
                    tier="YELLOW",
                    category="inverse_note_conformance",
                    file="GEM_ontology.ttl",
                    location=f"gem:{local}",
                    message=(
                        f"gem:{local}'s gem:llmInverseNote claims an inverse is "
                        f"materialized, but the term declares no owl:inverseOf "
                        f"partner. Either declare the inverse or reword the note."
                    ),
                ))
                continue
            for inv in inverses:
                n = sum(1 for _ in instances.triples((None, URIRef(inv), None)))
                if n == 0:
                    inv_local = inv.split("/")[-1]
                    findings.append(Finding(
                        tier="YELLOW",
                        category="inverse_note_conformance",
                        file="GEM_ontology.ttl",
                        location=f"gem:{local}",
                        message=(
                            f"gem:{local}'s gem:llmInverseNote claims its inverse "
                            f"gem:{inv_local} is materialized and traversable "
                            f"without inference, but gem:{inv_local} carries ZERO "
                            f"assertions in the instances files. The claim holds "
                            f"only under an OWL reasoner. Either materialize the "
                            f"inverse triples or reword the note to say the edge "
                            f"is entailed rather than asserted."
                        ),
                    ))
        elif denied and inverses:
            for inv in inverses:
                n = sum(1 for _ in instances.triples((None, URIRef(inv), None)))
                if n > 0:
                    inv_local = inv.split("/")[-1]
                    findings.append(Finding(
                        tier="YELLOW",
                        category="inverse_note_conformance",
                        file="GEM_ontology.ttl",
                        location=f"gem:{local}",
                        message=(
                            f"gem:{local}'s gem:llmInverseNote says no inverse is "
                            f"materialized, but its declared inverse "
                            f"gem:{inv_local} carries {n} assertion(s) in the "
                            f"instances files. The note understates the data; "
                            f"reword it."
                        ),
                    ))
    return findings



_HCPCS_NS = "http://purl.bioontology.org/ontology/HCPCS/"
_ICD10_NS = "http://purl.bioontology.org/ontology/ICD10CM/"
_CPT_NS = "https://www.ama-assn.org/cpt#"

# Classes whose individuals are typed OUTSIDE the canonical files: hcpcs: and
# icd10: members acquire rdf:type from the BioPortal conversion queries, cpt:
# members from cpt.ttl. None of those typing triples are in the validation
# graph, so conformance for these classes is judged by IRI namespace rather
# than by asserted type. This is the same in-namespace vs code-namespace split
# S78 drew for SHACL (sh:class for gem: ranges, sh:pattern for code ranges).
_EXTERNALLY_TYPED_CLASSES = {
    "HCPCSprocedure": (_HCPCS_NS, _CPT_NS),
    "HCPCScode": (_HCPCS_NS, _CPT_NS),
    "HCPCSmodifier": (_HCPCS_NS,),
    "CPTprocedure": (_CPT_NS,),
    "ICDdiagnosis": (_ICD10_NS,),
    "ICDgrouping": (_ICD10_NS,),
    "ICDconcept": (_ICD10_NS,),
}


def check_domain_range_conformance(
    files: dict[str, bytes], graph: rdflib.Graph,
) -> list[Finding]:
    """Every gem: property's asserted triples respect its rdfs:domain and
    rdfs:range.

    Generalises check_ruledescription_domain_conformance, which covers exactly
    one predicate. Before S197 the audit had no other domain check, and a
    gem:PolicyGroup carrying gem:referencesPolicy (domain gem:CMSpolicy) stood
    from S58 to S197 -- 139 sessions -- invisible to parse, SHACL, mass
    conservation and the whole self-test suite.

    Runs on the ASSERTED graph because the defect is self-concealing under
    inference: `P rdfs:domain C` plus `x P y` entails `x a C`, so in a
    reasoning triplestore the violation manufactures the very type that would
    satisfy it. Declared owl:unionOf domains are expanded; rdfs:subClassOf
    closure is applied to each member.

    Only classes in the gem: namespace are validated by type. Ranges naming an
    externally-typed code class are validated by IRI namespace instead (see
    _EXTERNALLY_TYPED_CLASSES) -- without that arm gem:modifierSemantics'
    four correct hcpcs: subjects would each be a false positive. Datatype
    ranges are xsd: types and are left to rdflib's parser.

    RED where a typed node contradicts the declaration; YELLOW where the node
    carries no asserted type at all. No autofix either way: widening the
    domain, retyping the individual and dropping the triple are three
    different judgments. Per the S144 inert-precondition rule, an ontology
    declaring no gem:-namespace domain or range returns YELLOW rather than a
    silent pass. Finding category is "domain_range_conformance".
    """
    findings: list[Finding] = []
    if graph is None:
        return findings
    # The merged asserted graph, NOT parse_instances_only: controlled-vocabulary
    # individuals are typed in GEM_ontology.ttl and gem:CodeGroup individuals in
    # GEM_code_group_instances.ttl, so a policy-instances-only type lookup reports
    # every one of them as untyped. Merged is still the asserted graph -- no
    # reasoner runs here -- so the self-concealment argument above is unaffected.
    instances = graph

    subclasses: dict[str, set] = {}
    for sub, _, sup in graph.triples((None, rdflib.RDFS.subClassOf, None)):
        subclasses.setdefault(str(sup), set()).add(str(sub))

    def closure(cls: str) -> set:
        seen: set = set()
        stack = [cls]
        while stack:
            cur = stack.pop()
            if cur in seen:
                continue
            seen.add(cur)
            stack.extend(subclasses.get(cur, ()))
        return seen

    def expand(node) -> list:
        """A declared class node -> the list of gem: class IRIs it names."""
        if isinstance(node, URIRef):
            return [str(node)]
        out = []
        for head in graph.objects(node, rdflib.OWL.unionOf):
            try:
                out.extend(str(m) for m in rdflib.collection.Collection(graph, head))
            except Exception:
                pass
        return out

    props = set(graph.subjects(rdflib.RDF.type, rdflib.OWL.ObjectProperty))
    props |= set(graph.subjects(rdflib.RDF.type, rdflib.OWL.DatatypeProperty))

    declarations = 0
    for prop in sorted(props, key=str):
        if not str(prop).startswith(str(GEM)):
            continue
        p_local = str(prop).split("/")[-1]
        for position, pred in (("domain", rdflib.RDFS.domain),
                               ("range", rdflib.RDFS.range)):
            for decl in graph.objects(prop, pred):
                names = [n for n in expand(decl) if n.startswith(str(GEM))]
                if not names:
                    continue
                declarations += 1
                locals_ = [n.split("/")[-1] for n in names]
                external = [_EXTERNALLY_TYPED_CLASSES[n]
                            for n in locals_ if n in _EXTERNALLY_TYPED_CLASSES]
                permitted: set = set()
                for n in names:
                    permitted |= closure(n)
                for subj, _, obj in instances.triples((None, prop, None)):
                    node = subj if position == "domain" else obj
                    if not isinstance(node, URIRef):
                        continue
                    types = {str(t) for t in instances.objects(node, rdflib.RDF.type)}
                    if external:
                        # Judged purely by IRI namespace: these classes' typing
                        # triples are not in the validation graph, so an
                        # asserted type is neither expected nor required.
                        allowed = tuple(ns for group in external for ns in group)
                        if str(node).startswith(allowed):
                            continue
                        if types & permitted:
                            continue
                        findings.append(Finding(
                            tier="RED",
                            category="domain_range_conformance",
                            file="GEM_policy_instances.ttl",
                            location=str(node).split("/")[-1],
                            message=(
                                f"gem:{p_local}'s rdfs:{position} is declared "
                                f"{'/'.join('gem:' + n for n in locals_)}, an "
                                f"externally-typed code class whose members live "
                                f"in {' or '.join(allowed)}, but {node} is in "
                                f"neither namespace. A code reference minted in "
                                f"the gem: namespace diverges from every other "
                                f"policy's IRI for the same code and is silently "
                                f"missed by cross-policy queries (see the "
                                f"external-code namespace divergence failure "
                                f"mode)."
                            ),
                        ))
                        continue
                    if not types:
                        findings.append(Finding(
                            tier="YELLOW",
                            category="domain_range_conformance",
                            file="GEM_policy_instances.ttl",
                            location=str(node).split("/")[-1],
                            message=(
                                f"gem:{p_local}'s rdfs:{position} is declared "
                                f"{'/'.join('gem:' + n for n in locals_)}, but "
                                f"{node} carries no asserted rdf:type. Either "
                                f"type it or drop the triple; an untyped node "
                                f"acquires the declared type by entailment and "
                                f"the gap stops being visible."
                            ),
                        ))
                        continue
                    if types & permitted:
                        continue
                    shown = ", ".join(sorted("gem:" + t.split("/")[-1]
                                             for t in types))
                    findings.append(Finding(
                        tier="RED",
                        category="domain_range_conformance",
                        file="GEM_policy_instances.ttl",
                        location=str(node).split("/")[-1],
                        message=(
                            f"gem:{p_local}'s rdfs:{position} is declared "
                            f"{'/'.join('gem:' + n for n in locals_)}, but "
                            f"{node} is asserted as {shown}. Under RDFS "
                            f"inference the declaration would type this node "
                            f"into the declared class, so the violation "
                            f"manufactures its own justification and the "
                            f"inferred class census is wrong. Widen the domain "
                            f"to a union, retype the individual, or drop the "
                            f"triple."
                        ),
                    ))

    if declarations == 0:
        findings.append(Finding(
            tier="YELLOW",
            category="domain_range_conformance",
            file="GEM_ontology.ttl",
            location="(ontology)",
            message=(
                "No gem: property declares an rdfs:domain or rdfs:range naming "
                "a gem: class, so this check had nothing to check with. The "
                "real ontology declares dozens. Inert-precondition rule "
                "(S144): a benign default is reported, not returned silently."
            ),
        ))
    return findings


def check_policyrule_completeness(
    files: dict[str, bytes], graph: rdflib.Graph,
) -> list[Finding]:
    """Decision 6 Part B (Phase 3): every gem:PolicyRule individual must carry:
      - exactly one gem:ruleDescription (RED if 0 or >1)
      - dc:source                       (RED if missing)
      - gem:memberOfOntology            (RED if missing)
      - gem:prefLabel                   (YELLOW if missing, per Decision 2)
      - gem:ruleType                    (YELLOW if missing, expected per gem_rule_categories.md)
      - gem:ruleDomain                  (smart per-policy check, B2.c):
          YELLOW only if the parent policy is multi-domain — i.e., some
          PolicyRules on it carry ruleDomain and some don't. Single-domain
          policies legitimately omit ruleDomain on all rules per the ontology's
          documented gem:ruleDomain semantics; that absence is silent.
    """
    findings: list[Finding] = []
    if graph is None:
        return findings
    instances = parse_instances_only(files)
    if instances is None:
        return findings

    # Collect all PolicyRules and bucket by their dc:source parent policy
    # for the smart-domain check.
    rules_by_policy: dict[URIRef, list[URIRef]] = {}
    all_rules: list[URIRef] = []
    for rule in instances.subjects(rdflib.RDF.type, GEM.PolicyRule):
        all_rules.append(rule)
        for src in instances.objects(rule, DC.source):
            if isinstance(src, URIRef):
                rules_by_policy.setdefault(src, []).append(rule)

    # Per-rule required and optional-expected checks.
    for rule in all_rules:
        local = str(rule).split("/")[-1]

        rd_count = sum(1 for _ in instances.objects(rule, GEM.ruleDescription))
        if rd_count != 1:
            findings.append(Finding(
                tier="RED",
                category="policyrule_completeness",
                file="GEM_policy_instances.ttl",
                location=f"gemi:{local}",
                message=(
                    f"gemi:{local} (gem:PolicyRule) carries {rd_count} "
                    f"gem:ruleDescription triple(s); exactly 1 is required."
                ),
            ))

        if not any(True for _ in instances.objects(rule, DC.source)):
            findings.append(Finding(
                tier="RED",
                category="policyrule_completeness",
                file="GEM_policy_instances.ttl",
                location=f"gemi:{local}",
                message=(
                    f"gemi:{local} (gem:PolicyRule) is missing dc:source. "
                    f"Required: a dc:source IRI pointing at the parent "
                    f"gem:CMSpolicy individual per Decision 5."
                ),
            ))

        if not any(True for _ in instances.objects(rule, GEM.memberOfOntology)):
            findings.append(Finding(
                tier="RED",
                category="policyrule_completeness",
                file="GEM_policy_instances.ttl",
                location=f"gemi:{local}",
                message=(
                    f"gemi:{local} (gem:PolicyRule) is missing gem:memberOfOntology."
                ),
            ))

        if not any(True for _ in instances.objects(rule, GEM.prefLabel)):
            findings.append(Finding(
                tier="YELLOW",
                category="policyrule_completeness",
                file="GEM_policy_instances.ttl",
                location=f"gemi:{local}",
                message=(
                    f"gemi:{local} (gem:PolicyRule) is missing gem:prefLabel. "
                    f"Expected per Decision 2 (format: '<policy-identifier> R<n>')."
                ),
            ))

        if not any(True for _ in instances.objects(rule, GEM.ruleType)):
            findings.append(Finding(
                tier="YELLOW",
                category="policyrule_completeness",
                file="GEM_policy_instances.ttl",
                location=f"gemi:{local}",
                message=(
                    f"gemi:{local} (gem:PolicyRule) carries zero gem:ruleType "
                    f"triples. Expected at least one categorization per "
                    f"gem_rule_categories.md."
                ),
            ))

    # Smart-domain ruleDomain check (B2.c): per parent policy, partition rules
    # by presence/absence of gem:ruleDomain. YELLOW only for rules missing
    # ruleDomain when SOME of their siblings have it (multi-domain policy
    # with partial-coverage gap). Silent when ALL rules on a policy lack
    # ruleDomain (single-domain policy, legitimate absence).
    for parent_policy, rules in rules_by_policy.items():
        has_domain: list[URIRef] = []
        no_domain: list[URIRef] = []
        for r in rules:
            if any(True for _ in instances.objects(r, GEM.ruleDomain)):
                has_domain.append(r)
            else:
                no_domain.append(r)
        if has_domain and no_domain:
            parent_local = str(parent_policy).split("/")[-1]
            for r in no_domain:
                local = str(r).split("/")[-1]
                findings.append(Finding(
                    tier="YELLOW",
                    category="policyrule_completeness",
                    file="GEM_policy_instances.ttl",
                    location=f"gemi:{local}",
                    message=(
                        f"gemi:{local} (gem:PolicyRule) is missing "
                        f"gem:ruleDomain, but its parent policy "
                        f"gemi:{parent_local} appears multi-domain "
                        f"({len(has_domain)} sibling rule(s) carry ruleDomain). "
                        f"Likely partial-coverage gap (B2.c smart-domain check)."
                    ),
                ))

    return findings


def check_policyrule_provenance_reciprocity(
    files: dict[str, bytes], graph: rdflib.Graph,
) -> list[Finding]:
    """Decision 6 Part B + Phase 4 (S83 generalization) — bidirectional,
    PolicyRule-scoped, polymorphic over both policy-scope and anchor-scope
    PolicyRules:

      Forward (X -> PR):
        every <X> gem:hasPolicyRule <PR>, where <X> is either a
        gem:CMSpolicy subclass (Phase 3 / policy-scope) or a
        gem:AnchoredCodingScope subclass (Phase 4 / anchor-scope), implies
        <PR> dc:source <expected_p>:
          - if <X> is a CMSpolicy, <expected_p> = <X> (Phase 3 case);
          - if <X> is an AnchoredCodingScope, <expected_p> = its parent
            CMSpolicy, determined by the unique node that links to <X> via
            gem:hasPolicyGroup or gem:hasPolicyCodingRule (the two
            sub-properties of gem:hasAnchoredCodingScope; OWL inference is
            NOT run during audit so the umbrella triple cannot be assumed
            materialized).
        If <X> is neither CMSpolicy nor AnchoredCodingScope, that is itself
        a type error (PolicyRule hung from an inappropriate subject).

      Backward (PR -> P, PolicyRule-scoped):
        every <PR> of type gem:PolicyRule with <PR> dc:source <P> implies
        SOME node from the candidate set carries gem:hasPolicyRule <PR>:
          candidate_set = {<P>} U {<A> : <P> hasPolicyGroup <A>
                                 or <P> hasPolicyCodingRule <A>}
        For Phase 3 the candidate is <P> itself; for Phase 4 it is one of
        <P>'s anchor-scope children. If no candidate carries the reciprocal
        triple, the PolicyRule is an orphan (likely partial-migration
        failure).

    The backward direction is scoped to gem:PolicyRule subjects to avoid
    false-flagging other dependent individuals (credentials, clinical
    concepts, AnchoredCodingScope subjects) whose dc:source values point at
    policies without an expected reciprocal predicate.

    Renamed from check_phase3_provenance_reciprocity at S83 (2026-06-22)
    to drop the phase-temporal naming now that PolicyRules attach to both
    policy-scope and anchor-scope subjects. Finding category is
    "policyrule_reciprocity".
    """
    findings: list[Finding] = []
    if graph is None:
        return findings
    instances = parse_instances_only(files)
    if instances is None:
        return findings

    # Subclass closure over gem:CMSpolicy and gem:AnchoredCodingScope
    # (precedent: check_workflow_state_coverage for the CMSpolicy closure).
    cms_classes = {GEM.CMSpolicy}
    for sub in graph.subjects(rdflib.RDFS.subClassOf, GEM.CMSpolicy):
        cms_classes.add(sub)
    acs_classes = {GEM.AnchoredCodingScope}
    for sub in graph.subjects(rdflib.RDFS.subClassOf, GEM.AnchoredCodingScope):
        acs_classes.add(sub)

    def is_cmspolicy(node: URIRef) -> bool:
        return any(
            (node, rdflib.RDF.type, c) in instances for c in cms_classes
        )

    def is_anchored_coding_scope(node: URIRef) -> bool:
        return any(
            (node, rdflib.RDF.type, c) in instances for c in acs_classes
        )

    def parent_policies_of_acs(acs: URIRef) -> list[URIRef]:
        """Return CMSpolicy nodes that link to <acs> via the
        sub-properties of gem:hasAnchoredCodingScope (no OWL inference is
        run during audit, so we query the sub-properties explicitly)."""
        parents: list[URIRef] = []
        for pred in (GEM.hasPolicyGroup, GEM.hasPolicyCodingRule):
            for parent in instances.subjects(pred, acs):
                if isinstance(parent, URIRef):
                    parents.append(parent)
        return parents

    # Forward direction
    for x, pr in instances.subject_objects(GEM.hasPolicyRule):
        if not isinstance(x, URIRef) or not isinstance(pr, URIRef):
            continue
        x_local = str(x).split("/")[-1]
        pr_local = str(pr).split("/")[-1]

        x_is_cms = is_cmspolicy(x)
        x_is_acs = is_anchored_coding_scope(x)

        if x_is_cms:
            # Phase 3 case: expected dc:source target is <x> itself.
            if (pr, DC.source, x) not in instances:
                findings.append(Finding(
                    tier="RED",
                    category="policyrule_reciprocity",
                    file="GEM_policy_instances.ttl",
                    location=f"gemi:{x_local} -> gemi:{pr_local}",
                    message=(
                        f"Forward reciprocity broken (policy-scope): "
                        f"gemi:{x_local} gem:hasPolicyRule gemi:{pr_local}, "
                        f"but gemi:{pr_local} is missing the reciprocal "
                        f"dc:source pointing at gemi:{x_local}."
                    ),
                ))
        elif x_is_acs:
            # Phase 4 case: expected dc:source target is x's parent CMSpolicy.
            parents = parent_policies_of_acs(x)
            if not parents:
                # AnchoredCodingScope with no parent policy — itself a
                # structural break (orphan anchor scope). Flag as a
                # reciprocity finding since it prevents Phase 4
                # provenance from being resolvable.
                findings.append(Finding(
                    tier="RED",
                    category="policyrule_reciprocity",
                    file="GEM_policy_instances.ttl",
                    location=f"gemi:{x_local} -> gemi:{pr_local}",
                    message=(
                        f"Forward reciprocity unresolvable (anchor-scope): "
                        f"gemi:{x_local} gem:hasPolicyRule gemi:{pr_local}, "
                        f"but gemi:{x_local} has no parent gem:CMSpolicy via "
                        f"gem:hasPolicyGroup or gem:hasPolicyCodingRule — "
                        f"cannot determine the expected dc:source target."
                    ),
                ))
            else:
                # PR must dc:source at least one of the parents (typically
                # exactly one — an anchor scope normally belongs to a
                # single policy).
                if not any((pr, DC.source, p) in instances for p in parents):
                    parent_locals = ", ".join(
                        f"gemi:{str(p).split('/')[-1]}" for p in parents
                    )
                    findings.append(Finding(
                        tier="RED",
                        category="policyrule_reciprocity",
                        file="GEM_policy_instances.ttl",
                        location=f"gemi:{x_local} -> gemi:{pr_local}",
                        message=(
                            f"Forward reciprocity broken (anchor-scope): "
                            f"gemi:{x_local} (gem:AnchoredCodingScope) "
                            f"gem:hasPolicyRule gemi:{pr_local}, but "
                            f"gemi:{pr_local} dc:source does not point at "
                            f"the expected parent policy ({parent_locals})."
                        ),
                    ))
        else:
            # X is neither CMSpolicy nor AnchoredCodingScope — type error.
            findings.append(Finding(
                tier="RED",
                category="policyrule_reciprocity",
                file="GEM_policy_instances.ttl",
                location=f"gemi:{x_local} -> gemi:{pr_local}",
                message=(
                    f"Type error: gemi:{x_local} gem:hasPolicyRule "
                    f"gemi:{pr_local}, but gemi:{x_local} is neither a "
                    f"gem:CMSpolicy subclass nor a gem:AnchoredCodingScope "
                    f"subclass. gem:hasPolicyRule's domain is restricted to "
                    f"the union of these two classes."
                ),
            ))

    # Backward direction (gem:PolicyRule-scoped)
    for pr in instances.subjects(rdflib.RDF.type, GEM.PolicyRule):
        for p in instances.objects(pr, DC.source):
            if not isinstance(p, URIRef):
                continue
            pr_local = str(pr).split("/")[-1]
            p_local = str(p).split("/")[-1]
            # Candidate-pointer set: P itself, plus P's anchor-scope children.
            candidates: list[URIRef] = [p]
            for pred in (GEM.hasPolicyGroup, GEM.hasPolicyCodingRule):
                for acs in instances.objects(p, pred):
                    if isinstance(acs, URIRef):
                        candidates.append(acs)
            if not any(
                (cand, GEM.hasPolicyRule, pr) in instances
                for cand in candidates
            ):
                findings.append(Finding(
                    tier="RED",
                    category="policyrule_reciprocity",
                    file="GEM_policy_instances.ttl",
                    location=f"gemi:{pr_local} -> gemi:{p_local}",
                    message=(
                        f"Backward reciprocity broken: gemi:{pr_local} "
                        f"(gem:PolicyRule) dc:source gemi:{p_local}, but "
                        f"neither gemi:{p_local} nor any of its "
                        f"anchor-scope children carries the reciprocal "
                        f"gem:hasPolicyRule pointing at gemi:{pr_local}. "
                        f"This is an orphan PolicyRule — likely a "
                        f"partial-migration failure."
                    ),
                ))

    return findings


def check_controlled_vocab_integrity(
    files: dict[str, bytes], graph: rdflib.Graph,
) -> list[Finding]:
    """Decision 6 Part B (Phase 3), B3.b resolution — value-type AND subject-type:

      Value-side (alpha): every gem:ruleDomain object must be a gem:RuleDomain
        individual; every gem:ruleType object must be a gem:RuleType individual.

      Subject-side (beta): both predicates may only appear with gem:PolicyRule
        subjects (their rdfs:domain). Use on a non-PolicyRule subject (policy,
        scope, etc.) is invalid.

    Both passes run graph-wide on the predicates' triple set. Type lookups use
    the full graph (which carries the ontology stub plus instances) so that
    controlled-vocab individuals declared in the ontology are correctly
    recognized as members of their class.
    """
    findings: list[Finding] = []
    if graph is None:
        return findings
    instances = parse_instances_only(files)
    if instances is None:
        return findings

    # Expected value-class per predicate
    pred_value_class = [
        (GEM.ruleDomain, GEM.RuleDomain),
        (GEM.ruleType, GEM.RuleType),
    ]

    for pred, expected_class in pred_value_class:
        pred_local = str(pred).split("/")[-1]
        expected_local = str(expected_class).split("/")[-1]

        for subj, obj in instances.subject_objects(pred):
            subj_local = str(subj).split("/")[-1]
            obj_local = (
                str(obj).split("/")[-1] if isinstance(obj, URIRef) else f'"{obj}"'
            )

            # alpha: value-side type check
            if isinstance(obj, URIRef) and (obj, rdflib.RDF.type, expected_class) in graph:
                obj_is_expected = True
            else:
                obj_is_expected = False
            if not obj_is_expected:
                findings.append(Finding(
                    tier="RED",
                    category="controlled_vocab",
                    file="GEM_policy_instances.ttl",
                    location=f"gemi:{subj_local} gem:{pred_local} {obj_local}",
                    message=(
                        f"Value-type misuse (alpha): {obj_local} is used as a "
                        f"gem:{pred_local} value on gemi:{subj_local}, but is "
                        f"not asserted as rdf:type gem:{expected_local}. Every "
                        f"gem:{pred_local} value must be a gem:{expected_local} "
                        f"individual from the controlled vocabulary."
                    ),
                ))

            # beta: subject-domain type check
            subj_is_policyrule = (subj, rdflib.RDF.type, GEM.PolicyRule) in graph
            if not subj_is_policyrule:
                findings.append(Finding(
                    tier="RED",
                    category="controlled_vocab",
                    file="GEM_policy_instances.ttl",
                    location=f"gemi:{subj_local} gem:{pred_local} {obj_local}",
                    message=(
                        f"Subject-domain misuse (beta): gemi:{subj_local} "
                        f"carries a gem:{pred_local} triple, but is not typed "
                        f"as gem:PolicyRule. The predicate's rdfs:domain is "
                        f"gem:PolicyRule; use on policies, scopes, or other "
                        f"subjects is invalid."
                    ),
                ))

    return findings


# ============================================================================
# Handoff drift check (v0.2 — Approach D: annotations + structured claims)
# ============================================================================
#
# Spec: scan handoff §4 prose for policy-identifier patterns and emit a
# "drift annotation" for each (current graph state). Also parse optional
# `<!-- AUDIT-CLAIMS ... -->` YAML blocks and verify each claim against the
# graph; failures fire RED findings.
#
# Tier semantics:
#   - Annotations: tier="INFO" — informational; do NOT affect exit code.
#     Rendered as a dedicated [HANDOFF ANNOTATIONS] section in emit_pretty.
#   - Structured-claim FAILURE → RED (handoff statement contradicts graph).
#   - Malformed YAML in a claim block → YELLOW (author must fix syntax).
#   - PyYAML unavailable → YELLOW once (claim track degrades; annotations still run).

IDENTIFIER_PATTERNS = [
    # (compiled_regex, group_index_for_payload, prefix_for_gemi_uri, case_transform)
    # Order matters — longer/more-specific patterns first.
    # gemi: local names are >=3 chars in practice; the bound skips template
    # placeholders like `gemi:a<NN>` that appear in prose.
    (re.compile(r'\bgemi:([a-zA-Z0-9_.\-]{3,})'), 1, "",      None),       # gemi:tn78 etc.
    (re.compile(r'\bNCD\s+(\d+(?:\.\d+)*)\b'),    1, "ncd",   None),       # NCD 240.2.1
    (re.compile(r'\bLCD\s+L?(\d+)\b'),            1, "lcd",   None),       # LCD L33797 or LCD 33797
    (re.compile(r'(?<![A-Za-z0-9])L(\d{5})\b'),   1, "lcd",   None),       # L33797 standalone
    (re.compile(r'(?<![A-Za-z0-9])A(\d{5})\b'),   1, "a",     None),       # A52466 standalone
    (re.compile(r'\bTN\s+(\d+)\b'),               1, "tn",    None),       # TN 78, TN 2476
    (re.compile(r'\bPM\s+([A-Z]+[\-A-Z0-9]*\d)', re.IGNORECASE), 1, "pm", None),   # PM B-01-28
    (re.compile(r'\bCAG-?(\d{5,}[A-Za-z]?)\b'),   1, "cag",   "lower"),    # CAG-00313R
]


def find_identifiers_in_text(text: str) -> list[tuple[str, str]]:
    """Find policy-identifier mentions. Returns [(raw_match, gemi_uri), ...]
    deduplicated by gemi_uri (earliest text-position wins), ordered by position."""
    all_matches = []  # list of (start_pos, raw_match, gemi_uri)
    for pat, group_idx, prefix, transform in IDENTIFIER_PATTERNS:
        for m in pat.finditer(text):
            payload = m.group(group_idx)
            if transform == "lower":
                payload = payload.lower()
            gemi_uri = f"gemi:{prefix}{payload}"
            all_matches.append((m.start(), m.group(0), gemi_uri))
    # Sort by text position so the earliest occurrence wins on dedup.
    all_matches.sort(key=lambda t: t[0])
    seen = set()
    result = []
    for _pos, raw, uri in all_matches:
        if uri not in seen:
            seen.add(uri)
            result.append((raw, uri))
    return result


def annotate_identifier(uri: str, graph) -> str:
    """One-line graph-state annotation for a gemi: URI. Fields whose value is
    zero/empty/none are omitted to keep output focused on actionable signal."""
    local = uri.split(":", 1)[1] if ":" in uri else uri
    iri = URIRef(str(GEMI) + local)
    rdf_type = URIRef("http://www.w3.org/1999/02/22-rdf-syntax-ns#type")
    types = list(graph.objects(iri, rdf_type))
    if not types:
        return "NOT IN GRAPH"
    type_names = [str(t).rsplit("/", 1)[-1] for t in types]

    parts = ["/".join(type_names)]

    nps_set = sorted({str(o).rsplit("/", 1)[-1]
                      for o in graph.objects(iri, GEM.nextPlannedStep)})
    if nps_set:
        parts.append(f"planStep={'/'.join(nps_set)}")

    iie_set = sorted({str(o) for o in graph.objects(iri, GEM.isInEffect)})
    if iie_set:
        parts.append(f"isInEffect={'/'.join(iie_set)}")

    refs_out = sum(1 for _ in graph.objects(iri, GEM.referencesPolicy))
    if refs_out:
        parts.append(f"refsOut={refs_out}")

    revises_out = sum(1 for _ in graph.objects(iri, GEM.revisesPolicy))
    if revises_out:
        parts.append(f"revisesOut={revises_out}")

    labels = list(graph.objects(iri, GEM.prefLabel))
    if labels:
        label_text = str(labels[0])
        label_disp = label_text[:55] + ("…" if len(label_text) > 55 else "")
        parts.append(f"label={label_disp!r}")

    return ", ".join(parts)


ITEM_FORM_NUMBERED = "N. **Title**"
ITEM_FORM_PARENTHESIZED = "**(a) Title**"


def parse_handoff_section_4(handoff_text: str) -> list[tuple[str, str]]:
    """Return [(item_heading, item_body), ...] from handoff §4.

    Two item forms are accepted:

        1. **NCD stub-promotion campaign.** 16 NCD stubs remain ...  <- corpus
        **(a) Some open item.** Body text ...                        <- legacy

    S144 defect (sibling of the check_empirical_counts session-regex defect):
    only the legacy form was matched, so on every real handoff this returned []
    and check_handoff_drift's `if not items: return findings` made audit
    category 11 inert — no §4 identifier annotations, no claim verification.
    As with the session regex, the self-test fixture (V33) synthesized the
    legacy form, so the suite could not see it. Fixtures now cover both
    (V33 corpus form, V44 legacy form).
    """
    m = re.search(r'^## §4 — Open items', handoff_text, re.MULTILINE)
    if not m:
        return []
    s4_start = m.end()
    m2 = re.search(r'^## ', handoff_text[s4_start:], re.MULTILINE)
    s4_text = (handoff_text[s4_start : s4_start + m2.start()]
               if m2 else handoff_text[s4_start:])

    # Alternation, not two passes: item order must follow document order so the
    # body of each item runs to the start of the next, whichever form it takes.
    # The title captures are non-greedy and newline-free, so they stop at the
    # closing "**" of the bolded lead-in even when the body continues on the
    # same line (e.g. "1. **Title.** More prose ...").
    item_re = re.compile(
        r'^(?:\*\*\((?P<pmark>[ivxlcdm]+|[a-z]+|\d+)\)\s+(?P<ptitle>[^\n]+?)\*\*'
        r'|(?P<nmark>\d+)\.[ \t]+\*\*(?P<ntitle>[^\n]+?)\*\*)',
        re.MULTILINE | re.IGNORECASE,
    )
    matches = list(item_re.finditer(s4_text))
    items = []
    for i, m_i in enumerate(matches):
        marker = m_i.group("pmark") if m_i.group("pmark") is not None else m_i.group("nmark")
        title = m_i.group("ptitle") if m_i.group("ptitle") is not None else m_i.group("ntitle")
        title = title.rstrip().rstrip(".").strip()
        body_start = m_i.start()
        body_end = matches[i + 1].start() if i + 1 < len(matches) else len(s4_text)
        body = s4_text[body_start:body_end]
        items.append((f"({marker}) {title}", body))
    return items


def parse_claim_blocks(text: str) -> tuple[list[dict], list[str]]:
    """Parse <!-- AUDIT-CLAIMS ... --> YAML blocks. Returns (claims, errors)."""
    try:
        import yaml
    except ImportError:
        return [], ["PyYAML not installed; structured claim blocks not parsed. "
                    "Install: pip install pyyaml --break-system-packages"]

    claims = []
    errors = []
    for m in re.finditer(r'<!--\s*AUDIT-CLAIMS\b(.*?)-->', text, re.DOTALL):
        body = m.group(1).strip()
        if not body:
            continue
        try:
            parsed = yaml.safe_load(body)
        except yaml.YAMLError as e:
            errors.append(f"Malformed YAML in AUDIT-CLAIMS block: {e}")
            continue
        if parsed is None:
            continue
        if not isinstance(parsed, list):
            errors.append(f"AUDIT-CLAIMS body must be a YAML list; "
                          f"got {type(parsed).__name__}")
            continue
        for entry in parsed:
            if not isinstance(entry, dict) or len(entry) != 1:
                errors.append(f"Each claim must be a single-key dict; got {entry!r}")
                continue
            ((ctype, cargs),) = entry.items()
            if not isinstance(cargs, dict):
                errors.append(f"Claim args for {ctype!r} must be a dict; got {cargs!r}")
                continue
            claims.append({"_type": ctype, **cargs})
    return claims, errors


def _resolve_curie(s) -> Optional[URIRef]:
    """Resolve 'gemi:foo' or 'gem:bar' to URIRef. None if not a string."""
    if not isinstance(s, str):
        return None
    if s.startswith("gemi:"):
        return URIRef(str(GEMI) + s.split(":", 1)[1])
    if s.startswith("gem:"):
        return URIRef(str(GEM) + s.split(":", 1)[1])
    return URIRef(s)


def verify_claim(claim: dict, graph) -> Optional[str]:
    """Verify a single claim against the graph. None on pass, error string on fail."""
    rdf_type = URIRef("http://www.w3.org/1999/02/22-rdf-syntax-ns#type")
    ctype = claim.get("_type")

    if ctype == "graph_state":
        uri = claim.get("uri")
        if not uri:
            return "graph_state claim missing 'uri'"
        iri = _resolve_curie(uri)
        actual_types = [str(t).rsplit("/", 1)[-1]
                        for t in graph.objects(iri, rdf_type)]
        if not actual_types:
            return f"graph_state {uri}: URI not in graph"
        problems = []
        if "type" in claim and claim["type"] not in actual_types:
            problems.append(f"type expected {claim['type']!r}, actual {actual_types!r}")
        if "nextPlannedStep" in claim:
            actual_nps = [str(o).rsplit("/", 1)[-1]
                          for o in graph.objects(iri, GEM.nextPlannedStep)]
            if claim["nextPlannedStep"] not in actual_nps:
                problems.append(f"nextPlannedStep expected "
                                f"{claim['nextPlannedStep']!r}, actual {actual_nps!r}")
        if "isInEffect" in claim:
            actual_iie = [str(o).lower()
                          for o in graph.objects(iri, GEM.isInEffect)]
            expected = str(claim["isInEffect"]).lower()
            if expected not in actual_iie:
                problems.append(f"isInEffect expected {expected!r}, actual {actual_iie!r}")
        if problems:
            return f"graph_state {uri}: " + "; ".join(problems)
        return None

    if ctype == "graph_triple_present":
        s = _resolve_curie(claim.get("subject"))
        p = _resolve_curie(claim.get("predicate"))
        o = _resolve_curie(claim.get("object"))
        if not (s and p and o):
            return "graph_triple_present: missing subject/predicate/object"
        if (s, p, o) not in graph:
            return f"graph_triple_present: <{s.n3()}> <{p.n3()}> <{o.n3()}> NOT in graph"
        return None

    if ctype == "graph_triple_absent":
        s = _resolve_curie(claim.get("subject"))
        p = _resolve_curie(claim.get("predicate"))
        o = _resolve_curie(claim.get("object"))
        if not (s and p and o):
            return "graph_triple_absent: missing subject/predicate/object"
        if (s, p, o) in graph:
            return (f"graph_triple_absent: <{s.n3()}> <{p.n3()}> <{o.n3()}> "
                    f"IS in graph (should be absent)")
        return None

    if ctype == "predicate_count":
        s_raw = claim.get("subject")
        o_raw = claim.get("object")
        s = _resolve_curie(s_raw) if s_raw else None
        o = _resolve_curie(o_raw) if o_raw else None
        p = _resolve_curie(claim.get("predicate"))
        if not p:
            return "predicate_count: missing 'predicate'"
        if s is None and o is None:
            return "predicate_count: must specify at least one of 'subject' or 'object'"
        expected = claim.get("expected")
        if not isinstance(expected, int):
            return f"predicate_count: 'expected' must be int; got {expected!r}"
        actual = sum(1 for _ in graph.triples((s, p, o)))
        if actual != expected:
            s_disp = s_raw if s_raw else "?"
            o_disp = o_raw if o_raw else "?"
            return (f"predicate_count: ({s_disp}, {claim.get('predicate')}, "
                    f"{o_disp}) expected {expected}, actual {actual}")
        return None

    return (f"Unknown claim type {ctype!r} (valid: graph_state, "
            "graph_triple_present, graph_triple_absent, predicate_count)")


def _section_4_inert_findings(
    handoff_text: str, handoff_label: str
) -> list[Finding]:
    """S144 inert-precondition guard for check_handoff_drift.

    parse_handoff_section_4 returning [] has two very different causes, and the
    original code could not tell them apart — it just returned, so a parser that
    matched nothing was indistinguishable from a handoff with nothing to say.
    That is how the item-form drift went unnoticed: category 11 reported clean
    while doing no work at all.

    Distinguisher: a §4 that genuinely has no open items has no bolded lead-ins
    either. Bolded content plus zero parsed items means the parser, not the
    handoff, is the problem. This also covers drift in the §4 *heading* regex
    (which pins an em-dash): the loose heading probe below still finds the
    section, so the mismatch surfaces here rather than vanishing.
    """
    m = re.search(r'^##\s*§4\b.*$', handoff_text, re.MULTILINE)
    if not m:
        return [Finding(
            tier="YELLOW", category="handoff_drift", file=handoff_label,
            message=(
                "No §4 section found in the handoff. Handoff-drift checking "
                "(§4 identifier annotation and claim verification) did no work "
                "this run."
            ),
        )]
    rest = handoff_text[m.end():]
    m2 = re.search(r'^## ', rest, re.MULTILINE)
    body = rest[:m2.start()] if m2 else rest
    if not re.search(r'\*\*.+?\*\*', body):
        return []  # genuinely itemless §4 — nothing to check, nothing wrong
    return [Finding(
        tier="YELLOW", category="handoff_drift", file=handoff_label,
        location="§4 item parser",
        message=(
            "§4 contains bolded item-like content but parse_handoff_section_4 "
            f"matched 0 items, so handoff-drift checking is inert. Expected item "
            f"form {ITEM_FORM_NUMBERED!r} or {ITEM_FORM_PARENTHESIZED!r}; the "
            "handoff's §4 uses neither. Extend the item regex or restore the form."
        ),
    )]


def check_handoff_drift(
    files: dict, graph, handoff_text: Optional[str]
) -> list[Finding]:
    """Annotate §4 identifier mentions; verify any structured claim blocks."""
    findings = []
    if handoff_text is None or graph is None:
        return findings

    handoff_label = "handoff §4"

    items = parse_handoff_section_4(handoff_text)
    if not items:
        return _section_4_inert_findings(handoff_text, handoff_label)
    annotation_chunks = []

    for heading, body in items:
        ids = find_identifiers_in_text(body)
        if ids:
            anns = [(raw, annotate_identifier(uri, graph)) for raw, uri in ids]
            annotation_chunks.append((heading, anns))

        claims, parse_errors = parse_claim_blocks(body)
        for err in parse_errors:
            findings.append(Finding(
                tier="YELLOW", category="handoff_claim",
                message=f"§4 {heading}: {err}",
                file=handoff_label, location=heading,
            ))
        for claim in claims:
            err = verify_claim(claim, graph)
            if err:
                findings.append(Finding(
                    tier="RED", category="handoff_claim",
                    message=f"§4 {heading}: {err}",
                    file=handoff_label, location=heading,
                ))

    if annotation_chunks:
        msg_lines = []
        for heading, anns in annotation_chunks:
            msg_lines.append(f"§4 {heading}")
            for raw, ann in anns:
                msg_lines.append(f"  {raw} → {ann}")
            msg_lines.append("")
        findings.append(Finding(
            tier="INFO", category="handoff_annotations",
            message="\n".join(msg_lines).rstrip(),
            file=handoff_label,
        ))

    return findings


# --- Orchestration -----------------------------------------------------------

def check_codegroup_link_drift(
    files: dict[str, bytes], graph: rdflib.Graph,
) -> list[Finding]:
    """S104: guard the materialized gem:refersToCodeGroup links.

    A policy P links to a code group G iff P references >=1 HCPCS procedure code
    that is a skos:narrower member of G or matches G's gem:memberCodePattern
    (polarity-agnostic; covers/excludes both count). These links are stored
    (materialized) in GEM_policy_instances.ttl and must stay in sync with policy
    code references and group membership. This check recomputes the expected link
    set from the current graph and diffs it against the stored links, flagging
    YELLOW on any missing (should exist, absent) or obsolete (present, should not)
    link. Fix: re-run the linking pass (regenerate the materialized block).
    """
    findings: list[Finding] = []
    if graph is None:
        return findings
    hcpcs_re = re.compile(r'^http://purl\.bioontology\.org/ontology/HCPCS/[A-Z]\d{4}$')
    skos_narrower = rdflib.URIRef("http://www.w3.org/2004/02/skos/core#narrower")
    policy_types = [GEM.CMSpolicy, GEM.NCDpolicy, GEM.LCDpolicy, GEM.ArticlePolicy,
                    GEM.TransmittalPolicy, GEM.ProgramMemorandumPolicy]
    policies = set()
    for t in policy_types:
        policies |= set(graph.subjects(rdflib.RDF.type, t))
    pol_codes: dict = {}
    for p in policies:
        codes = {str(o) for _, o in graph.predicate_objects(p)
                 if isinstance(o, rdflib.URIRef) and hcpcs_re.match(str(o))}
        if codes:
            pol_codes[p] = codes
    groups: dict = {}
    for grp in graph.subjects(rdflib.RDF.type, GEM.CodeGroup):
        members = {str(o) for o in graph.objects(grp, skos_narrower)}
        pats = []
        for o in graph.objects(grp, GEM.memberCodePattern):
            try:
                pats.append(re.compile(str(o)))
            except re.error:
                pass  # malformed regex is out of this check's scope
        groups[grp] = (members, pats)
    expected = set()
    for p, codes in pol_codes.items():
        for grp, (members, pats) in groups.items():
            if (codes & members) or any(any(pp.match(c) for c in codes) for pp in pats):
                expected.add((p, grp))
    stored = set(graph.subject_objects(GEM.refersToCodeGroup))
    missing = expected - stored
    obsolete = stored - expected
    if missing or obsolete:
        def _fmt(pairs, n=5):
            items = sorted(pairs, key=lambda x: (str(x[0]), str(x[1])))
            out = ["%s -> %s" % (str(s).split('/')[-1], str(o).split('/')[-1])
                   for s, o in items[:n]]
            return ", ".join(out) + (" ..." if len(pairs) > n else "")
        msg = ("gem:refersToCodeGroup drift: %d missing, %d obsolete "
               "(expected %d, stored %d). Re-run the linking pass to regenerate "
               "the materialized block." % (len(missing), len(obsolete),
                                            len(expected), len(stored)))
        if missing:
            msg += " Missing e.g.: %s." % _fmt(missing)
        if obsolete:
            msg += " Obsolete e.g.: %s." % _fmt(obsolete)
        findings.append(Finding(
            tier="YELLOW", category="codegroup_link_drift",
            message=msg, file="GEM_policy_instances.ttl",
        ))
    return findings


# --- codegroup_block_extent (S145) -------------------------------------------
#
# codegroup_link_drift (above) guards the materialized links' *content* against
# the graph. It never reads the file's text, so nothing guarded the block's
# *extent* — and the extent claim was false. Until S145 two comments in
# GEM_policy_instances.ttl asserted that the block "extends to EOF":
#   (i) the BEGIN marker, false from S131 onward — 49 hand-authored transmittal
#       and change-request stubs sat below the 56 link lines, inside the span the
#       documented regeneration procedure ("strip to EOF, recompute, re-append")
#       would have deleted;
#   (ii) an orphaned banner ~1,100 lines further up, which had drifted away from
#       its own block as later policy sections were inserted beneath it, so it
#       claimed 11 hand-authored policy sections as auto-generated content.
# Neither would have made a sound until someone acted on it. S145 bounded the
# block with an explicit END marker and narrowed both claims; this check enforces
# the boundary mechanically so the claim cannot silently decay again.
#
# A positional claim ("extends to EOF", "everything below") is falsified by the
# next append. The durable form is a delimited span plus a guard on it.

_CG_BEGIN_MARKER = "# === BEGIN MATERIALIZED gem:refersToCodeGroup LINKS ==="
_CG_END_MARKER = "# === END MATERIALIZED gem:refersToCodeGroup LINKS ==="
_CG_BEGIN_RE = re.compile(
    r"^#\s*===\s*BEGIN MATERIALIZED gem:refersToCodeGroup LINKS\s*===\s*$")
_CG_END_RE = re.compile(
    r"^#\s*===\s*END MATERIALIZED gem:refersToCodeGroup LINKS\s*===\s*$")
# A materialized link line, exactly as the linking pass emits it.
_CG_LINK_LINE_RE = re.compile(r"^gemi:\S+ gem:refersToCodeGroup gemi:\S+ \.$")
# Any *asserted* gem:refersToCodeGroup statement — the flat form the pass emits,
# or a predicate-list continuation inside a subject block. Comment lines are
# filtered out by the caller before this is applied, so prose mentions of the
# predicate (which are common in banners and descriptions) never match.
_CG_LINK_STMT_RE = re.compile(
    r"^\s*(?:gemi:\S+\s+)?gem:refersToCodeGroup\s+gemi:\S+\s*[;.]\s*$")


def check_codegroup_block_extent(files: dict[str, bytes]) -> list[Finding]:
    """S145: guard the *extent* of the materialized gem:refersToCodeGroup block.

    Four assertions, all YELLOW (tier matches its sibling codegroup_link_drift;
    a violation is a hazardous file state, not a wrong graph, and none of the
    four has a mechanical fix a human should not be looking at):

      1. Exactly one BEGIN marker and exactly one END marker. Zero of either is
         YELLOW, not a silent pass — the S144 inert-precondition rule: a check
         must distinguish "nothing to check" from "found nothing to check with."
         Marker drift is the exact failure mode this check exists to catch, so
         it may not be the failure mode that switches the check off.
      2. The BEGIN marker precedes the END marker.
      3. Every line strictly between the markers is a link line and nothing else.
         A hand-authored individual inside the span is a live data-loss hazard:
         the next regeneration deletes it.
      4. No asserted link statement lives outside the span. The block is the
         single home for these links; one written elsewhere survives the strip
         and comes back duplicated on the re-emit.
    """
    findings: list[Finding] = []
    data = files.get("GEM_policy_instances.ttl")
    if not data:
        return findings
    lines = data.decode("utf-8").split("\r\n")

    begins = [i for i, l in enumerate(lines) if _CG_BEGIN_RE.match(l)]
    ends = [i for i, l in enumerate(lines) if _CG_END_RE.match(l)]

    # (1) marker presence and uniqueness
    if len(begins) != 1 or len(ends) != 1:
        findings.append(Finding(
            tier="YELLOW", category="codegroup_block_extent",
            file="GEM_policy_instances.ttl",
            location="%d BEGIN / %d END markers" % (len(begins), len(ends)),
            message=(
                "materialized-block markers not found as an unambiguous pair: "
                "%d BEGIN marker(s), %d END marker(s) (expected 1 and 1). The "
                "block's extent cannot be established, so its boundary is "
                "unguarded. Expected literals: %r / %r."
                % (len(begins), len(ends), _CG_BEGIN_MARKER, _CG_END_MARKER)),
        ))
        return findings

    bi, ei = begins[0], ends[0]

    # (2) ordering
    if bi >= ei:
        findings.append(Finding(
            tier="YELLOW", category="codegroup_block_extent",
            file="GEM_policy_instances.ttl",
            location="BEGIN line %d, END line %d" % (bi + 1, ei + 1),
            message=("materialized-block markers are out of order: BEGIN at line "
                     "%d, END at line %d. BEGIN must precede END."
                     % (bi + 1, ei + 1)),
        ))
        return findings

    # (3) span contents
    intruders = [(i + 1, lines[i]) for i in range(bi + 1, ei)
                 if not _CG_LINK_LINE_RE.match(lines[i])]
    if intruders:
        sample = "; ".join("line %d: %r" % (n, l[:60]) for n, l in intruders[:5])
        findings.append(Finding(
            tier="YELLOW", category="codegroup_block_extent",
            file="GEM_policy_instances.ttl",
            location="inside block, line %d" % intruders[0][0],
            message=(
                "%d non-link line(s) inside the materialized block (lines %d-%d). "
                "The linking pass regenerates this span wholesale, so anything in "
                "it that is not a link line is deleted at the next regeneration. "
                "Move it above the BEGIN marker or below the END marker. E.g.: %s%s"
                % (len(intruders), bi + 2, ei, sample,
                   " ..." if len(intruders) > 5 else "")),
        ))

    # (4) link statements outside the span
    outside = [(i + 1, l) for i, l in enumerate(lines)
               if not (bi < i < ei)
               and not l.lstrip().startswith("#")
               and _CG_LINK_STMT_RE.match(l)]
    if outside:
        sample = "; ".join("line %d: %r" % (n, l.strip()[:60]) for n, l in outside[:5])
        findings.append(Finding(
            tier="YELLOW", category="codegroup_block_extent",
            file="GEM_policy_instances.ttl",
            location="outside block, line %d" % outside[0][0],
            message=(
                "%d gem:refersToCodeGroup statement(s) outside the materialized "
                "block. These links are a derived fact with a single home; one "
                "written elsewhere survives the strip and is duplicated by the "
                "re-emit. Move it inside the block (or delete it and re-run the "
                "linking pass). E.g.: %s%s"
                % (len(outside), sample, " ..." if len(outside) > 5 else "")),
        ))

    return findings


def check_register_section_coverage(
    files: dict[str, bytes], graph: rdflib.Graph,
) -> list[Finding]:
    """Every policy that has minted gem:PolicyRule individuals (planDone with
    >=1 hasPolicyRule) MUST have a per-policy '### <identifier>' section in
    gem_rule_categories.md, authored in the same session that minted the rules
    (SKILL.md S91 record-and-proceed; strengthened S120). A missing section is
    RED — the register may be partial only for policies not yet extracted.

    No-op when gem_rule_categories.md or the graph is unavailable (e.g. self-test
    variant contexts that emit no register file, or a graph-parse failure that is
    already surfaced by hash_verify).
    """
    findings: list[Finding] = []
    reg = files.get("gem_rule_categories.md")
    if reg is None or graph is None:
        return findings

    reg_text = reg.decode("utf-8", errors="replace")
    # Heading titles: text between '### ' and the first ' <dash> ' separator
    # (em-dash U+2014 or hyphen). Non-greedy stop at the first separator.
    titles = set(
        m.strip()
        for m in re.findall(r"^###\s+(.+?)\s+[\u2014\-]\s", reg_text, flags=re.MULTILINE)
    )

    plan_done = URIRef(str(GEM) + "planDone")
    for pol, _, _ in graph.triples((None, GEM.nextPlannedStep, plan_done)):
        if not any(True for _ in graph.objects(pol, GEM.hasPolicyRule)):
            continue  # no minted rules -> no register section required
        local = str(pol).rsplit("/", 1)[-1].rsplit("#", 1)[-1]
        ids = list(graph.objects(pol, GEM.identifier))
        if not ids:
            findings.append(Finding(
                tier="RED", category="register_section_coverage",
                file="GEM_policy_instances.ttl", location=local,
                message=(f"Rules-bearing planDone policy <{local}> has no "
                         f"gem:identifier, so its gem_rule_categories.md section "
                         f"cannot be verified."),
            ))
            continue
        idn = str(ids[0])
        if idn not in titles:
            findings.append(Finding(
                tier="RED", category="register_section_coverage",
                file="gem_rule_categories.md", location=idn,
                message=(f"Policy '{idn}' is planDone with minted gem:PolicyRule "
                         f"individuals but has no '### {idn}' section in "
                         f"gem_rule_categories.md. The per-policy section (rule "
                         f"table + borderline notes + edit-log line) must be "
                         f"authored in the same Generate turn that mints the rules "
                         f"(SKILL.md S91) and is not deferrable to a checkpoint."),
            ))
    return findings


def check_selftest_harness_integrity(
    files: dict[str, bytes], graph: rdflib.Graph,
) -> list[Finding]:
    """S104 process guard: run the self-test regression suite as part of every
    normal audit so harness degradation cannot recur silently.

    Motivated by the S103 defect: GEM_code_group_instances.ttl was added to
    TTL_FILES but the variant file-builder (_instances_graph_to_files) was not
    updated, so the guard `all(files.get(n) for n in TTL_FILES)` evaluated False
    and every variant ran with graph=None — silently no-op'ing all graph-dependent
    checks while the GREEN baselines masked it. Two layers:
      (1) structural: the variant file-builder must emit every TTL_FILES member;
      (2) behavioral: run all _VARIANTS quietly; any variant whose findings do not
          match its expectation is reported.
    This check is intentionally NOT itself a variant category (no variant runs it),
    so running the suite here cannot recurse.
    """
    findings: list[Finding] = []
    # (1) structural invariant
    try:
        emitted = set(_instances_graph_to_files(rdflib.Graph()).keys())
    except Exception as e:  # pragma: no cover
        findings.append(Finding(
            tier="RED", category="selftest_harness",
            message="self-test file-builder raised: %r" % e))
        return findings
    missing_ttls = set(TTL_FILES) - emitted
    if missing_ttls:
        findings.append(Finding(
            tier="YELLOW", category="selftest_harness",
            message=("_instances_graph_to_files omits TTL_FILES member(s) %s; "
                     "graph-dependent self-test variants will silently no-op. "
                     "Update the helper to emit them." % sorted(missing_ttls))))
    # (2) behavioral: run every variant quietly.
    # The fixtures declare the frozen _SELFTEST_GEM/_SELFTEST_GEMI namespace, which
    # is independent of the live (detected) GEM/GEMI. Bind the globals to the
    # fixture namespace for the duration of the suite so the checks — which key off
    # GEM/GEMI — match the fixture graphs, then restore in a finally so checks that
    # run after this one still see the detected namespace.
    global GEM, GEMI
    _saved_gem, _saved_gemi = GEM, GEMI
    GEM, GEMI = _SELFTEST_GEM, _SELFTEST_GEMI
    failed = []
    try:
        for label, category, builder, expected_list in _VARIANTS:
            try:
                ctx = builder()
                got = _run_variant_check(ctx, category)
                if not expected_list:
                    ok = (len(got) == 0)
                else:
                    ok = all(any(_finding_matches(f, exp) for f in got)
                             for exp in expected_list)
            except Exception:
                ok = False
            if not ok:
                failed.append(label.split(" (")[0])
    finally:
        GEM, GEMI = _saved_gem, _saved_gemi
    if failed:
        findings.append(Finding(
            tier="YELLOW", category="selftest_harness",
            message=("self-test suite degraded: %d/%d variant(s) failing: %s%s"
                     % (len(failed), len(_VARIANTS), ", ".join(failed[:8]),
                        " ..." if len(failed) > 8 else ""))))
    return findings


# --- source_availability_unverified (S156) -----------------------------------
#
# The obtainability of a pre-2000 Coverage Issues Manual transmittal's source
# rendition is a fact somebody has to go and check. S156 recorded the checked
# ones with gem:sourceAvailability; this check reports the rest.
#
# It is DERIVED, never a roster: a CIM transmittal (publicationNumber "6") with
# neither dc:source (a rendition exists and is recorded) nor gem:sourceAvailability
# (obtainability has been determined) has not been checked. Each one that
# resolves -- either way -- drops out of the report by itself, so there is no
# list to maintain and none to go stale. Tier is INFO deliberately: this is a
# work queue, not drift, and a YELLOW that fires every session until somebody
# does the work is a YELLOW that gets ignored.


def check_source_availability_unverified(
    files: dict[str, bytes], graph: rdflib.Graph,
) -> list[Finding]:
    """S156: report CIM transmittals whose source obtainability is undetermined.

    Derived from the graph, not from a roster: no dc:source AND no
    gem:sourceAvailability == nobody has checked. INFO tier; does not affect
    the exit code.
    """
    findings: list[Finding] = []
    if graph is None:
        return findings
    instances = parse_instances_only(files)
    if instances is None:
        return findings

    unverified = []
    for s in instances.subjects(rdflib.RDF.type, GEM.TransmittalPolicy):
        pub = instances.value(s, GEM.publicationNumber)
        if pub is None or str(pub) != "6":
            continue
        if instances.value(s, DC.source) is not None:
            continue
        if instances.value(s, GEM.sourceAvailability) is not None:
            continue
        unverified.append(str(s).rsplit("/", 1)[-1])

    if unverified:
        unverified.sort()
        findings.append(Finding(
            tier="INFO", category="source_availability_unverified",
            file="GEM_policy_instances.ttl",
            message=(
                "%d Coverage Issues Manual transmittal(s) carry neither dc:source nor "
                "gem:sourceAvailability, so their source obtainability is undetermined: %s. "
                "Each needs one check: if a rendition exists, add dc:source; if the document "
                "is paper-only (CMS's public transmittal archive begins at 2000), add "
                "gem:sourceAvailability gem:sourceUnobtainable and gem:nextPlannedStep "
                "gem:planNone. Resolved entries leave this list automatically."
                % (len(unverified), ", ".join("gemi:" + u for u in unverified))
            ),
        ))
    return findings


# --- ncd_census (morning count) ----------------------------------------------
#
# A status readout, not a drift check: count every gem:NCDpolicy individual and
# partition it into exactly one of five buckets, then report the buckets plus a
# total in a FIXED order. INFO tier -- it never affects the exit code and is
# always emitted (a count of zero in a bucket is itself a fact worth showing).
#
# Categorization follows claude/ncd-morning-count-rules.md. LIFECYCLE is tested
# first, read from the CMS section-title marker in gem:prefLabel AND corroborated
# by gem:isInEffect:
#   1. Retired  -- prefLabel carries the uppercase "RETIRED" marker (CMS renders
#      it "... - RETIRED (NCD N)") AND isInEffect is true (retired-in-place).
#      Retirement is independent of extraction state: a retired NCD may be
#      planDone OR planPromote and is counted here either way, never under
#      extracted/stub.
#   2. Deleted  -- prefLabel carries the "Deleted" marker ("Policy N Deleted")
#      AND isInEffect is false.
# A marker whose gem:isInEffect does NOT corroborate (a RETIRED with isInEffect
# false, a Deleted with isInEffect true, or either with isInEffect absent) is not
# trusted: it demotes to Unknown so the anomaly is investigated, never silently
# counted as retired/deleted (Tom, S244).
# WORKFLOW (gem:nextPlannedStep) then partitions the active-lifecycle remainder:
#   3. Active, extracted -- planDone.
#   4. Stub              -- planPromote.
#   5. Unknown           -- anything else: an uncorroborated lifecycle marker
#      (above), or an active-lifecycle NCD whose step is planNone, planRevisit, or
#      missing. Matches none of the four categories; usually a retired/removed
#      section whose title marker or isInEffect has not yet been set (the NCD
#      280.13 pre-correction state). Surfaced by name, never silently folded in.

_NCD_CENSUS_ORDER = [
    ("active", "Active, extracted"),
    ("stub", "Stubs"),
    ("retired", "Retired"),
    ("deleted", "Deleted"),
    ("unknown", "Unknown (uncategorized)"),
]

_RE_RETIRED_MARKER = re.compile(r"\bRETIRED\b")
_RE_DELETED_MARKER = re.compile(r"\bDeleted\b")


def _eff_repr(is_in_effect: Optional[bool]) -> str:
    if is_in_effect is None:
        return "absent"
    return "true" if is_in_effect else "false"


def _classify_ncd(
    label: str, step_localname: Optional[str], is_in_effect: Optional[bool],
) -> tuple[str, Optional[str]]:
    """Return (bucket_key, unknown_reason) for one gem:NCDpolicy.

    Lifecycle (prefLabel marker) is tested before workflow (nextPlannedStep).
    A lifecycle marker must be CORROBORATED by gem:isInEffect: retired-in-place
    requires isInEffect true, deleted requires isInEffect false. A marker whose
    isInEffect does not corroborate (incl. absent) is NOT trusted -- it demotes
    to Unknown so the anomaly gets investigated, rather than being silently
    counted as retired/deleted (Tom, S244).

    unknown_reason is None unless the bucket is 'unknown'.
    """
    if _RE_RETIRED_MARKER.search(label):
        if is_in_effect is True:
            return ("retired", None)
        return ("unknown", "RETIRED marker but isInEffect=%s" % _eff_repr(is_in_effect))
    if _RE_DELETED_MARKER.search(label):
        if is_in_effect is False:
            return ("deleted", None)
        return ("unknown", "Deleted marker but isInEffect=%s" % _eff_repr(is_in_effect))
    if step_localname == "planDone":
        return ("active", None)
    if step_localname == "planPromote":
        return ("stub", None)
    return ("unknown", step_localname or "no step")


def check_ncd_census(
    files: dict[str, bytes], graph: rdflib.Graph,
) -> list[Finding]:
    """Report a count of gem:NCDpolicy individuals by status (morning count).

    One INFO finding, always emitted, carrying a fixed-order count block. If the
    Unknown bucket is non-empty its members are named in the finding's location
    so they surface for Tom.
    """
    findings: list[Finding] = []
    if graph is None:
        return findings
    instances = parse_instances_only(files)
    if instances is None:
        return findings

    buckets: dict[str, list[str]] = {k: [] for k, _ in _NCD_CENSUS_ORDER}
    unknown_detail: list[str] = []
    for s in instances.subjects(rdflib.RDF.type, GEM.NCDpolicy):
        label = str(instances.value(s, GEM.prefLabel) or "")
        step = instances.value(s, GEM.nextPlannedStep)
        step_ln = str(step).rsplit("/", 1)[-1] if step is not None else None
        eff_lit = instances.value(s, GEM.isInEffect)
        is_in_effect = eff_lit.toPython() if eff_lit is not None else None
        bucket, reason = _classify_ncd(label, step_ln, is_in_effect)
        ln = str(s).rsplit("/", 1)[-1]
        buckets[bucket].append(ln)
        if bucket == "unknown":
            unknown_detail.append("gemi:%s (%s)" % (ln, reason))

    total = sum(len(v) for v in buckets.values())

    # Fixed-order, right-aligned count block. Width tracks the largest count.
    num_w = max([len(str(total))] + [len(str(len(v))) for v in buckets.values()])
    lines = ["gem:NCDpolicy census (GEM_policy_instances.ttl):"]
    for key, human_label in _NCD_CENSUS_ORDER:
        lines.append("  %-24s %*d" % (human_label, num_w, len(buckets[key])))
    lines.append("  %-24s %*d" % ("Total NCDs", num_w, total))

    location = None
    if unknown_detail:
        unknown_detail.sort()
        lines.append("")
        lines.append("  FLAG -- Unknown NCD(s) matching none of the four "
                     "categories; surface for Tom:")
        for d in unknown_detail:
            lines.append("    " + d)
        location = "unknown: " + ", ".join(unknown_detail)

    findings.append(Finding(
        tier="INFO", category="ncd_census",
        file="GEM_policy_instances.ttl",
        message="\n".join(lines),
        location=location,
    ))
    return findings


# --- policy_effective_date_v1 (S192) -----------------------------------------
#
# deferred_proposals[107]: gem:policyEffectiveDate and gem:policyImplementationDate
# are policy-level facts and must carry VERSION 1's values, not whichever version
# happens to be current. Both predicates move together or neither (S192, Tom).
#
# The migration is deliberately partial. All 41 NCD candidates were corrected at
# S192; the 18 LCDs/Articles were not, and gem_reference.md's definitions still
# describe the OLD reading on purpose -- [107]'s own constraint forbids the
# definition landing ahead of its values (the S45 failure mode). This check is
# what makes that half-done state visible at every bootstrap instead of only to a
# session that re-reads the proposal.
#
# KNOWN_V1_DATES is hand-maintained and deliberately so: a V1 date is a research
# result read off the source's Tracking Information block, not something derivable
# from the graph. Its value here is that it turns a research result into a
# regression test. Add a row when a policy's V1 dates are established.
#
# S260 (Tom): adding the row is part of the SAME Generate turn that mints a
# policyVersion > 1 policy, and is not asked about. Otherwise the policy enters
# the INFO queue below with its V1 dates already known -- a queue entry whose
# answer was in hand when it was created. See SKILL.md, Policy dates anchor to
# Version 1.
#
# Two tiers, split on the codebase's own INFO/YELLOW rationale (see
# source_availability_unverified):
#   INFO   -- a candidate whose V1 dates are not yet known. That is a WORK QUEUE,
#             and a YELLOW that fires every session until somebody does the work
#             is a YELLOW that gets ignored.
#   YELLOW -- a candidate whose V1 dates ARE known and whose recorded values
#             disagree with them. That is DRIFT: something re-introduced a defect
#             [107] already corrected. No autofix -- the graph edit is a value
#             correction and belongs in an extraction pass, not a sweep.
#
# Absence of gem:policyImplementationDate is NEVER a finding. A None entry in
# KNOWN_V1_DATES means V1 publishes no implementation date and the triple was
# dropped under the S192 no-manufacture ruling; 34 individuals correctly carry
# none. A guard that flagged them would manufacture the same defect by another
# route.
#
# Version 1 individuals are not candidates: their recorded dates ARE V1's.

KNOWN_V1_DATES: dict[str, tuple[str, Optional[str]]] = {
    "ncd10.2": ("1995-08-07", None),
    "ncd10.6": ("1988-07-27", None),
    "ncd20.8": ("1985-05-09", None),
    "ncd20.15": ("1985-06-01", None),
    "ncd20.16": ("1999-07-01", "1999-07-01"),
    "ncd20.19": ("2002-04-01", "2002-04-01"),
    "ncd20.25": ("1979-08-01", "1979-08-01"),
    "ncd20.29": ("2000-10-19", None),
    "ncd30.3": ("1966-01-01", None),
    "ncd30.3.1": ("2004-04-16", "2004-04-16"),
    "ncd30.3.2": ("2004-04-16", "2004-04-16"),
    "ncd40.2": ("1995-04-27", "2002-11-29"),
    "ncd50.1": ("2001-01-01", "2001-01-01"),
    "ncd50.3": ("1998-05-01", None),
    "ncd80.11": ("1992-10-01", None),
    "ncd110.4": ("1988-04-08", None),
    "ncd110.17": ("2005-01-28", "2005-04-18"),
    "ncd110.18": ("2005-04-04", "2005-07-05"),
    "ncd110.19": ("2005-03-15", "2005-05-25"),
    "ncd140.1": ("1998-10-01", "1999-04-01"),
    "ncd150.5": ("1980-03-01", None),
    "ncd160.2": ("1997-04-15", None),
    "ncd160.6": ("1966-01-01", None),
    "ncd160.7.1": ("1995-08-07", None),
    "ncd160.8": ("1966-01-01", None),
    "ncd160.12": ("2003-04-01", "2003-04-01"),
    "ncd160.18": ("1999-07-01", "1999-07-01"),
    "ncd160.22": ("1984-06-12", None),
    "ncd160.23": ("2002-10-01", "2002-10-01"),
    "ncd180.2": ("1984-07-11", None),
    "ncd190.2": ("1978-05-15", None),
    "ncd190.4": ("1966-01-01", None),
    "ncd190.14": ("2002-11-25", "2003-01-01"),
    "ncd190.20": ("2002-11-25", "2003-01-01"),
    "ncd150.3": ("1998-07-01", "1998-07-01"),
    "ncd210.1": ("2000-01-01", "2000-01-01"),
    "ncd210.2": ("2001-07-01", None),
    "ncd210.4.1": ("2010-08-25", "2011-01-03"),
    "ncd220.1": ("1985-11-22", None),
    "ncd220.6.20": ("2013-09-27", "2014-07-07"),
    "ncd230.8": ("2001-04-01", "2001-04-01"),
    "ncd230.19": ("2003-01-01", "2003-01-01"),
    "ncd240.1": ("1997-08-11", "1997-08-11"),
    "ncd240.2": ("1993-10-27", None),
    "ncd240.2.2": ("2011-01-04", "2011-02-15"),
    "ncd240.4": ("2002-04-01", "2002-04-01"),
    "ncd260.1": ("2001-09-01", "2001-09-01"),
    "ncd270.1": ("1997-07-14", None),
    "ncd280.1": ("2003-04-01", "2003-04-01"),
    "ncd280.3": ("1966-01-01", None),
    "ncd280.14": ("2002-01-01", "2002-01-01"),
    "ncd300.1": ("1997-01-01", "1997-01-01"),
    "ncd310.1": ("2000-09-19", "2000-09-19"),
}


def _pedv1_candidates(instances: rdflib.Graph) -> list[tuple[str, str, str, Optional[str]]]:
    """Every individual whose recorded gem:policyVersion is greater than 1.

    Returns (local_name, version, effective, implementation-or-None). Accepts the
    bare-numeric NCD form and the R-prefixed LCD/Article form; a version that
    parses as neither is treated as a candidate, since it cannot be shown to be 1.
    """
    out = []
    for s, eff in instances.subject_objects(GEM.policyEffectiveDate):
        ver = instances.value(s, GEM.policyVersion)
        if ver is None:
            continue
        vs = str(ver).strip()
        m = re.match(r"^R?(\d+)$", vs)
        if m and int(m.group(1)) <= 1:
            continue
        impl = instances.value(s, GEM.policyImplementationDate)
        out.append((str(s).rsplit("/", 1)[-1], vs, str(eff),
                    None if impl is None else str(impl)))
    out.sort()
    return out


def check_policy_effective_date_v1(
    files: dict[str, bytes], graph: rdflib.Graph,
) -> list[Finding]:
    """S192 / deferred_proposals[107]: policy dates must carry V1's values.

    YELLOW on disagreement with a known V1 date (drift); INFO on a candidate
    whose V1 dates are not yet researched (work queue). Missing implementation
    date is never a finding.
    """
    findings: list[Finding] = []
    if graph is None:
        return findings
    instances = parse_instances_only(files)
    if instances is None:
        return findings

    mismatched: list[str] = []
    unknown: list[str] = []
    confirmed = 0

    for name, ver, eff, impl in _pedv1_candidates(instances):
        known = KNOWN_V1_DATES.get(name)
        if known is None:
            unknown.append(name)
            continue
        want_eff, want_impl = known
        problems = []
        if eff != want_eff:
            problems.append("effective %s should be %s" % (eff, want_eff))
        if want_impl is None:
            if impl is not None:
                problems.append(
                    "implementation %s recorded but V1 publishes none; "
                    "the triple should be absent" % impl)
        elif impl is None:
            problems.append("implementation absent but V1 publishes %s" % want_impl)
        elif impl != want_impl:
            problems.append("implementation %s should be %s" % (impl, want_impl))
        if problems:
            mismatched.append("gemi:%s (%s)" % (name, "; ".join(problems)))
        else:
            confirmed += 1

    if mismatched:
        mismatched.sort()
        findings.append(Finding(
            tier="YELLOW", category="policy_effective_date_v1",
            file="GEM_policy_instances.ttl",
            message=(
                "%d individual(s) disagree with their KNOWN Version 1 dates, so a "
                "correction deferred_proposals[107] already made has been reverted or "
                "overwritten: %s. Re-read V1's Tracking Information block and restore "
                "the value; if the source has genuinely changed, update KNOWN_V1_DATES "
                "in the same pass so the two never drift apart. No autofix: this is a "
                "value correction, not a formatting sweep."
                % (len(mismatched), ", ".join(mismatched))
            ),
        ))

    if unknown:
        unknown.sort()
        findings.append(Finding(
            tier="INFO", category="policy_effective_date_v1",
            file="GEM_policy_instances.ttl",
            message=(
                "%d candidate(s) (gem:policyVersion > 1) have no researched Version 1 "
                "dates, so their recorded dates are still version facts under a "
                "policy-level name: %s. deferred_proposals[107] is 'implemented', not "
                "'complete': the NCD half was corrected at S192 and this is the "
                "remainder. Each needs V1's Tracking Information block read once; add "
                "the result to KNOWN_V1_DATES and correct the triples. Until the list "
                "empties, gem_reference.md's definitions of both properties "
                "deliberately still describe the old reading -- do not 'fix' that "
                "disagreement with SKILL.md in either direction. %d candidate(s) "
                "already confirmed against known V1 dates."
                % (len(unknown), ", ".join("gemi:" + u for u in unknown), confirmed)
            ),
        ))

    return findings


# --- skill_checklist_sync (S175) ---------------------------------------------
#
# SKILL.md's "What the audit covers" list is a hand-authored orientation
# enumeration that MUST name every ALL_CHECKS member. Before S175 it was framed
# as "orientation, never coverage" precisely because it had fallen behind the
# roster (14 documented against 28 registered, widening every session since
# S145 -- handoff item 7). This check makes the list guardable: every ALL_CHECKS
# id token must appear verbatim inside the sentinel-bracketed region, so a check
# added to the roster without a documentation line goes YELLOW.
#
# Name-presence only: the region's prose descriptions stay richer than the bare
# ids; this asserts the id string is present, not that its description is right.
# Forward-only (ALL_CHECKS subset of region); it does not flag a listed id later
# removed from the roster.
#
# The region is delimited by explicit HTML-comment sentinels (mirroring the
# codegroup BEGIN/END materialized-block markers). If the sentinels are absent
# the check raises YELLOW rather than returning silently -- an inert precondition
# is a finding, not a clean pass (S144 inert-precondition rule).

SKILL_CHECKLIST_START = "<!-- AUDIT-CHECKLIST-START -->"
SKILL_CHECKLIST_END = "<!-- AUDIT-CHECKLIST-END -->"


def check_skill_checklist_sync(
    files: dict[str, bytes], graph: rdflib.Graph,
) -> list[Finding]:
    """Every ALL_CHECKS member must be named verbatim inside SKILL.md's
    sentinel-bracketed 'What the audit covers' region (S175, handoff item 7).

    No-op when SKILL.md is unavailable (e.g. self-test variants that emit no
    markdown). YELLOW, no autofix -- each check's per-line description is
    authored, not derived, so a missing line is written by a human.
    """
    findings: list[Finding] = []
    raw = files.get("SKILL.md")
    if raw is None:
        return findings
    text = raw.decode("utf-8", errors="replace")

    start = text.find(SKILL_CHECKLIST_START)
    end = text.find(SKILL_CHECKLIST_END)
    if start == -1 or end == -1 or end < start:
        findings.append(Finding(
            tier="YELLOW", category="skill_checklist_sync", file="SKILL.md",
            message=(
                "SKILL.md audit-checklist sentinels %s / %s not found (or out "
                "of order); the 'What the audit covers' list cannot be "
                "reconciled against ALL_CHECKS. Restore the marker pair around "
                "the list." % (SKILL_CHECKLIST_START, SKILL_CHECKLIST_END)),
        ))
        return findings

    region = text[start + len(SKILL_CHECKLIST_START):end]
    missing = [name for name, _ in ALL_CHECKS if name not in region]
    if missing:
        findings.append(Finding(
            tier="YELLOW", category="skill_checklist_sync", file="SKILL.md",
            message=(
                "SKILL.md's 'What the audit covers' list omits %d ALL_CHECKS "
                "member(s): %s. Add a line naming each inside the sentinel "
                "region so the documented list stays complete against the "
                "roster." % (len(missing), ", ".join(missing))),
        ))
    return findings


# --- llm_annotation_drift (S140) ---------------------------------------------
#
# gem_llm_annotations.json is an external, hash-tracked mirror of the
# individual-level gem:llmDetailedDefinition annotations carried on GEM's
# controlled-vocabulary (enumerated-value) individuals. GEM_ontology.ttl is
# authoritative; this check keeps the mirror honest so it can never silently
# diverge (parallels processed_list / codegroup_link_drift).
#
# NOTE (S156): this tuple is a HAND-MAINTAINED ROSTER, and that is a live
# defect, not a design. New *individuals* in a listed family flow into the
# mirror automatically; a new *family* does not, and its absence is silent --
# the mirror stays green while omitting the family entirely. gem:SourceAvailability
# was added here by hand at S156 for exactly that reason, one session after the
# S140 checkpoint declared "no families pending". Deriving the roster (every
# class with >=1 individual carrying gem:llmDetailedDefinition) would close it;
# see handoff S156 §4 item 7 (hardcoded lists in prose decay) -- this is the
# same disease in code.

LLM_ANNOTATION_FILE = "gem_llm_annotations.json"
# Hand-maintained roster (S156 finding): the controlled-vocabulary
# (enumerated-value) class LOCAL NAMES that gem_llm_annotations.json mirrors.
# Edit this tuple when a family is added — a new FAMILY does not flow in
# automatically. Only the local names are hand-maintained; the URIRefs are built
# from the live (detected) GEM namespace by llm_annotated_vocab_classes(), so a
# namespace version bump needs no edit here. (Previously this was a tuple of
# GEM.-qualified URIRefs frozen at import time, which broke under runtime
# namespace detection.)
_LLM_ANNOTATED_VOCAB_LOCALNAMES = (
    "RuleType", "RuleDomain", "RestrictionType", "NextPlannedStep",
    "SourceAvailability",
)


def llm_annotated_vocab_classes() -> tuple:
    """The controlled-vocabulary classes mirrored by gem_llm_annotations.json,
    as URIRefs under the live GEM namespace (rebuilt each call so it tracks a
    runtime namespace rebind)."""
    return tuple(GEM[name] for name in _LLM_ANNOTATED_VOCAB_LOCALNAMES)


def _graph_llm_detailed_defs(graph: rdflib.Graph) -> dict[str, str]:
    """The set gem_llm_annotations.json mirrors: every individual-level
    gem:llmDetailedDefinition carried by a controlled-vocabulary individual,
    keyed by full subject URI."""
    out: dict[str, str] = {}
    for cls in llm_annotated_vocab_classes():
        for s in graph.subjects(rdflib.RDF.type, cls):
            v = graph.value(s, GEM.llmDetailedDefinition)
            if v is not None:
                out[str(s)] = str(v)
    return out


def _serialize_llm_annotations(obj: dict) -> bytes:
    """Canonical LF serialization of gem_llm_annotations.json: 2-space indent,
    non-ASCII preserved, gem:llmDetailedDefinition map sorted by subject URI,
    single trailing newline. Deterministic, so the file hash is stable and the
    autofix round-trips byte-identically."""
    obj = dict(obj)
    defs = obj.get("gem:llmDetailedDefinition", {})
    obj["gem:llmDetailedDefinition"] = {k: defs[k] for k in sorted(defs)}
    return (json.dumps(obj, indent=2, ensure_ascii=False) + "\n").encode("utf-8")


def check_llm_annotation_drift(
    files: dict[str, bytes], graph: rdflib.Graph,
) -> list[Finding]:
    """gem_llm_annotations.json's gem:llmDetailedDefinition map must equal the
    graph's individual-level gem:llmDetailedDefinition annotations on
    controlled-vocabulary individuals exactly. Any missing/extra/mismatched
    entry is drift -> YELLOW, autofixable by regenerating the map from the graph
    (GEM_ontology.ttl is authoritative). File absence is left to hash_verify;
    formatting drift is left to hash_verify. This check is purely semantic.
    """
    findings: list[Finding] = []
    raw = files.get(LLM_ANNOTATION_FILE)
    if raw is None:
        return findings  # absence surfaced by hash_verify
    if graph is None:
        return findings

    try:
        doc = json.loads(raw.decode("utf-8"))
    except (ValueError, UnicodeDecodeError) as e:
        findings.append(Finding(
            tier="RED", category="llm_annotation_drift", file=LLM_ANNOTATION_FILE,
            message=f"{LLM_ANNOTATION_FILE} is not valid JSON: {e}"))
        return findings

    json_defs = doc.get("gem:llmDetailedDefinition", {})
    if not isinstance(json_defs, dict):
        findings.append(Finding(
            tier="RED", category="llm_annotation_drift", file=LLM_ANNOTATION_FILE,
            message=("'gem:llmDetailedDefinition' must be a JSON object mapping "
                     "subject URI -> definition string.")))
        return findings

    graph_defs = _graph_llm_detailed_defs(graph)

    missing = {k for k in graph_defs if k not in json_defs}         # in graph, absent from file
    extra = {k for k in json_defs if k not in graph_defs}           # in file, not in graph
    mismatch = {k for k in set(graph_defs) & set(json_defs)
                if graph_defs[k] != json_defs[k]}
    if not (missing or extra or mismatch):
        return findings

    def _ln(uri: str) -> str:
        return uri.rsplit("/", 1)[-1]

    drift_uris = sorted(missing | extra | mismatch)
    parts = []
    if missing:
        parts.append(f"{len(missing)} in graph but absent from file")
    if extra:
        parts.append(f"{len(extra)} in file but absent from graph")
    if mismatch:
        parts.append(f"{len(mismatch)} value mismatch(es)")

    def _autofix(f: dict, _defs=dict(graph_defs), _raw=raw) -> None:
        try:
            cur = json.loads(_raw.decode("utf-8"))
        except Exception:
            cur = {}
        if not isinstance(cur, dict):
            cur = {}
        cur["gem:llmDetailedDefinition"] = _defs
        f[LLM_ANNOTATION_FILE] = _serialize_llm_annotations(cur)

    findings.append(Finding(
        tier="YELLOW", category="llm_annotation_drift", file=LLM_ANNOTATION_FILE,
        location=", ".join(_ln(u) for u in drift_uris),
        message=(
            f"{LLM_ANNOTATION_FILE} is out of sync with the graph's individual-level "
            f"gem:llmDetailedDefinition annotations ({'; '.join(parts)}). "
            f"GEM_ontology.ttl is authoritative; regenerate the mirror from the graph."),
        autofixable=True,
        autofix_fn=_autofix,
        autofix_description=(
            f"Regenerate {LLM_ANNOTATION_FILE}'s gem:llmDetailedDefinition map from "
            f"the graph ({len(graph_defs)} entr{'y' if len(graph_defs)==1 else 'ies'})."),
    ))
    return findings



# --- llm_annotation_count_drift (S166) ---------------------------------------
#
# gem_llm_annotations.json's _meta.coverage states, in hand-written prose, the
# per-family and total individual counts of the annotated controlled-vocabulary
# families ("... gem:RuleType (21), gem:RuleDomain (3), ... - 33 individuals").
# llm_annotation_drift's autofix regenerates the gem:llmDetailedDefinition MAP
# from the graph but never touches _meta, so those numbers can drift silently
# the moment a family gains or loses an annotated individual. This is handoff
# item 7 -- "hardcoded lists/counts in prose decay" -- in its load-bearing
# instance: the sibling of the S156 hand-maintained-roster defect, one field
# over. The guard reconciles the prose counts against the graph. YELLOW, no
# autofix: the sentence carries meaning around the numbers (which families,
# "No families pending", the fold-in history) that a mechanical rewrite would
# flatten, so a human edits _meta -- exactly as the new-family checklist in
# SKILL.md Common Failure Modes already requires.

def check_llm_annotation_count_drift(
    files: dict[str, bytes], graph: rdflib.Graph,
) -> list[Finding]:
    """The family/individual counts stated in gem_llm_annotations.json's
    _meta.coverage prose must match the graph. For each family in
    LLM_ANNOTATED_VOCAB_CLASSES the prose count must equal the number of that
    family's individuals carrying gem:llmDetailedDefinition; the stated total
    must equal their sum; and a family with >=1 annotated individual must be
    named. YELLOW, no autofix (the prose is human-authored around the numbers).
    Absence/JSON-validity of the file is llm_annotation_drift's to report; this
    check is silent when the file is missing or _meta.coverage is empty.
    """
    findings: list[Finding] = []
    raw = files.get(LLM_ANNOTATION_FILE)
    if raw is None or graph is None:
        return findings
    try:
        doc = json.loads(raw.decode("utf-8"))
    except (ValueError, UnicodeDecodeError):
        return findings  # JSON validity is llm_annotation_drift's to report
    coverage = ((doc.get("_meta") or {}).get("coverage") or "")
    if not coverage:
        return findings  # nothing stated -> nothing to reconcile

    # Graph truth: annotated-individual count per family, and the total.
    graph_counts: dict[str, int] = {}
    for cls in llm_annotated_vocab_classes():
        ln = str(cls).rsplit("/", 1)[-1]
        graph_counts[ln] = sum(
            1 for s in graph.subjects(rdflib.RDF.type, cls)
            if graph.value(s, GEM.llmDetailedDefinition) is not None)
    graph_total = sum(graph_counts.values())
    roster_lns = set(graph_counts)

    # Prose claims: "gem:Family (n)" tokens and the "<N> individuals" total.
    prose_counts = {ln: int(n)
                    for ln, n in re.findall(r"gem:(\w+)\s*\((\d+)\)", coverage)}
    m = re.search(r"(\d+)\s+individuals", coverage)
    prose_total = int(m.group(1)) if m else None

    problems: list[str] = []
    loc_families: list[str] = []
    for ln in sorted(roster_lns):
        gn = graph_counts[ln]
        pn = prose_counts.get(ln)
        if pn is None:
            if gn > 0:
                problems.append(
                    f"gem:{ln}: graph has {gn} annotated, not stated in _meta.coverage")
                loc_families.append(ln)
        elif pn != gn:
            problems.append(f"gem:{ln}: _meta.coverage says {pn}, graph has {gn}")
            loc_families.append(ln)
    for ln in sorted(prose_counts):
        if ln not in roster_lns:
            problems.append(
                f"gem:{ln}: stated in _meta.coverage but not in LLM_ANNOTATED_VOCAB_CLASSES")
            loc_families.append(ln)
    if prose_total is not None and prose_total != graph_total:
        problems.append(f"total: _meta.coverage says {prose_total}, graph has {graph_total}")
        loc_families.append("total")

    if not problems:
        return findings

    findings.append(Finding(
        tier="YELLOW", category="llm_annotation_count_drift", file=LLM_ANNOTATION_FILE,
        location=", ".join(loc_families),
        message=(
            "_meta.coverage's hand-written family/individual counts have drifted "
            "from the graph: " + "; ".join(problems) + ". Update _meta.coverage "
            "(and _meta.sync_note if the fold-in history is affected) to match the "
            "graph; llm_annotation_drift keeps the gem:llmDetailedDefinition map in "
            "sync but never touches _meta prose."),
    ))
    return findings


# --- literal_escape_artifact (S157) ------------------------------------------
# Hand-escaping TTL string literals in a generator's Python source is the
# project's most reliably repeated authoring error, and its failure mode is the
# dangerous kind: OVER-escaping produces a file that parses cleanly. `\\\\"` in the
# Turtle source is an escaped backslash followed by a closing quote, so the
# literal's VALUE carries a stray backslash -- `\\"attending physician\\"` where the
# author meant `"attending physician"`. Nothing else in the verification stack
# sees it: rdflib round-trips it, SHACL conforms, the triple count is right, and
# the predicate is right. Only a human reading the rendered value notices, and by
# then it is in the graph.
#
# S157 found three (credentialAttendingPhysician and
# credentialDoctorOfMedicineOrOsteopathy from S41, conceptSevereCardiacCondition
# from S155 -- two sessions old, so this is a live authoring mode and not a
# legacy artifact) after hitting the same class three times in one session's own
# emitter. The structural fix is to escape at emit time and let authors write
# plain text (SKILL.md, Session Close / emitter contract); this check is the
# guard that keeps the class from recurring silently if someone hand-writes a
# block anyway.
#
# YELLOW, autofixable: the repair is deterministic (`\\\\"` -> `\\"`), because a
# literal backslash immediately preceding a quote has no legitimate use in this
# corpus's prose -- every real occurrence is a quotation mark that was escaped
# twice. UNDER-escaping is not checkable here: it terminates the literal early
# and the file fails to parse, which is loud and immediate.
def check_literal_escape_artifact(files: dict[str, bytes]) -> list[Finding]:
    """S157: flag over-escaped quotes inside TTL string literals."""
    findings: list[Finding] = []
    # The artifact is THREE backslashes before a quote: `\\` (escaped backslash,
    # yielding a literal backslash in the value) immediately followed by `\"` (escaped
    # quote). Matching the two-backslash TAIL of that sequence and collapsing it is
    # itself a bug -- it leaves `\\"`, an escaped backslash then a live quote, which
    # terminates the literal early and fails to parse. (S157 wrote that bug first and
    # the rdflib re-parse caught it; the variants below pin the distinction.)
    artifact = "\\\\\\" + '"'          # source: \\\"  -> value carries \"
    repair = "\\" + '"'              # source: \"    -> value carries "

    for fname in sorted(TTL_FILES | {"cpt.ttl"}):
        data = files.get(fname)
        if not data:
            continue
        text = data.decode("utf-8")
        n = text.count(artifact)
        if not n:
            continue

        subjects: list[str] = []
        for m in re.finditer(re.escape(artifact), text):
            head = text.rfind("\n" + "gemi:", 0, m.start())
            if head < 0:
                head = text.rfind("\n" + "gem:", 0, m.start())
            if head >= 0:
                sm = re.match(r"([\w:.\-]+)", text[head + 1:])
                if sm:
                    subjects.append(sm.group(1))
        roster = sorted(set(subjects))

        # Compute the repair HERE and parse-probe it, rather than trusting the
        # fix closure. Two reasons, both learned at S157. (1) An escaping autofix
        # that is itself mis-escaped writes an unparseable file, and a check that
        # only counts findings cannot see it -- S157's first attempt matched the
        # artifact's two-backslash TAIL, collapsing `\\\\\\"` to `\\\\"`, an escaped
        # backslash then a live quote, which ended the literal early. (2) Because
        # the wrong pattern still FIRES, a variant asserting "YELLOW on the
        # defect" passes it. Probing at detection time makes the mutation visible
        # in the finding's TIER, which a variant can pin: a check that cannot
        # verify its own repair reports RED and offers no autofix.
        raw = data
        crlf = b"\r\n" in raw
        fixed = raw.decode("utf-8").replace("\r\n", "\n").replace(artifact, repair)
        if crlf:
            fixed = fixed.replace("\n", "\r\n")
        out = fixed.encode("utf-8")
        try:
            rdflib.Graph().parse(data=out.decode("utf-8"), format="turtle")
            # ...and that it actually removed the artifact. A repair equal to the
            # artifact is a silent no-op: the check would report YELLOW with an
            # autofix every run, the file would never change, and the finding
            # would read as actionable forever. Idempotence is the property, and
            # it has to be asserted rather than assumed.
            if artifact in out.decode("utf-8"):
                raise RuntimeError("repair left the artifact in place (no-op fix)")
            verified = True
            probe_err = None
        except Exception as e:
            verified = False
            probe_err = e

        if not verified:
            findings.append(Finding(
                tier="RED", category="literal_escape_artifact",
                file=fname,
                location=", ".join(roster[:8]),
                message=(
                    f"{n} over-escaped quote(s) detected in {fname}, but the "
                    f"computed repair does not parse ({probe_err!r}). The check's "
                    f"own escape pattern is wrong -- do NOT hand-apply it. See the "
                    f"S157 note above this check."
                ),
            ))
            continue

        def make_fix(fn=fname, payload=out):
            def apply(files_inner):
                files_inner[fn] = payload
            return apply

        findings.append(Finding(
            tier="YELLOW", category="literal_escape_artifact",
            file=fname,
            location=", ".join(roster[:8]) + (" ..." if len(roster) > 8 else ""),
            message=(
                f"{n} over-escaped quote(s) inside string literals: the source writes "
                f"a doubled backslash before a quote, so the literal's VALUE carries a "
                f"stray backslash. Affects {len(roster)} individual(s): "
                f"{', '.join(roster[:8])}{' ...' if len(roster) > 8 else ''}. "
                f"The file parses and SHACL conforms -- only the rendered text is wrong. "
                f"Authors should not hand-escape literals; escape at emit time "
                f"(SKILL.md, emitter contract)."
            ),
            autofixable=True,
            autofix_fn=make_fix(),
            autofix_description=(
                f"Collapse {n} doubled backslash-quote sequence(s) to a single escaped "
                f"quote in {fname}, preserving the file's line endings."
            ),
        ))
    return findings


# --- deferred_proposals_id (S161, deferred_proposals[101]) -------------------
#
# The citation key every companion file uses for a deferred proposal --
# deferred_proposals[NN] -- was a hand-maintained pseudo-ID assumed to equal the
# array index. The two drifted (a +1 offset entered when [97] was logged at
# S150), producing two near-misses (S152, S160) and one committed mislabel
# (S161). deferred_proposals[101] option (a) added an explicit immutable integer
# 'id' to every entry; this check guards it. It also folds in handoff §4 item 39
# (status-vocabulary validation), which had no check for eight sessions.

_VALID_DP_STATUSES = frozenset({
    "logged", "approved", "implemented", "complete",  # build lifecycle
    "rejected", "resolved", "obsolete",               # terminal no-build
})

_DP_CITATION_FILES = (
    "SKILL.md", "gem_rule_categories.md", "gem_reference.md",
    "worklist_schema.md", "manifest_format.md",
)


def check_deferred_proposals_id(
    files: dict[str, bytes], handoff_text: Optional[str],
) -> list[Finding]:
    """Guard the deferred_proposals 'id' field (S161, deferred_proposals[101]).

    (a) every entry carries an 'id'; (b) ids are unique; (c) every 'status' and
    'parts[].status' is one of the seven valid values (folds in handoff §4 item
    39); (d) every deferred_proposals[NN] cited in a durable companion file (or
    the handoff) resolves to an entry whose id is NN. No-op when the worklist is
    absent or unparseable (a parse error surfaces elsewhere).
    """
    findings: list[Finding] = []
    raw = files.get("policy_worklist.json")
    if raw is None:
        return findings
    try:
        wl = json.loads(raw.decode("utf-8"))
    except Exception:
        return findings
    dp = wl.get("deferred_proposals")
    if not isinstance(dp, list):
        return findings

    seen: dict = {}
    for i, e in enumerate(dp):
        if not isinstance(e, dict):
            continue
        eid = e.get("id")
        if eid is None:
            findings.append(Finding(
                tier="RED", category="deferred_proposals_id",
                file="policy_worklist.json", location="index %d" % i,
                message=("deferred_proposals entry at index %d has no 'id' field. "
                         "Every entry must carry a stable integer id (deferred_proposals[101]) "
                         "so citations key on identity, not array position." % i)))
        elif eid in seen:
            findings.append(Finding(
                tier="RED", category="deferred_proposals_id",
                file="policy_worklist.json", location="id %r" % eid,
                message=("deferred_proposals id %r is used by both index %d and index %d; "
                         "ids must be unique." % (eid, seen[eid], i))))
        else:
            seen[eid] = i
        st = e.get("status")
        if st is not None and st not in _VALID_DP_STATUSES:
            findings.append(Finding(
                tier="RED", category="deferred_proposals_id",
                file="policy_worklist.json", location="index %d" % i,
                message=("deferred_proposals entry at index %d has status %r, not one of the "
                         "seven valid values %s." % (i, st, sorted(_VALID_DP_STATUSES)))))
        for p in (e.get("parts") or []):
            ps = p.get("status") if isinstance(p, dict) else None
            if ps is not None and ps not in _VALID_DP_STATUSES:
                findings.append(Finding(
                    tier="RED", category="deferred_proposals_id",
                    file="policy_worklist.json", location="index %d" % i,
                    message=("deferred_proposals entry at index %d has a parts[].status %r not "
                             "among the seven valid values." % (i, ps))))

    valid_ids = set(seen.keys())
    scan: list[tuple] = []
    for name in _DP_CITATION_FILES:
        b = files.get(name)
        if b:
            scan.append((name, b.decode("utf-8", errors="replace")))
    if handoff_text:
        scan.append(("handoff", handoff_text))
    for name, text in scan:
        for mm in sorted(set(re.findall(r"deferred_proposals\[(\d+)\]", text))):
            nn = int(mm)
            if nn not in valid_ids:
                findings.append(Finding(
                    tier="RED", category="deferred_proposals_id",
                    file=name, location="deferred_proposals[%d]" % nn,
                    message=("%s cites deferred_proposals[%d], which resolves to no entry id in "
                             "policy_worklist.json (deferred_proposals[101] guard)." % (name, nn))))
    return findings


def check_revises_references_redundancy(
    files: dict[str, bytes], graph: rdflib.Graph,
) -> list[Finding]:
    """A subject must not assert BOTH gem:revisesPolicy and gem:referencesPolicy
    to the same object. gem:revisesPolicy rdfs:subPropertyOf gem:referencesPolicy,
    so the reference direction is entailed and asserting it explicitly is always
    redundant -> YELLOW, autofixable by deleting the redundant gem:referencesPolicy
    line (the stronger gem:revisesPolicy is kept). The check reads only ASSERTED
    triples (the audit's parse_graph does no RDFS entailment), so it flags genuine
    dual assertions, not the entailed reference direction. (Added S169,
    deferred_proposals[99] mutual-exclusivity guard; precedent tn48NCD->ncd210.2.)
    """
    findings: list[Finding] = []
    if graph is None:
        return findings

    revises = GEM.revisesPolicy
    references = GEM.referencesPolicy
    redundant = sorted(
        (s, o)
        for s, o in graph.subject_objects(revises)
        if (s, references, o) in graph
    )
    if not redundant:
        return findings

    def _ln(u) -> str:
        return str(u).rsplit("/", 1)[-1]

    ttl = files.get("GEM_policy_instances.ttl")

    def _make_fix(pairs):
        def _fix(f: dict) -> None:
            raw = f.get("GEM_policy_instances.ttl")
            if raw is None:
                return
            text = raw.decode("utf-8")
            for s, o in pairs:
                s_ln, o_ln = _ln(s), _ln(o)
                # locate the subject block and drop its redundant references line
                m = re.search(
                    r"(?ms)^(gemi:" + re.escape(s_ln) + r" a .*?\.)\r\n", text)
                if not m:
                    continue
                block = m.group(1)
                newblock = re.sub(
                    r"    gem:referencesPolicy gemi:" + re.escape(o_ln) + r" ;\r\n",
                    "", block, count=1)
                if newblock != block:
                    text = text[:m.start(1)] + newblock + text[m.end(1):]
            f["GEM_policy_instances.ttl"] = text.encode("utf-8")
        return _fix

    for s, o in redundant:
        findings.append(Finding(
            tier="YELLOW", category="revises_references_redundancy",
            file="GEM_policy_instances.ttl",
            location="%s -> %s" % (_ln(s), _ln(o)),
            message=(
                "%s asserts BOTH gem:revisesPolicy and gem:referencesPolicy to %s. "
                "gem:revisesPolicy entails gem:referencesPolicy (subPropertyOf), so "
                "the explicit gem:referencesPolicy is redundant."
                % (_ln(s), _ln(o))),
            autofixable=(ttl is not None),
            autofix_fn=_make_fix(redundant) if ttl is not None else None,
            autofix_description=(
                "Delete the redundant gem:referencesPolicy line(s) from "
                "GEM_policy_instances.ttl, keeping gem:revisesPolicy."),
        ))
    return findings


# --- description_workflow_leak (S173) ----------------------------------------
#
# The gem:description / gem:workflowDescription contract (gem_reference.md 1a):
# gem:description is the consumer-facing gloss; gem:workflowDescription is the
# catch-all for verbatim source text, provenance, and minting/workflow notes.
# A description must never carry that workflow material. The S172/S173 leak-
# cleanup tranches moved ~220 leaked tails out of gem:description into
# gem:workflowDescription; this guard keeps them out.
#
# Group (b) -- OWL schema terms (Class/ObjectProperty/DatatypeProperty/
# AnnotationProperty), SHACL NodeShapes, and the five controlled-vocab families
# (RuleType, RestrictionType, RuleDomain, NextPlannedStep, SourceAvailability) --
# carry "(Session ...)" provenance and predicate-name mentions in their glosses
# by convention, and are excluded from the leak-marker sub-check.

_DWL_LEAK_MARKERS = [
    "Governing text:", "Verbatim governing text", "Stub for policy reference discovered",
    "as named in", "dc:source", "Minted 20", "(Session ", "planPromote", "planDone",
]
_DWL_SHACL_NODESHAPE = URIRef("http://www.w3.org/ns/shacl#NodeShape")
_DWL_VOCAB_FAMILIES = ("RuleType", "RestrictionType", "RuleDomain", "NextPlannedStep", "SourceAvailability")


def _dwl_group_b_uris(graph: rdflib.Graph) -> set:
    """Group-(b) subjects excluded from the leak-marker sub-check."""
    excl = set()
    for cls in (rdflib.OWL.Class, rdflib.OWL.ObjectProperty, rdflib.OWL.DatatypeProperty,
                rdflib.OWL.AnnotationProperty, _DWL_SHACL_NODESHAPE):
        excl.update(graph.subjects(rdflib.RDF.type, cls))
    for fam in _DWL_VOCAB_FAMILIES:
        excl.update(graph.subjects(rdflib.RDF.type, GEM[fam]))
    return excl


def check_description_workflow_leak(
    files: dict[str, bytes], graph: rdflib.Graph,
) -> list[Finding]:
    """S173: enforce the gem:description / gem:workflowDescription contract.

    Three sub-checks:
      (1) a subject carrying gem:workflowDescription but no gem:description -> RED
          (structural: the consumer-facing field is missing);
      (2) gem:description byte-identical to gem:workflowDescription -> RED
          (the split never happened -- workflow text was copied, not moved);
      (3) a workflow/verbatim leak marker in gem:description -> YELLOW, group-(b)
          excluded (leaked material left in the consumer gloss; move it into
          gem:workflowDescription).

    Sub-check (3) scans every in-scope description regardless of whether the
    subject also has a workflowDescription: a leaked description with no wf at
    all is still a leak (this is how S173 caught gemi:settingClinic).
    """
    findings: list[Finding] = []
    if graph is None:
        return findings
    excl = _dwl_group_b_uris(graph)
    subjects = (set(graph.subjects(GEM.workflowDescription, None))
                | set(graph.subjects(GEM.description, None)))
    for s in sorted(subjects, key=str):
        local = str(s).rsplit("/", 1)[-1]
        f_file = "GEM_policy_instances.ttl" if str(s).startswith(str(GEMI)) else None
        descs = [str(d) for d in graph.objects(s, GEM.description)]
        wfs = [str(w) for w in graph.objects(s, GEM.workflowDescription)]
        # (1) structural: wf present, desc absent
        if wfs and not descs:
            findings.append(Finding(
                tier="RED", category="description_workflow_leak", file=f_file, location=local,
                message=("%s carries gem:workflowDescription but no gem:description; "
                         "the consumer-facing gloss is missing." % local)))
            continue
        # (2) desc byte-identical to wf
        if any(d in wfs for d in descs):
            findings.append(Finding(
                tier="RED", category="description_workflow_leak", file=f_file, location=local,
                message=("%s gem:description is byte-identical to its "
                         "gem:workflowDescription; the description/workflow split "
                         "never happened." % local)))
        # (3) leak marker in description (group-(b) excluded)
        if s in excl:
            continue
        for d in descs:
            hits = [m for m in _DWL_LEAK_MARKERS if m in d]
            if hits:
                findings.append(Finding(
                    tier="YELLOW", category="description_workflow_leak", file=f_file, location=local,
                    message=("%s gem:description contains workflow/verbatim leak marker(s) %s; "
                             "move the leaked clause into gem:workflowDescription." % (local, hits))))
                break
    return findings


# --- workflow_header_counts (S182) -------------------------------------------
#
# The consolidated WORKFLOW STATE block in GEM_policy_instances.ttl is labelled
# by four hand-maintained comment headers of the form
#     # --- <planState> / isInEffect=<Bool> (N individuals) ---
# whose N had drifted from the graph (S181 SS4: file 84/6/9/218 vs graph-wide
# 88/6/11/391). These labels were previously unaudited. This check reconciles
# each header's N against the GRAPH-WIDE count of individuals carrying that exact
# (gem:nextPlannedStep, gem:isInEffect) pair -- the source of truth -- regardless
# of where the assertion physically sits (consolidated block, inline stub, or a
# misfiled intruder). Physical placement and re-homing are deliberately OUT of
# scope (that was S181 resolution (b), not chosen); this check trues only the
# numbers. Tier YELLOW, autofixable: the fix rewrites the integer in place, CRLF
# preserved, touching nothing else on the line. A graph combo that no header
# covers is surfaced YELLOW but NOT autofixed -- inserting a header and choosing
# its placement is a structural edit, not a number rewrite.

_WORKFLOW_HEADER_RE = re.compile(
    r"(# --- (planDone|planNone|planPromote|planRevisit) / isInEffect=(True|False) \()"
    r"(\d+)"
    r"( individual)"
)


def _workflow_state_combo_counts(instances: rdflib.Graph) -> dict:
    """Graph-wide count of individuals per (nextPlannedStep-localname, isInEffect-bool).

    Counts only cleanly-typed individuals (exactly one nextPlannedStep and one
    isInEffect); a subject with a conflicting or missing pair is a different
    defect owned by check_workflow_state_coverage, not this count reconciler.
    """
    counts: dict = {}
    for s in set(instances.subjects(GEM.nextPlannedStep, None)):
        steps = list(instances.objects(s, GEM.nextPlannedStep))
        effs = list(instances.objects(s, GEM.isInEffect))
        if len(steps) != 1 or len(effs) != 1:
            continue
        state = str(steps[0]).rsplit("/", 1)[-1]
        eff = bool(effs[0].toPython())
        counts[(state, eff)] = counts.get((state, eff), 0) + 1
    return counts


def check_workflow_header_counts(
    files: dict[str, bytes], graph: rdflib.Graph,
) -> list[Finding]:
    findings: list[Finding] = []
    raw = files.get("GEM_policy_instances.ttl")
    if not raw:
        return findings
    instances = parse_instances_only(files)
    if instances is None:
        return findings
    text = raw.decode("utf-8")

    counts = _workflow_state_combo_counts(instances)

    drifts = []      # (state, bool, claimed, actual)
    headed = set()   # (state, bool) combos a header covers
    for m in _WORKFLOW_HEADER_RE.finditer(text):
        state = m.group(2)
        eff = (m.group(3) == "True")
        claimed = int(m.group(4))
        actual = counts.get((state, eff), 0)
        headed.add((state, eff))
        if claimed != actual:
            drifts.append((state, eff, claimed, actual))

    if drifts:
        def fix_headers(files_inner):
            original = files_inner["GEM_policy_instances.ttl"].decode("utf-8")

            def repl(mm):
                st = mm.group(2)
                bl = (mm.group(3) == "True")
                act = counts.get((st, bl), 0)
                return mm.group(1) + str(act) + mm.group(5)

            updated = _WORKFLOW_HEADER_RE.sub(repl, original)
            files_inner["GEM_policy_instances.ttl"] = updated.encode("utf-8")

        detail = "; ".join(
            "%s/isInEffect=%s %d->%d" % (st, bl, cl, ac) for st, bl, cl, ac in drifts
        )
        findings.append(Finding(
            tier="YELLOW", category="workflow_header_counts",
            file="GEM_policy_instances.ttl",
            location="WORKFLOW STATE group-count headers",
            message=(
                "Consolidated WORKFLOW STATE header count(s) disagree with the "
                "graph-wide nextPlannedStep x isInEffect count (source of truth): "
                + detail + ". Header labels are hand-maintained and drift as "
                "individuals are added or re-homed; the graph is authoritative."
            ),
            autofixable=True,
            autofix_fn=fix_headers,
            autofix_description=(
                "Rewrite WORKFLOW STATE header count(s) to graph-wide actuals: "
                + detail + "."
            ),
        ))

    # Un-headed combo: a (state,bool) present in the graph that no header covers.
    for (state, eff), n in sorted(counts.items()):
        if (state, eff) not in headed:
            findings.append(Finding(
                tier="YELLOW", category="workflow_header_counts",
                file="GEM_policy_instances.ttl",
                location="%s / isInEffect=%s (no header)" % (state, eff),
                message=(
                    "Graph holds %d individual(s) with nextPlannedStep=%s, "
                    "isInEffect=%s but the consolidated WORKFLOW STATE block has "
                    "no matching header. Not autofixed: inserting a header and "
                    "choosing its placement is a structural edit."
                    % (n, state, str(eff).lower())
                ),
            ))
    return findings



ALL_CHECKS = [
    ("hash_verify",        lambda files, graph, expected, handoff_text: check_hashes(files, expected)),
    ("formatting",         lambda files, graph, expected, handoff_text: check_formatting_integrity(files)),
    ("empirical_counts",   lambda files, graph, expected, handoff_text: check_empirical_counts(files, graph, handoff_text)),
    ("processed_list",     lambda files, graph, expected, handoff_text: check_processed_list(files, graph)),
    ("uri_scheme",         lambda files, graph, expected, handoff_text: check_uri_scheme_consistency(files, graph)),
    ("transmittal_manual_token", lambda files, graph, expected, handoff_text: check_transmittal_manual_token(files, graph)),
    ("nca_uri_derivation", lambda files, graph, expected, handoff_text: check_nca_uri_derivation(files, graph)),
    ("doc_uri_examples",   lambda files, graph, expected, handoff_text: check_doc_uri_examples(files, graph)),
    ("proposal_b",         lambda files, graph, expected, handoff_text: check_proposal_b(files, graph)),
    ("workflow_state",     lambda files, graph, expected, handoff_text: check_workflow_state_coverage(files, graph)),
    ("workflow_header_counts", lambda files, graph, expected, handoff_text: check_workflow_header_counts(files, graph)),
    ("uri_collision",      lambda files, graph, expected, handoff_text: check_uri_collisions(files, graph)),
    ("deleted_twin_collision", lambda files, graph, expected, handoff_text: check_deleted_twin_collision(files, graph)),
    ("predicate_order",    lambda files, graph, expected, handoff_text: check_predicate_ordering(files)),
    ("ruledescription_domain", lambda files, graph, expected, handoff_text: check_ruledescription_domain_conformance(files, graph)),
    ("inverse_note_conformance", lambda files, graph, expected, handoff_text: check_inverse_note_conformance(files, graph)),
    ("domain_range_conformance", lambda files, graph, expected, handoff_text: check_domain_range_conformance(files, graph)),
    ("policyrule_completeness",lambda files, graph, expected, handoff_text: check_policyrule_completeness(files, graph)),
    ("policyrule_reciprocity", lambda files, graph, expected, handoff_text: check_policyrule_provenance_reciprocity(files, graph)),
    ("controlled_vocab",       lambda files, graph, expected, handoff_text: check_controlled_vocab_integrity(files, graph)),
    ("handoff_drift",      lambda files, graph, expected, handoff_text: check_handoff_drift(files, graph, handoff_text)),
    ("codegroup_link_drift", lambda files, graph, expected, handoff_text: check_codegroup_link_drift(files, graph)),
    ("codegroup_block_extent", lambda files, graph, expected, handoff_text: check_codegroup_block_extent(files)),
    ("llm_annotation_drift", lambda files, graph, expected, handoff_text: check_llm_annotation_drift(files, graph)),
    ("llm_annotation_count_drift", lambda files, graph, expected, handoff_text: check_llm_annotation_count_drift(files, graph)),
    ("register_section_coverage", lambda files, graph, expected, handoff_text: check_register_section_coverage(files, graph)),
    ("source_availability_unverified", lambda files, graph, expected, handoff_text: check_source_availability_unverified(files, graph)),
    ("ncd_census",         lambda files, graph, expected, handoff_text: check_ncd_census(files, graph)),
    ("literal_escape_artifact", lambda files, graph, expected, handoff_text: check_literal_escape_artifact(files)),
    ("deferred_proposals_id", lambda files, graph, expected, handoff_text: check_deferred_proposals_id(files, handoff_text)),
    ("revises_references_redundancy", lambda files, graph, expected, handoff_text: check_revises_references_redundancy(files, graph)),
    ("description_workflow_leak", lambda files, graph, expected, handoff_text: check_description_workflow_leak(files, graph)),
    ("skill_checklist_sync", lambda files, graph, expected, handoff_text: check_skill_checklist_sync(files, graph)),
    ("policy_effective_date_v1", lambda files, graph, expected, handoff_text: check_policy_effective_date_v1(files, graph)),
    ("selftest_harness",   lambda files, graph, expected, handoff_text: check_selftest_harness_integrity(files, graph)),
]


def audit_files_dict(
    files: dict[str, bytes],
    expected: dict[str, tuple[str, int]],
    handoff_text: Optional[str] = None,
) -> list[Finding]:
    """Run all audit checks against a pre-loaded files dict.

    Used by run_audit (which loads from disk) and by main()'s post-autofix
    re-audit (which uses the in-memory modified state instead of re-reading).

    handoff_text is the full text of the latest handoff document; used by
    check_handoff_drift. None disables that check.
    """
    # Detect the data namespace from the audited files' own @prefix declarations
    # and rebind the module-level GEM/GEMI globals BEFORE any check runs, so every
    # graph query keys off the namespace the files actually use (a namespace
    # version bump requires no code edit). The rebind is a global reassignment;
    # all checks look up GEM/GEMI at call time, so they see the detected values.
    global GEM, GEMI
    GEM, GEMI = detect_gem_namespace(files)

    # Try to build the graph (best-effort — parse errors will surface in
    # the hash_verify finding, but we still want to run as many checks as possible).
    try:
        graph = parse_graph(files) if all(files.get(n) for n in TTL_FILES) else None
    except Exception as e:
        graph = None
        sys.stderr.write(f"WARNING: graph parse failed: {e}\n")

    findings = []
    for name, fn in ALL_CHECKS:
        try:
            findings.extend(fn(files, graph, expected, handoff_text))
        except Exception as e:
            findings.append(Finding(
                tier="RED", category=name,
                message=f"Audit check raised exception: {e!r}",
            ))
    return findings


def run_audit(files_dir: Path, handoff_path: Optional[Path]) -> tuple[list[Finding], dict[str, bytes], dict[str, tuple[str, int]], Optional[str], list[Finding]]:
    """Load canonical files from disk and run the audit.

    Returns (findings, files, expected_hash_table, handoff_text,
    resolution_findings). The middle three are returned so callers (e.g. autofix
    re-audit) can avoid reloading.

    resolution_findings is checklist item 34 (S260): the handoff-location
    ambiguity guard. It is deliberately NOT an ALL_CHECKS member — every member
    has signature (files, graph, expected, handoff_text) and never sees a
    directory, so it is filesystem-scoped and cannot be registered without
    changing all 34 registrations. It is returned SEPARATELY rather than merged
    into `findings` because main()'s post-autofix pass calls audit_files_dict
    directly, which never sees a directory; a merged finding would silently
    vanish from the post-autofix report. That is the inert-default class S144
    codified against, so main() prepends these to BOTH findings and findings2.
    """
    files = load_canonical_files(files_dir)

    sub_dir = files_dir / _HANDOFF_SUBDIR
    resolution_findings = _handoff_resolution_findings(
        [p.name for p in sub_dir.glob(_HANDOFF_GLOB)] if sub_dir.is_dir() else [],
        [p.name for p in files_dir.glob(_HANDOFF_GLOB)],
    )

    if handoff_path is None:
        handoff_path = find_latest_handoff(files_dir)
    if handoff_path is None:
        expected = {}
        handoff_text = None
    else:
        expected = parse_handoff_table(handoff_path)
        try:
            handoff_text = handoff_path.read_text(encoding="utf-8")
        except OSError:
            handoff_text = None

    findings = audit_files_dict(files, expected, handoff_text)
    return findings, files, expected, handoff_text, resolution_findings


def apply_autofixes(findings: list[Finding], files: dict[str, bytes]) -> tuple[list[str], set[str]]:
    """Apply all autofixable findings. Mutates `files` in place.

    Returns (descriptions, modified_names) — the list of human-readable
    descriptions of fixes applied, and the set of canonical filenames whose
    bytes actually changed.
    """
    snapshot = {k: v for k, v in files.items() if v is not None}
    applied = []
    for f in findings:
        if f.autofixable and f.autofix_fn:
            f.autofix_fn(files)
            applied.append(f.autofix_description or f"Autofix: {f.category} in {f.file}")
    modified = {name for name, original in snapshot.items()
                if files.get(name) is not None and files[name] != original}
    return applied, modified


def emit_pretty(findings: list[Finding]) -> None:
    tier_order = ["RED", "YELLOW", "GREEN"]
    by_tier = defaultdict(list)
    for f in findings:
        by_tier[f.tier].append(f)

    red_n = len(by_tier["RED"])
    yellow_n = len(by_tier["YELLOW"])
    info_findings = by_tier.get("INFO", [])

    # Header: red/yellow count summary. INFO does not affect tier counts.
    if red_n == 0 and yellow_n == 0:
        print("=" * 72)
        print("GEM audit — all checks GREEN. No drift detected.")
        print("=" * 72)
    else:
        print("=" * 72)
        print(f"GEM audit — {red_n} RED, {yellow_n} YELLOW")
        print("=" * 72)
        for tier in tier_order:
            if not by_tier[tier]:
                continue
            for f in by_tier[tier]:
                prefix = {"RED": "[RED]   ", "YELLOW": "[YELLOW]", "GREEN": "[GREEN] "}[tier]
                loc = f" — {f.file}" if f.file else ""
                if f.location:
                    loc += f" :: {f.location}"
                print(f"\n{prefix} [{f.category}]{loc}")
                msg = f.message
                for line in _wrap(msg, 80, indent="    "):
                    print(line)
                if f.autofixable:
                    print(f"    AUTOFIX-AVAILABLE: {f.autofix_description}")
        print()

    # Other INFO findings (work queues, not drift): shown, never tier-counted.
    # ncd_census and handoff_annotations render as their own verbatim sections
    # below (their messages are multi-line and must not be reflowed by _wrap).
    _own_section = {"handoff_annotations", "ncd_census"}
    for f in info_findings:
        if f.category in _own_section:
            continue
        loc = f" — {f.file}" if f.file else ""
        print(f"\n[INFO]   [{f.category}]{loc}")
        for line in _wrap(f.message, 80, indent="    "):
            print(line)
    if any(f.category not in _own_section for f in info_findings):
        print()

    # NCD census: fixed-order status readout, printed verbatim if present.
    for f in [f for f in info_findings if f.category == "ncd_census"]:
        print()
        print("=" * 72)
        print("[NCD CENSUS] — gem:NCDpolicy counts by status")
        print("(informational; not part of tier counts)")
        print("=" * 72)
        for line in f.message.splitlines():
            print(line)
        print()

    # Handoff annotations: separate informational section, always shown if present.
    handoff_anns = [f for f in info_findings if f.category == "handoff_annotations"]
    for f in handoff_anns:
        print()
        print("=" * 72)
        print("[HANDOFF ANNOTATIONS] — current graph state for §4 mentions")
        print("(informational; not part of tier counts)")
        print("=" * 72)
        for line in f.message.splitlines():
            print(line)
        print()


def _wrap(text: str, width: int, indent: str = "") -> list[str]:
    import textwrap
    return textwrap.wrap(text, width=width - len(indent),
                         initial_indent=indent, subsequent_indent=indent) or [indent]


# ============================================================================
# Self-test harness for audit checks (--self-test mode)
# ============================================================================
#
# Embedded regression suite for the audit's check functions. Each variant
# applies a known input to a single check (or, for Phase 3 baselines, all four
# Phase 3 checks) and asserts the expected findings.
#
# Two batteries:
#   - Variants 1-11 (S72 Cycle 0): Phase 3 check coverage, sharing a single
#     synthetic NCD-210.10-style baseline graph. Variant 1 invokes all four
#     Phase 3 checks via the "policyrule_all" sentinel; Variants 2-11 each invoke
#     the single Phase 3 check their mutation targets.
#   - Variants 12-33 (S73 §4.11 backfill): pre-Phase-3 check coverage, one
#     mini-baseline per check plus one or three negative variants per check.
#
# Registry shape (uniform 4-tuple):
#   (label, check_category, builder, expected_findings)
#     label              str  - human-readable variant name
#     check_category     str  - matches a key in ALL_CHECKS, OR the sentinel
#                               "policyrule_all" meaning "run all 4 Phase 3 checks"
#     builder            callable - returns a context dict with keys:
#                          "files"           dict[str, bytes]  (required)
#                          "expected_hashes" dict[str, tuple]  (optional, default {})
#                          "handoff_text"    str | None        (optional, default None)
#     expected_findings  list[tuple(tier, category, location_substring)]
#                        empty list -> "no findings expected" (baseline GREEN)
#                        non-empty  -> each tuple must match at least one
#                                      finding in the run result. Findings
#                                      beyond the expected set are tolerated.
#
# Invoked via:  python3 gem_audit.py --self-test
# Returns 0 if all variants behave as expected, 1 otherwise. Does NOT load
# any files from disk; the harness is fully self-contained.
#
# Convention for future check additions: every new check function ships with
# its self-test entries (positive baseline + >=1 negative variant per check).


_SELF_TEST_ONTOLOGY_STUB = """\
@prefix gem:   <http://www.cms.hhs.gov/ontology/2026/07/GEM/> .
@prefix gemi:  <http://www.cms.hhs.gov/ontology/2026/07/GEM/instances/> .
@prefix rdf:   <http://www.w3.org/1999/02/22-rdf-syntax-ns#> .
@prefix rdfs:  <http://www.w3.org/2000/01/rdf-schema#> .
@prefix owl:   <http://www.w3.org/2002/07/owl#> .
@prefix xsd:   <http://www.w3.org/2001/XMLSchema#> .
@prefix dc:    <http://purl.org/dc/elements/1.1/> .

# Minimal schema stubs - enough for both Phase 3 and pre-Phase-3 checks
gem:CMSpolicy a owl:Class .
gem:NCDpolicy a owl:Class ; rdfs:subClassOf gem:CMSpolicy .
gem:LCDpolicy a owl:Class ; rdfs:subClassOf gem:CMSpolicy .
gem:ArticlePolicy a owl:Class ; rdfs:subClassOf gem:CMSpolicy .
gem:TransmittalPolicy a owl:Class ; rdfs:subClassOf gem:CMSpolicy .
gem:NCAdocument a owl:Class ; rdfs:subClassOf gem:CMSpolicy .
gem:ProgramMemorandumPolicy a owl:Class ; rdfs:subClassOf gem:CMSpolicy .
gem:PolicyRule a owl:Class .
gem:RuleDomain a owl:Class .
gem:RuleType   a owl:Class .

# Controlled-vocab individuals (Phase 3)
gem:ruleDomain_screening    a gem:RuleDomain .
gem:ruleDomain_hibc         a gem:RuleDomain .
gem:ruleDomain_crossCutting a gem:RuleDomain .
gem:ruleType_eligibility    a gem:RuleType .
gem:ruleType_frequency      a gem:RuleType .
gem:ruleType_coverageScope  a gem:RuleType .

# Ontology individual
gem:GEM a owl:Ontology .

# An inverse-bearing property carrying the corpus's most common
# gem:llmInverseNote form (11 of the ontology's 15 notes read this way), so
# check_inverse_note_conformance's inert-precondition path is satisfied in
# every stub-based variant. No owl:inverseOf is declared, so the denial the
# note states is true and no conformance finding can fire from the stub.
gem:refersToClinicalConcept a owl:ObjectProperty ;
    gem:llmInverseNote "No materialized inverse; find policies mentioning a concept by querying the concept in the object position." .

# A domain/range declaration in the gem: namespace, so
# check_domain_range_conformance's inert-precondition path is satisfied in every
# stub-based variant. Mirrors the real ontology's declaration verbatim; no
# fixture asserts this predicate, so it contributes no triples to validate.
gem:BenefitCategory a owl:Class .
gem:refersToBenefitCategory a owl:ObjectProperty ;
    rdfs:domain gem:CMSpolicy ;
    rdfs:range gem:BenefitCategory .
"""


def _build_baseline_instances_graph() -> rdflib.Graph:
    """Build the synthetic baseline post-migration NCD 210.10 instance state.

    A multi-domain policy (gemi:ncd210.10) with 18 PolicyRule individuals.
    Domains and rule types are distributed in round-robin across the three
    controlled-vocab values each. Every rule carries all required predicates
    plus the optional-expected ones (prefLabel, ruleType, ruleDomain).
    """
    g = rdflib.Graph()
    g.bind("gem", GEM)
    g.bind("gemi", GEMI)
    g.bind("dc", DC)

    ncd = GEMI["ncd210.10"]
    g.add((ncd, rdflib.RDF.type, GEM.NCDpolicy))
    g.add((ncd, GEM.memberOfOntology, GEM.GEM))

    domains = [GEM.ruleDomain_screening, GEM.ruleDomain_hibc, GEM.ruleDomain_crossCutting]
    rtypes = [GEM.ruleType_eligibility, GEM.ruleType_frequency, GEM.ruleType_coverageScope]

    for n in range(1, 19):
        rule = GEMI[f"ncd210.10_r{n}"]
        g.add((ncd, GEM.hasPolicyRule, rule))
        g.add((rule, rdflib.RDF.type, GEM.PolicyRule))
        g.add((rule, GEM.prefLabel, rdflib.Literal(f"NCD 210.10 R{n}")))
        g.add((rule, GEM.ruleDescription, rdflib.Literal(f"Synthetic rule description R{n}.")))
        g.add((rule, GEM.ruleDomain, domains[(n - 1) % 3]))
        g.add((rule, GEM.ruleType, rtypes[(n - 1) % 3]))
        g.add((rule, DC.source, ncd))
        g.add((rule, GEM.memberOfOntology, GEM.GEM))
    return g


def _instances_graph_to_files(instances_g: rdflib.Graph) -> dict[str, bytes]:
    """Wrap an instances graph plus the static schema stub into a files dict."""
    out = instances_g.serialize(format="turtle")
    if isinstance(out, str):
        instances_bytes = out.encode("utf-8")
    else:
        instances_bytes = out
    return {
        "GEM_ontology.ttl": _SELF_TEST_ONTOLOGY_STUB.encode("utf-8"),
        "GEM_policy_instances.ttl": instances_bytes,
        # S104 harness repair: TTL_FILES gained GEM_code_group_instances.ttl in
        # S103, but this helper was not updated, so the variant graph-build guard
        # `all(files.get(n) for n in TTL_FILES)` evaluated False and every variant
        # ran with graph=None (silently no-op'ing all graph-dependent checks).
        # Emit a valid (empty) stub so parse_graph builds. Variant code-group
        # individuals live in the instances graph above; this stub only satisfies
        # the presence guard.
        "GEM_code_group_instances.ttl": b"# GEM self-test code-group stub (intentionally empty)\n",
    }


def _run_policyrule_checks_only(files: dict[str, bytes]) -> list[Finding]:
    """Run only the four Phase 3 check functions against a synthetic files dict.

    Used by the self-test harness's "policyrule_all" sentinel to assert that the
    baseline passes ALL four Phase 3 checks without the noise of unrelated
    checks (hash-verify, formatting, handoff-drift, etc.) that don't apply
    to synthetic graphs.
    """
    graph = parse_graph(files)
    findings: list[Finding] = []
    findings.extend(check_ruledescription_domain_conformance(files, graph))
    findings.extend(check_inverse_note_conformance(files, graph))
    findings.extend(check_domain_range_conformance(files, graph))
    findings.extend(check_policyrule_completeness(files, graph))
    findings.extend(check_policyrule_provenance_reciprocity(files, graph))
    findings.extend(check_controlled_vocab_integrity(files, graph))
    return findings


# ----- Phase 3 variant constructors (V1-V11) -------------------------------
#
# Each returns a context dict containing at minimum the "files" key.
# Variant 1 is the GREEN baseline; variants 2-11 each apply one mutation.


def _variant_1_baseline() -> dict:
    """GREEN baseline: valid post-migration NCD 210.10 state (all 4 Phase 3 checks)."""
    return {"files": _instances_graph_to_files(_build_baseline_instances_graph())}


def _variant_2_ruledescription_domain() -> dict:
    """A non-PolicyRule subject carries gem:ruleDescription with NO hasPolicyRule.

    Exercises the ruledescription_domain check and demonstrates its strengthening
    over the retired three-state BOTH check: the subject has gem:ruleDescription but
    no gem:hasPolicyRule and is not a gem:PolicyRule, so the old CMSpolicy-only
    BOTH-state check would have missed it; the domain check flags it."""
    g = _build_baseline_instances_graph()
    stray = GEMI["a99999"]
    g.add((stray, rdflib.RDF.type, GEM.ArticlePolicy))
    g.add((stray, GEM.memberOfOntology, GEM.GEM))
    g.add((stray, GEM.ruleDescription, rdflib.Literal("Stray legacy rule string on a non-PolicyRule subject.")))
    return {"files": _instances_graph_to_files(g)}


def _variant_3_orphan_policyrule() -> dict:
    """Policy is missing the reciprocal hasPolicyRule for one of its rules."""
    g = _build_baseline_instances_graph()
    ncd = GEMI["ncd210.10"]
    r1 = GEMI["ncd210.10_r1"]
    g.remove((ncd, GEM.hasPolicyRule, r1))
    return {"files": _instances_graph_to_files(g)}


def _variant_4_missing_dc_source() -> dict:
    """One PolicyRule is missing its dc:source triple."""
    g = _build_baseline_instances_graph()
    g.remove((GEMI["ncd210.10_r1"], DC.source, None))
    return {"files": _instances_graph_to_files(g)}


def _variant_5_zero_rule_description() -> dict:
    """One PolicyRule has zero gem:ruleDescription triples."""
    g = _build_baseline_instances_graph()
    g.remove((GEMI["ncd210.10_r1"], GEM.ruleDescription, None))
    return {"files": _instances_graph_to_files(g)}


def _variant_6_duplicate_rule_description() -> dict:
    """One PolicyRule has two gem:ruleDescription triples."""
    g = _build_baseline_instances_graph()
    g.add((GEMI["ncd210.10_r1"], GEM.ruleDescription, rdflib.Literal("Spurious second description.")))
    return {"files": _instances_graph_to_files(g)}


def _variant_7_value_type_misuse() -> dict:
    """One PolicyRule's gem:ruleDomain value is not a gem:RuleDomain individual."""
    g = _build_baseline_instances_graph()
    r1 = GEMI["ncd210.10_r1"]
    g.remove((r1, GEM.ruleDomain, None))
    # gem:ruleDomain_typo is NOT declared as rdf:type gem:RuleDomain in the stub
    g.add((r1, GEM.ruleDomain, GEM.ruleDomain_typo))
    return {"files": _instances_graph_to_files(g)}


def _variant_8_subject_domain_misuse() -> dict:
    """The policy individual itself carries gem:ruleDomain - invalid by domain."""
    g = _build_baseline_instances_graph()
    g.add((GEMI["ncd210.10"], GEM.ruleDomain, GEM.ruleDomain_screening))
    return {"files": _instances_graph_to_files(g)}


def _variant_9_missing_pref_label() -> dict:
    """One PolicyRule is missing gem:prefLabel (YELLOW)."""
    g = _build_baseline_instances_graph()
    g.remove((GEMI["ncd210.10_r1"], GEM.prefLabel, None))
    return {"files": _instances_graph_to_files(g)}


def _variant_10_missing_rule_type() -> dict:
    """One PolicyRule is missing gem:ruleType (YELLOW)."""
    g = _build_baseline_instances_graph()
    g.remove((GEMI["ncd210.10_r1"], GEM.ruleType, None))
    return {"files": _instances_graph_to_files(g)}


def _variant_11_smart_domain_gap() -> dict:
    """One PolicyRule on a multi-domain policy is missing gem:ruleDomain (YELLOW)."""
    g = _build_baseline_instances_graph()
    # Remove ruleDomain only from r1; r2..r18 still carry it -> partial coverage
    g.remove((GEMI["ncd210.10_r1"], GEM.ruleDomain, None))
    return {"files": _instances_graph_to_files(g)}


# ----- Pre-Phase-3 variant constructors (V12-V33) ---------------------------
#
# Each check gets its own minimal synthetic input (per S73 §4.11 decision (β)
# minimalist per-check). Heterogeneous input requirements naturally argue for
# heterogeneous test infrastructure; per-check mini-baselines isolate the test
# surface and double as executable documentation of each check's expected
# input shape.


# --- hash_verify (V12-V13) ----------------------------------------------------

def _hash_verify_clean_files() -> dict[str, bytes]:
    """Build a files dict where every CANONICAL_FILES entry has the same bytes."""
    data = b"# synthetic canonical file content\r\n"
    return {name: data for name in CANONICAL_FILES}


def _variant_12_hash_verify_baseline() -> dict:
    """hash_verify GREEN: every file's actual hash matches the expected table."""
    files = _hash_verify_clean_files()
    md5 = hashlib.md5(b"# synthetic canonical file content\r\n").hexdigest()
    sz = len(b"# synthetic canonical file content\r\n")
    expected = {name: (md5, sz) for name in CANONICAL_FILES}
    return {"files": files, "expected_hashes": expected}


def _variant_13_hash_verify_mismatch() -> dict:
    """hash_verify mismatch -> RED: one file's expected hash is wrong."""
    files = _hash_verify_clean_files()
    md5 = hashlib.md5(b"# synthetic canonical file content\r\n").hexdigest()
    sz = len(b"# synthetic canonical file content\r\n")
    expected = {name: (md5, sz) for name in CANONICAL_FILES}
    # Corrupt the expected hash for one specific file
    expected["GEM_policy_instances.ttl"] = ("00000000000000000000000000000000", 999)
    return {"files": files, "expected_hashes": expected}


# --- formatting (V14-V17) -----------------------------------------------------

def _formatting_clean_files() -> dict[str, bytes]:
    """Build a files dict with one clean TTL (CRLF, no tabs, ends `.\\r\\n`)
    and one clean markdown (LF-only)."""
    ttl = (
        b"@prefix ex: <http://example.com/> .\r\n"
        b"ex:foo a ex:Bar .\r\n"
    )
    md = b"# Synthetic doc\n\nSome content.\n"
    return {
        "GEM_policy_instances.ttl": ttl,
        "GEM_ontology.ttl": ttl,
        "SKILL.md": md,
    }


def _variant_14_formatting_baseline() -> dict:
    """formatting GREEN: clean CRLF TTL + clean LF markdown."""
    return {"files": _formatting_clean_files()}


def _variant_15_formatting_lone_lf() -> dict:
    """formatting lone-LF -> RED: TTL contains a bare \\n among the CRLFs."""
    files = _formatting_clean_files()
    # Insert a lone LF into the TTL (no preceding CR)
    files["GEM_policy_instances.ttl"] = (
        b"@prefix ex: <http://example.com/> .\r\n"
        b"ex:foo a ex:Bar ;\n"   # <-- lone LF
        b"    ex:p ex:o .\r\n"
    )
    return {"files": files}


def _variant_16_formatting_tab() -> dict:
    """formatting tab character -> RED: TTL contains a tab byte."""
    files = _formatting_clean_files()
    files["GEM_policy_instances.ttl"] = (
        b"@prefix ex: <http://example.com/> .\r\n"
        b"ex:foo a ex:Bar ;\r\n"
        b"\tex:p ex:o .\r\n"   # <-- leading tab
    )
    return {"files": files}


def _variant_17_formatting_no_terminator() -> dict:
    """formatting missing terminating `.\\r\\n` -> RED."""
    files = _formatting_clean_files()
    files["GEM_policy_instances.ttl"] = (
        b"@prefix ex: <http://example.com/> .\r\n"
        b"ex:foo a ex:Bar ."  # <-- no trailing \r\n
    )
    return {"files": files}


# --- empirical_counts (V18-V19) -----------------------------------------------

def _empirical_counts_skill_text(rev: int, revby: int, ref: int, session: int) -> bytes:
    """Build a SKILL.md with the empirical-counts sentence matching the params."""
    text = (
        "# Synthetic SKILL.md\n"
        "\n"
        "Some text...\n"
        "\n"
        f"Empirical counts: as of S{session}, {rev} `gem:revisesPolicy` triples, "
        f"{revby} `gem:revisedByPolicy` triples, and {ref} `gem:referencesPolicy` triples.\n"
    )
    return text.encode("utf-8")


def _empirical_counts_graph(rev: int, revby: int, ref: int) -> rdflib.Graph:
    """Build an instances graph with exactly `rev` revisesPolicy, `revby`
    revisedByPolicy, and `ref` referencesPolicy triples."""
    g = rdflib.Graph()
    for i in range(rev):
        g.add((GEMI[f"src_rev_{i}"], GEM.revisesPolicy, GEMI[f"tgt_rev_{i}"]))
    for i in range(revby):
        g.add((GEMI[f"src_revby_{i}"], GEM.revisedByPolicy, GEMI[f"tgt_revby_{i}"]))
    for i in range(ref):
        g.add((GEMI[f"src_ref_{i}"], GEM.referencesPolicy, GEMI[f"tgt_ref_{i}"]))
    return g


def _empirical_counts_handoff(session: int, legacy: bool = False) -> str:
    """Synthetic handoff whose title declares `session`.

    Default is the form the corpus actually uses. The pre-S144 fixture hard-coded
    the `legacy` form instead — a form no real handoff has — which is exactly why
    V18/V19 stayed green across every session in which check_empirical_counts'
    session detection was dead. Fixtures model the corpus; `legacy=True` is kept
    only so V42 can pin back-compatibility explicitly.
    """
    if legacy:
        title = f"# GEM Policy-Extraction Session {session} Handoff"
    else:
        title = f"# GEM Policy-Extraction Handoff — Session {session} (2026-07-14)"
    return f"{title}\n\nSynthetic body.\n"


def _variant_18_empirical_counts_baseline() -> dict:
    """empirical_counts GREEN: SKILL.md counts + handoff session = graph state."""
    session = 99
    rev, revby, ref = 2, 1, 3
    files = _instances_graph_to_files(_empirical_counts_graph(rev, revby, ref))
    files["SKILL.md"] = _empirical_counts_skill_text(rev, revby, ref, session)
    return {"files": files, "handoff_text": _empirical_counts_handoff(session)}


def _variant_19_empirical_counts_mismatch() -> dict:
    """empirical_counts mismatch -> YELLOW: SKILL.md claims 5/1/3, graph has 2/1/3."""
    session = 99
    actual_rev, actual_revby, actual_ref = 2, 1, 3
    files = _instances_graph_to_files(_empirical_counts_graph(actual_rev, actual_revby, actual_ref))
    # SKILL.md asserts a different revisesPolicy count
    files["SKILL.md"] = _empirical_counts_skill_text(5, actual_revby, actual_ref, session)
    return {"files": files, "handoff_text": _empirical_counts_handoff(session)}


# --- empirical_counts session detection (V41-V43; S144) ------------------------
#
# V18/V19 hold both sessions equal, so they never exercise the marker-advance
# branch at all: they pass whether session detection works or not. V41-V43 pin
# the branch itself. V41 and V43 fail against the pre-S144 code and pass after
# the fix — they are regression tests for the defect, not just coverage.

def _empirical_counts_stale_marker(legacy: bool) -> dict:
    """Counts correct, marker one session behind the handoff -> YELLOW advance.

    This is the real S143 situation: nothing about the counts is wrong, so the
    ONLY thing that can raise a finding is successful session detection.
    """
    marker_session, handoff_session = 99, 100
    rev, revby, ref = 2, 1, 3
    files = _instances_graph_to_files(_empirical_counts_graph(rev, revby, ref))
    files["SKILL.md"] = _empirical_counts_skill_text(rev, revby, ref, marker_session)
    return {"files": files,
            "handoff_text": _empirical_counts_handoff(handoff_session, legacy=legacy)}


def _variant_41_empirical_counts_marker_advance() -> dict:
    """Corpus title form + stale marker -> YELLOW (marker must advance)."""
    return _empirical_counts_stale_marker(legacy=False)


def _variant_42_empirical_counts_marker_advance_legacy() -> dict:
    """Legacy title form + stale marker -> YELLOW (back-compat pinned)."""
    return _empirical_counts_stale_marker(legacy=True)


def _variant_43_empirical_counts_session_undetectable() -> dict:
    """Handoff present, title declares no session -> YELLOW detection failure.

    Counts and marker are self-consistent, so pre-S144 code returns GREEN here:
    the silent fallback makes an unreadable handoff look identical to a correct
    one. That silence is the finding.
    """
    session = 99
    rev, revby, ref = 2, 1, 3
    files = _instances_graph_to_files(_empirical_counts_graph(rev, revby, ref))
    files["SKILL.md"] = _empirical_counts_skill_text(rev, revby, ref, session)
    return {"files": files,
            "handoff_text": "# GEM Policy-Extraction Handoff (untitled run)\n\nSynthetic body.\n"}


# --- processed_list (V20-V21) -------------------------------------------------

def _processed_list_graph(n_done: int) -> rdflib.Graph:
    """Build a graph with `n_done` individuals carrying nextPlannedStep planDone."""
    g = rdflib.Graph()
    for i in range(n_done):
        u = GEMI[f"pdone_{i}"]
        g.add((u, rdflib.RDF.type, GEM.NCDpolicy))
        g.add((u, GEM.nextPlannedStep, GEM.planDone))
    return g


def _processed_list_ttl_with_header(header_idents: list) -> bytes:
    """Wrap a serialized graph with a `# Policies processed:` header line."""
    header = f"# Policies processed: {', '.join(header_idents)}\r\n\r\n"
    return header.encode("utf-8")


def _processed_list_worklist(policies_processed: int) -> bytes:
    return json.dumps({
        "metadata": {"policies_processed": policies_processed},
        "related_policies": [],
        "uncoded_clinical_concepts": [],
        "deferred_proposals": [],
    }).encode("utf-8")


def _variant_20_processed_list_baseline() -> dict:
    """processed_list GREEN: header list, worklist counter, and graph all agree at 3."""
    g = _processed_list_graph(3)
    files = _instances_graph_to_files(g)
    # Prepend the `# Policies processed:` header to the instances TTL
    files["GEM_policy_instances.ttl"] = (
        _processed_list_ttl_with_header(["pdone_0", "pdone_1", "pdone_2"])
        + files["GEM_policy_instances.ttl"]
    )
    files["policy_worklist.json"] = _processed_list_worklist(3)
    return {"files": files}


def _variant_21_processed_list_disagreement() -> dict:
    """processed_list disagreement -> YELLOW: header=3, worklist=3, graph planDone=4."""
    g = _processed_list_graph(4)  # graph has 4 planDone
    files = _instances_graph_to_files(g)
    # Header lists only 3
    files["GEM_policy_instances.ttl"] = (
        _processed_list_ttl_with_header(["pdone_0", "pdone_1", "pdone_2"])
        + files["GEM_policy_instances.ttl"]
    )
    files["policy_worklist.json"] = _processed_list_worklist(3)  # worklist says 3
    return {"files": files}


# --- uri_scheme (V22-V23) -----------------------------------------------------

def _uri_scheme_graph_with_articles() -> rdflib.Graph:
    """Build a graph with Articles in `a_form` (gemi:a<digits>)."""
    g = rdflib.Graph()
    g.add((GEMI["a52514"], rdflib.RDF.type, GEM.ArticlePolicy))
    g.add((GEMI["a55426"], rdflib.RDF.type, GEM.ArticlePolicy))
    return g


def _variant_22_uri_scheme_baseline() -> dict:
    """uri_scheme GREEN: graph uses a_form Articles; markdown docs are clean."""
    files = _instances_graph_to_files(_uri_scheme_graph_with_articles())
    files["gem_reference.md"] = b"# gem_reference.md\n\nArticles use the gemi:a<id> URI form.\n"
    return {"files": files}


def _variant_23_uri_scheme_doc_drift() -> dict:
    """uri_scheme drift -> YELLOW: docs reference `gemi:article<id>` while graph uses `gemi:a<id>`."""
    files = _instances_graph_to_files(_uri_scheme_graph_with_articles())
    files["gem_reference.md"] = (
        b"# gem_reference.md\n\n"
        b"Articles are recorded as gemi:article52514, gemi:article55426.\n"
    )
    return {"files": files}


# --- proposal_b (V24-V25, V36) ------------------------------------------------

def _proposal_b_graph_bidirectional() -> rdflib.Graph:
    """A revises B AND B references A (both directions asserted)."""
    g = rdflib.Graph()
    a, b = GEMI["ncdA"], GEMI["ncdB"]
    g.add((a, rdflib.RDF.type, GEM.NCDpolicy))
    g.add((b, rdflib.RDF.type, GEM.NCDpolicy))
    g.add((a, GEM.nextPlannedStep, GEM.planDone))
    g.add((b, GEM.nextPlannedStep, GEM.planDone))
    g.add((a, GEM.revisesPolicy, b))
    g.add((b, GEM.referencesPolicy, a))  # reciprocal present -> GREEN
    return g


def _variant_24_proposal_b_baseline() -> dict:
    """proposal_b GREEN: bidirectional revises/references between two planDone NCDs."""
    return {"files": _instances_graph_to_files(_proposal_b_graph_bidirectional())}


def _variant_25_proposal_b_category_d_gap() -> dict:
    """proposal_b Category D gap -> RED: A revises B (planDone, not deleted, not
    transmittal), but B fails to reference A."""
    g = rdflib.Graph()
    a, b = GEMI["ncdA"], GEMI["ncdB"]
    g.add((a, rdflib.RDF.type, GEM.NCDpolicy))
    g.add((b, rdflib.RDF.type, GEM.NCDpolicy))
    g.add((a, GEM.nextPlannedStep, GEM.planDone))
    g.add((b, GEM.nextPlannedStep, GEM.planDone))
    g.add((a, GEM.revisesPolicy, b))  # forward only; no reciprocal -> Category D
    return {"files": _instances_graph_to_files(g)}


def _proposal_b_graph_superseded_revision() -> rdflib.Graph:
    """proposal_b Category E -> GREEN: tnA revises ncdB (planDone) with no
    reciprocal, but a different transmittal tnC also revises ncdB AND ncdB
    references tnC (tnC is ncdB's current transmittal). tnA is therefore a
    superseded historical revision, not an extraction gap. (Registered as
    Variant 36; models the tn48/tn203/ncd20.29 case from S107.)"""
    g = rdflib.Graph()
    a, b, c = GEMI["tnA"], GEMI["ncdB"], GEMI["tnC"]
    g.add((b, rdflib.RDF.type, GEM.NCDpolicy))
    g.add((a, rdflib.RDF.type, GEM.TransmittalPolicy))
    g.add((c, rdflib.RDF.type, GEM.TransmittalPolicy))
    g.add((b, GEM.nextPlannedStep, GEM.planDone))
    g.add((a, GEM.revisesPolicy, b))     # superseded historical revision (no reciprocal)
    g.add((c, GEM.revisesPolicy, b))     # current transmittal
    g.add((b, GEM.referencesPolicy, c))  # reciprocated -> marks tnA as superseded
    return g


def _variant_36_proposal_b_category_e_superseded() -> dict:
    """proposal_b Category E superseded-revision -> GREEN."""
    return {"files": _instances_graph_to_files(_proposal_b_graph_superseded_revision())}


# --- workflow_state (V26-V27) -------------------------------------------------

def _variant_26_workflow_state_baseline() -> dict:
    """workflow_state GREEN: CMSpolicy carries both nextPlannedStep and isInEffect."""
    g = rdflib.Graph()
    u = GEMI["ncdFoo"]
    g.add((u, rdflib.RDF.type, GEM.NCDpolicy))
    g.add((u, GEM.nextPlannedStep, GEM.planDone))
    g.add((u, GEM.isInEffect, rdflib.Literal(True)))
    return {"files": _instances_graph_to_files(g)}


def _variant_27_workflow_state_missing_step() -> dict:
    """workflow_state missing nextPlannedStep -> RED."""
    g = rdflib.Graph()
    u = GEMI["ncdFoo"]
    g.add((u, rdflib.RDF.type, GEM.NCDpolicy))
    # nextPlannedStep deliberately omitted
    g.add((u, GEM.isInEffect, rdflib.Literal(True)))
    return {"files": _instances_graph_to_files(g)}


# --- uri_collision (V28-V29) --------------------------------------------------

def _variant_28_uri_collision_baseline() -> dict:
    """uri_collision GREEN: instance has exactly one prefLabel and one description."""
    g = rdflib.Graph()
    u = GEMI["ncdFoo"]
    g.add((u, rdflib.RDF.type, GEM.NCDpolicy))
    g.add((u, GEM.prefLabel, rdflib.Literal("Foo")))
    g.add((u, GEM.description, rdflib.Literal("A single description.")))
    return {"files": _instances_graph_to_files(g)}


def _variant_29_uri_collision_dup_prefLabel() -> dict:
    """uri_collision duplicate prefLabel -> YELLOW."""
    g = rdflib.Graph()
    u = GEMI["ncdFoo"]
    g.add((u, rdflib.RDF.type, GEM.NCDpolicy))
    g.add((u, GEM.prefLabel, rdflib.Literal("Foo")))
    g.add((u, GEM.prefLabel, rdflib.Literal("Foo (alt)")))   # second prefLabel
    return {"files": _instances_graph_to_files(g)}


# --- deleted_twin_collision (V50-V52) -----------------------------------------
#
# The three states of the §5.3 reservation. The pair is the only YELLOW; both
# lone forms are the normal, correct corpus shapes and must stay silent, or the
# check would fire on all five existing _DELETED stubs.

def _variant_50_deleted_twin_pair() -> dict:
    """deleted_twin_collision: bare + _DELETED both minted -> YELLOW."""
    g = rdflib.Graph()
    bare = GEMI["ncdFoo"]
    retiree = GEMI["ncdFoo_DELETED"]
    g.add((bare, rdflib.RDF.type, GEM.NCDpolicy))
    g.add((bare, GEM.prefLabel, rdflib.Literal("Foo")))
    g.add((retiree, rdflib.RDF.type, GEM.NCDpolicy))
    g.add((retiree, GEM.prefLabel, rdflib.Literal("Policy Foo Deleted")))
    return {"files": _instances_graph_to_files(g)}


def _variant_51_deleted_twin_bare_only() -> dict:
    """deleted_twin_collision: bare URI with no retiree -> GREEN.

    The ordinary case for every live policy in the corpus.
    """
    g = rdflib.Graph()
    bare = GEMI["ncdFoo"]
    g.add((bare, rdflib.RDF.type, GEM.NCDpolicy))
    g.add((bare, GEM.prefLabel, rdflib.Literal("Foo")))
    return {"files": _instances_graph_to_files(g)}


def _variant_52_deleted_twin_retiree_only() -> dict:
    """deleted_twin_collision: retiree with its bare URI unreserved -> GREEN.

    The §5.3 convention working as designed — the shape of all five _DELETED
    stubs in the corpus after the S146 consolidation. A retiree alone must
    never fire, or the check would report the convention as a defect.
    """
    g = rdflib.Graph()
    retiree = GEMI["ncdFoo_DELETED"]
    g.add((retiree, rdflib.RDF.type, GEM.NCDpolicy))
    g.add((retiree, GEM.prefLabel, rdflib.Literal("Policy Foo Deleted")))
    return {"files": _instances_graph_to_files(g)}


# --- predicate_order (V30-V31) ------------------------------------------------
#
# predicate_ordering operates on raw TTL text (not the parsed graph), so these
# variants hand-craft byte-level TTL rather than going through rdflib serialization.

def _variant_30_predicate_order_baseline() -> dict:
    """predicate_order GREEN: memberOfOntology at n-2, dc:source at n-1."""
    ttl = (
        b"@prefix gemi: <http://www.cms.hhs.gov/ontology/2026/07/GEM/instances/> .\r\n"
        b"@prefix gem:  <http://www.cms.hhs.gov/ontology/2026/07/GEM/> .\r\n"
        b"@prefix dc:   <http://purl.org/dc/elements/1.1/> .\r\n"
        b"\r\n"
        b"gemi:ncdFoo a gem:NCDpolicy ;\r\n"
        b"    gem:prefLabel \"Foo\" ;\r\n"
        b"    gem:memberOfOntology gem:GEM ;\r\n"
        b"    dc:source gemi:bar .\r\n"
    )
    return {"files": {
        "GEM_policy_instances.ttl": ttl,
        "GEM_ontology.ttl": _SELF_TEST_ONTOLOGY_STUB.encode("utf-8"),
    }}


def _variant_31_predicate_order_reversed() -> dict:
    """predicate_order reversed -> YELLOW: dc:source at n-2, memberOfOntology at n-1."""
    ttl = (
        b"@prefix gemi: <http://www.cms.hhs.gov/ontology/2026/07/GEM/instances/> .\r\n"
        b"@prefix gem:  <http://www.cms.hhs.gov/ontology/2026/07/GEM/> .\r\n"
        b"@prefix dc:   <http://purl.org/dc/elements/1.1/> .\r\n"
        b"\r\n"
        b"gemi:ncdFoo a gem:NCDpolicy ;\r\n"
        b"    gem:prefLabel \"Foo\" ;\r\n"
        b"    dc:source gemi:bar ;\r\n"
        b"    gem:memberOfOntology gem:GEM .\r\n"
    )
    return {"files": {
        "GEM_policy_instances.ttl": ttl,
        "GEM_ontology.ttl": _SELF_TEST_ONTOLOGY_STUB.encode("utf-8"),
    }}


# --- handoff_drift (V32-V33) --------------------------------------------------

def _variant_32_handoff_drift_baseline() -> dict:
    """handoff_drift GREEN: empty §4 (no items, no claim blocks, no identifier
    mentions) -> 0 findings."""
    handoff = (
        "# GEM Policy-Extraction Session 99 Handoff\n"
        "\n"
        "## §1 — Files\n"
        "\n"
        "(synthetic)\n"
        "\n"
        "## §4 — Open items\n"
        "\n"
        "(no items in this synthetic handoff)\n"
        "\n"
        "## §5 — Next steps\n"
    )
    files = _instances_graph_to_files(rdflib.Graph())
    return {"files": files, "handoff_text": handoff}


def _handoff_drift_claim_handoff(item_line: str) -> str:
    """A §4 carrying one item, whose body holds a claim block that must fail.

    The RED is the assertion that matters, and it is load-bearing in a second
    way: claim blocks are only ever parsed out of an *item body*, so the RED
    firing is proof the item form was recognized. If the item regex stops
    matching, the RED disappears and the variant fails — which is precisely the
    signal that was missing while V33 synthesized a form no handoff uses.
    """
    return (
        "# GEM Policy-Extraction Handoff — Session 99 (2026-07-14)\n"
        "\n"
        "## §4 — Open items\n"
        "\n"
        f"{item_line}\n"
        "\n"
        "<!-- AUDIT-CLAIMS\n"
        "- graph_state:\n"
        "    uri: gemi:ghost_policy\n"
        "    type: NCDpolicy\n"
        "-->\n"
        "\n"
        "Body text references the claim block above.\n"
        "\n"
        "## §5 — Next\n"
    )


def _variant_33_handoff_drift_claim_mismatch() -> dict:
    """handoff_drift claim mismatch -> RED: AUDIT-CLAIMS asserts graph_state of a
    URI not in the graph. Corpus item form (S144: was the legacy form, see V44)."""
    files = _instances_graph_to_files(rdflib.Graph())
    return {"files": files,
            "handoff_text": _handoff_drift_claim_handoff(
                "1. **Synthetic item with a failing claim.**")}


# --- handoff_drift item-form coverage (V44-V45; S144) -------------------------

def _variant_44_handoff_drift_legacy_item_form() -> dict:
    """Legacy '**(a) Title**' item form still parses -> RED claim fires."""
    files = _instances_graph_to_files(rdflib.Graph())
    return {"files": files,
            "handoff_text": _handoff_drift_claim_handoff(
                "**(a) Synthetic item with a failing claim.**")}


def _variant_45_handoff_drift_inert_parser() -> dict:
    """§4 has bolded items in an unrecognized form -> YELLOW inert-parser guard.

    Pre-S144 this returned GREEN: zero parsed items was indistinguishable from
    zero actual items, so a dead parser reported clean.
    """
    handoff = (
        "# GEM Policy-Extraction Handoff — Session 99 (2026-07-14)\n"
        "\n"
        "## §4 — Open items\n"
        "\n"
        "- **Bulleted item in a form the parser does not know.** Body text.\n"
        "\n"
        "## §5 — Next\n"
    )
    files = _instances_graph_to_files(rdflib.Graph())
    return {"files": files, "handoff_text": handoff}


# --- codegroup_block_extent (V46-V49; S145) ----------------------------------
#
# codegroup_block_extent reads raw file text, not the graph, so these fixtures
# are built as bytes rather than via _instances_graph_to_files. Per the S144
# corpus-fixture rule they reproduce the shape GEM_policy_instances.ttl actually
# uses: CRLF endings, the real prefix header, hand-authored subject blocks above
# the BEGIN marker and below the END marker, and the marker literals verbatim.
#
# V47 is the regression evidence for the S145 repair. There is no pre-repair
# version of this check to run it against, so instead its fixture reproduces the
# pre-repair *corpus* — 49-stub tail included in the span, in the S131 shape —
# and demonstrates the guard fires on the state the file was actually in.

_CG_FIXTURE_PREFIXES = "\r\n".join([
    "@prefix rdf:   <http://www.w3.org/1999/02/22-rdf-syntax-ns#> .",
    "@prefix xsd:   <http://www.w3.org/2001/XMLSchema#> .",
    "@prefix dc:    <http://purl.org/dc/elements/1.1/> .",
    "@prefix gem:   <http://www.cms.hhs.gov/ontology/2026/07/GEM/> .",
    "@prefix gemi:  <http://www.cms.hhs.gov/ontology/2026/07/GEM/instances/> .",
    "",
])

# A hand-authored stub in the S131 tail shape — the content the false extent
# claim put at risk.
_CG_FIXTURE_TAIL_STUB = "\r\n".join([
    "# --- S131: transmittal & CR stubs from NCD 160.18 revision history ---",
    "gemi:tn10432NCD a gem:TransmittalPolicy ;",
    '    gem:identifier "TN 10432" ;',
    '    gem:publicationNumber "100-03" ;',
    "    gem:nextPlannedStep gem:planPromote ;",
    "    gem:memberOfOntology gem:gemOntology .",
])

_CG_FIXTURE_LINKS = "\r\n".join([
    "gemi:a52466 gem:refersToCodeGroup gemi:codeGroupHCPCSAcodes .",
    "gemi:a52466 gem:refersToCodeGroup gemi:codeGroupHCPCSdme .",
    "gemi:lcd33797 gem:refersToCodeGroup gemi:codeGroupOxygenEquipment .",
])


def _cg_extent_files(body: str) -> dict:
    """Wrap a fixture body in the prefix header and emit it as a files dict.

    Only GEM_policy_instances.ttl matters to this check; the sibling TTLs are
    omitted, so _run_variant_check builds graph=None — which the check does not
    use.
    """
    text = _CG_FIXTURE_PREFIXES + "\r\n" + body + "\r\n"
    return {"GEM_policy_instances.ttl": text.encode("utf-8")}


def _variant_46_codegroup_block_extent_baseline() -> dict:
    """codegroup_block_extent GREEN: a properly delimited block, with
    hand-authored content both above the BEGIN marker and below the END marker
    — the S145 post-repair corpus shape -> 0 findings."""
    body = "\r\n".join([
        "gemi:ncd280.4 a gem:NCDpolicy ;",
        "    gem:memberOfOntology gem:gemOntology .",
        "",
        _CG_BEGIN_MARKER,
        _CG_FIXTURE_LINKS,
        _CG_END_MARKER,
        "",
        _CG_FIXTURE_TAIL_STUB,
    ])
    return {"files": _cg_extent_files(body)}


def _variant_47_codegroup_block_extent_intruder() -> dict:
    """codegroup_block_extent YELLOW: hand-authored individuals sit *inside* the
    span, so the next regeneration deletes them.

    This is the pre-S145 corpus state: the marker claimed the block ran to EOF
    while the S131 transmittal/CR stubs sat below the links inside that claim.
    Nothing reported it, because no check read the block's extent."""
    body = "\r\n".join([
        "gemi:ncd280.4 a gem:NCDpolicy ;",
        "    gem:memberOfOntology gem:gemOntology .",
        "",
        _CG_BEGIN_MARKER,
        _CG_FIXTURE_LINKS,
        "",
        _CG_FIXTURE_TAIL_STUB,
        _CG_END_MARKER,
    ])
    return {"files": _cg_extent_files(body)}


def _variant_48_codegroup_block_extent_marker_missing() -> dict:
    """codegroup_block_extent YELLOW: the END marker is absent, so the block's
    extent cannot be established.

    The S144 inert-precondition rule applied to this check: a missing marker is
    the very drift the check guards, so it must be loud rather than a silent
    'nothing to check'."""
    body = "\r\n".join([
        _CG_BEGIN_MARKER,
        _CG_FIXTURE_LINKS,
        "",
        _CG_FIXTURE_TAIL_STUB,
    ])
    return {"files": _cg_extent_files(body)}


def _variant_49_codegroup_block_extent_link_outside() -> dict:
    """codegroup_block_extent YELLOW: a link statement is authored outside the
    block (here as a predicate-list continuation inside a policy's subject
    block), so it survives the strip and is duplicated by the re-emit.

    The banner mention of gem:refersToCodeGroup in the same fixture is a comment
    and must NOT be counted — the check filters comment lines first."""
    body = "\r\n".join([
        "# MATERIALIZED gem:refersToCodeGroup LINKS  (auto-generated; do not hand-edit)",
        "gemi:ncd280.6 a gem:NCDpolicy ;",
        "    gem:refersToCodeGroup gemi:codeGroupHCPCSdme ;",
        "    gem:memberOfOntology gem:gemOntology .",
        "",
        _CG_BEGIN_MARKER,
        _CG_FIXTURE_LINKS,
        _CG_END_MARKER,
    ])
    return {"files": _cg_extent_files(body)}


# --- codegroup_link_drift (V34-V35) ------------------------------------------

def _variant_34_codegroup_link_drift_baseline() -> dict:
    """codegroup_link_drift GREEN: a policy references an E-code, a group matches
    it via gem:memberCodePattern, and the gem:refersToCodeGroup link is present
    -> 0 findings."""
    g = rdflib.Graph()
    P = GEMI.ncdFoo
    GRP = GEMI.codeGroupFoo
    E = rdflib.URIRef("http://purl.bioontology.org/ontology/HCPCS/E0470")
    g.add((P, rdflib.RDF.type, GEM.NCDpolicy))
    g.add((P, GEM.coversProcedure, E))
    g.add((GRP, rdflib.RDF.type, GEM.CodeGroup))
    g.add((GRP, GEM.memberCodePattern,
           rdflib.Literal(r"^http://purl\.bioontology\.org/ontology/HCPCS/E\d{4}$")))
    g.add((P, GEM.refersToCodeGroup, GRP))
    return {"files": _instances_graph_to_files(g)}


def _variant_35_codegroup_link_drift_missing() -> dict:
    """codegroup_link_drift YELLOW: identical to the baseline but the expected
    gem:refersToCodeGroup link is absent -> 1 missing link -> YELLOW."""
    g = rdflib.Graph()
    P = GEMI.ncdFoo
    GRP = GEMI.codeGroupFoo
    E = rdflib.URIRef("http://purl.bioontology.org/ontology/HCPCS/E0470")
    g.add((P, rdflib.RDF.type, GEM.NCDpolicy))
    g.add((P, GEM.coversProcedure, E))
    g.add((GRP, rdflib.RDF.type, GEM.CodeGroup))
    g.add((GRP, GEM.memberCodePattern,
           rdflib.Literal(r"^http://purl\.bioontology\.org/ontology/HCPCS/E\d{4}$")))
    # deliberately no gem:refersToCodeGroup link -> drift
    return {"files": _instances_graph_to_files(g)}


# ----- Variant registry and assertion logic ---------------------------------

# 4-tuple: (label, check_category, builder, expected_findings)
#   check_category: a name in ALL_CHECKS, or the sentinel "policyrule_all" meaning
#                   "run all 4 Phase 3 checks via _run_policyrule_checks_only".
#   expected_findings: list of (tier, category, location_substring) tuples;
#                      empty list -> no findings expected; non-empty -> each
#                      tuple must match at least one actual finding.

def _build_register_variant_instances() -> rdflib.Graph:
    """Minimal instances graph: one planDone NCD policy with one rule, for the
    register_section_coverage self-test variants."""
    g = rdflib.Graph()
    g.bind("gem", GEM); g.bind("gemi", GEMI); g.bind("dc", DC)
    pol = GEMI["ncd999.9"]
    g.add((pol, rdflib.RDF.type, GEM.NCDpolicy))
    g.add((pol, GEM.identifier, rdflib.Literal("NCD 999.9")))
    g.add((pol, GEM.nextPlannedStep, GEM.planDone))
    g.add((pol, GEM.memberOfOntology, GEM.GEM))
    rule = GEMI["ncd999.9_r1"]
    g.add((pol, GEM.hasPolicyRule, rule))
    g.add((rule, rdflib.RDF.type, GEM.PolicyRule))
    g.add((rule, GEM.prefLabel, rdflib.Literal("NCD 999.9 R1")))
    g.add((rule, GEM.ruleDescription, rdflib.Literal("Synthetic rule.")))
    g.add((rule, GEM.ruleType, GEM.ruleType_coverageScope))
    g.add((rule, DC.source, pol))
    g.add((rule, GEM.memberOfOntology, GEM.GEM))
    return g


def _variant_37_register_section_present() -> dict:
    files = _instances_graph_to_files(_build_register_variant_instances())
    files["gem_rule_categories.md"] = (
        "# Rule Category Register\n\n"
        "### NCD 999.9 — Synthetic Test Policy\n\n"
        "| Rule | Source / topic | Rule type(s) |\n"
        "| :--- | :--- | :--- |\n"
        "| R1 | synthetic | coverage-scope |\n"
    ).encode("utf-8")
    return {"files": files}


def _variant_38_register_section_missing() -> dict:
    files = _instances_graph_to_files(_build_register_variant_instances())
    files["gem_rule_categories.md"] = (
        "# Rule Category Register\n\n"
        "### NCD 111.1 — Some Other Policy\n\n"
        "(no section for NCD 999.9)\n"
    ).encode("utf-8")
    return {"files": files}


def _llm_annotation_variant_graph() -> rdflib.Graph:
    """Two gem:RuleType individuals (declared in the self-test ontology stub)
    carrying gem:llmDetailedDefinition — the graph side of the mirror."""
    g = rdflib.Graph()
    g.add((GEM.ruleType_eligibility, GEM.llmDetailedDefinition,
           rdflib.Literal("who/when is eligible.")))
    g.add((GEM.ruleType_frequency, GEM.llmDetailedDefinition,
           rdflib.Literal("how often / repeat-screening intervals.")))
    return g


def _variant_39_llm_annotation_drift_baseline() -> dict:
    """llm_annotation_drift GREEN: file mirrors the graph exactly."""
    files = _instances_graph_to_files(_llm_annotation_variant_graph())
    files[LLM_ANNOTATION_FILE] = _serialize_llm_annotations({
        "gem:llmDetailedDefinition": {
            str(GEM.ruleType_eligibility): "who/when is eligible.",
            str(GEM.ruleType_frequency): "how often / repeat-screening intervals.",
        }
    })
    return {"files": files}


def _variant_40_llm_annotation_drift_mismatch() -> dict:
    """llm_annotation_drift YELLOW: file omits ruleType_frequency (present in graph)."""
    files = _instances_graph_to_files(_llm_annotation_variant_graph())
    files[LLM_ANNOTATION_FILE] = _serialize_llm_annotations({
        "gem:llmDetailedDefinition": {
            str(GEM.ruleType_eligibility): "who/when is eligible.",
        }
    })
    return {"files": files}


# --- S149 variants (V53-V63): manual token, NCA derivation, doc URI examples ---

def _tn(g, ln, pub=None, desc=None):
    s = GEMI[ln]
    g.add((s, rdflib.RDF.type, GEM.TransmittalPolicy))
    g.add((s, GEM.prefLabel, rdflib.Literal(ln)))
    if pub is not None:
        g.add((s, GEM.publicationNumber, rdflib.Literal(pub)))
    if desc is not None:
        g.add((s, GEM.description, rdflib.Literal(desc)))
    return s


def _variant_53_manual_token_baseline() -> dict:
    """transmittal_manual_token: one of each token, each with its publicationNumber,
    plus a properly declared bare stub -> GREEN."""
    g = rdflib.Graph()
    _tn(g, "tn144CIM", "6")
    _tn(g, "tn96NCD", "100-03")
    _tn(g, "tn961CP", "100-04")
    _tn(g, "tn1194OTN", "100-20")
    _tn(g, "tn999", None, "Manual undetermined -- no verified rendition, no stated manual, "
                          "no datable era; on the reference-stub backlog.")
    return {"files": _instances_graph_to_files(g)}


def _variant_54_manual_token_bare_with_pub() -> dict:
    """Bare URI asserting a publicationNumber: the manual is determined, so the URI
    must carry its token. This is the shape 61 of 85 transmittals were in at S148."""
    g = rdflib.Graph()
    _tn(g, "tn48", "100-03")
    return {"files": _instances_graph_to_files(g)}


def _variant_55_manual_token_bare_undeclared() -> dict:
    """Bare and silent about it -> RED. A bare URI means *unresolved*, never *fine*."""
    g = rdflib.Graph()
    _tn(g, "tn10515", None, "Transmittal 10515, named in NCD 160.18's Revision History.")
    return {"files": _instances_graph_to_files(g)}


def _variant_56_manual_token_bare_declared() -> dict:
    """Bare, no publicationNumber, description declares it -> GREEN (the escape hatch)."""
    g = rdflib.Graph()
    _tn(g, "tn10515", None, "Manual undetermined: no verified rendition filename and the "
                            "citing policy states no manual. Reference-stub backlog.")
    return {"files": _instances_graph_to_files(g)}


def _variant_57_manual_token_pub_mismatch() -> dict:
    """Token says CIM, publicationNumber says 100-03 -> RED (the tn78/tn36 shape)."""
    g = rdflib.Graph()
    _tn(g, "tn78CIM", "100-03")
    return {"files": _instances_graph_to_files(g)}


def _variant_58_manual_token_missing_pub() -> dict:
    """Token present, publicationNumber absent -> RED (biconditional, other direction)."""
    g = rdflib.Graph()
    _tn(g, "tn100CIM", None)
    return {"files": _instances_graph_to_files(g)}


def _variant_59_manual_token_unknown_token() -> dict:
    """A token outside the controlled vocabulary -> RED."""
    g = rdflib.Graph()
    _tn(g, "tn55ZZZ", "14")
    return {"files": _instances_graph_to_files(g)}


def _variant_60_manual_token_cim_era_gate() -> dict:
    """CIM token above the manual's extent (TN 1-167) -> RED."""
    g = rdflib.Graph()
    _tn(g, "tn13374CIM", "6")
    return {"files": _instances_graph_to_files(g)}


def _variant_61_nca_derivation_case_drift() -> dict:
    """NCA local name lowercases a revision letter its own identifier uppercases -> RED."""
    g = rdflib.Graph()
    s = GEMI["cag00313r"]
    g.add((s, rdflib.RDF.type, GEM.NCAdocument))
    g.add((s, GEM.identifier, rdflib.Literal("CAG-00313R")))
    return {"files": _instances_graph_to_files(g)}


def _variant_62_nca_derivation_clean() -> dict:
    """NCA local name == cag + identifier minus 'CAG-' -> GREEN."""
    g = rdflib.Graph()
    for ln, ident in [("cag00296N", "CAG-00296N"), ("cag00296R2", "CAG-00296R2")]:
        s = GEMI[ln]
        g.add((s, rdflib.RDF.type, GEM.NCAdocument))
        g.add((s, GEM.identifier, rdflib.Literal(ident)))
    return {"files": _instances_graph_to_files(g)}


_DOC_TABLE_TMPL = """## 5. Instance Namespace and Stubs

### Instance URI naming schemes

| Kind | Scheme | Examples |
|------|--------|----------|
| NCD policy / stub | `gemi:ncd<section>` | `gemi:ncd240.2` |
| Transmittal | `gemi:tn<NN><MANUAL>` | %s |
| Draft LCD | `gemi:dl<id>` | *reserved; no instances in the graph* |

### Next section
"""


def _variant_63_doc_uri_examples_dead() -> dict:
    """A naming-table example that names nothing in the graph -> YELLOW.
    The Draft LCD row is marked *reserved* and must be skipped, so a single
    finding proves both halves."""
    g = rdflib.Graph()
    g.add((GEMI["ncd240.2"], rdflib.RDF.type, GEM.NCDpolicy))
    files = _instances_graph_to_files(g)
    files["gem_reference.md"] = (_DOC_TABLE_TMPL % "`gemi:tn44NCD`").encode("utf-8")
    return {"files": files}


def _variant_64_doc_uri_examples_live() -> dict:
    """Every naming-table example exists -> GREEN."""
    g = rdflib.Graph()
    g.add((GEMI["ncd240.2"], rdflib.RDF.type, GEM.NCDpolicy))
    _tn(g, "tn96NCD", "100-03")
    files = _instances_graph_to_files(g)
    files["gem_reference.md"] = (_DOC_TABLE_TMPL % "`gemi:tn96NCD`").encode("utf-8")
    return {"files": files}


def _variant_65_uri_scheme_nca_doc_drift() -> dict:
    """Docs say `gemi:ncaCAG*`, graph says `gemi:cag*` -> YELLOW, autofixable.
    The four-sessions-late twin of the Article branch."""
    g = rdflib.Graph()
    s = GEMI["cag00296N"]
    g.add((s, rdflib.RDF.type, GEM.NCAdocument))
    g.add((s, GEM.identifier, rdflib.Literal("CAG-00296N")))
    files = _instances_graph_to_files(g)
    files["gem_reference.md"] = b"| NCA | `gemi:ncaCAG<NNNNN>` | `gemi:ncaCAG00405N` |\n"
    return {"files": files}


def _variant_66_source_availability_unverified() -> dict:
    """A CIM transmittal with neither dc:source nor gem:sourceAvailability is
    undetermined -> INFO. The non-CIM sibling and the two resolved CIM ones must
    NOT be reported, which is what makes this a test of the derivation rather
    than of the loop."""
    g = rdflib.Graph()
    # unchecked CIM -> reported
    s = GEMI["tn26CIM"]
    g.add((s, rdflib.RDF.type, GEM.TransmittalPolicy))
    g.add((s, GEM.publicationNumber, rdflib.Literal("6")))
    # CIM with a rendition -> not reported
    s2 = GEMI["tn128CIM"]
    g.add((s2, rdflib.RDF.type, GEM.TransmittalPolicy))
    g.add((s2, GEM.publicationNumber, rdflib.Literal("6")))
    g.add((s2, DC.source, rdflib.URIRef("https://example.invalid/R128CIM.pdf")))
    # CIM already determined unobtainable -> not reported
    s3 = GEMI["tn78CIM"]
    g.add((s3, rdflib.RDF.type, GEM.TransmittalPolicy))
    g.add((s3, GEM.publicationNumber, rdflib.Literal("6")))
    g.add((s3, GEM.sourceAvailability, GEM.sourceUnobtainable))
    # non-CIM with no rendition -> not reported (post-2003, obtainable, item 9)
    s4 = GEMI["tn768CP"]
    g.add((s4, rdflib.RDF.type, GEM.TransmittalPolicy))
    g.add((s4, GEM.publicationNumber, rdflib.Literal("100-04")))
    return {"files": _instances_graph_to_files(g)}


def _variant_67_source_availability_all_resolved() -> dict:
    """Every CIM transmittal is resolved one way or the other -> GREEN. Pins the
    self-emptying property: the queue is derived, so it drains to nothing without
    anyone editing a list."""
    g = rdflib.Graph()
    s = GEMI["tn128CIM"]
    g.add((s, rdflib.RDF.type, GEM.TransmittalPolicy))
    g.add((s, GEM.publicationNumber, rdflib.Literal("6")))
    g.add((s, DC.source, rdflib.URIRef("https://example.invalid/R128CIM.pdf")))
    s2 = GEMI["tn78CIM"]
    g.add((s2, rdflib.RDF.type, GEM.TransmittalPolicy))
    g.add((s2, GEM.publicationNumber, rdflib.Literal("6")))
    g.add((s2, GEM.sourceAvailability, GEM.sourceUnobtainable))
    return {"files": _instances_graph_to_files(g)}


def _variant_68_source_availability_non_cim_ignored() -> dict:
    """A non-CIM transmittal with no dc:source is NOT undetermined -- it postdates
    2003, its rendition is published, and its URL is merely un-backfilled (handoff
    item 9). -> GREEN. Pins the publicationNumber "6" filter: without it this
    check would swallow item 9's ~45 obtainable stubs and become noise."""
    g = rdflib.Graph()
    s = GEMI["tn768CP"]
    g.add((s, rdflib.RDF.type, GEM.TransmittalPolicy))
    g.add((s, GEM.publicationNumber, rdflib.Literal("100-04")))
    s2 = GEMI["tn2439NCD"]
    g.add((s2, rdflib.RDF.type, GEM.TransmittalPolicy))
    g.add((s2, GEM.publicationNumber, rdflib.Literal("100-03")))
    return {"files": _instances_graph_to_files(g)}



# --- S157 variants (V69-V71; literal_escape_artifact) ------------------------
# Mutation-tested. V69 fires on the defect. V70 pins that a correctly escaped
# quote is NOT flagged -- without it the check could match one backslash and
# rewrite all 3,117 legitimate escapes in the corpus. V71 pins the three-vs-two
# backslash distinction, which is the bug S157 wrote into the autofix on the
# first attempt: matching the two-backslash tail of the artifact and collapsing
# it leaves an escaped backslash followed by a live quote, which terminates the
# literal early. V71 asserts the repaired file still parses -- a variant that
# only counted findings would have passed the broken autofix.
def _ttl(body: str) -> dict:
    header = (
        '@prefix gem:   <http://www.cms.hhs.gov/ontology/2026/07/GEM/> .' + chr(10) +
        '@prefix gemi:  <http://www.cms.hhs.gov/ontology/2026/07/GEM/instances/> .' + chr(10) +
        '@prefix dc:    <http://purl.org/dc/elements/1.1/> .' + chr(10) +
        '@prefix xsd:   <http://www.w3.org/2001/XMLSchema#> .' + chr(10) * 2
    )
    files = _instances_graph_to_files(rdflib.Graph())
    files["GEM_policy_instances.ttl"] = (header + body).replace(chr(10), chr(13) + chr(10)).encode("utf-8")
    return {"files": files}


def _variant_69_literal_escape_artifact() -> dict:
    """A description whose source writes THREE backslashes before a quote: the
    literal's value carries a stray backslash. Parses fine. -> YELLOW."""
    bs = chr(92)
    body = (
        'gemi:conceptV69 a gem:ClinicalConcept ;' + chr(10) +
        '    gem:prefLabel "v69" ;' + chr(10) +
        '    gem:description "The source calls it ' + bs*3 + '"a thing' + bs*3 + '" here." ;' + chr(10) +
        '    gem:memberOfOntology gem:gemOntology .' + chr(10)
    )
    return _ttl(body)


def _variant_70_literal_escape_correct_ignored() -> dict:
    """A correctly escaped quote -- the corpus's normal case, 3,117 of them at
    S157. -> GREEN. Without this variant the check could be written to match a
    single backslash and would rewrite every legitimate escape in the graph."""
    bs = chr(92)
    body = (
        'gemi:conceptV70 a gem:ClinicalConcept ;' + chr(10) +
        '    gem:prefLabel "v70" ;' + chr(10) +
        '    gem:description "Governing text: ' + bs + '"a thing' + bs + '" Location: A." ;' + chr(10) +
        '    gem:memberOfOntology gem:gemOntology .' + chr(10)
    )
    return _ttl(body)


def _variant_71_literal_escape_lone_backslash_ignored() -> dict:
    """A legitimately escaped backslash NOT adjacent to a quote is not this
    defect. -> GREEN. Pins the `before a quote` half of the pattern: a check
    written as `count(escaped-backslash)` would flag it, and its autofix would
    silently delete a character the author meant. Zero such literals exist at
    S157 -- which is exactly why the variant is needed, since the corpus cannot
    disconfirm the over-broad pattern on its own (the S144 regression-test rule:
    a variant that passes a broken check is coverage, not a test)."""
    bs = chr(92)
    body = (
        'gemi:conceptV71 a gem:ClinicalConcept ;' + chr(10) +
        '    gem:prefLabel "v71" ;' + chr(10) +
        '    gem:description "A path like C:' + bs*2 + 'temp uses an escaped backslash." ;' + chr(10) +
        '    gem:memberOfOntology gem:gemOntology .' + chr(10)
    )
    return _ttl(body)


# --- deferred_proposals_id variant builders (S161, V72-V76) ------------------
def _dp_worklist_bytes(entries: list) -> bytes:
    return json.dumps(
        {"metadata": {}, "related_policies": [], "deferred_proposals": entries},
        indent=2, ensure_ascii=False).encode("utf-8")


def _variant_72_dp_baseline() -> dict:
    entries = [
        {"id": 0, "concept_group": "x", "status": "logged"},
        {"id": 1, "concept_group": "y", "status": "complete"},
        {"id": 3, "concept_group": "z", "status": "resolved"},
    ]
    return {"files": {"policy_worklist.json": _dp_worklist_bytes(entries)}}


def _variant_73_dp_missing_id() -> dict:
    entries = [
        {"id": 0, "concept_group": "x", "status": "logged"},
        {"concept_group": "y", "status": "logged"},  # no id at index 1
    ]
    return {"files": {"policy_worklist.json": _dp_worklist_bytes(entries)}}


def _variant_74_dp_duplicate_id() -> dict:
    entries = [
        {"id": 5, "concept_group": "x", "status": "logged"},
        {"id": 5, "concept_group": "y", "status": "logged"},  # dup id
    ]
    return {"files": {"policy_worklist.json": _dp_worklist_bytes(entries)}}


def _variant_75_dp_invalid_status() -> dict:
    entries = [
        {"id": 0, "concept_group": "x", "status": "open"},  # not one of the seven
    ]
    return {"files": {"policy_worklist.json": _dp_worklist_bytes(entries)}}


def _variant_76_dp_dangling_citation() -> dict:
    entries = [{"id": 0, "concept_group": "x", "status": "logged"}]
    return {"files": {
        "policy_worklist.json": _dp_worklist_bytes(entries),
        "SKILL.md": b"Refer to deferred_proposals[999] for the rationale.\n",
    }}


def _variant_77_llm_annotation_count_baseline() -> dict:
    """llm_annotation_count_drift GREEN: _meta.coverage's stated counts match the
    graph (two annotated gem:RuleType individuals; two total)."""
    files = _instances_graph_to_files(_llm_annotation_variant_graph())
    files[LLM_ANNOTATION_FILE] = _serialize_llm_annotations({
        "_meta": {"coverage": "Annotated families: gem:RuleType (2) - 2 individuals."},
        "gem:llmDetailedDefinition": {
            str(GEM.ruleType_eligibility): "who/when is eligible.",
            str(GEM.ruleType_frequency): "how often / repeat-screening intervals.",
        },
    })
    return {"files": files}


def _variant_78_llm_annotation_count_drift() -> dict:
    """llm_annotation_count_drift YELLOW: _meta.coverage overstates the gem:RuleType
    count (says 3; graph has 2)."""
    files = _instances_graph_to_files(_llm_annotation_variant_graph())
    files[LLM_ANNOTATION_FILE] = _serialize_llm_annotations({
        "_meta": {"coverage": "Annotated families: gem:RuleType (3) - 3 individuals."},
        "gem:llmDetailedDefinition": {
            str(GEM.ruleType_eligibility): "who/when is eligible.",
            str(GEM.ruleType_frequency): "how often / repeat-screening intervals.",
        },
    })
    return {"files": files}


def _revises_redundancy_variant_graph(redundant: bool) -> rdflib.Graph:
    """One transmittal that revisesPolicy an NCD. When `redundant` is True it
    ALSO asserts referencesPolicy to the same NCD (the dual assertion the guard
    flags); when False it asserts revises only (GREEN)."""
    g = rdflib.Graph()
    g.bind("gem", GEM)
    g.bind("gemi", GEMI)
    tn = GEMI["tn999NCD"]
    ncd = GEMI["ncd999.9"]
    g.add((tn, rdflib.RDF.type, GEM.TransmittalPolicy))
    g.add((tn, GEM.revisesPolicy, ncd))
    if redundant:
        g.add((tn, GEM.referencesPolicy, ncd))
    return g


def _variant_79_revises_redundancy_baseline() -> dict:
    """revises_references_redundancy GREEN: revises only, no co-asserted references."""
    return {"files": _instances_graph_to_files(
        _revises_redundancy_variant_graph(redundant=False))}


def _variant_80_revises_redundancy() -> dict:
    """revises_references_redundancy YELLOW: same subject asserts both revises and
    references to the same object."""
    return {"files": _instances_graph_to_files(
        _revises_redundancy_variant_graph(redundant=True))}


def _variant_81_dwl_baseline() -> dict:
    """description_workflow_leak GREEN baseline: clean gem:description, with the
    verbatim/provenance material living in gem:workflowDescription. -> GREEN."""
    body = (
        'gemi:conceptV81 a gem:ClinicalConcept ;' + chr(10) +
        '    gem:prefLabel "v81" ;' + chr(10) +
        '    gem:description "A device the policy requires for the covered service." ;' + chr(10) +
        '    gem:workflowDescription "Governing text: the device must be used here. Minted 2026-07-19 (Session 173)." ;' + chr(10) +
        '    gem:memberOfOntology gem:gemOntology .' + chr(10)
    )
    return _ttl(body)


def _variant_82_dwl_wf_without_desc() -> dict:
    """A subject carrying gem:workflowDescription but no gem:description
    (structural). -> RED."""
    body = (
        'gemi:conceptV82 a gem:ClinicalConcept ;' + chr(10) +
        '    gem:prefLabel "v82" ;' + chr(10) +
        '    gem:workflowDescription "Minted as a stub under the S131 mint-every-referenced-policy rule." ;' + chr(10) +
        '    gem:memberOfOntology gem:gemOntology .' + chr(10)
    )
    return _ttl(body)


def _variant_83_dwl_leak_marker() -> dict:
    """A workflow/verbatim leak marker left in gem:description on a plain
    (non-group-(b)) instance. -> YELLOW."""
    body = (
        'gemi:conceptV83 a gem:ClinicalConcept ;' + chr(10) +
        '    gem:prefLabel "v83" ;' + chr(10) +
        '    gem:description "A device the policy requires. Governing text: the device must be used." ;' + chr(10) +
        '    gem:memberOfOntology gem:gemOntology .' + chr(10)
    )
    return _ttl(body)


def _variant_84_skill_checklist_drift() -> dict:
    """S175: a SKILL.md 'What the audit covers' region naming every ALL_CHECKS
    member except one -> skill_checklist_sync YELLOW.

    The name list is built FROM ALL_CHECKS (not a hardcoded roster) so the
    fixture cannot silently diverge from the live set (S144 fixture-encodes-the-
    spec trap); the drift form drops the first member. The variant fails against
    the pre-S175 script, which has no skill_checklist_sync category and raises
    ValueError in _run_variant_check (S144 regression-test rule).
    """
    names = [name for name, _ in ALL_CHECKS]
    dropped = names[0]
    lines = chr(10).join(
        "%d. `%s` -- self-test fixture line." % (i + 1, n)
        for i, n in enumerate(names) if n != dropped
    )
    skill = (
        "## Session Bootstrap and Drift Audit" + chr(10) * 2 +
        "**What the audit covers:**" + chr(10) * 2 +
        SKILL_CHECKLIST_START + chr(10) +
        lines + chr(10) +
        SKILL_CHECKLIST_END + chr(10)
    )
    return {"files": {"SKILL.md": skill.encode("utf-8")}}


def _pedv1_files(rows: str) -> dict:
    """Fixture: an instances file whose subjects carry version/effective/
    implementation triples, for the policy_effective_date_v1 variants."""
    return _ttl(rows)



def _inverse_note_files(onto_extra: str, inst_body: str,
                       base: Optional[str] = None) -> dict:
    """Fixture: the self-test ontology stub plus inverse-bearing property
    declarations, and an instances file whose assertions the note is checked
    against.

    Corpus-fixture rule (S144): the note strings below are the phrasings the
    real ontology used, not a synthesized paraphrase of the format.
    """
    nl = chr(10)
    files = _instances_graph_to_files(rdflib.Graph())
    ontology_base = _SELF_TEST_ONTOLOGY_STUB if base is None else base
    files["GEM_ontology.ttl"] = (
        ontology_base + nl + onto_extra
    ).encode("utf-8")
    header = (
        '@prefix gem:   <http://www.cms.hhs.gov/ontology/2026/07/GEM/> .' + nl +
        '@prefix gemi:  <http://www.cms.hhs.gov/ontology/2026/07/GEM/instances/> .' + nl +
        '@prefix dc:    <http://purl.org/dc/elements/1.1/> .' + nl +
        '@prefix xsd:   <http://www.w3.org/2001/XMLSchema#> .' + nl * 2
    )
    files["GEM_policy_instances.ttl"] = (
        (header + inst_body).replace(nl, chr(13) + nl).encode("utf-8")
    )
    return {"files": files}


_INV_ONTO = (
    'gem:revisesPolicy a owl:ObjectProperty ;' + chr(10) +
    '    owl:inverseOf gem:revisedByPolicy ;' + chr(10) +
    '    gem:llmInverseNote "%s" .' + chr(10) +
    'gem:revisedByPolicy a owl:ObjectProperty .' + chr(10)
)


def _variant_92_inverse_note_baseline() -> dict:
    """The note claims the inverse is materialized and it genuinely is. -> GREEN."""
    nl = chr(10)
    onto = _INV_ONTO % (
        "Materialized both ways: gem:revisesPolicy (subject revises object) and "
        "its inverse gem:revisedByPolicy are both asserted in the data, so "
        "traverse in either direction without inference."
    )
    body = ('gemi:tnV92 gem:revisesPolicy gemi:ncdV92 .' + nl +
            'gemi:ncdV92 gem:revisedByPolicy gemi:tnV92 .' + nl)
    return _inverse_note_files(onto, body)


def _variant_93_inverse_note_false_claim() -> dict:
    """The note claims the inverse is materialized; the inverse has zero
    assertions. The pre-S197 corpus state. -> YELLOW."""
    nl = chr(10)
    onto = _INV_ONTO % (
        "Materialized both ways: gem:revisesPolicy (subject revises object) and "
        "its inverse gem:revisedByPolicy are both asserted in the data, so "
        "traverse in either direction without inference."
    )
    body = 'gemi:tnV93 gem:revisesPolicy gemi:ncdV93 .' + nl
    return _inverse_note_files(onto, body)


def _variant_94_inverse_note_understated() -> dict:
    """The note denies materialization while the inverse is in fact asserted.
    -> YELLOW (the converse drift)."""
    nl = chr(10)
    onto = _INV_ONTO % "No materialized inverse."
    body = ('gemi:tnV94 gem:revisesPolicy gemi:ncdV94 .' + nl +
            'gemi:ncdV94 gem:revisedByPolicy gemi:tnV94 .' + nl)
    return _inverse_note_files(onto, body)


def _variant_95_inverse_note_inert() -> dict:
    """No gem:llmInverseNote anywhere: the check has nothing to check with.
    Inert-precondition rule (S144) -> YELLOW, not a silent pass."""
    nl = chr(10)
    onto = ('gem:revisesPolicy a owl:ObjectProperty ;' + nl +
            '    owl:inverseOf gem:revisedByPolicy .' + nl +
            'gem:revisedByPolicy a owl:ObjectProperty .' + nl)
    body = 'gemi:tnV95 gem:revisesPolicy gemi:ncdV95 .' + nl
    # Prefix-only base: the stub carries a gem:llmInverseNote by design, and
    # this variant must present an ontology that carries none.
    bare = (
        '@prefix gem:   <http://www.cms.hhs.gov/ontology/2026/07/GEM/> .' + nl +
        '@prefix gemi:  <http://www.cms.hhs.gov/ontology/2026/07/GEM/instances/> .' + nl +
        '@prefix owl:   <http://www.w3.org/2002/07/owl#> .' + nl +
        '@prefix rdfs:  <http://www.w3.org/2000/01/rdf-schema#> .' + nl
    )
    return _inverse_note_files(onto, body, base=bare)



_DRC_ONTO = (
    'gem:PolicyGroup a owl:Class .' + chr(10) +
    'gem:HealthcareSetting a owl:Class .' + chr(10) +
    'gem:referencesPolicy a owl:ObjectProperty ;' + chr(10) +
    '    rdfs:domain gem:CMSpolicy ;' + chr(10) +
    '    rdfs:range gem:CMSpolicy .' + chr(10) +
    'gem:refersToHealthcareSetting a owl:ObjectProperty ;' + chr(10) +
    '    rdfs:domain gem:CMSpolicy ;' + chr(10) +
    '    rdfs:range gem:HealthcareSetting .' + chr(10) +
    'gem:coversProcedure a owl:ObjectProperty ;' + chr(10) +
    '    rdfs:domain gem:CMSpolicy ;' + chr(10) +
    '    rdfs:range gem:HCPCSprocedure .' + chr(10) +
    'gem:HCPCSprocedure a owl:Class .' + chr(10)
)


def _drc_files(inst_body: str, onto_extra: str = "", base: Optional[str] = None) -> dict:
    """Fixture for the domain_range_conformance variants.

    Corpus-fixture rule (S144): the declarations mirror the real ontology --
    gem:referencesPolicy really does declare domain and range gem:CMSpolicy,
    and gem:coversProcedure really does range over the externally-typed
    gem:HCPCSprocedure.
    """
    nl = chr(10)
    files = _instances_graph_to_files(rdflib.Graph())
    ontology_base = _SELF_TEST_ONTOLOGY_STUB if base is None else base
    files["GEM_ontology.ttl"] = (
        ontology_base + nl + (onto_extra or _DRC_ONTO)
    ).encode("utf-8")
    header = (
        '@prefix gem:   <http://www.cms.hhs.gov/ontology/2026/07/GEM/> .' + nl +
        '@prefix gemi:  <http://www.cms.hhs.gov/ontology/2026/07/GEM/instances/> .' + nl +
        '@prefix hcpcs: <http://purl.bioontology.org/ontology/HCPCS/> .' + nl +
        '@prefix dc:    <http://purl.org/dc/elements/1.1/> .' + nl +
        '@prefix xsd:   <http://www.w3.org/2001/XMLSchema#> .' + nl * 2
    )
    files["GEM_policy_instances.ttl"] = (
        (header + inst_body).replace(nl, chr(13) + nl).encode("utf-8")
    )
    return {"files": files}


def _variant_96_drc_baseline() -> dict:
    """Every subject and object conforms to its declaration. -> GREEN."""
    nl = chr(10)
    body = ('gemi:ncdV96 a gem:NCDpolicy ;' + nl +
            '    gem:referencesPolicy gemi:lcdV96 .' + nl +
            'gemi:lcdV96 a gem:LCDpolicy .' + nl)
    return _drc_files(body)


def _variant_97_drc_domain_violation() -> dict:
    """A gem:PolicyGroup carries gem:referencesPolicy, whose domain is
    gem:CMSpolicy. The A54969 shape, live in the corpus S58-S197. -> RED."""
    nl = chr(10)
    body = ('gemi:groupV97 a gem:PolicyGroup ;' + nl +
            '    gem:referencesPolicy gemi:lcdV97 .' + nl +
            'gemi:lcdV97 a gem:LCDpolicy .' + nl)
    return _drc_files(body)


def _variant_98_drc_range_violation() -> dict:
    """The object of gem:refersToHealthcareSetting is typed as something other
    than gem:HealthcareSetting. -> RED."""
    nl = chr(10)
    body = ('gemi:ncdV98 a gem:NCDpolicy ;' + nl +
            '    gem:refersToHealthcareSetting gemi:conceptV98 .' + nl +
            'gemi:conceptV98 a gem:PolicyGroup .' + nl)
    return _drc_files(body)


def _variant_99_drc_untyped_object() -> dict:
    """The object carries no asserted rdf:type at all: a gap, not a
    contradiction, because entailment would supply the declared type and hide
    it. -> YELLOW."""
    nl = chr(10)
    body = ('gemi:ncdV99 a gem:NCDpolicy ;' + nl +
            '    gem:referencesPolicy gemi:lcdV99 .' + nl)
    return _drc_files(body)


def _variant_100_drc_external_namespace() -> dict:
    """gem:coversProcedure ranges over gem:HCPCSprocedure, whose members are
    typed by the BioPortal conversion query and are absent from the validation
    graph. An hcpcs: object is correct and must NOT fire -- without this arm
    every code reference in the corpus is a false positive. -> GREEN."""
    nl = chr(10)
    body = ('gemi:ncdV100 a gem:NCDpolicy ;' + nl +
            '    gem:coversProcedure hcpcs:E1390 .' + nl)
    return _drc_files(body)


def _variant_101_drc_inert() -> dict:
    """No gem: property declares a gem:-namespace domain or range, so the check
    has nothing to check with. Inert-precondition rule (S144) -> YELLOW."""
    nl = chr(10)
    bare = (
        '@prefix gem:   <http://www.cms.hhs.gov/ontology/2026/07/GEM/> .' + nl +
        '@prefix gemi:  <http://www.cms.hhs.gov/ontology/2026/07/GEM/instances/> .' + nl +
        '@prefix owl:   <http://www.w3.org/2002/07/owl#> .' + nl +
        '@prefix rdfs:  <http://www.w3.org/2000/01/rdf-schema#> .' + nl
    )
    onto = 'gem:referencesPolicy a owl:ObjectProperty .' + nl
    body = 'gemi:ncdV101 gem:referencesPolicy gemi:lcdV101 .' + nl
    return _drc_files(body, onto_extra=onto, base=bare)


def _variant_88_pedv1_baseline() -> dict:
    """policy_effective_date_v1 GREEN: a version-1 individual (not a candidate)
    and a candidate whose recorded dates match KNOWN_V1_DATES exactly, including
    one whose V1 publishes no implementation date. -> GREEN.

    The matching rows are read FROM KNOWN_V1_DATES rather than hardcoded, so the
    fixture cannot silently diverge from the live table (S144 fixture-encodes-
    the-spec trap).
    """
    nl = chr(10)
    with_impl = next(k for k, v in KNOWN_V1_DATES.items() if v[1] is not None)
    without_impl = next(k for k, v in KNOWN_V1_DATES.items() if v[1] is None)
    e1, i1 = KNOWN_V1_DATES[with_impl]
    e2, _ = KNOWN_V1_DATES[without_impl]
    body = (
        'gemi:' + with_impl + ' gem:policyVersion "2" ;' + nl +
        '    gem:policyEffectiveDate "' + e1 + '"^^xsd:date ;' + nl +
        '    gem:policyImplementationDate "' + i1 + '"^^xsd:date .' + nl +
        'gemi:' + without_impl + ' gem:policyVersion "3" ;' + nl +
        '    gem:policyEffectiveDate "' + e2 + '"^^xsd:date .' + nl +
        'gemi:ncdV88v1 gem:policyVersion "1" ;' + nl +
        '    gem:policyEffectiveDate "1999-01-01"^^xsd:date .' + nl
    )
    return _pedv1_files(body)


def _variant_89_pedv1_known_mismatch() -> dict:
    """policy_effective_date_v1 YELLOW: a candidate whose V1 dates are known but
    whose recorded effective date is the wrong one -> drift, no autofix."""
    nl = chr(10)
    name = next(k for k, v in KNOWN_V1_DATES.items() if v[1] is not None)
    _, impl = KNOWN_V1_DATES[name]
    body = (
        'gemi:' + name + ' gem:policyVersion "2" ;' + nl +
        '    gem:policyEffectiveDate "2099-12-31"^^xsd:date ;' + nl +
        '    gem:policyImplementationDate "' + impl + '"^^xsd:date .' + nl
    )
    return _pedv1_files(body)


def _variant_90_pedv1_unknown_candidate() -> dict:
    """policy_effective_date_v1 INFO: a candidate absent from KNOWN_V1_DATES is
    the outstanding work queue, reported but not YELLOW."""
    nl = chr(10)
    body = (
        'gemi:lcdV90 gem:policyVersion "R7" ;' + nl +
        '    gem:policyEffectiveDate "2024-01-01"^^xsd:date .' + nl
    )
    return _pedv1_files(body)


def _variant_91_pedv1_phantom_implementation() -> dict:
    """policy_effective_date_v1 YELLOW: a candidate carrying an implementation
    date where V1 publishes none -- the manufactured value the S192 no-manufacture
    ruling forbids. The mirror of variant 88's second subject."""
    nl = chr(10)
    name = next(k for k, v in KNOWN_V1_DATES.items() if v[1] is None)
    eff, _ = KNOWN_V1_DATES[name]
    body = (
        'gemi:' + name + ' gem:policyVersion "2" ;' + nl +
        '    gem:policyEffectiveDate "' + eff + '"^^xsd:date ;' + nl +
        '    gem:policyImplementationDate "2013-01-07"^^xsd:date .' + nl
    )
    return _pedv1_files(body)


def _variant_85_workflow_header_counts_baseline() -> dict:
    """workflow_header_counts GREEN: every header's N equals the graph-wide
    (nextPlannedStep x isInEffect) count. -> GREEN."""
    nl = chr(10)
    body = (
        "# --- planDone / isInEffect=True (2 individuals) ---" + nl +
        'gemi:ncdV85a gem:nextPlannedStep gem:planDone ;' + nl +
        '    gem:isInEffect "true"^^xsd:boolean .' + nl +
        'gemi:ncdV85b gem:nextPlannedStep gem:planDone ;' + nl +
        '    gem:isInEffect "true"^^xsd:boolean .' + nl +
        "# --- planNone / isInEffect=False (1 individuals) ---" + nl +
        'gemi:ncdV85c gem:nextPlannedStep gem:planNone ;' + nl +
        '    gem:isInEffect "false"^^xsd:boolean .' + nl +
        "# --- planPromote / isInEffect=True (1 individuals) ---" + nl +
        'gemi:tnV85d gem:nextPlannedStep gem:planPromote ;' + nl +
        '    gem:isInEffect "true"^^xsd:boolean .' + nl
    )
    return _ttl(body)


def _variant_86_workflow_header_counts_drift() -> dict:
    """workflow_header_counts YELLOW: a header's N overstates the graph-wide
    count (5 claimed, 2 actual). Autofixable. -> YELLOW."""
    nl = chr(10)
    body = (
        "# --- planDone / isInEffect=True (5 individuals) ---" + nl +
        'gemi:ncdV86a gem:nextPlannedStep gem:planDone ;' + nl +
        '    gem:isInEffect "true"^^xsd:boolean .' + nl +
        'gemi:ncdV86b gem:nextPlannedStep gem:planDone ;' + nl +
        '    gem:isInEffect "true"^^xsd:boolean .' + nl
    )
    return _ttl(body)


def _variant_87_workflow_header_counts_unheaded() -> dict:
    """workflow_header_counts YELLOW: a graph combo (planRevisit/True) that no
    header covers is surfaced (non-autofixable). The present planDone header is
    correct, so the only finding is the un-headed-combo one. -> YELLOW."""
    nl = chr(10)
    body = (
        "# --- planDone / isInEffect=True (1 individuals) ---" + nl +
        'gemi:ncdV87a gem:nextPlannedStep gem:planDone ;' + nl +
        '    gem:isInEffect "true"^^xsd:boolean .' + nl +
        'gemi:ncdV87b gem:nextPlannedStep gem:planRevisit ;' + nl +
        '    gem:isInEffect "true"^^xsd:boolean .' + nl
    )
    return _ttl(body)


# --- ncd_census variants (V102-V105) -----------------------------------------
def _census_ncd(g, local, label, step, eff):
    s = GEMI[local]
    g.add((s, rdflib.RDF.type, GEM.NCDpolicy))
    g.add((s, GEM.prefLabel, rdflib.Literal(label)))
    if step is not None:
        g.add((s, GEM.nextPlannedStep, GEM[step]))
    if eff is not None:
        g.add((s, GEM.isInEffect, rdflib.Literal(eff)))


def _variant_102_ncd_census_mixed() -> dict:
    """One NCD in each bucket, exercising both lifecycle-over-workflow and the
    corroboration rule: a RETIRED planPromote (isInEffect true) counts RETIRED
    (not stub), a corroborated "Deleted" counts deleted (not unknown), and an
    active-lifecycle planNone surfaces as UNKNOWN. -> INFO naming the unknown."""
    g = rdflib.Graph()
    _census_ncd(g, "ncdV102a", "Some Covered Service (NCD V102a)", "planDone", True)      # active
    _census_ncd(g, "ncdV102b", "Some Stub (NCD V102b)", "planPromote", True)             # stub
    _census_ncd(g, "ncdV102c", "Some Service - RETIRED (NCD V102c)", "planDone", True)   # retired (extracted)
    _census_ncd(g, "ncdV102d", "Some Service - RETIRED (NCD V102d)", "planPromote", True)# retired (stub)
    _census_ncd(g, "ncdV102e", "Policy V102e Deleted", "planNone", False)                # deleted
    _census_ncd(g, "ncdV102f", "Untitled Removed Section (NCD V102f)", "planNone", True) # unknown (planNone)
    return {"files": _instances_graph_to_files(g)}


def _variant_103_ncd_census_no_unknown() -> dict:
    """A census with an empty Unknown bucket still emits the readout: the count
    block is always shown, never suppressed. -> INFO, no unknown flag."""
    g = rdflib.Graph()
    _census_ncd(g, "ncdV103a", "Some Covered Service (NCD V103a)", "planDone", True)     # active
    _census_ncd(g, "ncdV103b", "Some Stub (NCD V103b)", "planPromote", True)            # stub
    _census_ncd(g, "ncdV103c", "Some Service - RETIRED (NCD V103c)", "planDone", True)  # retired
    _census_ncd(g, "ncdV103d", "Policy V103d Deleted", "planNone", False)               # deleted
    return {"files": _instances_graph_to_files(g)}


def _variant_104_ncd_census_retired_uncorroborated() -> dict:
    """A RETIRED marker with isInEffect=false does not corroborate -> Unknown, not
    retired. Pins the S244 corroboration demotion for the retired side."""
    g = rdflib.Graph()
    _census_ncd(g, "ncdV104a", "Some Service - RETIRED (NCD V104a)", "planDone", False)  # unknown
    return {"files": _instances_graph_to_files(g)}


def _variant_105_ncd_census_deleted_uncorroborated() -> dict:
    """A Deleted marker with isInEffect=true does not corroborate -> Unknown, not
    deleted. Pins the S244 corroboration demotion for the deleted side."""
    g = rdflib.Graph()
    _census_ncd(g, "ncdV105a", "Policy V105a Deleted", "planNone", True)                 # unknown
    return {"files": _instances_graph_to_files(g)}


# --- handoff resolution / selection (V106-V108; S260) ------------------------
#
# The three pure functions behind checklist item 34. They take FILENAME LISTS
# rather than a directory precisely so the in-memory suite can reach them; only
# find_latest_handoff's two glob calls stay uncovered, and those are covered
# end-to-end by the S260 migration probe instead.
#
# All three fail against the pre-S260 script (NameError: the functions do not
# exist), verified by running both scripts over the same fixtures — the S144
# regression-test rule, which holds that a variant passing both is coverage
# rather than a regression test.


def _variant_106_handoff_select_mixed_width() -> dict:
    """Same-date pair, mixed digit width. Lexicographic picks session259
    ('2' > '0'); the numeric key picks 260. The corpus form is 5-digit (S260,
    Tom), so the fixture is built at 5 digits per the S144 corpus-fixture rule."""
    return {
        "names": [
            "GEM_Policy-Extraction_Handoff_2026-08-01_session259.md",
            "GEM_Policy-Extraction_Handoff_2026-08-01_session00260.md",
        ],
        "expect": "GEM_Policy-Extraction_Handoff_2026-08-01_session00260.md",
    }


def _variant_107_handoff_select_digit_boundary() -> dict:
    """The digit-width boundary itself: 3-digit 999 against 4-digit 1000.

    The pair is deliberately NOT the brief's `session0999` / `session1000`,
    which is a broken fixture in two ways at once: both names are four digits,
    so it crosses no width boundary, and lexicographic order returns 1000
    anyway ('0' < '1'), so it agrees with the numeric key and can witness no
    defect. The pair below diverges — lexicographic picks 999 ('9' > '1'),
    numeric picks 1000 — which is what makes it a regression test rather than
    coverage (S144). 3-digit is also the real legacy corpus form, so this pins
    width-independence against a shape the corpus actually carried."""
    return {
        "names": [
            "GEM_Policy-Extraction_Handoff_2026-08-01_session999.md",
            "GEM_Policy-Extraction_Handoff_2026-08-01_session1000.md",
        ],
        "expect": "GEM_Policy-Extraction_Handoff_2026-08-01_session1000.md",
    }


def _variant_108_handoff_resolution_both_populated() -> dict:
    """Both locations populated — unresolvable by rule, so exactly one YELLOW."""
    return {
        "sub": ["GEM_Policy-Extraction_Handoff_2026-08-03_session00260.md"],
        "flat": ["GEM_Policy-Extraction_Handoff_2026-08-01_session259.md"],
    }


_VARIANTS = [
    # --- Phase 3 variants (V1-V11; S72 Cycle 0) ----------------------------
    (
        "Variant 1 (baseline GREEN - all 4 Phase 3 checks)",
        "policyrule_all",
        _variant_1_baseline,
        [],
    ),
    (
        "Variant 2 (ruleDescription on non-PolicyRule subject -> RED)",
        "ruledescription_domain",
        _variant_2_ruledescription_domain,
        [("RED", "ruledescription_domain", "a99999")],
    ),
    (
        "Variant 3 (orphan PolicyRule -> RED)",
        "policyrule_reciprocity",
        _variant_3_orphan_policyrule,
        [("RED", "policyrule_reciprocity", "ncd210.10_r1")],
    ),
    (
        "Variant 4 (missing dc:source -> RED)",
        "policyrule_completeness",
        _variant_4_missing_dc_source,
        [("RED", "policyrule_completeness", "ncd210.10_r1")],
    ),
    (
        "Variant 5 (zero ruleDescription -> RED)",
        "policyrule_completeness",
        _variant_5_zero_rule_description,
        [("RED", "policyrule_completeness", "ncd210.10_r1")],
    ),
    (
        "Variant 6 (duplicate ruleDescription -> RED)",
        "policyrule_completeness",
        _variant_6_duplicate_rule_description,
        [("RED", "policyrule_completeness", "ncd210.10_r1")],
    ),
    (
        "Variant 7 (value-type misuse alpha -> RED)",
        "controlled_vocab",
        _variant_7_value_type_misuse,
        [("RED", "controlled_vocab", "ncd210.10_r1")],
    ),
    (
        "Variant 8 (subject-domain misuse beta -> RED)",
        "controlled_vocab",
        _variant_8_subject_domain_misuse,
        [("RED", "controlled_vocab", "ncd210.10")],
    ),
    (
        "Variant 9 (missing prefLabel -> YELLOW)",
        "policyrule_completeness",
        _variant_9_missing_pref_label,
        [("YELLOW", "policyrule_completeness", "ncd210.10_r1")],
    ),
    (
        "Variant 10 (missing ruleType -> YELLOW)",
        "policyrule_completeness",
        _variant_10_missing_rule_type,
        [("YELLOW", "policyrule_completeness", "ncd210.10_r1")],
    ),
    (
        "Variant 11 (smart-domain partial coverage -> YELLOW)",
        "policyrule_completeness",
        _variant_11_smart_domain_gap,
        [("YELLOW", "policyrule_completeness", "ncd210.10_r1")],
    ),

    # --- Pre-Phase-3 variants (V12-V33; S73 §4.11 backfill) ---------------
    (
        "Variant 12 (hash_verify baseline GREEN)",
        "hash_verify",
        _variant_12_hash_verify_baseline,
        [],
    ),
    (
        "Variant 13 (hash_verify mismatch -> RED)",
        "hash_verify",
        _variant_13_hash_verify_mismatch,
        [("RED", "hash_verify", "")],
    ),
    (
        "Variant 14 (formatting baseline GREEN)",
        "formatting",
        _variant_14_formatting_baseline,
        [],
    ),
    (
        "Variant 15 (formatting lone-LF -> RED)",
        "formatting",
        _variant_15_formatting_lone_lf,
        [("RED", "formatting", "")],
    ),
    (
        "Variant 16 (formatting tab character -> RED)",
        "formatting",
        _variant_16_formatting_tab,
        [("RED", "formatting", "")],
    ),
    (
        "Variant 17 (formatting missing terminator -> RED)",
        "formatting",
        _variant_17_formatting_no_terminator,
        [("RED", "formatting", "")],
    ),
    (
        "Variant 18 (empirical_counts baseline GREEN)",
        "empirical_counts",
        _variant_18_empirical_counts_baseline,
        [],
    ),
    (
        "Variant 19 (empirical_counts mismatch -> YELLOW)",
        "empirical_counts",
        _variant_19_empirical_counts_mismatch,
        [("YELLOW", "empirical_counts", "")],
    ),
    (
        "Variant 20 (processed_list baseline GREEN)",
        "processed_list",
        _variant_20_processed_list_baseline,
        [],
    ),
    (
        "Variant 21 (processed_list disagreement -> YELLOW)",
        "processed_list",
        _variant_21_processed_list_disagreement,
        [("YELLOW", "processed_list", "")],
    ),
    (
        "Variant 22 (uri_scheme baseline GREEN)",
        "uri_scheme",
        _variant_22_uri_scheme_baseline,
        [],
    ),
    (
        "Variant 23 (uri_scheme doc drift -> YELLOW)",
        "uri_scheme",
        _variant_23_uri_scheme_doc_drift,
        [("YELLOW", "uri_scheme", "")],
    ),
    (
        "Variant 24 (proposal_b baseline GREEN)",
        "proposal_b",
        _variant_24_proposal_b_baseline,
        [],
    ),
    (
        "Variant 25 (proposal_b Category D gap -> RED)",
        "proposal_b",
        _variant_25_proposal_b_category_d_gap,
        [("RED", "proposal_b", "ncdB")],
    ),
    (
        "Variant 26 (workflow_state baseline GREEN)",
        "workflow_state",
        _variant_26_workflow_state_baseline,
        [],
    ),
    (
        "Variant 27 (workflow_state missing nextPlannedStep -> RED)",
        "workflow_state",
        _variant_27_workflow_state_missing_step,
        [("RED", "workflow_state", "ncdFoo")],
    ),
    (
        "Variant 28 (uri_collision baseline GREEN)",
        "uri_collision",
        _variant_28_uri_collision_baseline,
        [],
    ),
    (
        "Variant 29 (uri_collision duplicate prefLabel -> YELLOW)",
        "uri_collision",
        _variant_29_uri_collision_dup_prefLabel,
        [("YELLOW", "uri_collision", "ncdFoo")],
    ),
    (
        "Variant 30 (predicate_order baseline GREEN)",
        "predicate_order",
        _variant_30_predicate_order_baseline,
        [],
    ),
    (
        "Variant 31 (predicate_order reversed -> YELLOW)",
        "predicate_order",
        _variant_31_predicate_order_reversed,
        [("YELLOW", "predicate_ordering", "")],
    ),
    (
        "Variant 32 (handoff_drift baseline GREEN)",
        "handoff_drift",
        _variant_32_handoff_drift_baseline,
        [],
    ),
    (
        "Variant 33 (handoff_drift claim mismatch -> RED)",
        "handoff_drift",
        _variant_33_handoff_drift_claim_mismatch,
        [("RED", "handoff_claim", "")],
    ),
    (
        "Variant 34 (codegroup_link_drift baseline GREEN)",
        "codegroup_link_drift",
        _variant_34_codegroup_link_drift_baseline,
        [],
    ),
    (
        "Variant 35 (codegroup_link_drift missing link -> YELLOW)",
        "codegroup_link_drift",
        _variant_35_codegroup_link_drift_missing,
        [("YELLOW", "codegroup_link_drift", "")],
    ),
    (
        "Variant 36 (proposal_b Category E superseded-revision -> GREEN)",
        "proposal_b",
        _variant_36_proposal_b_category_e_superseded,
        [],
    ),
    (
        "Variant 37 (register_section_coverage present -> GREEN)",
        "register_section_coverage",
        _variant_37_register_section_present,
        [],
    ),
    (
        "Variant 38 (register_section_coverage missing -> RED)",
        "register_section_coverage",
        _variant_38_register_section_missing,
        [("RED", "register_section_coverage", "NCD 999.9")],
    ),
    # --- llm_annotation_drift variants (V39-V40; S140) ---------------------
    (
        "Variant 39 (llm_annotation_drift baseline GREEN)",
        "llm_annotation_drift",
        _variant_39_llm_annotation_drift_baseline,
        [],
    ),
    (
        "Variant 40 (llm_annotation_drift missing entry -> YELLOW)",
        "llm_annotation_drift",
        _variant_40_llm_annotation_drift_mismatch,
        [("YELLOW", "llm_annotation_drift", "ruleType_frequency")],
    ),

    # --- Handoff-parser variants (V41-V45; S144) --------------------------
    # V41, V43 and V45 fail against the pre-S144 script by construction: each
    # covers a path where a dead parser previously reported clean.
    (
        "Variant 41 (empirical_counts stale marker, corpus title -> YELLOW)",
        "empirical_counts",
        _variant_41_empirical_counts_marker_advance,
        [("YELLOW", "empirical_counts", "empirical-counts sentence")],
    ),
    (
        "Variant 42 (empirical_counts stale marker, legacy title -> YELLOW)",
        "empirical_counts",
        _variant_42_empirical_counts_marker_advance_legacy,
        [("YELLOW", "empirical_counts", "empirical-counts sentence")],
    ),
    (
        "Variant 43 (empirical_counts session undetectable -> YELLOW)",
        "empirical_counts",
        _variant_43_empirical_counts_session_undetectable,
        [("YELLOW", "empirical_counts", "handoff title")],
    ),
    (
        "Variant 44 (handoff_drift legacy item form -> RED claim)",
        "handoff_drift",
        _variant_44_handoff_drift_legacy_item_form,
        [("RED", "handoff_claim", "")],
    ),
    (
        "Variant 45 (handoff_drift inert item parser -> YELLOW)",
        "handoff_drift",
        _variant_45_handoff_drift_inert_parser,
        [("YELLOW", "handoff_drift", "§4 item parser")],
    ),

    # --- codegroup_block_extent variants (V46-V49; S145) ------------------
    # V47 reproduces the pre-S145 corpus state (hand-authored stubs inside the
    # claimed span) and is the evidence that the guard catches the defect it
    # was written for.
    (
        "Variant 46 (codegroup_block_extent baseline GREEN)",
        "codegroup_block_extent",
        _variant_46_codegroup_block_extent_baseline,
        [],
    ),
    (
        "Variant 47 (codegroup_block_extent hand-authored content inside span -> YELLOW)",
        "codegroup_block_extent",
        _variant_47_codegroup_block_extent_intruder,
        [("YELLOW", "codegroup_block_extent", "inside block")],
    ),
    (
        "Variant 48 (codegroup_block_extent END marker missing -> YELLOW)",
        "codegroup_block_extent",
        _variant_48_codegroup_block_extent_marker_missing,
        [("YELLOW", "codegroup_block_extent", "0 END markers")],
    ),
    (
        "Variant 49 (codegroup_block_extent link statement outside span -> YELLOW)",
        "codegroup_block_extent",
        _variant_49_codegroup_block_extent_link_outside,
        [("YELLOW", "codegroup_block_extent", "outside block")],
    ),
    (
        "Variant 50 (deleted_twin_collision bare + _DELETED pair -> YELLOW)",
        "deleted_twin_collision",
        _variant_50_deleted_twin_pair,
        [("YELLOW", "deleted_twin_collision", "ncdFoo")],
    ),
    (
        "Variant 51 (deleted_twin_collision bare-only -> GREEN)",
        "deleted_twin_collision",
        _variant_51_deleted_twin_bare_only,
        [],
    ),
    (
        "Variant 52 (deleted_twin_collision retiree-only -> GREEN)",
        "deleted_twin_collision",
        _variant_52_deleted_twin_retiree_only,
        [],
    ),
    (
        "Variant 53 (manual_token baseline: 4 tokens + declared bare -> GREEN)",
        "transmittal_manual_token", _variant_53_manual_token_baseline, [],
    ),
    (
        "Variant 54 (manual_token bare URI asserting publicationNumber -> RED)",
        "transmittal_manual_token", _variant_54_manual_token_bare_with_pub,
        [("RED", "transmittal_manual_token", "tn48")],
    ),
    (
        "Variant 55 (manual_token bare + undeclared -> RED)",
        "transmittal_manual_token", _variant_55_manual_token_bare_undeclared,
        [("RED", "transmittal_manual_token", "tn10515")],
    ),
    (
        "Variant 56 (manual_token bare + 'Manual undetermined' declared -> GREEN)",
        "transmittal_manual_token", _variant_56_manual_token_bare_declared, [],
    ),
    (
        "Variant 57 (manual_token token/publicationNumber disagree -> RED)",
        "transmittal_manual_token", _variant_57_manual_token_pub_mismatch,
        [("RED", "transmittal_manual_token", "tn78CIM")],
    ),
    (
        "Variant 58 (manual_token token present, publicationNumber absent -> RED)",
        "transmittal_manual_token", _variant_58_manual_token_missing_pub,
        [("RED", "transmittal_manual_token", "tn100CIM")],
    ),
    (
        "Variant 59 (manual_token token outside controlled vocabulary -> RED)",
        "transmittal_manual_token", _variant_59_manual_token_unknown_token,
        [("RED", "transmittal_manual_token", "tn55ZZZ")],
    ),
    (
        "Variant 60 (manual_token CIM above TN 168 era gate -> RED)",
        "transmittal_manual_token", _variant_60_manual_token_cim_era_gate,
        [("RED", "transmittal_manual_token", "tn13374CIM")],
    ),
    (
        "Variant 61 (nca_uri_derivation revision-letter case drift -> RED)",
        "nca_uri_derivation", _variant_61_nca_derivation_case_drift,
        [("RED", "nca_uri_derivation", "cag00313r")],
    ),
    (
        "Variant 62 (nca_uri_derivation URI == derived from identifier -> GREEN)",
        "nca_uri_derivation", _variant_62_nca_derivation_clean, [],
    ),
    (
        "Variant 63 (doc_uri_examples dead example, *reserved* row skipped -> YELLOW)",
        "doc_uri_examples", _variant_63_doc_uri_examples_dead,
        [("YELLOW", "doc_uri_examples", "tn44NCD")],
    ),
    (
        "Variant 64 (doc_uri_examples all examples live -> GREEN)",
        "doc_uri_examples", _variant_64_doc_uri_examples_live, [],
    ),
    (
        "Variant 65 (uri_scheme docs say ncaCAG*, graph says cag* -> YELLOW)",
        "uri_scheme", _variant_65_uri_scheme_nca_doc_drift,
        [("YELLOW", "uri_scheme", "ncaCAG")],
    ),
    # --- S156 variants (V66-V67; gem:SourceAvailability) -------------------
    (
        "Variant 66 (CIM transmittal, no dc:source, no sourceAvailability -> INFO)",
        "source_availability_unverified", _variant_66_source_availability_unverified,
        [("INFO", "source_availability_unverified", "")],
    ),
    (
        "Variant 67 (every CIM transmittal resolved -> GREEN)",
        "source_availability_unverified", _variant_67_source_availability_all_resolved, [],
    ),
    (
        "Variant 68 (non-CIM transmittal with no dc:source ignored -> GREEN)",
        "source_availability_unverified", _variant_68_source_availability_non_cim_ignored, [],
    ),
    # --- S157 variants (V69-V71; literal_escape_artifact) ------------------
    (
        "Variant 69 (over-escaped quote in a literal -> YELLOW)",
        "literal_escape_artifact", _variant_69_literal_escape_artifact,
        [("YELLOW", "literal_escape_artifact", "conceptV69")],
    ),
    (
        "Variant 70 (correctly escaped quote ignored -> GREEN)",
        "literal_escape_artifact", _variant_70_literal_escape_correct_ignored, [],
    ),
    (
        "Variant 71 (escaped backslash not before a quote ignored -> GREEN)",
        "literal_escape_artifact", _variant_71_literal_escape_lone_backslash_ignored, [],
    ),
    # --- S161 variants (V72-V76; deferred_proposals_id) --------------------
    (
        "Variant 72 (deferred_proposals all valid -> GREEN)",
        "deferred_proposals_id", _variant_72_dp_baseline, [],
    ),
    (
        "Variant 73 (deferred_proposals entry missing id -> RED)",
        "deferred_proposals_id", _variant_73_dp_missing_id,
        [("RED", "deferred_proposals_id", "index 1")],
    ),
    (
        "Variant 74 (deferred_proposals duplicate id -> RED)",
        "deferred_proposals_id", _variant_74_dp_duplicate_id,
        [("RED", "deferred_proposals_id", "id 5")],
    ),
    (
        "Variant 75 (deferred_proposals invalid status -> RED)",
        "deferred_proposals_id", _variant_75_dp_invalid_status,
        [("RED", "deferred_proposals_id", "index 0")],
    ),
    (
        "Variant 76 (deferred_proposals dangling citation -> RED)",
        "deferred_proposals_id", _variant_76_dp_dangling_citation,
        [("RED", "deferred_proposals_id", "deferred_proposals[999]")],
    ),
    # --- llm_annotation_count_drift variants (V77-V78; S166) --------------
    (
        "Variant 77 (llm_annotation_count_drift baseline GREEN)",
        "llm_annotation_count_drift",
        _variant_77_llm_annotation_count_baseline,
        [],
    ),
    (
        "Variant 78 (llm_annotation_count_drift prose count overstates graph -> YELLOW)",
        "llm_annotation_count_drift",
        _variant_78_llm_annotation_count_drift,
        [("YELLOW", "llm_annotation_count_drift", "RuleType")],
    ),
    # --- revises_references_redundancy variants (V79-V80; S169) -----------
    (
        "Variant 79 (revises_references_redundancy baseline GREEN)",
        "revises_references_redundancy",
        _variant_79_revises_redundancy_baseline,
        [],
    ),
    (
        "Variant 80 (subject asserts both revises and references to same policy -> YELLOW)",
        "revises_references_redundancy",
        _variant_80_revises_redundancy,
        [("YELLOW", "revises_references_redundancy", "tn999NCD")],
    ),
    # --- description_workflow_leak variants (V81-V83; S173) ---------------
    (
        "Variant 81 (description_workflow_leak baseline GREEN)",
        "description_workflow_leak",
        _variant_81_dwl_baseline,
        [],
    ),
    (
        "Variant 82 (workflowDescription present, description absent -> RED)",
        "description_workflow_leak",
        _variant_82_dwl_wf_without_desc,
        [("RED", "description_workflow_leak", "conceptV82")],
    ),
    (
        "Variant 83 (leak marker left in description -> YELLOW)",
        "description_workflow_leak",
        _variant_83_dwl_leak_marker,
        [("YELLOW", "description_workflow_leak", "conceptV83")],
    ),
    (
        "Variant 84 (SKILL.md checklist omits an ALL_CHECKS member -> YELLOW)",
        "skill_checklist_sync",
        _variant_84_skill_checklist_drift,
        [("YELLOW", "skill_checklist_sync", "")],
    ),
    # --- workflow_header_counts variants (V85-V87; S182) -----------------
    (
        "Variant 85 (workflow_header_counts baseline GREEN)",
        "workflow_header_counts",
        _variant_85_workflow_header_counts_baseline,
        [],
    ),
    (
        "Variant 86 (WORKFLOW STATE header overstates graph-wide count -> YELLOW)",
        "workflow_header_counts",
        _variant_86_workflow_header_counts_drift,
        [("YELLOW", "workflow_header_counts", "WORKFLOW STATE")],
    ),
    (
        "Variant 87 (graph combo with no matching header -> YELLOW, no autofix)",
        "workflow_header_counts",
        _variant_87_workflow_header_counts_unheaded,
        [("YELLOW", "workflow_header_counts", "planRevisit")],
    ),
    # --- policy_effective_date_v1 variants (V88-V91; S192) ---------------
    (
        "Variant 88 (policy_effective_date_v1 baseline GREEN)",
        "policy_effective_date_v1",
        _variant_88_pedv1_baseline,
        [],
    ),
    (
        "Variant 89 (recorded dates disagree with known V1 dates -> YELLOW)",
        "policy_effective_date_v1",
        _variant_89_pedv1_known_mismatch,
        [("YELLOW", "policy_effective_date_v1", "")],
    ),
    (
        "Variant 90 (candidate with no researched V1 dates -> INFO)",
        "policy_effective_date_v1",
        _variant_90_pedv1_unknown_candidate,
        [("INFO", "policy_effective_date_v1", "")],
    ),
    (
        "Variant 91 (implementation date recorded where V1 publishes none -> YELLOW)",
        "policy_effective_date_v1",
        _variant_91_pedv1_phantom_implementation,
        [("YELLOW", "policy_effective_date_v1", "")],
    ),
    (
        "Variant 92 (inverse note true: inverse is asserted -> GREEN)",
        "inverse_note_conformance",
        _variant_92_inverse_note_baseline,
        [],
    ),
    (
        "Variant 93 (inverse note claims materialization, inverse empty -> YELLOW)",
        "inverse_note_conformance",
        _variant_93_inverse_note_false_claim,
        [("YELLOW", "inverse_note_conformance", "")],
    ),
    (
        "Variant 94 (inverse note denies materialization, inverse asserted -> YELLOW)",
        "inverse_note_conformance",
        _variant_94_inverse_note_understated,
        [("YELLOW", "inverse_note_conformance", "")],
    ),
    (
        "Variant 95 (no gem:llmInverseNote at all -> YELLOW, inert precondition)",
        "inverse_note_conformance",
        _variant_95_inverse_note_inert,
        [("YELLOW", "inverse_note_conformance", "")],
    ),
    (
        "Variant 96 (domain_range_conformance baseline GREEN)",
        "domain_range_conformance",
        _variant_96_drc_baseline,
        [],
    ),
    (
        "Variant 97 (PolicyGroup subject on a gem:CMSpolicy-domain predicate -> RED)",
        "domain_range_conformance",
        _variant_97_drc_domain_violation,
        [("RED", "domain_range_conformance", "")],
    ),
    (
        "Variant 98 (object contradicts declared range -> RED)",
        "domain_range_conformance",
        _variant_98_drc_range_violation,
        [("RED", "domain_range_conformance", "")],
    ),
    (
        "Variant 99 (object carries no asserted rdf:type -> YELLOW)",
        "domain_range_conformance",
        _variant_99_drc_untyped_object,
        [("YELLOW", "domain_range_conformance", "")],
    ),
    (
        "Variant 100 (hcpcs: object on an externally-typed range -> GREEN)",
        "domain_range_conformance",
        _variant_100_drc_external_namespace,
        [],
    ),
    (
        "Variant 101 (no gem:-namespace domain or range declared -> YELLOW, inert)",
        "domain_range_conformance",
        _variant_101_drc_inert,
        [("YELLOW", "domain_range_conformance", "")],
    ),
    # --- ncd_census variants (V102-V103; morning count) -------------------
    (
        "Variant 102 (NCD census, one per bucket incl. active-lifecycle planNone -> INFO w/ unknown flag)",
        "ncd_census",
        _variant_102_ncd_census_mixed,
        [("INFO", "ncd_census", "ncdV102f")],
    ),
    (
        "Variant 103 (NCD census, empty Unknown bucket still emits readout -> INFO)",
        "ncd_census",
        _variant_103_ncd_census_no_unknown,
        [("INFO", "ncd_census", "")],
    ),
    (
        "Variant 104 (RETIRED marker with isInEffect=false -> Unknown)",
        "ncd_census",
        _variant_104_ncd_census_retired_uncorroborated,
        [("INFO", "ncd_census", "ncdV104a")],
    ),
    (
        "Variant 105 (Deleted marker with isInEffect=true -> Unknown)",
        "ncd_census",
        _variant_105_ncd_census_deleted_uncorroborated,
        [("INFO", "ncd_census", "ncdV105a")],
    ),
    # --- handoff resolution / selection (V106-V108; S260) -----------------
    (
        "Variant 106 (same-date mixed-width pair -> selects session00260)",
        "handoff_selection",
        _variant_106_handoff_select_mixed_width,
        [],
    ),
    (
        "Variant 107 (digit-width boundary 999/1000 -> selects 1000)",
        "handoff_selection",
        _variant_107_handoff_select_digit_boundary,
        [],
    ),
    (
        "Variant 108 (handoffs in both handoffs/ and flat dir -> YELLOW)",
        "handoff_resolution",
        _variant_108_handoff_resolution_both_populated,
        [("YELLOW", "handoff_resolution", "")],
    ),
]


def _run_variant_check(ctx: dict, check_category: str) -> list[Finding]:
    """Run a single check (or all 4 Phase 3 checks for the sentinel) against
    a variant's context dict.

    The context dict must contain "files" (dict[str, bytes]); it may also
    contain "expected_hashes" (dict, default {}) and "handoff_text"
    (str | None, default None).

    Two S260 sentinel categories are handled first and take a different context
    shape, because handoff resolution is filesystem-scoped and neither of its
    functions is an ALL_CHECKS member (see run_audit's docstring). Both are
    pure-function probes over FILENAME LISTS, which is what keeps them reachable
    from an in-memory suite at all:
      "handoff_selection"  — ctx {names: list[str], expect: str}; emits a RED
                             when _select_latest_handoff picks the wrong name,
                             so the variant's expectation is "zero findings".
      "handoff_resolution" — ctx {sub: list[str], flat: list[str]}; returns
                             _handoff_resolution_findings verbatim.
    """
    if check_category == "handoff_selection":
        got = _select_latest_handoff(ctx["names"])
        if got == ctx["expect"]:
            return []
        return [Finding(
            tier="RED", category="handoff_selection",
            message=(f"_select_latest_handoff picked {got!r}; expected "
                     f"{ctx['expect']!r} from {ctx['names']!r}"))]
    if check_category == "handoff_resolution":
        return _handoff_resolution_findings(ctx["sub"], ctx["flat"])

    files = ctx["files"]
    expected = ctx.get("expected_hashes", {})
    handoff_text = ctx.get("handoff_text")

    if check_category == "policyrule_all":
        return _run_policyrule_checks_only(files)

    # Build the graph best-effort; some checks tolerate graph=None
    try:
        graph = parse_graph(files) if all(files.get(n) for n in TTL_FILES) else None
    except Exception:
        graph = None

    for name, fn in ALL_CHECKS:
        if name == check_category:
            return fn(files, graph, expected, handoff_text)
    raise ValueError(
        f"Unknown check_category {check_category!r}. "
        f"Expected one of: {[n for n, _ in ALL_CHECKS]} or 'policyrule_all'."
    )


def _finding_matches(f: Finding, expected: tuple) -> bool:
    """True if Finding f matches an (tier, category, location_substring) tuple.

    An empty location_substring skips the location check (useful for checks
    whose Findings don't set the location field, such as hash_verify and
    formatting)."""
    tier, category, location_sub = expected
    if f.tier != tier:
        return False
    if f.category != category:
        return False
    if location_sub and (f.location is None or location_sub not in f.location):
        return False
    return True


def run_self_test() -> int:
    """Run all variants. Print PASS/FAIL per variant. Return 0 on full pass, 1 otherwise."""
    # The embedded fixtures declare the frozen _SELFTEST_GEM/_SELFTEST_GEMI
    # namespace. This standalone path does not go through audit_files_dict's
    # detection, so bind the globals to the fixture namespace here (matching what
    # check_selftest_harness_integrity does) so the checks match the fixtures.
    global GEM, GEMI
    GEM, GEMI = _SELFTEST_GEM, _SELFTEST_GEMI
    label_width = max(len(label) for label, _, _, _ in _VARIANTS) + 4
    pass_count = 0
    fail_details: list[str] = []

    print()
    print("=" * 72)
    print("GEM audit self-test - check regression suite")
    print(f"  Phase 3 variants:     V1-V11  (11 variants)")
    print(f"  Pre-Phase-3 variants: V12-V33 (22 variants)")
    print(f"  S104 variants:        V34-V35 (2 variants)")
    print(f"  S120 variants:        V37-V38 (register_section_coverage)")
    print(f"  S156 variants:        V66-V68 (source_availability_unverified)")
    print(f"  S157 variants:        V69-V71 (literal_escape_artifact)")
    print(f"  S161 variants:        V72-V76 (deferred_proposals_id)")
    print(f"  S173 variants:        V81-V83 (description_workflow_leak)")
    print(f"  S182 variants:        V85-V87 (workflow_header_counts)")
    print(f"  S260 variants:        V106-V108 (handoff selection / resolution)")
    print(f"  Total:                {len(_VARIANTS)} variants")
    print("=" * 72)

    for label, check_category, builder, expected_list in _VARIANTS:
        try:
            ctx = builder()
            findings = _run_variant_check(ctx, check_category)
        except Exception as e:
            print(f"{label.ljust(label_width)} FAIL (exception during build/run: {e!r})")
            fail_details.append(f"{label}: exception {e!r}")
            continue

        # Baseline-pass case: no findings expected
        if not expected_list:
            if not findings:
                print(f"{label.ljust(label_width)} PASS")
                pass_count += 1
            else:
                print(f"{label.ljust(label_width)} FAIL (expected 0 findings, got {len(findings)})")
                for f in findings[:5]:
                    print(f"    {f.tier} {f.category}: {f.message[:80]}")
                fail_details.append(f"{label}: unexpected findings")
            continue

        # Negative-case: each expected finding must match at least one actual
        all_matched = True
        unmatched: list[tuple] = []
        for expected in expected_list:
            if any(_finding_matches(f, expected) for f in findings):
                continue
            all_matched = False
            unmatched.append(expected)

        if all_matched:
            print(f"{label.ljust(label_width)} PASS")
            pass_count += 1
        else:
            print(f"{label.ljust(label_width)} FAIL (unmatched: {unmatched})")
            print(f"    actual findings ({len(findings)}):")
            for f in findings[:8]:
                loc = f.location or "-"
                print(f"      [{f.tier}] {f.category} @ {loc}")
            fail_details.append(f"{label}: unmatched {unmatched}")

    total = len(_VARIANTS)
    print("-" * 72)
    print(f"{pass_count} of {total} variants behaved as expected.")
    if fail_details:
        print()
        print("FAILURES:")
        for d in fail_details:
            print(f"  - {d}")
        print("=" * 72)
        return 1
    print("=" * 72)
    return 0


def main() -> int:
    # The emitter owns the emitted bytes (SKILL.md §Session Close), and stdout is
    # emitted bytes like any other. Findings carry '->' arrows, section signs and
    # Greek letters; under a non-UTF-8 locale (cp1252 on a default Windows box)
    # emit_pretty dies on the first one with UnicodeEncodeError.
    #
    # The failure this prevents is worse than a plain crash: it fires AFTER the
    # "all checks GREEN" line is printed, and it exits 1 -- which this script's
    # own contract defines as "any YELLOW". A crash therefore reads as a drift
    # finding. --json was immune (json.dumps defaults to ensure_ascii=True), so
    # the healthy-looking path was the one nobody bootstraps with.
    #
    # PYTHONUTF8=1 in .claude/settings.json masked this until S260 removed it.
    # An env var is not a fix: it covers only sessions launched through that
    # settings file, on this machine. Owning the stream here covers every caller.
    for stream in (sys.stdout, sys.stderr):
        try:
            stream.reconfigure(encoding="utf-8", errors="replace")
        except (AttributeError, ValueError):
            pass  # already-wrapped or non-reconfigurable stream; not fatal

    p = argparse.ArgumentParser(description="GEM canonical-file drift audit.")
    p.add_argument("--files-dir", type=Path, default=Path("."),
                   help="Directory containing the canonical files (read-only OK).")
    p.add_argument("--output-dir", type=Path, default=None,
                   help=("Directory to write autofix-modified files to. If omitted, "
                         "modifications are written back to --files-dir in place. Use this "
                         "when --files-dir is read-only (e.g. /mnt/user-data/uploads/). "
                         "Only files actually modified by autofix are written; unchanged "
                         "files are not copied."))
    p.add_argument("--handoff", type=Path, default=None,
                   help="Handoff document. If omitted, auto-finds the latest.")
    p.add_argument("--autofix", action="store_true",
                   help="Apply mechanical-only fixes.")
    p.add_argument("--json", action="store_true", help="Emit findings as JSON.")
    p.add_argument("--self-test", action="store_true",
                   help=("Run the embedded self-test harness for Phase 3 checks "
                         "and exit. Independent of --files-dir: no canonical "
                         "files are loaded; all variants are constructed in memory."))
    args = p.parse_args()

    if args.self_test:
        return run_self_test()

    findings, files, expected, handoff_text, resolution = run_audit(
        args.files_dir, args.handoff)
    # Checklist item 34 rides on BOTH passes: audit_files_dict never sees a
    # directory, so without this the post-autofix report would silently drop it.
    findings = resolution + findings

    if args.autofix:
        applied, modified_names = apply_autofixes(findings, files)

        # Write modified files. If --output-dir is set, write there (and create
        # it if needed); otherwise write back to --files-dir in place.
        write_dir = args.output_dir if args.output_dir is not None else args.files_dir
        if args.output_dir is not None:
            args.output_dir.mkdir(parents=True, exist_ok=True)
        for name in sorted(modified_names):
            (write_dir / name).write_bytes(files[name])

        # Re-run the audit on the in-memory post-fix state. This avoids
        # re-reading from disk (which would be wrong when --output-dir is
        # set since unmodified files aren't there).
        findings2 = resolution + audit_files_dict(files, expected, handoff_text)

        if args.json:
            print(json.dumps({
                "initial_findings": [f.to_dict() for f in findings],
                "autofixes_applied": applied,
                "modified_files": sorted(modified_names),
                "write_dir": str(write_dir),
                "post_autofix_findings": [f.to_dict() for f in findings2],
            }, indent=2))
        else:
            print(f"Initial audit found {len(findings)} findings.")
            if applied:
                print(f"Applied {len(applied)} autofix(es):")
                for a in applied:
                    print(f"  • {a}")
                print(f"Wrote {len(modified_names)} modified file(s) to {write_dir}/:")
                for name in sorted(modified_names):
                    print(f"  • {name}")
            else:
                print("No autofixable findings; nothing written.")
            print()
            print("Post-autofix audit:")
            emit_pretty(findings2)
        findings = findings2  # for exit-code computation
    else:
        if args.json:
            print(json.dumps([f.to_dict() for f in findings], indent=2))
        else:
            emit_pretty(findings)

    # Exit code
    if any(f.tier == "RED" for f in findings):
        return 2
    if any(f.tier == "YELLOW" for f in findings):
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
