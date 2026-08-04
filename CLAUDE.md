# GEM — Global Edit Model

RDF/Turtle knowledge graph extracting CMS Medicare NCD/LCD/Article/Transmittal
policy content. GEM identifies which policies apply to a claim and documents the
rules for evaluating it. GEM does **not** evaluate claims.

## Authority

`.claude/skills/policy-extraction/SKILL.md` is the methodology authority for
everything below. This file is a pointer, not a summary — where the two appear to
disagree, SKILL.md wins and this file is the bug.

Canonical directory: `.claude/skills/policy-extraction/` — all 15 canonical files
live there, flat. The audit resolves the handoff document itself; see SKILL.md
§Session Bootstrap.

## Session bootstrap (auto-authorized — run without asking)

From the canonical directory — read the latest handoff in `handoffs/`, then:

    python gem_audit.py --files-dir . --autofix

Dependencies are declared in `requirements.txt` at the repo root.

Report the outcome, then ask which §4 open item from the latest handoff is first.
Do not pause between reading the handoff and running the audit.

**Halt rule.** Any RED halts the session for human reconciliation. Surface YELLOW
for decision. INFO is a work queue, not a finding.

Fifteen simultaneous `hash_verify` YELLOWs reading "present but not listed in
handoff §1 table" is one cause, not fifteen problems: no handoff was resolved.
`handoff_drift` and the `empirical_counts` session marker are silently inert in
that state. Fix the handoff resolution before trusting any other finding.

## Working rules

- **Two-turn discipline.** Plan (manifest + borderlines) → Tom confirms →
Generate. No file edits before confirmation.
- **Accuracy over speed.** Ask rather than struggle.
- **Terse.** Work silently through tool calls. Surface decisions, questions, and
results only. No narration.
- Source PDFs are in `sources/`, text-layer only. Diagnose with `pdffonts`; an
empty font table means rasterized, which is not acceptable as a source.
- `export/` is a delivery drop for GraphDB/Dropbox. It is gitignored and is never
read back as input.

## Never touch

`owl:versionInfo`, the `# Produced:` header date, and Tom-supplied `dc:source`
URLs. Do not edit, flag, analyze, or propose changes to any of them.

## Version control

`git` is the undo. Commit at session open; `git diff` is the review; `git checkout -- .` reverts. Session close commits via `/gem-close`. Never push to a remote.



