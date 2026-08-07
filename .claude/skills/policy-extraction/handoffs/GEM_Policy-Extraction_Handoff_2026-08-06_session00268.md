# GEM Policy-Extraction Handoff — Session 268 (2026-08-06)

## §1 — Canonical files (post-close state)

Hashes are md5 over the frozen output set; **M** marks a file changed this session. The canonical set is **15 files**.

| File | md5 | size | S268 |
| :--- | :--- | :--- | :--- |
| `GEM_ontology.ttl` | `5a77000e27e2ce03d6e2e0596e716934` | 340257 |  |
| `GEM_policy_instances.ttl` | `facc826632613ca0b257ab7207384332` | 6170368 | **M** |
| `GEM_code_group_instances.ttl` | `10a70c01175dcf714a4bd8307bd07eeb` | 25942 |  |
| `cpt.ttl` | `351aa816b978ec63a6800feb50bfb5c4` | 35223 |  |
| `SKILL.md` | `10ee139b6c97b09a2b5ff0aedf99a95f` | 285703 | **M** |
| `gem_reference.md` | `bd2a8164afcf31ccfeda5dc242fd6f63` | 121808 |  |
| `gem_rule_categories.md` | `17fba5bb6e13df1eb680ebb1e1f14bf0` | 1549135 | **M** |
| `gem_edit_log.md` | `ad673c04373682f2c6bb35f44a327594` | 174314 | **M** |
| `gem_structured_rule_guide.md` | `5dc562fdf25cdd7a492969be2b82fee5` | 60817 |  |
| `gem_turtle_style_guide.md` | `0c82c21cb54232de2c731fb1dcfce117` | 26524 |  |
| `manifest_format.md` | `24d134579244454795e39b2be1ce80d3` | 26227 |  |
| `policy_worklist.json` | `0f68b183bfc618166112ec9b9b3ce19b` | 322732 | **M** |
| `gem_llm_annotations.json` | `ae89620445889e7137e2bdc5ba4cd669` | 7213 |  |
| `worklist_schema.md` | `2519964abbdba260c621a6a5e9f8318b` | 16521 |  |
| `gem_audit.py` | `83f1d5a9ca76928f84bb5137f165979b` | 339976 | **M** |

## §2 — Work completed in S268

**Four extractions and one promotion closed the FDG PET family.** NCD 220.6.3, 220.6.7 and 220.6.11 are replacement-lifecycle siblings; **NCD 220.6.17 is the keystone they all point at** — the section their coverage was moved into, and the only live coverage section in the family. It is the **largest single extraction in the corpus** at +626 triples and 33 rules. No schema change (`GEM_ontology.ttl` byte-identical).

**Graph movement:** `policies_processed` **182 → 186**. Instances triples **54,687 → 55,438** (+751). Workflow `planDone` **182 → 186**, `planPromote` **791 → 803**, `planNone` **17** unchanged. NCD census **Active 141 → 142**, Stubs **6 → 5**, Retired **19 → 22**, Deleted 5, Unknown 0, **Total 171 → 174**. Clinical concepts **2,999 → 3,027**; policy rules **1,998 → 2,034**; credentials **138** and settings **26** unchanged. `referencesPolicy` **1295 → 1385**, `revisesPolicy` **296 → 318**, `revisedByPolicy` **0** (invariant), `referencesChangeRequest` **151 → 178**.

**`sources/` gained 13 PDFs.** Re-measured at close: **353 PDFs, 280 NCD-named across 163 sections, 0 unparsed, 0 sections without a `planDone` individual.**

### (a) The extractions

| Policy | Rules | Concepts | Refs / new stubs | Δ |
| :--- | ---: | :--- | :--- | ---: |
| **NCD 220.6.3** FDG PET for Esophageal Cancer — RETIRED | 1 | 0 | 11 + 2 CRs / **0** | +41 |
| **NCD 220.6.7** FDG PET for Head and Neck Cancers — RETIRED | 1 | 0 | 12 + 2 CRs / 1 | +50 |
| **NCD 220.6.11** FDG PET for Thyroid Cancer — RETIRED *(promotion)* | 1 | 0 | 12 + 2 CRs / **0** | +34 |
| **NCD 220.6.17** PET (FDG) for Oncologic Conditions *(promotion)* | **33** | 28 mint, 15 reuse | **55 + 21 CRs / 13** | **+626** |

All four share the TN 31 family date pair **2005-01-28 / 2005-04-18** except 220.6.17, whose V1 dates are **2009-04-03 / 2009-10-30** — it was created by the transmittal that replaced the others. `KNOWN_V1_DATES` rows added for all four per S260 D8.

### (b) The round-trip pattern was falsified (§3 D1)

| | benefit-category round-trip |
| :--- | :--- |
| 220.6.4 · .10 · .14 · .15 (S264) · .3 · .7 (S268) — all replaced | **yes**, 6 |
| **220.6.11 — also replaced** | **no** — V2 keeps Diagnostic Tests (other) |
| 220.6.13 — never replaced | no |
| 220.6.17 — never replaced | no |

S266 D1 reattributed the round-trip from the TN 106/108/120 revision to the **replacement** of the section. S268 read that as confirmed twice (220.6.3, 220.6.7) and then **broke it** at 220.6.11. **Replacement is not sufficient**; six of seven is a pattern, not a rule. Only S266 D1's negative half survives — the round-trip is not a property of TN 106/108/120. What it *is* remains unknown; most defensibly an MCD metadata artifact varying by section.

### (c) A halt that paid for itself (§3 D2)

NCD 220.6.7's `sources/` held only V1 and V2 while Tom's URL named `ncdver=3`. Extracting from V2 would have written four wrong facts, the sharpest being **zero benefit categories, because V2 reads "No Benefit Category."** Tom supplied V3; it confirmed every prediction including the restored category. Cost: one exchange. Cost of proceeding: a silent wrong triple no audit check looks for.

### (d) The S169 sharpening at scale (§3 D4)

NCD 220.6.17 names **35 coverage transmittals**. Seven revise; **twenty-eight are quarterly ICD-10 coding-maintenance updates stating "No policy is being changed"** and take `referencesPolicy` only. It also yields **zero codes** despite those twenty-eight — no Coding Information section in any rendition.

## §3 — Decisions (S268)

- **D1 — a pattern that survives three tests and fails the fourth was still worth testing each time.** The round-trip's falsification at 220.6.11 is the S266 D1 discipline firing *against* a reading rather than for one, the first time in this family. **The two S268 register entries claiming confirmation are deliberately not amended** — they describe what was true of the documents at the time, and rewriting them would erase the sequence that produced the correction. **Separate the stakes:** the round-trip is an observation; *read the benefit category from the live version* is the load-bearing rule, and it gave the right answer in all nine family cases.
- **D2 — when the live rendition is missing, halt; do not extract from the newest one on hand.** The live version governs `prefLabel` (including the `- RETIRED` marker `ncd_census` reads), `policyVersion`, the rule text, and the benefit category. A superseded rendition can be wrong on all four at once, silently.
- **D3 — a reference that lives only inside removed rule content is still a reference (220.6.7 B1, Tom).** `ncd220.6.11` is cited nowhere but V1's Limitations paragraph — no other version, no reference field. Every prior dead-version reference came from a reference **field** that survives the body. **The S152 corollary does not generalise from concepts to references:** a concept is minted *from* rule text and loses its anchor when the rule goes; a reference records a dependency that happened and stays true — the same reason `tn31NCD` keeps its `revisesPolicy` edge though everything it delivered is gone. Counter-argument recorded: a reader of the live page never encounters §220.6.11.
- **D4 — a table row is a source unit (220.6.17 B1, Tom).** The synopsis table decides **fifteen tumor types the prose never names**, so it is not a restatement. One rule per row, dual-typed where the row splits — S262 D6 applied directly. Cell-level rules would fragment the units that rule keeps whole; a single table rule would bury fifteen tumor types beyond query.
- **D5 — provenance is not a rule (220.6.17 B2, Tom).** The NOPR paragraph records who asked for the reconsideration and what the comments said. It goes to `gem:description`; NOPR and CED become concepts. Minting it would put *"CMS received public input"* in the same class as a coverage grant.
- **D6 — an article is not a distinct source phrasing (220.6.17 B4, Tom).** *"adenocarcinoma of the prostate"* reuses NCD 210.1's `conceptAdenocarcinomaOfProstate`. Decisive: **NCD 210.1's own description already reads "of the prostate" with the article** while its prefLabel drops it. The strict §2f reading (never consolidate) is the recorded counter-argument. Word changes still split — `conceptMyeloma`, `conceptSmallCellLungCancer`, `conceptNeurologicDisorder` were all minted separately.
- **D7 — a stub's `prefLabel` comes from the cited policy's own rendition when one exists.** `ncd220.6.11`'s stub took its real title from its V3 Tracking block, and **the promotion two turns later left it byte-identical**. Contrast `ncd220.12` (S267 §4 item 55), which kept a bare identifier because no rendition existed. The discriminator is availability of the **cited** document, not the citing document's wording.

## §4 — Open items

Items 1–55 carry from S267 unless restated.

1. **Cadence checkpoint — next at 200.** `policies_processed` is **186**; 14 out. Not due. The item-52 agenda entry stands.
2. **LCD/Article V1-date research — 18 candidates.** `policy_effective_date_v1` INFO unchanged.
3. **CIM stub source availability.** `tn106CIM` and `tn113CIM` (S267) remain the two strong `sourceUnobtainable` candidates awaiting Tom's direction rather than inference.
4. **Era-gate mistokens — retrospective sweep still pending Tom.** S268 adds three more collisions (`tn110CIM`/`tn110NCD`, `tn124CP`/`tn124NCD`, `tn168CIM`/`tn168NCD`), bringing the case for the sweep to nine in two sessions.
5.–51. **Carry unchanged.**
52. **DEFERRED to the 200-policy checkpoint (Tom, S266).** Unchanged; all four S268 policies relocated correctly on promotion.
53. **No audit check covers banner presence — and S268 found a second shape of the same gap.** The stub run in NCD 220.6.15's section (`tn1817CP`, `tn1833CP`, `cr6632`, `cr3741`, formerly `ncd220.6.17`) sits under **no sub-banner at all**, not a wrong one. A `banner_presence` check keyed on planDone policies would not catch this; the gap is banner **coverage** of stub runs, which is a second criterion.
54. **`sources/` filename convention has a third form.** All 13 S268 arrivals use it (`NCD X vN.pdf`). Census now **166 dated · 94 undated · 20 versioned**.
55. **`gemi:ncd220.12` bare-identifier `prefLabel`.** Unchanged — still no rendition. D7 above states the rule that governs it.

56. **NEW (S268) — the benefit-category round-trip has no known cause.** Six of seven replaced sections show it; 220.6.11 does not. Replacement is falsified as the discriminator and TN 106/108/120 was falsified at S266. Do **not** propose a third causal reading without evidence from outside the 220.6 family — and do not let the pattern's absence or presence influence what is written, since the live-version rule already decides it.
57. **NEW (S268) — TN 13401's revision-history wording deserves a second look at its own extraction.** Its 09/2025 entry says it was issued *"to add a new attachment … and to update the Policy section"*, which reads like a policy change; S268 resolved it as the **transmittal's** own Policy section, since the same entry gives the CR's purpose as a quarterly ICD-10 maintenance update, and kept it a mention under S169(a). If TN 13401's own extraction shows otherwise, `ncd220.6.17` needs a `revisesPolicy` edge added.

## §5 — Plan for S269

### §5.1 — Bootstrap (auto-authorized)

From the canonical directory, read the latest handoff in `handoffs/`, then run `python gem_audit.py --files-dir . --autofix` immediately, without asking. Expect a clean run with **no autofix write**, two INFO, plus **`[NCD CENSUS]`** (Active 142 · Stubs 5 · Retired 22 · Deleted 5 · Unknown 0 · Total 174). Any RED is a halt; surface YELLOW for decision.

**Mid-session `hash_verify` RED is normal.** The halt rule is about RED at **bootstrap**.

### §5.2 — Standing priority: finish the NCDs (Tom, S260)

**Check `sources/` before naming any NCD target** (Tom, S267) — cross-reference `^NCD\s+<section>` over `sources/*.pdf`, tolerating all **three** filename forms (§4 item 54), against `planDone` read from the **graph**.

Measured at the S268 close: **0 of 163 NCD sections in `sources/` lack a `planDone` individual.** As at S267, **every remaining NCD target needs a rendition from Tom before it can be planned.** The FDG PET family is complete — 220.6 and all eight subsections extracted.

| Policy | Note |
| :--- | :--- |
| **NCD 20.4** | Implantable Automatic Defibrillators; CED with registry requirements; expect multi-version |
| **NCD 210.3** | Colorectal Cancer Screening Tests; extensive coding, long revision history |
| **NCD 280.13** | TENS - RETIRED; counted under **Retired**, not Stubs |
| **NCD 80.7** | Cited by NCD 80.8 for excluded refractive procedures |
| **NCD 10.1** | Cited by NCD 80.8's bundling rule |
| **NCD 220.12** | SPECT; cited by NCD 220.6's Cross Reference (§4 item 55) |

### §5.2a — After the NCDs

§4 items 53, 54, 57 are small and each prevents a recurrence. Then 52 (at the checkpoint), 4, 37, 38, 40, 46, 47, 49. Items 35 and 36 also stand. `sources/` holds **47 non-NCD documents not yet `planDone`** — the deferred non-NCD phase, available if Tom redirects, **not** to be started unprompted.

### §5.3 — Do not

- `policies_processed` is **186** — advance it only on a genuine new extraction/promotion.
- Do not re-hardcode the audit namespace; do not re-add the frozen `LLM_ANNOTATED_VOCAB_CLASSES` tuple; do not promote the PyYAML lazy import to module level; do not split `SKILL.md` without agreement.
- `owl:versionInfo`, the `# Produced:` header date, and Tom-supplied `dc:source` URLs remain untouched.
- **Do not extract from a superseded rendition when the live one is missing (S268 D2).** Halt and ask. V2 of a replaced section can be wrong on prefLabel, version, rule text and benefit category simultaneously.
- **Do not propose a third causal reading of the benefit-category round-trip (S268 D1, §4 item 56).** Two have been falsified. The live-version rule decides the value regardless.
- **Do not drop a reference because the text citing it was removed (S268 D3).** The S152 corollary covers concepts, not references.
- **Do not split a table row into per-cell rules (S268 D4), and do not collapse a decision table into one rule.**
- **Do not mint a provenance paragraph as a rule (S268 D5).**
- **Do not mint a near-duplicate concept over an article (S268 D6)** — but do mint over a word change (S156).
- **Do not lower `CIM_MAX_TN` (S267 D4).** Raise only on a rendition; read a CIM-token RED as a question about the ceiling first.
- **Do not mint a transmittal because it is known to exist (S267 D4).** S131 mints what is *referenced*.
- **Do not assert `sourceAvailability` from the archive-line pattern (S267 D5).**
- **Do not duplicate a transmittal across a differing CR or effective date within one manual (S267 D3).**
- **Do not read a cumulative revision history as the complete reference set (S267 D7).**
- **Do not retain removed content because there is a lot of it (S267 D1).** ~17,000 words of CED text yielded zero rules at 220.6.17.
- **Do not link a mention within a mention (S264 D2).** S268: TN 13383, and eight CRs inside a narrative list.
- **Do not treat revision-history volume as evidence of codeable content (S268).** Twenty-eight ICD-10 maintenance transmittals, zero codes.
- **Do not collapse `predicate_target_sort` to a single tier (S261).** V110/V111 guard both directions.
- **Do not re-introduce the literal-matching bug in `check_predicate_ordering` (S262 D7).** V112 pins it.
- **Do not restore the ambiguous block regex (S266 D4).** V115 pins it; the failure mode is a silent multi-minute hang.
- **Do not remove `block_terminator` as redundant with `predicate_order` (S266 D4).**
- **Do not treat a clean rdflib triple-count as sufficient verification of emitted bytes (S266 D5).**
- **Do not treat the source's own lettering as the rule count (S266 D2).** Grammatical dependence keeps a condition whole; a modal shift breaks it apart.
- **Do not carry a family finding forward untested (S266 D1).** S268 falsified one.
- **Do not treat a same-stem reuse hit as identity (S265 D2).** Read the existing description first — S268's B4 turned on exactly that.
- **Do not assume a transmittal number identifies a document (S263 D2), in either direction (S264), or within one policy's own version set (S267 D2).**
- **Do not chase an authoritative CMS NCD index to measure remaining work (item 41).**
- **Do not count graph facts, or file structure, with a regex over the TTL (item 43, S266).** Use rdflib.
- **Do not name an NCD target without cross-referencing `sources/` first (Tom, S267).**
- **Do not reprocess any already-extracted NCD until every NCD is processed (Tom, S260).**
- **Do not delete anything from `sources/`, and do not delete the Dropbox originals** (Tom, S260).
- **Do not read other policy-PDF locations.** `Dropbox\Projects\HOO2pilot\policies` is the sanctioned source directory.
- **Push at session close, not before.** The remote is the only off-machine copy of `sources/`.
