# GEM Policy-Extraction Handoff — Session 264 (2026-08-05)

## §1 — Canonical files (post-close state)

Hashes are md5 over the frozen output set; **M** marks a file changed this session. The canonical set is **15 files**.

| File | md5 | size | S264 |
| :--- | :--- | :--- | :--- |
| `GEM_ontology.ttl` | `5a77000e27e2ce03d6e2e0596e716934` | 340257 |  |
| `GEM_policy_instances.ttl` | `e743dfe1f5371081223466d7378dd06b` | 5944458 | **M** |
| `GEM_code_group_instances.ttl` | `10a70c01175dcf714a4bd8307bd07eeb` | 25942 |  |
| `cpt.ttl` | `351aa816b978ec63a6800feb50bfb5c4` | 35223 |  |
| `SKILL.md` | `8acb4fb27083372279c2aacd4f509ce3` | 284429 | **M** |
| `gem_reference.md` | `4ddd97d8b96dec2b4aff8e0318376c46` | 120152 |  |
| `gem_rule_categories.md` | `5dc5b3d7297df6e40c750723a3447a84` | 1487660 | **M** |
| `gem_edit_log.md` | `b47a6e5795d68fa3bfd2f45c0fe7def0` | 144038 | **M** |
| `gem_structured_rule_guide.md` | `5dc562fdf25cdd7a492969be2b82fee5` | 60817 |  |
| `gem_turtle_style_guide.md` | `0c82c21cb54232de2c731fb1dcfce117` | 26524 |  |
| `manifest_format.md` | `24d134579244454795e39b2be1ce80d3` | 26227 |  |
| `policy_worklist.json` | `80052ec130ba417677c87fb9a5812956` | 322732 | **M** |
| `gem_llm_annotations.json` | `ae89620445889e7137e2bdc5ba4cd669` | 7213 |  |
| `worklist_schema.md` | `2519964abbdba260c621a6a5e9f8318b` | 16521 |  |
| `gem_audit.py` | `890ace764a5077b5031c1fb3fdd3001d` | 331607 | **M** |

## §2 — Work completed in S264

**One `SKILL.md` rule promoted, four extractions — the complete FDG PET family.** No schema change: `GEM_ontology.ttl` is **byte-identical**, and `gem_audit.py`'s only edits are four `KNOWN_V1_DATES` rows.

**Graph movement:** `policies_processed` **175 → 179**; `referencesPolicy` **1196 → 1243**; `revisesPolicy` **258 → 279**; `revisedByPolicy` stays **0**; `referencesChangeRequest` **139**. Instances triples **53,401 → 53,698** (+297). Workflow state `planDone` **175 → 179**, `planPromote` **744 → 759**, `planNone` **16**. NCD census **Active 139 (unchanged), Stubs 4 → 6, Retired 14 → 18, Deleted 5, Unknown 0, Total 162 → 168**. Both INFO queues unchanged: `source_availability_unverified` **49**, `policy_effective_date_v1` **24**. Corpus totals: **2,949** clinical concepts (**unchanged — all four extractions yielded zero**), **1,974** policy rules, **117** NCA documents, **72** CIM transmittals.

### (a) The four extractions

| Policy | Rules | Concepts | Refs / new stubs | Δ |
| :--- | ---: | :--- | :--- | ---: |
| **NCD 220.6.15** FDG PET, All Other Cancer Indications - RETIRED | 1 | 0 | 13 / 12 | +146 |
| **NCD 220.6.14** FDG PET, Brain/Cervical/Ovarian/Pancreatic/SCLC/Testicular - RETIRED | 1 | 0 | 15 / 2 | +59 |
| **NCD 220.6.10** FDG PET for Breast Cancer - RETIRED | 1 | 0 | 14 / 1 | +51 |
| **NCD 220.6.4** FDG PET for Colorectal Cancer - RETIRED | 1 | 0 | 13 / 0 | +41 |

All four minted direct to the graph; **none was ever worklisted**. Four `KNOWN_V1_DATES` rows added — the S260 D8 step's fifth through eighth exercises, and all four carry the identical pair `2005-01-28` / `2005-04-18`, the sections having been created by the same TN 31.

**The decreasing stub column is the session's shape.** 12 → 2 → 1 → 0. The first sibling built the neighbourhood; the fourth had nothing left to mint and no borderline to raise.

### (b) The S152 corollary, tested four times against rising stakes (§3 D1)

The corollary — *if a later version reports removal, prior content and the concepts named only inside it go with it* — has always been exercised on thin content. This family escalates it deliberately:

| Policy | What V1 actually carried, and was removed |
| :--- | :--- |
| **220.6.15** | Uniformly *coverage with evidence development* |
| **220.6.14** | Section A **ordinary coverage** for cervical staging; Section B CED |
| **220.6.10** | **Ordinary national coverage** from 10/01/2002, three indications, **plus explicit national non-coverage** of initial diagnosis and axillary node staging |
| **220.6.4** | **Three stacked, separately dated regimes spanning six years** — ordinary coverage from 07/01/1999 (recurrent carcinoma, rising CEA, 12-month frequency limit), ordinary coverage from 07/01/2001 (diagnosis/staging/re-staging), CED from 01/28/2005 (monitoring response) — plus requirements A/B/C |

**All four removed identically; 0 retained rules and 0 clinical concepts in every case.** 220.6.10's pair is the sharp instance: a *covered-under-X / non-covered-under-Y* unit of exactly the kind S262 D6 measured and said to keep whole — kept whole, then removed whole. **The rule keys on the source reporting its own removal, not on the substance of what was removed.** One instance looked like a rule about thin content; four make it a rule about reporting.

### (c) One transmittal, four different descriptions (§3 D2)

TN 31 created all four sections and is described differently in each policy's Revision History:

| Policy | TN 31's entry says | Edge earned |
| :--- | :--- | :--- |
| **220.6.15** | CED coverage for unspecified cancers | `revisesPolicy` → that policy |
| **220.6.14** | Coverage for cervical staging | `revisesPolicy` → that policy |
| **220.6.10** | *"Removed text from PET Scans NCD (§220.6) and created a separate NCD."* | **`revisesPolicy` → `ncd220.6`** (B1) |
| **220.6.4** | CED coverage for monitoring response | `revisesPolicy` → that policy |

**Only one of the four descriptions carries the edge to `ncd220.6`** — the first inbound revision edge that individual has, and the graph's only record of how the 220.6.x family came to exist. Had the sibling's description been assumed to apply, either an edge would have been missed or three unsupported ones asserted. **A transmittal's edges are read per citing document; a sibling's account of the same transmittal is not evidence about this one.** This is the S263 D2 lesson (a number does not identify a document) advanced one step: *the same document does not carry the same edges everywhere it is cited.*

### (d) Two rules moved from observation to measurement

**The No-Benefit-Category rule (S262 `SKILL.md`) round-trips 4 for 4.** Every sibling: V1 Diagnostic Tests (other) → V2 **"No Benefit Category"** → V3 restores it. Four policies revised by the same TN 106/108/120 chain behave identically, so **the round-trip is a property of that revision, not a per-policy accident** — and reading the field from the live version resolves all four without a borderline. Extracting any of them from V2 would have recorded zero categories. This is the rule's first live exercise since it was written, and it is now a measured regularity.

**NCD 220.6.15's §200.6 is confirmed a typo by three independent documents.** That policy publishes *"See NCD for PET Scans (§200.6)."* in all three versions and S264 redirected the link to §220.6 on internal evidence alone (V1's own *"Section 220.6 above"*). **220.6.14, 220.6.10 and 220.6.4 — same family, same transmittals, same dates, the same sentence — all publish `§220.6`.** Three against one.

### (e) The bare-term linking rule promoted (§4 item 48 → CLOSED)

Added to `SKILL.md` §Clinical Concepts after the composite-concepts rule: the converse of single-term linkage (*an existing bare concept is not linked merely because it exists*), the **grammatical test** (compound modifier → decline; object of a preposition or sentence subject → link), a two-row table contrasting NCD 160.10's declined `conceptBrain` with NCD 20.2's reused one, the further declines (`conceptLarynx`, `conceptEndothelialCell`, `conceptTumor`, `conceptHypertension`, `conceptEndStageRenalDisease`), and a paragraph reconciling it with single-term linkage — **the two rules share a single test and differ only in what it returns.** Backed by six worked decisions across S261–S263.

### (f) The `ncd220.6` stub, enriched twice in one session

Minted at 220.6.15 naming one citer. Enriched at 220.6.14 (second citer; the cross-reference corroboration). Enriched again at 220.6.10 (third citer; the carve-out and the new revision edge). **The evidence for a Tom-confirmed decision lives beside the individual that decision created** — the `ontology-cumulative-merge` ENRICHED path, exercised twice on the same stub within hours.

## §3 — Decisions (S264)

- **D1 — the S152 corollary is indifferent to the substance of removed content (four confirmations).** See §2(b). **Carry forward:** when a later version *reports* removal, do not retain, however substantive the removed rules; check only whether the removal is reported.
- **D2 (NCD 220.6.10 B1, Tom) — a transmittal's edges are read per citing document.** See §2(c). `gemi:tn31NCD gem:revisesPolicy gemi:ncd220.6` asserted from that policy's TN 31 entry alone.
- **D3 (NCD 220.6.14 B1 / NCD 220.6.10, Tom) — an existing stub's prose is enriched when a later extraction adds citers or evidence.** Not left frozen at its minting state. Two applications, same stub.
- **D4 — a body date is not a candidate for `policyEffectiveDate`.** NCD 220.6.10's V1 text is effective 10/01/2002 and NCD 220.6.4's carries 07/01/1999 and 07/01/2001, all **earlier than their sections' own effective dates**, because the text came across from §220.6 in the carve-out. The Tracking block governs (S192); the earlier dates stay in prose.
- **D5 — an apparent U+FFFD can be the console, not the text layer.** `pdftotext -layout` without `-enc UTF-8` rendered `§` as a replacement character and looked like a damaged source; `-enc UTF-8` gives `§220.6` and **0 U+FFFD across all twelve renditions**. The third entry in the S262/S263 D9 series: NCD 160.9's defect *was* tooling, NCD 100.4's was *not*, and this one is tooling again — **check, every time.**
- **D6 — zero borderlines is a legitimate outcome.** NCD 220.6.4 raised none: every reference target existed and no NCAs were listed. A Plan turn that finds nothing to ask is a fully precedented extraction, not an under-read one, and it says so explicitly.

## §4 — Open items

Items 1–49 carry from S263 unless restated.

1. **Cadence checkpoint — next at 200.** `policies_processed` is **179**; 21 out. Not due.
2. **LCD/Article V1-date research — 18 candidates.** `policy_effective_date_v1` INFO = **24**, unchanged.
3. **CIM stub source availability — 49**, unchanged (S264 minted no CIM transmittals; the whole family is post-crystallization).
4. **Era-gate mistokens — procedure established, retrospective sweep still pending Tom.** S264 confirmed the rule is **symmetric**: at NCD 220.6.15 the graph held `tn120CIM` (12/1999) while the source wanted the 05/2010 Pub. 100-03 document (link `R120NCD.pdf`), the mirror of every S263 case. `tn120NCD` minted distinct.
5.–44. **Carry unchanged.**
45. **RE-MEASURED (S264) — AND THE PRIOR MEASUREMENT WAS BROKEN. See item 50.** `sources/` holds **330 PDFs, 257 NCD-named across 157 distinct sections** — **94 of them undated single-version files, 163 dated multi-version renditions** — and **one section with no graph individual at all: NCD 20.23**.
46. **`predicate_order` vs `predicate_ordering` name mismatch.** Unchanged; still a live trap.
47. **Stub `dc:source` convention is inconsistent.** Unchanged. S264 added to both sides again: `tn120NCD` carries a Tom-supplied URL; the three NCA stubs and `ncd220.6.17` carry none.
48. **CLOSED (S264).** The bare-term linking rule is in `SKILL.md`. See §2(e).
49. **Carry unchanged** — the reuse search still needs an acronym-tolerant pass. Not exercised in S264 (zero concepts across all four extractions).

50. **NEW (S264) — `sources/NCD 20.23.pdf` is unextracted and absent from the graph, and the re-measure that should have caught it was itself defective.** The file is **tracked in `git` as of S263** and the graph has no `NCD 20.23` individual of any kind — not a stub, not a retiree. It was missed twice: S263's close reported *"0 NCD PDFs without a graph individual"*, and a mid-S264 re-measure reported only NCD 220.6.4 outstanding. **Both were wrong for the same reason, and the reason is the measuring instrument, not the source library.**

    **The naming convention is correct and was misread (Tom, S264).** `sources/` names a **single-version** NCD without a dated suffix — `NCD 20.23.pdf` — and a multi-version one with `NCD X YYYY-MM-DD Effect.pdf`, one file per rendition. **94 of the 257 NCD-named PDFs are undated single-version files**, 37% of the library and entirely regular. An earlier draft of this item called `NCD 20.23.pdf` the only undated rendition and treated the filename as an anomaly; that was wrong on both counts and is corrected here so the bad diagnostic does not propagate.

    **What actually broke:** the section-name regex `^(NCD [\d.]+?)\s` required whitespace after the section number, so it matched no undated filename at all — **all 94 were silently dropped**, collapsing 157 distinct source sections to 67. The corpus was lucky: 93 of the 94 were already extracted, so exactly one false clean surfaced. **Item 45's standing instruction is necessary but not sufficient — re-measuring with a broken instrument reports the same false clean as not re-measuring at all.** The corrected form is `^NCD\s*([0-9]+(?:\.[0-9]+)*)`, greedy and not whitespace-anchored, with an explicit unparsed-file count that must be zero. S265 should extract NCD 20.23 first, and should print the parsed-section count alongside the result so a collapse is visible rather than inferred.

## §5 — Plan for S265

### §5.1 — Bootstrap (auto-authorized)

From the canonical directory, read the latest handoff in `handoffs/`, then run `python gem_audit.py --files-dir . --autofix` immediately, without asking. Expect a clean run with **no autofix write**, two INFO (`source_availability_unverified` **49**; `policy_effective_date_v1` **24**), plus **`[NCD CENSUS]`** (Active 139 · Stubs 6 · Retired 18 · Deleted 5 · Unknown 0 · Total 168). Any RED is a halt; surface YELLOW for decision.

**Mid-session `hash_verify` RED is normal** — it means canonical files have been edited since the previous handoff's §1 table was computed. The halt rule is about RED at **bootstrap**.

### §5.2 — Standing priority: finish the NCDs (Tom, S260)

**Re-measure `sources/` against the graph before planning (§4 item 45) — and use the corrected regex from item 50, printing the section count so a collapse is visible.**

**First: `NCD 20.23.pdf`, on hand and unextracted** (§4 item 50). The undated filename means **single-version** under the `sources/` naming convention (Tom, S264), so Pre-Extraction requirement 5 is satisfied by the one file — the same footing as the 93 other undated NCDs already extracted. Ask Tom only for the MCD URL.

Then the five stubs needing renditions from Tom:

| Policy | Note |
| :--- | :--- |
| **NCD 20.4** | Implantable Automatic Defibrillators (ICDs); CED with registry requirements; expect multi-version |
| **NCD 210.3** | Colorectal Cancer Screening Tests; extensive coding, long revision history; expect multi-version |
| **NCD 280.13** | TENS - RETIRED; counted under **Retired**, not **Stubs** |
| **NCD 80.7** | Cited by NCD 80.8 for excluded refractive procedures |
| **NCD 10.1** | Cited by NCD 80.8's bundling rule |

**`NCD 220.6` and `NCD 220.6.17` are now high-value promote targets.** Both are stubs cited by all four siblings; 220.6 is the parent the family was carved out of, and 220.6.17 is the section that replaced all four. Extracting either would close the family's outbound edges onto real content.

### §5.2a — After the NCDs

§4 items 37, 38, 40, 46, 47, 49, all small. Items 35 and 36 also stand.

### §5.3 — Do not

- `policies_processed` is **179** — advance it only on a genuine new extraction/promotion.
- Do not re-hardcode the audit namespace; do not re-add the frozen `LLM_ANNOTATED_VOCAB_CLASSES` tuple; do not promote the PyYAML lazy import to module level; do not split `SKILL.md` without agreement.
- `owl:versionInfo`, the `# Produced:` header date, and Tom-supplied `dc:source` URLs remain untouched.
- **Do not collapse `predicate_target_sort` to a single tier (S261).** V110/V111 guard both directions.
- **Do not re-introduce the literal-matching bug in `check_predicate_ordering` (S262 D7).** V112 pins it.
- **Do not split a single source unit that says *covered under X / not covered under Y* (S262 D6).** Keep it whole and dual-type it.
- **Do not retain removed content because it looks substantive (S264 D1).** Check only whether the removal is reported.
- **Do not carry a transmittal's edges across from a sibling policy (S264 D2).** Read its entry in the document in hand.
- **Do not assume a transmittal number identifies a document (S263 D2), in either direction (S264 §4 item 4).** Check the era and check for an existing individual of the same number.
- **Do not trust an exact-prefLabel reuse search alone (S263 D5).** The forward URI pre-flight is the guarantee.
- **Do not conclude a text layer is damaged without re-extracting with `-enc UTF-8` (S262, S264 D5), and do not assume an apparent defect is tooling either (S263 D9).** Check.
- **Do not chase an authoritative CMS NCD index to measure remaining work (item 41).**
- **Do not read the census `Stubs` count as the promote queue, and do not count graph facts with a regex over the TTL (item 43).** Use rdflib.
- **Do not carry forward a previous session's "`sources/` is fully extracted" answer (item 45) — and do not trust a re-measure whose parsing you have not checked (item 50).** Print the section count.
- **Do not reprocess any already-extracted NCD until every NCD is processed (Tom, S260).**
- **Do not delete anything from `sources/`, and do not delete the Dropbox originals** (Tom, S260).
- **Do not read other policy-PDF locations.** `Dropbox\Projects\HOO2pilot\policies` is the sanctioned source directory.
- **Push at session close, not before.** The remote is the only off-machine copy of `sources/`.
