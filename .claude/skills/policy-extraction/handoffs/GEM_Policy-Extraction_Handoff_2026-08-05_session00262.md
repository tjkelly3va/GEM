# GEM Policy-Extraction Handoff — Session 262 (2026-08-05)

## §1 — Canonical files (post-close state)

Hashes are md5 over the frozen output set; **M** marks a file changed this session. The canonical set is **15 files**.

| File | md5 | size | S262 |
| :--- | :--- | :--- | :--- |
| `GEM_ontology.ttl` | `5a77000e27e2ce03d6e2e0596e716934` | 340257 |  |
| `GEM_policy_instances.ttl` | `feda26e321b3fa725f550ffef5807000` | 5789156 | **M** |
| `GEM_code_group_instances.ttl` | `10a70c01175dcf714a4bd8307bd07eeb` | 25942 |  |
| `cpt.ttl` | `351aa816b978ec63a6800feb50bfb5c4` | 35223 |  |
| `SKILL.md` | `54b8350a1b01c495d5de72a2eeff2074` | 281863 | **M** |
| `gem_reference.md` | `4ddd97d8b96dec2b4aff8e0318376c46` | 120152 |  |
| `gem_rule_categories.md` | `10485733e4677d7fbbdba1fa1148c0cc` | 1438135 | **M** |
| `gem_edit_log.md` | `f7188cbad1df1718d570b55a7d75b9b7` | 116936 | **M** |
| `gem_structured_rule_guide.md` | `5dc562fdf25cdd7a492969be2b82fee5` | 60817 |  |
| `gem_turtle_style_guide.md` | `0c82c21cb54232de2c731fb1dcfce117` | 26524 |  |
| `manifest_format.md` | `24d134579244454795e39b2be1ce80d3` | 26227 |  |
| `policy_worklist.json` | `129ca56db5c5d3f56fed01f6ec6d2e5e` | 322732 | **M** |
| `gem_llm_annotations.json` | `ae89620445889e7137e2bdc5ba4cd669` | 7213 |  |
| `worklist_schema.md` | `2519964abbdba260c621a6a5e9f8318b` | 16521 |  |
| `gem_audit.py` | `bbe90fd1543e9a13bbabd7b227a7c7f7` | 331321 | **M** |

## §2 — Work completed in S262

**Six extractions**, one audit-check repair, a permissions overhaul, and four in-place corrections to prior handoffs. No schema change: `GEM_ontology.ttl` is **byte-identical**.

**Graph movement:** `policies_processed` **164 → 170**; `referencesPolicy` **1122 → 1149**; `revisesPolicy` **242 → 248**; `revisedByPolicy` stays **0**. Instances triples **51,781 → 52,587** (+806). Workflow state `planDone` **164 → 170**, `planPromote` **709 → 720**, `planNone` 16. NCD census **Active 131 → 135, Stubs 2 → 4, Retired 11 → 13, Total 149 → 157** (Deleted 5, Unknown 0). `source_availability_unverified` **42 → 43**; `policy_effective_date_v1` unchanged at **24**. Self-test **111 → 112**.

### (a) The six extractions

| Policy | Rules | Concepts | Refs / new stubs | Δ |
| :--- | ---: | :--- | :--- | ---: |
| **NCD 30.4** Electrosleep Therapy - RETIRED | 1 | 1 mint | 2 / 1 (`tn10838NCD`) | +44 |
| **NCD 160.15** Electrotherapy for Facial Nerve Paralysis | 2 | 11 mint, 2 reuse | 0 / 0 | +108 |
| **NCD 100.2** Endoscopy | 2 | 8 mint, 0 reuse | 0 / 0 | +86 |
| **NCD 160.9** EEG Monitoring During Open-Heart Surgery - RETIRED | 1 | 0 | 2 / 0 | +27 |
| **NCD 80.8** Endothelial Cell Photography | 3 | 19 mint, 1 reuse | 3 / 3 | +207 |
| **NCD 110.21** ESAs in Cancer and Related Neoplastic Conditions | 9 | 21 mint, 12 reuse | 29 / 7 | +334 |

All six were minted direct to the graph; **none was ever worklisted**. Full decision registers in `gem_rule_categories.md`; one `gem_edit_log.md` line each.

**Two `KNOWN_V1_DATES` rows added** — `ncd30.4` and `ncd160.9`, both `("1966-01-01", None)`. S262 is the S260 D8 standing step's **first and second live exercises**; the four V1 policies correctly owe nothing.

**Polarity, and the finding that reversed a recommendation (§3 D6).** NCD 110.21 §B's stem is *conjunctive*, so NCD 80.8's disjunctive fold did not apply, and bullets 4 and 5 each pair a positive statement with an embedded *"not reasonable and necessary"* clause. The Plan proposed **splitting** them into single-polarity rules. **Tom asked whether the corpus already had a pattern, and it does**: of 1,946 rules, **18 carry `coverageScope` and `nonCoverage` on the same individual**, four of them structurally identical — `lcd33612_r15`, `a55426_r66`, `lcd33718_r28`, `lcd33612_r1`, each a *covered-when-X / denied-when-Y* pair kept whole. The settled practice is to keep the conditional with its complement and dual-type; R5 and R6 do. **The split would have been the corpus's first departure from that shape.** Note the 183 adjacent opposite-polarity *sibling* pairs are a different phenomenon (separate source statements → separate rules) and would have looked like support for splitting if the headline number were taken alone.

**Two folds, measured not judged.** NCD 80.8 R2 folds seven criteria and NCD 110.21 R8 folds eight, both on the `ncd190.14_r1` precedent (25 findings in one 2,032-char rule). NCD 100.2 R2 takes `coverageScope` **without** `statutoryFraming`: of 199 corpus rules using *"reasonable and necessary"*, 173 cite no statute and exactly **one** carries the tag — the tag tracks a **citation**, not the phrase.

**Two era/identity calls.** NCD 160.9's title is misspelled by CMS in every Manual Section Title field (*"Electro**n**ecephalographic"*) while its own V3 body spells it correctly; `prefLabel` carries the corrected form and the published misspelling is preserved **verbatim inside `gem:description`** (§3 D4). NCD 80.8's TN 61 is a **CIM** transmittal, `tn61CIM`, minted distinct from the pre-existing `tn61NCD` — the era gate plus the CIM's monotonic dated series (`tn59CIM` 07/1992, `tn60CIM` 08/1992) (§3 D5).

### (b) `check_predicate_ordering` repaired (§3 D7)

The check scanned raw lines and matched `dc:source` **inside string literals**, reporting a misplaced triple on `gemi:ncd10.1` and `gemi:ncd80.7`, which have none. **194 corpus `workflowDescription` literals already mention the term**; the bug bites whenever a block has no real `dc:source` but explains why — the shape of every stub minted without a URL. Fixed by blanking Turtle literals before locating predicates. **V112** pins it, and the S144 regression rule was verified properly: the fixture **FIRES** `YELLOW/predicate_ordering` against the pre-edit script and is GREEN against the fixed one.

### (c) Permissions (§3 D8)

Measured 28 transcripts: Bash was already broadly allowed, and the recurring prompts were **Edit (213), Write (104) and Read (115)** — none of which had any path rule. `.claude/settings.json` gained the per-policy invariant paths; `.claude/settings.local.json` was pruned from **37 one-shot rules to 1**, several containing dead session UUIDs. `Bash(git fetch:*)` was later narrowed to `Bash(git fetch)` after a background review correctly noted that `--upload-pack=<cmd>` is arbitrary code execution.

### (d) Four in-place corrections to prior handoffs (§3 D9)

At Tom's request, and each with a dated note preserving the original wording:

- **S260 §5.2 and S261 §5.2** — the NCD queue read "two policies"; it was **three**, `gemi:ncd280.13` having carried `planPromote` at both sessions' own close commits. Root cause: the audit's `[NCD CENSUS]` **`Stubs`** line was read as the promote queue, but `ncd_census` tests **lifecycle before workflow**, so a `planPromote` NCD with a `- RETIRED` prefLabel is counted under **Retired**. **S260 contradicts itself** — its §4 items 14–30 correctly enumerate all three.
- **S260 and S261 §4 item 41** — reframed from *"no denominator, this gates 'all NCDs are processed'"* to *"the NCD queue is not the NCD corpus"*; completion is not the target (§4 item 41).
- **S261 §4 item 39** — marked RESOLVED; the promote-queue ratio is phase ordering, not a measurement gap.

Handoffs are **not** canonical files and the audit opens only the latest, so amending old ones is inert to every check — correcting an earlier claim of mine that it would produce a spurious `hash_verify` RED.

### (e) No edit-log entry for (b), (c) or (d)

Per S260 D5, `gem_edit_log.md` is scoped to corpus changes.

## §3 — Decisions (S262)

- **D1 (NCD 30.4 B1) — no benefit category asserted (Tom).** V1 listed Physicians' Services; live V3 lists *"No Benefit Category"*. Capture-current-version-metadata-only governs. **First TN 11892 sibling to carry zero** — `ncd160.22` and `ncd180.2` each *round-trip* back to their original category at V3, which is the trap. Promoted to `SKILL.md` §Extraction Taxonomy the same session, with the round-trip warning as the load-bearing half.
- **D2 (NCD 30.4 B2) — V1's content removed, not retained (Tom).** V2 reports the removal and V3 carries no Item/Service Description at all. **The legible contrast is `ncd160.22`**, whose description survives *on the live version* and is kept: the test is what the live version carries, not which retirement verb CMS used.
- **D3 (NCD 160.15 B1–B4; NCD 100.2 B1–B3; NCD 80.8 B2–B4) — concept-minting calls.** Composite plus both single terms where the source names all three; bare entities minted where the corpus already holds 18 bare-anatomy and 8 bare-mechanism individuals; anaphoric qualifiers dropped (*"affected"* facial muscle) and defining ones kept (*"uncontrolled"* hypertension, *"small portable"* generator). Bare terms that exist but are **not independently named** are deliberately not linked — `conceptEndothelialCell`, `conceptHypertension`, `conceptLeukemia`, `conceptErythropoietin`, `conceptMyelofibrosis`, `conceptEndStageRenalDisease`.
- **D4 (NCD 160.9 B1) — CMS misspells its own section title (Tom).** `prefLabel` takes the **corrected** spelling; the published misspelling is preserved **verbatim in `gem:description`**. Tom's own framing, not one of the three options put to him — and better, because it needs no alternate-label schema term. The corpus's first title-vs-body spelling conflict.
- **D5 (NCD 80.8 B1) — TN 61 is a CIM transmittal (Tom).** `tn61CIM` minted distinct from `tn61NCD`. A live instance of §4 item 4's era-gate question.
- **D6 (NCD 110.21, §B granularity) — mixed polarity stays in one dual-typed rule (Tom, standing).** See §2(a). **Carry this forward:** when a single source unit says *covered under X / not covered under Y*, keep it whole and dual-type it. Established by 18 existing rules and four exact-shape precedents.
- **D7 — a check that misfires gets repaired, not worked around (Tom).** See §2(b). The D12 idiom from S261.
- **D8 — allowlist the per-policy invariants; prune dead permission rules (Tom).** See §2(c).
- **D9 — correct prior handoffs in place, preserving the original wording (Tom).** See §2(d).

## §4 — Open items

Items 1–44 carry from S261 unless restated.

1. **Cadence checkpoint — next at 200.** `policies_processed` is **170**; 30 out. Not due.
2. **LCD/Article V1-date research — 18 candidates.** `policy_effective_date_v1` INFO = **24**, unchanged; the "already confirmed" tally rose by two on the new `KNOWN_V1_DATES` rows.
3. **CIM stub source availability — 43** (was 42; `tn61CIM` joined, pre-2000 CIM with no rendition URL).
4. **Era-gate mistokens among pre-crystallization transmittals.** **Exercised this session** at NCD 80.8 (D5) with a clean corroborating series. The general sweep is still pending Tom.
5.–38. **Carry unchanged.** Items 37, 38 and 40 remain cheap and pending.
39. **RESOLVED (S262).** Promote-queue ratio needs no instrumentation — phase ordering. Now 720 `planPromote` against 170 `planDone`.
41. **REFRAMED (S262).** The NCD queue is not the NCD corpus; completion is not the target; an authoritative list, if ever useful, is for **change detection** (item 44).
42. **Sort-guard tiers still exercised only against the instances file.** Unchanged.
43. **The census `Stubs` bucket is not the promote queue.** Restated with the S260/S261 corrections applied. **Query `gem:nextPlannedStep gem:planPromote` on `gem:NCDpolicy` directly, with rdflib** — a line-anchored regex over the TTL undercounts badly (it returned 423 of the true 710 `planPromote` subjects, and 96/316 revision targets for two transmittals, by over-running block terminators into prose inside `workflowDescription` literals). **That trap fired twice in this session alone.**
44. **Policy-change management is named future work (Tom).** Unchanged.

45. **NEW (S262) — `sources/NCD 100.4.pdf` is on hand and unextracted.** It appeared during the close fetch, after the library had been reconciled. `gemi:ncd100.4` is absent from the graph. **This is the third time in one session that a "sources/ is fully extracted" claim went stale within the hour** (NCD 100.2, then NCD 80.8 / NCD 110.21, now this). **Re-measure `sources/` against the graph at the start of any session that plans NCD work; never carry the previous session's answer forward.**
46. **NEW (S262) — `predicate_order` vs `predicate_ordering` name mismatch.** The check is registered in `ALL_CHECKS` as **`predicate_order`** but emits findings with category **`predicate_ordering`**. The audit therefore prints a name that is not the registry key, and a self-test variant registered under the printed name raises `ValueError: Unknown check_category`. Cost a cycle this session. Cosmetic but a live trap; aligning them touches the handoff-facing category string, so it is an agreed-scope change, not a drive-by.
47. **NEW (S262) — stub `dc:source` convention is inconsistent.** `cr12027` carries `dc:source gemi:tn10566NCD`, i.e. a provenance pointer at the *discovering document*. The nine stubs minted this session (`ncd80.7`, `ncd10.1`, `tn61CIM`, and NCD 110.21's seven) carry **no `dc:source` at all**, on the reasoning that no URL was supplied. Both readings are defensible; the corpus should pick one. No graph change made.

## §5 — Plan for S263

### §5.1 — Bootstrap (auto-authorized)

From the canonical directory, read the latest handoff in `handoffs/`, then run `python gem_audit.py --files-dir . --autofix` immediately, without asking. Expect a clean run with **no autofix write**, two INFO (`source_availability_unverified` **43**; `policy_effective_date_v1` **24**), plus **`[NCD CENSUS]`** (Active 135 · Stubs 4 · Retired 13 · Deleted 5 · Unknown 0 · Total 157). Any RED is a halt; surface YELLOW for decision.

**Mid-session `hash_verify` RED is normal and is not the halt case** — it means canonical files have been edited since the last §1 table was computed. The halt rule is about RED at **bootstrap**.

### §5.2 — Standing priority: finish the NCDs (Tom, S260)

**Two kinds of remaining work, and they must not be conflated.**

**PDF on hand, not extracted — no gate, start immediately:**

| Policy | File |
| :--- | :--- |
| **NCD 100.4** | `sources/NCD 100.4.pdf` (arrived during the S262 close; see §4 item 45) |

**Queue stubs with no rendition — need PDFs from Tom:**

| Policy | Note |
| :--- | :--- |
| **NCD 20.4** | Implantable Automatic Defibrillators (ICDs); CED with registry requirements; expect multi-version |
| **NCD 210.3** | Colorectal Cancer Screening Tests; extensive coding, long revision history; expect multi-version |
| **NCD 280.13** | TENS - RETIRED; counted under **Retired**, not **Stubs** |
| **NCD 80.7** | New at S262, cited by NCD 80.8 for excluded refractive procedures |
| **NCD 10.1** | New at S262, cited by NCD 80.8's bundling rule |

**Re-measure `sources/` against the graph before planning** (§4 item 45). Pre-Extraction requirement 5 applies: **every version, not just the one in effect**.

### §5.2a — After the NCDs

§4 items **37, 38, 40** remain cheap, plus **46** and **47** which are new and small. Items 35 and 36 also stand. Then: process the next policy, or promote a `planPromote` stub. **Reprocessing remains closed** until every NCD is processed.

### §5.3 — Do not

- `policies_processed` is **170** — advance it only on a genuine new extraction/promotion.
- Do not re-hardcode the audit namespace; do not re-add the frozen `LLM_ANNOTATED_VOCAB_CLASSES` tuple; do not promote the PyYAML lazy import to module level; do not split `SKILL.md` without agreement.
- `owl:versionInfo`, the `# Produced:` header date, and Tom-supplied `dc:source` URLs remain untouched.
- **Do not collapse `predicate_target_sort` to a single tier (S261).** V110 and V111 exist to make either collapse turn the suite red.
- **Do not re-introduce the literal-matching bug in `check_predicate_ordering` (S262 D7).** V112 pins it.
- **Do not split a single source unit that says *covered under X / not covered under Y* (S262 D6).** Keep it whole and dual-type it — 18 existing rules and four exact-shape precedents.
- **Do not read a primary/secondary convention into `gem:ruleType` order (S261 D10).**
- **Do not chase an authoritative CMS NCD index to measure remaining work (item 41).**
- **Do not read the census `Stubs` count as the promote queue, and do not count graph facts with a regex over the TTL (item 43).** Use rdflib.
- **Do not carry forward a previous session's "`sources/` is fully extracted" answer (item 45).**
- **Do not reprocess any already-extracted NCD until every NCD is processed (Tom, S260).**
- **Do not delete anything from `sources/`, and do not delete the Dropbox originals** (Tom, S260).
- **Do not read other policy-PDF locations.** `Dropbox\Projects\HOO2pilot\policies` is the sanctioned source directory.
- **Push at session close, not before.** The remote is the only off-machine copy of `sources/`.
