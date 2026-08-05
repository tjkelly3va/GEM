# GEM Policy-Extraction Handoff — Session 263 (2026-08-05)

## §1 — Canonical files (post-close state)

Hashes are md5 over the frozen output set; **M** marks a file changed this session. The canonical set is **15 files**.

| File | md5 | size | S263 |
| :--- | :--- | :--- | :--- |
| `GEM_ontology.ttl` | `5a77000e27e2ce03d6e2e0596e716934` | 340257 |  |
| `GEM_policy_instances.ttl` | `cf686f1dea5c38059bf508584404ef6e` | 5888470 | **M** |
| `GEM_code_group_instances.ttl` | `10a70c01175dcf714a4bd8307bd07eeb` | 25942 |  |
| `cpt.ttl` | `351aa816b978ec63a6800feb50bfb5c4` | 35223 |  |
| `SKILL.md` | `b5389dfb9c5222364402ba0af35ec234` | 281863 | **M** |
| `gem_reference.md` | `4ddd97d8b96dec2b4aff8e0318376c46` | 120152 |  |
| `gem_rule_categories.md` | `c0a19590efbe652dfcaddd5eeeebf6c6` | 1464860 | **M** |
| `gem_edit_log.md` | `4b56f6a521febadf61632b5d0d3cef83` | 130802 | **M** |
| `gem_structured_rule_guide.md` | `5dc562fdf25cdd7a492969be2b82fee5` | 60817 |  |
| `gem_turtle_style_guide.md` | `0c82c21cb54232de2c731fb1dcfce117` | 26524 |  |
| `manifest_format.md` | `24d134579244454795e39b2be1ce80d3` | 26227 |  |
| `policy_worklist.json` | `de5a2d1863dca8dabe8ee8dcc3b4ac34` | 322732 | **M** |
| `gem_llm_annotations.json` | `ae89620445889e7137e2bdc5ba4cd669` | 7213 |  |
| `worklist_schema.md` | `2519964abbdba260c621a6a5e9f8318b` | 16521 |  |
| `gem_audit.py` | `5ec8c49bfb6e80b1ac1334108ac23eef` | 331412 | **M** |

## §2 — Work completed in S263

**Five extractions.** No schema change: `GEM_ontology.ttl` is **byte-identical**, and `gem_audit.py`'s only edits are two `KNOWN_V1_DATES` rows.

**Graph movement:** `policies_processed` **170 → 175**; `referencesPolicy` **1149 → 1196**; `revisesPolicy` **248 → 258**; `revisedByPolicy` stays **0**. Instances triples **52,587 → 53,401** (+814). Workflow state `planDone` **170 → 175**, `planPromote` **720 → 744**, `planNone` 16. NCD census **Active 135 → 139, Retired 13 → 14, Total 157 → 162** (Stubs 4, Deleted 5, Unknown 0). `source_availability_unverified` **43 → 49**; `policy_effective_date_v1` unchanged at **24**. Corpus totals: **2,949** clinical concepts, **1,970** policy rules, **72** CIM transmittals.

### (a) The five extractions

| Policy | Rules | Concepts | Refs / new stubs | Δ |
| :--- | ---: | :--- | :--- | ---: |
| **NCD 100.4** Esophageal Manometry | 2 | 19 mint, 2 reuse | 0 / 0 | +164 |
| **NCD 160.10** Evoked Response Tests | 2 | 6 mint, 0 reuse | 0 / 0 | +71 |
| **NCD 20.5** ECI Using Protein A Columns - RETIRED | 1 | 2 mint, 0 reuse | 22 / 6 | +118 |
| **NCD 20.20** External Counterpulsation for Severe Angina | 9 | 14 mint, 7 reuse | 41 / 17 | +389 |
| **NCD 20.2** EC-IC Arterial Bypass Surgery | 1 | 5 mint, 2 reuse | 1 / 1 | +72 |

All five minted direct to the graph; **none was ever worklisted**. Two `KNOWN_V1_DATES` rows added (`ncd20.5`, `ncd20.20`) — the S260 D8 step's third and fourth exercises.

### (b) The era gate hardened into a rule (§3 D2)

**Seven CIM transmittals minted, four of them number collisions with existing Pub. 100-03 individuals:**

| Transmittal | Policy | Collides with | Evidence |
| :--- | :--- | :--- | :--- |
| `tn127CIM` | NCD 20.5 | `tn127NCD` (2010, NCD 110.23 HSCT) | **link reads `R127CIM.pdf`** |
| `tn46CIM` | NCD 20.5 | `tn46NCD` (2006, NCD 20.25 repeal) | 04/1991; series `tn44CIM`/`tn55CIM` |
| `tn146CIM` | NCD 20.20 | `tn146NCD` (NCD 260.1 liver transplant) | **link reads `R146CIM.pdf`** |
| `tn122CIM` | NCD 20.20 | `tn122NCD` (NCD 250.5) | 02/2000 predates Pub. 100-03 |
| `tn118CIM`, `tn111CIM` | NCD 20.20 | — | 1999 entries, clean |
| `tn47CIM` | NCD 20.2 | — | 06/1991, clean |

**The generalisable finding: a transmittal number alone never identifies a document.** Two of the four collisions were settled by the source naming its own manual family in the Coverage Transmittal Link (`R127CIM.pdf`, `R146CIM.pdf`) — stronger evidence than S262's TN 61, which rested on the dated series alone. This substantially advances §4 item 4 from "some pre-crystallization transmittals may be mistokened" to a positive resolution procedure.

### (c) The URI pre-flight earned its keep (§3 D5)

At NCD 20.20, `conceptAcuteMyocardialInfarction` was planned as a **mint** because the exact-prefLabel search returned nothing for *"acute myocardial infarction"*. It exists — from NCD 20.8, stored as **`"acute myocardial infarction (MI)"`**. The forward URI check raised `AssertionError: collision` and **stopped the generator before any write**.

**Exact-prefLabel matching misses acronym-suffixed variants.** The reuse search is a convenience; the URI pre-flight is the guarantee. Reuse went 6 → 7, mints 15 → 14.

### (d) `conceptBrain` — the same rule, opposite outcomes (§3 D3)

**Declined at NCD 160.10, reused at NCD 20.2, hours apart.** The grammar is the entire distinction: *"brain responses"* is a compound modifier, so the organ is a word-part and not independently named (the NCD 80.8 B3 rule); *"the blood supply **to the brain**"* makes it the object of a preposition, naming it directly. Recorded as a **matched pair in both registers**, because two decisions that look contradictory in a summary are exactly what a later reader flags as inconsistency.

The declining half is now a three-policy pattern in its own right — NCD 80.8's `conceptEndothelialCell`, NCD 100.4's `conceptTumor`, NCD 160.10's `conceptBrain`. **Worth promoting to `SKILL.md` alongside the No-Benefit-Category sentence; see §4 item 48.**

### (e) Two same-day reuse payoffs

`conceptEndoscopy`, minted at NCD 100.2 in S262, was reused at **NCD 100.4** hours later. `tn10838NCD`, minted at NCD 30.4 in S262, was reused at **NCD 20.5**. The concept and reference spaces are starting to close on themselves rather than only growing.

## §3 — Decisions (S263)

- **D1 (NCD 20.20) — V2 is a superset of V1, verified sentence by sentence.** Every V1 sentence recurs in V2, reorganised into sections A/B/C with three additions. **No silent drops**, so S151 retention is moot and all rules come from V2; V2's own Revision History agrees (*"Current coverage remains in effect"*). **The inverse of the run's retirement-lifecycle policies**, where V2 removed content. Verified rather than assumed, and recorded as such.
- **D2 — the era gate (Tom, four confirmations).** See §2(b). **Carry forward:** when a policy names a transmittal, check the era *and* check for an existing individual of the same number; they are frequently different documents.
- **D3 (NCD 160.10 B1 / NCD 20.2 B2) — bare-term linking turns on grammar (Tom).** See §2(d).
- **D4 (NCD 20.2 B1) — publication-number anomaly (Tom).** The Tracking block publishes **`100-4`** (Claims Processing Manual) for an NCD. Measured: 148 NCDs at 100-3, 3 at 100-03, 10 at none, **zero at 100-4**. `gem:publicationNumber` records **100-3**; the published `"100-4"` is preserved verbatim in `gem:description`. The corrected-value half of the NCD 160.9 split, applied to a metadata field rather than a title.
- **D5 — pre-flight over search.** See §2(c).
- **D6 (NCD 20.20 B1) — descriptive paragraphs are captured as rules (Tom).** `SKILL.md`'s two-layer framing is explicit that the rule-documentation layer is **not** gated by the claim-readability test. They also carried concepts appearing nowhere else in the policy.
- **D7 (NCD 20.5 B3 / NCD 20.20) — nested CRs are not linked (Tom).** CRs named only inside a quoted narrative explaining an *earlier* CR's provenance are mentions within a mention. Only each entry's own change request is linked. The S169 sharpening, one level deeper. **Recorded in the policy `workflowDescription` at Tom's request.**
- **D8 (NCD 20.5) — the first V1 implementation date of the retirement-lifecycle run.** NCD 30.4, 190.4 and 160.9 all had a V1 publishing none, so S192 dropped the triple each time; NCD 20.5's V1 publishes one and it is asserted. **The pattern was three coincidences, not a rule.**
- **D9 (NCD 100.4) — source-text defects must be checked, not assumed.** *"X- rays"* appears in **both** the `-layout` and raw `pdftotext` output, so it is in the PDF's text layer and the rule keeps it verbatim; only the concept prefLabel normalises. **Contrast NCD 160.9 (S262)**, where the apparent defect *was* tooling and vanished under `-enc UTF-8`. Both cases are recorded side by side.

## §4 — Open items

Items 1–47 carry from S262 unless restated.

1. **Cadence checkpoint — next at 200.** `policies_processed` is **175**; 25 out. Not due.
2. **LCD/Article V1-date research — 18 candidates.** `policy_effective_date_v1` INFO = **24**, unchanged.
3. **CIM stub source availability — 49** (was 43; the seven new CIM stubs joined, none carrying a rendition URL except `tn127CIM`, whose URL Tom supplied).
4. **Era-gate mistokens — SUBSTANTIALLY ADVANCED (S263).** Seven CIM mints and four number collisions resolved this session, two of them by the source's own Coverage Transmittal Link. The **resolution procedure** is now established (§2(b)); what remains is the retrospective sweep of pre-crystallization transmittals already in the graph, still pending Tom.
5.–44. **Carry unchanged.**
45. **RE-MEASURED (S263).** `sources/` holds **317 PDFs, 244 NCD-named across 152 sections, and 0 NCD PDFs without a graph individual.** The re-measure instruction worked: it caught NCD 20.5 and NCD 20.20 arriving mid-session, and NCD 160.10 arriving on request. **Keep re-measuring; do not carry this answer forward.**
46. **`predicate_order` vs `predicate_ordering` name mismatch.** Unchanged; still a live trap.
47. **Stub `dc:source` convention is inconsistent.** Unchanged, and S263 added to both sides: `tn127CIM` carries a Tom-supplied URL while the other six CIM stubs carry none.

48. **NEW (S263) — promote the bare-term linking rule to `SKILL.md`.** *"Do not link an existing bare concept the source does not independently name"* is now a four-policy pattern with a grammatical test attached: NCD 80.8 (`conceptEndothelialCell`), NCD 100.4 (`conceptTumor`), NCD 160.10 (`conceptBrain`, declined) and NCD 20.2 (`conceptBrain`, **reused** — object of a preposition, not a compound modifier). One paragraph in §Clinical Concepts would close it, and it is the same shape as the No-Benefit-Category sentence added in S262.
49. **NEW (S263) — the reuse search needs an acronym-tolerant pass.** The exact-prefLabel method missed `conceptAcuteMyocardialInfarction` because the stored label carries `(MI)`. A normalised comparison — strip parenthetical acronyms, case-fold — would catch this class before the pre-flight has to. Low cost, and the pre-flight is a hard backstop meanwhile, so this is convenience rather than correctness.

## §5 — Plan for S264

### §5.1 — Bootstrap (auto-authorized)

From the canonical directory, read the latest handoff in `handoffs/`, then run `python gem_audit.py --files-dir . --autofix` immediately, without asking. Expect a clean run with **no autofix write**, two INFO (`source_availability_unverified` **49**; `policy_effective_date_v1` **24**), plus **`[NCD CENSUS]`** (Active 139 · Stubs 4 · Retired 14 · Deleted 5 · Unknown 0 · Total 162). Any RED is a halt; surface YELLOW for decision.

**Mid-session `hash_verify` RED is normal** — it means canonical files have been edited since the previous handoff's §1 table was computed. The halt rule is about RED at **bootstrap**.

### §5.2 — Standing priority: finish the NCDs (Tom, S260)

**Re-measure `sources/` against the graph before planning** (§4 item 45) — it changed four times during S262–S263.

As of this close, **no NCD PDF is on hand without a graph individual**. The queue is five stubs needing renditions from Tom:

| Policy | Note |
| :--- | :--- |
| **NCD 20.4** | Implantable Automatic Defibrillators (ICDs); CED with registry requirements; expect multi-version |
| **NCD 210.3** | Colorectal Cancer Screening Tests; extensive coding, long revision history; expect multi-version |
| **NCD 280.13** | TENS - RETIRED; counted under **Retired**, not **Stubs** |
| **NCD 80.7** | Cited by NCD 80.8 for excluded refractive procedures |
| **NCD 10.1** | Cited by NCD 80.8's bundling rule |

Pre-Extraction requirement 5 applies: **every version, not just the one in effect**.

### §5.2a — After the NCDs

**Item 48 is the highest-value cheap item** — one paragraph promoting the bare-term linking rule, now backed by four policies. Then §4 items 37, 38, 40, 46, 47, 49, all small. Items 35 and 36 also stand.

### §5.3 — Do not

- `policies_processed` is **175** — advance it only on a genuine new extraction/promotion.
- Do not re-hardcode the audit namespace; do not re-add the frozen `LLM_ANNOTATED_VOCAB_CLASSES` tuple; do not promote the PyYAML lazy import to module level; do not split `SKILL.md` without agreement.
- `owl:versionInfo`, the `# Produced:` header date, and Tom-supplied `dc:source` URLs remain untouched.
- **Do not collapse `predicate_target_sort` to a single tier (S261).** V110/V111 guard both directions.
- **Do not re-introduce the literal-matching bug in `check_predicate_ordering` (S262 D7).** V112 pins it.
- **Do not split a single source unit that says *covered under X / not covered under Y* (S262 D6).** Keep it whole and dual-type it.
- **Do not assume a transmittal number identifies a document (S263 D2).** Check the era and check for an existing individual of the same number.
- **Do not trust an exact-prefLabel reuse search alone (S263 D5).** The forward URI pre-flight is the guarantee.
- **Do not conclude a text layer is damaged without re-extracting with `-enc UTF-8` (S262, NCD 160.9), and do not assume an apparent defect is tooling either (S263 D9, NCD 100.4).** Check.
- **Do not chase an authoritative CMS NCD index to measure remaining work (item 41).**
- **Do not read the census `Stubs` count as the promote queue, and do not count graph facts with a regex over the TTL (item 43).** Use rdflib.
- **Do not carry forward a previous session's "`sources/` is fully extracted" answer (item 45).**
- **Do not reprocess any already-extracted NCD until every NCD is processed (Tom, S260).**
- **Do not delete anything from `sources/`, and do not delete the Dropbox originals** (Tom, S260).
- **Do not read other policy-PDF locations.** `Dropbox\Projects\HOO2pilot\policies` is the sanctioned source directory.
- **Push at session close, not before.** The remote is the only off-machine copy of `sources/`.
