---
name: gem-policy-docx
description: >-
  Export a single GEM (Global Edit Model) Medicare policy to a Microsoft Word
  (.docx) readout, given a policy identifier such as "NCD 30.3", "NCD 190.3",
  "L33718", or "A52519". Use this skill WHENEVER the user wants a Word document,
  .docx, or "write-up" of a GEM policy, or asks to export / dump / print / render
  a policy and its rules, or wants to see a policy's gem:NCDpolicy individual
  together with its gem:PolicyRule, gem:PolicyGroup, and gem:PolicyCodingRule
  instances — even if they don't say "docx" explicitly but ask for a policy in
  Word format or a shareable policy document. Do NOT use it for extracting new
  policies into the graph (that is the policy-extraction skill), for spreadsheets,
  or for PDFs.
---

# GEM Policy → Word (.docx)

Turn one policy identifier into a professional Word document that reads out the
policy individual and everything hanging off it that the user cares about:

- the **policy** individual (`gem:NCDpolicy` / any `gem:CMSpolicy`) as a curated
  readout — identity, dates, publication, benefit categories, clinical concepts,
  provider credentials, healthcare settings, and outbound references;
- its **policy rules** (`gem:hasPolicyRule` → `gem:PolicyRule`);
- any linked **Policy Groups** (`gem:hasPolicyGroup` → `gem:PolicyGroup`), with
  their ICD-10 / HCPCS code anchors;
- any linked **Policy Coding Rules** (`gem:hasPolicyCodingRule` →
  `gem:PolicyCodingRule`), with their code anchors and nested rules.

## How to run

The whole job is done by the bundled script. Do **not** hand-build the document.

Run from the repo root:

```bash
python .claude/skills/gem-policy-docx/scripts/gem_policy_to_docx.py \
    --identifier "NCD 30.3" \
    --files-dir .claude/skills/policy-extraction \
    --output export/NCD_30.3.docx
```

Then tell the user the path. `export/` is the delivery drop for GraphDB/Dropbox —
it is gitignored and never read back as input, which is exactly what a generated
readout wants.

- `--identifier` (required): the policy number exactly as it appears in the
  graph's `gem:identifier`, e.g. `"NCD 30.3"`. Matching is whitespace-collapsed
  and case-insensitive, so `ncd 30.3` also resolves, but it is otherwise **exact**
  (see decisions below).
- `--files-dir` (optional, default `.`): the directory holding the GEM `.ttl`
  files — the canonical directory, `.claude/skills/policy-extraction/`. The
  script loads `GEM_policy_instances.ttl`, `GEM_code_group_instances.ttl`, and
  `cpt.ttl` if present; if none are found it parses every `.ttl` in the
  directory. The default is relative, so invoking from inside the canonical
  directory needs no flag.
- `--output` (optional): output path. If omitted, a filename is derived from the
  identifier and written to the current directory. Prefer passing `export/…`
  explicitly rather than relying on the default.

The script prints a one-line summary (rule / group / coding-rule counts) so you
can sanity-check the result before presenting it.

## Verify before reporting

Render the first page and read it — the script's one-line summary confirms the
counts, not that the document renders:

```bash
soffice --headless --convert-to pdf --outdir export export/NCD_30.3.docx
pdftoppm -jpeg -r 100 export/NCD_30.3.pdf export/page && ls export/page-*.jpg
```

LibreOffice (`soffice`) and `pdftoppm` are optional local tools, not declared in
`requirements.txt`. Where neither is installed, say the visual check was skipped
rather than implying the output was inspected.

## Baked-in design decisions (confirmed by Tom, S235)

These are already implemented in the script; keep them unless Tom changes them.

1. **Exact identifier match only.** `"NCD 30.3"` resolves the 30.3 individual
   and does **not** pull in descendant sections 30.3.1 / 30.3.2 / 30.3.3 — those
   are distinct policies. To export a child section, pass its own identifier.
2. **Nested rules are included.** `gem:hasPolicyRule` can hang off a Policy Group
   or a Policy Coding Rule (its domain is the union of `gem:CMSpolicy` and
   `gem:AnchoredCodingScope`), not just the policy. Those nested rules are rendered
   under their parent scope ("Rules on this scope").
3. **The policy individual is a curated readout.** `gem:workflowDescription` (the
   internal extraction/audit narrative) is intentionally omitted; `gem:description`
   (the plain-language policy summary) is kept.

## What the document contains

Section order, always:

```
<prefLabel>                       (title)
<identifier> · <type>             (subtitle)

Policy                            identity table + gem:description
  Attributes & references         grouped object properties (benefit categories,
                                  clinical concepts, credentials, settings,
                                  references, change requests, …)
Policy rules                      each rule: label, rule type(s), description
                                  ("None." if the policy has no direct rules)
Policy groups                     each group: label, description, code anchors,
                                  nested rules   ("None." if absent)
Policy coding rules               each coding rule: label, description, code
                                  anchors, nested rules   ("None." if absent)

  ── page break ──
RDF triples (Turtle)              complete triple set, indented Turtle (below)
```

### Triples appendix (new page)

After all of the above, on a fresh page, the document lists the triple set for
the policy as indented Turtle. This is the raw view of the graph. `gem:workflowDescription`
triples are **omitted throughout** (internal extraction narrative the readout
audience does not need); every other triple is shown. Indentation reflects nesting:

- the **policy** individual at depth 0 (predicates indented 4 spaces, `a` first,
  `dc:source` last, house Turtle conventions for literals);
- its **rules, groups, and coding rules** nested one level in (subject at 4 spaces);
- **rules on a group or coding rule** nested one level deeper (subject at 8 spaces).

Each subject is emitted once. Literals follow Turtle style (`"…"^^xsd:date`,
`"true"^^xsd:boolean`, bare integers); external codes use the `icd10:` / `hcpcs:` /
`cpt:` prefixes. The block is set in a monospace font with leading whitespace
preserved, so the indentation renders faithfully in Word.

Most NCDs (e.g. NCD 30.3) have policy rules but **no** groups or coding rules, so
those two sections routinely read "None." — that is expected, not an error. Policy
Groups and Coding Rules mostly appear on Articles/LCDs; the skill renders them
whenever present regardless of policy type.

## Code rendering

External code URIs are rendered as `CODE (System)` — e.g. `J95.00 (ICD-10-CM)`,
`A4605 (HCPCS)`, `12345 (CPT)`. AMA CPT long descriptors are never reproduced;
only the code itself is shown.

## Edge cases

- **No match** → the script exits with an error naming the identifier. Re-check
  the exact `gem:identifier` spelling (it lives on the policy individual).
- **Multiple matches** → the script exits and lists the colliding subjects (should
  not happen with well-formed data; surface it rather than guessing).
- **Non-NCD identifiers** (LCD `L…`, Article `A…`) resolve too; the readout adapts
  to whatever properties the individual carries.

## Dependencies

`rdflib` and `python-docx` (both preinstalled in the GEM environment; if missing,
`pip install rdflib python-docx --break-system-packages`). Verification uses
LibreOffice (`soffice`) and `pdftoppm`.
