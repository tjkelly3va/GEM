# GEM Policy-Extraction Handoff — Session 260 (2026-08-03)

## §1 — Canonical files (post-close state)

Hashes are md5 over the frozen output set; **M** marks a file changed this session. The canonical set is **15 files**.

| File | md5 | size | S260 |
| :--- | :--- | :--- | :--- |
| `GEM_ontology.ttl` | `5a77000e27e2ce03d6e2e0596e716934` | 340257 |  |
| `GEM_policy_instances.ttl` | `646723062e55e457473f0f6e7a3cbd97` | 5575270 |  |
| `GEM_code_group_instances.ttl` | `10a70c01175dcf714a4bd8307bd07eeb` | 25942 |  |
| `cpt.ttl` | `351aa816b978ec63a6800feb50bfb5c4` | 35223 |  |
| `SKILL.md` | `8a1e6681b6667a69c868a006cdc4ec10` | 275540 | **M** |
| `gem_reference.md` | `4ddd97d8b96dec2b4aff8e0318376c46` | 120152 |  |
| `gem_rule_categories.md` | `26b9e8184ed210db35d81c023bd91a83` | 1367326 |  |
| `gem_edit_log.md` | `8e7b26c10bc37a63d146cf986ba12785` | 87487 |  |
| `gem_structured_rule_guide.md` | `5dc562fdf25cdd7a492969be2b82fee5` | 60817 |  |
| `gem_turtle_style_guide.md` | `1983054a2c8a5601ed9cbaa2c624b74f` | 24849 |  |
| `manifest_format.md` | `24d134579244454795e39b2be1ce80d3` | 26227 |  |
| `policy_worklist.json` | `6354d9e3b70868d259ca9e2f19167fed` | 322762 |  |
| `gem_llm_annotations.json` | `ae89620445889e7137e2bdc5ba4cd669` | 7213 |  |
| `worklist_schema.md` | `3f012027bb2d328e229042ed2e89b5d9` | 16002 |  |
| `gem_audit.py` | `73b3311387189997186edc1375fe1fb8` | 315654 | **M** |

## §2 — Work completed in S260

**Stage B — the Claude Chat → Claude Code port of the `policy-extraction` skill.** A transport-layer migration plus three `gem_audit.py` corrections. **No graph change**: `GEM_ontology.ttl`, `GEM_policy_instances.ttl`, `GEM_code_group_instances.ttl`, `cpt.ttl`, `policy_worklist.json`, `gem_llm_annotations.json`, `gem_reference.md`, `gem_rule_categories.md`, `gem_edit_log.md`, `gem_structured_rule_guide.md`, `gem_turtle_style_guide.md`, `manifest_format.md` and `worklist_schema.md` are all byte-identical to S259. `policies_processed` stays **159**; the cadence checkpoint stays **due at 160**; empirical counts stay **239 / 0 / 1109**; the census stays **Active 127 · Stubs 2 · Retired 10 · Deleted 5 · Unknown 0 · Total 144**. No `gem_rule_categories.md` section and no `gem_edit_log.md` entry were authored — `register_section_coverage` binds only rules-bearing `planDone` policies and this session minted none, and the edit log is scoped to corpus changes (see §3 D5).

Run as a normal two-turn pass: manifest first, thirteen borderlines resolved one at a time, then Generate.

### (a) `gem_audit.py` — three corrections

- **L214 encoding.** `parse_handoff_table` now reads `read_text(encoding="utf-8")`, matching L4151. **The brief's stated rationale did not reproduce and is corrected here** — see §3 D3.
- **Handoff resolution.** `find_latest_handoff` replaced by five constructs: `_HANDOFF_GLOB`, `_HANDOFF_SUBDIR`, `_HANDOFF_SESSION_RE`, `_handoff_sort_key`, `_select_latest_handoff`, `_handoff_resolution_findings`, and a thin `find_latest_handoff` wrapper. `handoffs/` wins when populated; the flat canonical directory is the pre-S260 fallback, so an unmigrated layout keeps working. Every decision sits in a **pure function over filename lists**, which is what makes it reachable from the in-memory self-test; only the wrapper's two `glob` calls stay uncovered by the suite, and those were probed end-to-end (§2(d)).
- **Sort key.** Primary key is the parsed session integer, so selection is width-independent and immune to date/session inversion. Any digit width parses; a name with no parseable session sorts below every name that has one.
- **Output-stream encoding (added late in the session, see §4 item 34).** `main()` reconfigures `sys.stdout`/`sys.stderr` to UTF-8 so the pretty emitter cannot die on a `→`. This is the same L214 principle applied one layer out: the script must be correct without an environment variable a future machine may not have.

**Wiring — the trap the brief flagged, and it was real.** `_handoff_resolution_findings` cannot join `ALL_CHECKS`: every member has signature `(files, graph, expected, handoff_text)` and never sees a directory. `run_audit` therefore returns it as a **fifth tuple element** and `main()` prepends it to **both** `findings` and `findings2` — because `main()`'s post-autofix pass calls `audit_files_dict` directly, and a merged finding would have vanished silently from the post-autofix report. That is the inert-default class S144 codified against. `run_audit` has exactly one caller, so the arity change is contained. Documented as checklist **item 34** inside the `AUDIT-CHECKLIST` sentinels, noting the deliberate exclusion; precedent is `selftest_harness`, which is likewise intentionally not a variant category. `skill_checklist_sync` is one-directional (`ALL_CHECKS` ⊆ region), so the extra line is safe.

**Self-test: V106–V108, suite 105 → 108, all green.** Two new sentinel categories are handled at the top of `_run_variant_check`, before it reads `ctx["files"]`, so both the `--self-test` path and `check_selftest_harness_integrity` reach them. All three were **verified to fail against the pre-edit script** (S144 regression-test rule) by loading a pristine copy as a module and calling the functions.

| # | Category | Fixture | Pre-edit behaviour |
| :--- | :--- | :--- | :--- |
| V106 | `handoff_selection` | same-date `session259` / `session00260` | `sorted()[-1]` picks **session259** — wrong |
| V107 | `handoff_selection` | `session999` / `session1000` | `sorted()[-1]` picks **session999** — wrong |
| V108 | `handoff_resolution` | `sub=[x]`, `flat=[y]` | function absent |

**V107's fixture is not the brief's.** The brief specified `session0999` / `session1000`, which is a broken fixture twice over: both names are four digits, so it crosses no width boundary, and lexicographic order returns 1000 anyway (`'0' < '1'`), so it agrees with the numeric key and can witness no defect — coverage, not a regression test. The pair used instead, 3-digit `999` against 4-digit `1000`, diverges (lexicographic picks 999) and is also the real legacy corpus form.

### (b) `SKILL.md` — transport-layer loci

`allowed-tools` added to the frontmatter (§3 D9). Canonical invocation is now `python gem_audit.py --files-dir . --autofix`, run from the canonical directory with `--output-dir` deliberately omitted. The uploads-read-only / outputs-writable split is deleted throughout §Session Close, along with the memory-#13 upload-back editor-normalization rationale — the reason for batching does not exist when no file leaves the working tree. `present_files` is replaced by close verification plus `git commit`. The Fix-A close protocol is **retained**, retargeted to the working directory. §Pre-Extraction requirement 1 no longer says to re-read this SKILL.md, which is already in context when the skill triggers. The companion-files line now names the directory and is true. Canonical count 14 → 15 with `gem_edit_log.md` added to the §Session Close enumeration (D3 of the brief) and the §1-table row count 14 → 15. §Session Close records the `handoffs/` location and the naming rule; §Session Bootstrap gains a paragraph on the `CLAUDE.md` boundary. `python3` → `python` throughout (§3 D4).

### (c) Dependencies, `CLAUDE.md`, and the docx skill

- **`requirements.txt`** at the repo root: `rdflib`, `pyshacl`, `pyyaml`, `pdfplumber`, `python-docx`. Not canonical — no §1 row, no `CANONICAL_FILES` entry. The PyYAML lazy import inside `parse_claim_blocks` **stays lazy**: it is what lets the audit run and report its other 30-odd checks when PyYAML is absent, and the failure is already loud.
- **`CLAUDE.md` §Session bootstrap had lost its command block entirely** — it read "From the canonical directory:" followed by a blank line. Restored, with the one-line `requirements.txt` reference.
- **`gem-policy-docx` ported and runtime-verified** to `.claude/skills/gem-policy-docx/{SKILL.md, scripts/gem_policy_to_docx.py}`. The port also required a **namespace fix the brief did not anticipate** — see §4 item 32. Defaults made relative, not re-hardcoded: `--files-dir` → `.`, output → cwd, with the documented invocation writing to `export/`. `present_files` removed; the verify step retargeted off `/mnt/skills/public/docx/…` to plain `soffice` + `pdftoppm`, with an explicit instruction to say the visual check was skipped rather than imply inspection. The redundant `gem-policy-docx.skill` zip (byte-identical copies of the two files) was deleted rather than committed. Both skills register — `/skills` lists `policy-extraction` and `gem-policy-docx`.

### (d) Handoff migration

`handoffs/` created under the canonical directory; S259 `git mv`'d in and renamed to the 5-digit form. Probes run against the real corpus confirmed: pre-S260 flat layout still resolves (back-compat), `handoffs/` wins when populated, and both-populated yields exactly one `handoff_resolution` YELLOW naming both counts.

**Correction to the brief's acceptance claim.** The migration is *not* "variant (a)'s scenario reproduced against the real corpus." S259 is dated `2026-08-01` and S260 `2026-08-03`, and the date prefix dominates lexicographic order, so lexicographic selection returns S260 too — the corpus cannot witness the inversion. The brief's own reasoning says mixed widths mis-select only on a **same-date** pair. What the corpus probe proves is subdir-wins, the ambiguity YELLOW, and back-compat; the lexicographic inversion is proven by **V106 alone**.

### (e) `sources/` populated — 291 policy PDFs

`sources/` had been an empty, committed-by-convention directory since the repo was created: the `.gitignore` rationale and `/gem-close` both assumed source PDFs would be there, but no commit had ever touched it, because the 159 processed policies were read in the chat environment where the PDFs lived in uploads and never crossed over.

- **291 policy PDFs copied** from `Dropbox\Projects\HOO2pilot\policies` into `sources/`, ~69 MB (commit `3288095`). **Scope was deliberately narrow**: that one directory only. Other locations on the machine hold policy PDFs — including a near-twin `OneDrive\Projects\HOO2pilot\policies` and a per-version set under `Dropbox\Projects\GEMrag\docRepository` — and are **off-limits unless Tom names them** (Tom, S260). The Dropbox originals were copied, never moved; nothing was deleted.
- **`pdffonts` triage on all 291**: 289 text-layer, **2 rasterized** — `A58824.pdf` and `NCA CAG-00296R3.pdf`, both with an empty font table, which CLAUDE.md makes unacceptable as an extraction source. Tom regenerated both; re-verified at 4 embedded fonts each and committed (`cea0295`). **`sources/` is now 291 text-layer, 0 rasterized**, so every file in it can back a reprocessing pass.
- The **Dropbox originals of those two remain rasterized** — the two directories legitimately differ on exactly those files.
- **No canonical file touched, audit unaffected.** `sources/` sits outside `CANONICAL_FILES`, `TTL_FILES` and `MARKDOWN_FILES`, and no check reads it, so its contents can never move the audit off GREEN. The §1 table is untouched by any of this.

## §3 — Decisions (S260)

Thirteen borderlines, each Tom-confirmed individually.

- **D1 (B2) — "every handoff" is the one tracked file.** The repo tracked exactly one handoff; ~250 others sit untracked in `Downloads`. Importing them is not a transport port.
- **D2 (B3) — probe before renaming; 5-digit padding.** Ordering chosen so the end-to-end probe runs while a legacy 3-digit name is still present. **Padding is 5 digits, not the brief's 4** (Tom) — `sessionNNNNN`. No code change: the parse and sort key are width-independent by construction, which is the point of doing both.
- **D3 (B5) — the L214 rationale was wrong; the fix is still right.** The brief says the missing `encoding=` "raises `UnicodeDecodeError` — a hard crash on the first check." Tested: with `PYTHONUTF8` unset, `read_text()` resolves to cp1252 and decodes the S259 handoff **without raising**, silently mojibaking non-ASCII instead. cp1252 rejects only five byte values (`0x81 0x8D 0x8F 0x90 0x9D`) and this handoff contains none; `parse_handoff_table` reads only the ASCII §1 rows, so the corruption never reaches a parsed value. The bug is **latent, not a crash**. The fix stands on the internal inconsistency with L4151 and on the silent-corruption risk. Recorded so the brief's diagnostic does not propagate.
- **D4 (B6) — `python3` → `python`.** Not on PATH on Windows.
- **D5 (B8) — no `gem_edit_log.md` entry.** Evidence, not assumption: the log's header scopes it to **corpus** changes, and every audit-script/methodology session in range — S144, S145, S156, S157, S158, S159, S175, S182, S197, S237 — has no entry, including those that added whole audit checks.
- **D6 (B4/B7/B9/B10–B13).** Handoff filename keeps the date. `CLAUDE.md` bootstrap block restored. `allowed-tools: Read, Write, Edit, Bash, Glob, Grep, WebSearch, WebFetch` — `WebSearch`/`WebFetch` because §Policy-to-Policy References makes web resolution a **required** step for a cited-policy URL not already in hand. `.skill` zip deleted; docx verify step retargeted; `python-docx` added to `requirements.txt`; plain `mv` for the untracked docx files, `git mv` only for the handoff.
- **D7 — `sources/` files are not annotated in the graph; `dc:source` is sufficient (Tom, S260).** No triple links a policy individual to the PDF in `sources/` that backed its extraction, and none is wanted: `dc:source` already carries the provenance the graph needs. The directory is a human-facing archive, not a modelled entity. This **closes the S260 §4 item** that proposed settling a `sources/` naming convention to record which rendition was read — the item is struck rather than deferred, so a future session should not re-file it. The eventual answer is a different shape entirely: **version-level policy instances, each with `dc:source` pointing at that version's own online document URL**, which makes the rendition identifiable from the graph without a filename convention. That work is weeks to months out and is not queued here.

## §4 — Open items

Items 1–31 carry from S259 **unchanged in substance**; the transport port touched no graph state, so every graph-dependent item stands exactly as S259 left it. Renumbered items below are new or materially updated.

1. **Cadence checkpoint — next DUE at 160.** `policies_processed` is **159**. **One out** — the next extraction/promotion triggers it. (S260 was a transport port and did not advance it.)
2. **LCD/Article V1-date research — 18 candidates (`[107]` remainder).** Unchanged: `a52467, a52492, a52494, a52495, a52510, a52514, a52517, a52519, a54969, a55426, a57115, a58075, lcd33612, lcd33718, lcd33797, lcd33800, lcd33923, lcd36524`. Blocked on Tom's renditions. `policy_effective_date_v1` INFO = **24**.
3. **CIM stub source availability — 42.** Unchanged. `tn33CIM` (S259) and `tn159CIM` (S249) both expected to stay Source-pending.
4. **Possible era-gate mistokens among pre-crystallization transmittals (S236); CIM ceiling 169 (S247).** Pending Tom.
5.–13. **Referenced-document stubs** from NCD 220.5 (S251, five), NCD 220.13 (S249, five), NCD 210.4 (S248, five), NCD 110.23 (S247, thirty-five), NCD 90.2 (S246, sixteen), NCD 20.33 (S245, twelve), NCD 40.1 (S243, twelve), and prior NCDs S234–S259. All `planPromote`. Item 11 (NCD 20.14, S244) remains RESOLVED and untracked.
14.–30. **Carry unchanged from S259**: `gem_reference.md` implementation-date clarification (S240); credential-URI consolidation (S222); setting-URI consolidation (S238); `gemi:pub100_02_ch2` prefLabel (S221) and `pub100_04_ch32` title-free (S237); `# Extracted:` banner sweep-or-bless (S237); reused-transmittal internal-edge retrofit (S242); promote-queue stubs `gemi:ncd20.4`, `gemi:ncd210.3`, retired-in-place `gemi:ncd280.13` (S214–S241); `[87]` transmittal-content validation; the § verbatim rule undocumented in `gem_turtle_style_guide.md` (S241); KNOWN_V1_DATES nudges; NCD census documentation doc (S244); cross-reference/pure-pointer NCD shape (S243/S254); registered patterns; namespace auto-detection (S255); `gem_edit_log.md` S245-at-top ordering anomaly (S255); `register_section_coverage` message wording (S255).
31. **Plan-turn reuse-search hygiene (S259).** Unchanged. Pending Tom's call on promoting a one-line rule into `SKILL.md` §Clinical Concepts.
32. **RESOLVED (S260) — `gem-policy-docx` runtime verified, after a namespace fix.** No longer tracked. The first real run surfaced a defect static verification could not: the script **hardcoded the `2026/07` namespace**, which the corpus left at S255. Under it every `gem:` query returned zero rows — 0 `gem:identifier` triples against 881 under `2026/08` — and zero rows is indistinguishable from "no such policy", so the script exited advising *"Check the identifier (exact match only)"* for an identifier that was correct, and would have done so for **every** policy. Fixed by porting `gem_audit.py`'s Option-B runtime detection: `detect_gem_namespace` reads the parsed graph's own prefix bindings, `bind_gem_namespace` rebinds and **rebuilds the two GEM-derived module constants** (`POLICY_IDENTITY_PREDS`, `SUPPRESS_PREDS` — built inside a function precisely because a `GEM.`-qualified URIRef captured at import freezes the namespace and makes a later rebind look successful while doing nothing), and `main()` binds before the first query, with an explicit exit distinguishing a namespace mismatch from an identifier miss. Verified end-to-end: `NCD 30.3` → `export/NCD_30.3.docx`, 83 paragraphs, 3/3 rule texts present, triples appendix rendered, and the one `gem:workflowDescription` triple on `ncd30.3` correctly **absent** (a non-vacuous check — the triple exists).
33. **SKILL.md progressive-disclosure split — still deferred.** By agreement it did not ride along with a transport port; it touches `CANONICAL_FILES`, the `skill_checklist_sync` sentinels, and the §1 table. `SKILL.md` is ~275 KB and is loaded in full on every trigger.
34. **RESOLVED (S260) — `PYTHONUTF8=1` removed from `.claude/settings.json`; the audit now owns its output stream.** No longer tracked. Removing the env var revealed it was **load-bearing, not belt-and-braces**: with stdout at cp1252, `emit_pretty` died on the first `→` in the handoff annotations — `UnicodeEncodeError: 'charmap' codec can't encode character '→'` at L4305. Three bad properties: it fired **after** the "all checks GREEN" line printed; it exited **1**, which this script's own contract defines as "any YELLOW", so a crash read as drift; and `--json` was immune (`json.dumps` defaults `ensure_ascii=True`), so the healthy-looking path was the one nobody bootstraps with. Fixed by reconfiguring `sys.stdout`/`sys.stderr` to UTF-8 (`errors="replace"`) at the top of `main()` — the §Session Close **emitter contract** applied to stdout rather than to a `.ttl`: an env var covers only sessions launched through one settings file on one machine, while owning the stream covers every caller. File IO was never at risk; every `read_text`/`write_text` in both scripts already names `encoding=`, verified before removal. Re-verified with `PYTHONUTF8` unset and `-X utf8=0`: audit renders all 13 arrows with empty stderr, `--self-test` **108/108** exit 0.

35. **`sources/` gitignore question — raised and deliberately deferred (S260).** Tom asked for `sources/` to be excluded from pushes, then withdrew it pending a decision ("until I decide to ignore the sources directory"), so **the directory remains tracked**. If it is ever adopted, three places assert the opposite and must change **together**: `.gitignore`'s comment block (which explains at length why `sources/` is deliberately *not* ignored), `SKILL.md` §Session Close, and `/gem-close` step 6. Note also that ignoring it means git stops tracking the PDFs entirely — no history, no protection against an overwrite — and that the repo currently has **no remote** while the standing rule is *never push*, so nothing is reaching GitHub today regardless.
36. **Two `sources/` files differ from their Dropbox originals (S260).** `A58824.pdf` and `NCA CAG-00296R3.pdf` are text-layer in `sources/` and still rasterized in `Dropbox\Projects\HOO2pilot\policies`. Expected, not drift — but a future sync or re-copy from Dropbox would silently reintroduce the rasterized versions.

---

## §5 — Plan for S261

### §5.1 — Bootstrap (auto-authorized)

From the canonical directory, read the latest handoff in `handoffs/`, then run `python gem_audit.py --files-dir . --autofix` immediately on the first prompt, without asking. Dependencies are in `requirements.txt` at the repo root. Expect a clean run with **no autofix write**, two INFO (`source_availability_unverified` **42**; `policy_effective_date_v1` **24**), plus the always-on **`[NCD CENSUS]`** block (Active 127 · Stubs 2 · Retired 10 · Deleted 5 · Unknown 0 · Total 144). Any RED is a halt; surface YELLOW for decision.

**Fifteen simultaneous `hash_verify` YELLOWs** reading "present but not listed in handoff §1 table" is one cause, not fifteen problems: no handoff was resolved. `handoff_drift` and the `empirical_counts` session marker are silently inert in that state. Fix resolution first. A `handoff_resolution` YELLOW (item 34) means handoffs exist in both `handoffs/` and the flat canonical directory — move or delete the flat copies.

### §5.2 — First action

**Cadence checkpoint is due at 160 — one out**, so the next new extraction or promotion triggers the 20-policy checkpoint review. No forced order otherwise: process the next policy; promote a `planPromote` stub through its own Plan/Generate cycle (items 5–13, 21, incl. `gemi:ncd20.4` and `gemi:ncd210.3`); or advance a §4 item — items 32 and 34 are both cheap and both new.

### §5.3 — Do not

- `policies_processed` is **159** — advance it only on a genuine new extraction/promotion.
- Do not re-hardcode the audit namespace — detection is deliberate (Option B, S255).
- Do not re-add the frozen `LLM_ANNOTATED_VOCAB_CLASSES` tuple — edit `_LLM_ANNOTATED_VOCAB_LOCALNAMES` when a vocab family is added.
- Do not promote the PyYAML lazy import to module level — it is what keeps a PyYAML-less run useful.
- Do not split `SKILL.md` without agreement (item 33).
- `owl:versionInfo`, the `# Produced:` header date, and Tom-supplied `dc:source` URLs remain untouched.
- **Do not reprocess any already-extracted NCD until every NCD is processed (Tom, S260).** Forward progress on unprocessed NCDs takes priority over revisiting finished ones; reprocessing resumes only once the NCD corpus is complete. This is a standing constraint, not an S261-only one — carry it forward. It **supersedes any individual reprocessing flag already on the books**, including `SKILL.md`'s standing note that *"NCD 240.2 R1 carries the un-rejoined `long- term` form and is flagged for a verbatim-review check"* (S102, line-wrap de-hyphenation). That flag stays where it is and stays unactioned; do not surface it as available work. Enrichment of an *unfinished* policy, and promotion of a `planPromote` stub through its own Plan/Generate cycle, are not reprocessing and are unaffected.
- **Do not delete anything from `sources/`, and do not delete the Dropbox originals** (Tom, S260). Deletions happen only on an explicit request naming the files — and are not to be volunteered, suggested, or made convenient.
- **Do not read other policy-PDF locations.** `Dropbox\Projects\HOO2pilot\policies` is the sanctioned source directory; `OneDrive\Projects\HOO2pilot\policies`, `Dropbox\Projects\GEMrag\docRepository` and any others are off-limits unless Tom names them.
- Never push to a remote.
