# GEM Policy-Extraction Handoff — Session 265 (2026-08-05)

## §1 — Canonical files (post-close state)

Hashes are md5 over the frozen output set; **M** marks a file changed this session. The canonical set is **15 files**.

| File | md5 | size | S265 |
| :--- | :--- | :--- | :--- |
| `GEM_ontology.ttl` | `5a77000e27e2ce03d6e2e0596e716934` | 340257 |  |
| `GEM_policy_instances.ttl` | `183fb0e21e319e09beade707db8e98d0` | 5958758 | **M** |
| `GEM_code_group_instances.ttl` | `10a70c01175dcf714a4bd8307bd07eeb` | 25942 |  |
| `cpt.ttl` | `351aa816b978ec63a6800feb50bfb5c4` | 35223 |  |
| `SKILL.md` | `16b5287f1a83ee45a0b1ef37a3bae7c5` | 284429 | **M** |
| `gem_reference.md` | `4ddd97d8b96dec2b4aff8e0318376c46` | 120152 |  |
| `gem_rule_categories.md` | `03119e90c0fd470ae08d8199b1c965a6` | 1493105 | **M** |
| `gem_edit_log.md` | `85717608a1c0d84be2aaf7f406e9277c` | 147289 | **M** |
| `gem_structured_rule_guide.md` | `5dc562fdf25cdd7a492969be2b82fee5` | 60817 |  |
| `gem_turtle_style_guide.md` | `0c82c21cb54232de2c731fb1dcfce117` | 26524 |  |
| `manifest_format.md` | `24d134579244454795e39b2be1ce80d3` | 26227 |  |
| `policy_worklist.json` | `35550e7dd263cfdbab53598bd0cc2454` | 322732 | **M** |
| `gem_llm_annotations.json` | `ae89620445889e7137e2bdc5ba4cd669` | 7213 |  |
| `worklist_schema.md` | `2519964abbdba260c621a6a5e9f8318b` | 16521 |  |
| `gem_audit.py` | `890ace764a5077b5031c1fb3fdd3001d` | 331607 |  |

## §2 — Work completed in S265

**One extraction: NCD 20.23, the policy S264's broken re-measure had hidden.** A short session by design — it closed item 50 by extracting its subject. No schema change (`GEM_ontology.ttl` byte-identical) and **no `gem_audit.py` change** — `policyVersion` is 1, so no `KNOWN_V1_DATES` row was due.

**Graph movement:** `policies_processed` **179 → 180**. Instances triples **53,698 → 53,792** (+94). Workflow `planDone` **179 → 180**; `planPromote` **759** and `planNone` **16** both unchanged. NCD census **Active 139 → 140**, Stubs 6, Retired 18, Deleted 5, Unknown 0, **Total 168 → 169**. Clinical concepts **2,949 → 2,957**; policy rules **1,974 → 1,977**. `referencesPolicy` **1243**, `revisesPolicy` **279**, `revisedByPolicy` **0** — **all three unchanged**, because NCD 20.23 cites nothing. Both INFO queues unchanged: `source_availability_unverified` **49**, `policy_effective_date_v1` **24**.

**Active +1 is the first in five extractions.** S264's four were all retirees; this is the run's first policy that actually determines coverage.

### (a) The extraction

| Policy | Rules | Concepts | Refs / new stubs | Δ |
| :--- | ---: | :--- | :--- | ---: |
| **NCD 20.23** Fabric Wrapping of Abdominal Aneurysms | 3 | 8 mint, 0 reuse | 0 / 0 | +94 |

Single-version longstanding non-coverage NCD, effective **1966-01-01** by the longstanding-NCD rule (the Tracking block declines to post a date, so the read moves to the Other Versions table). **No implementation date is published anywhere and none was manufactured** (S192). At 240 words it is among the smallest complete NCDs in the corpus, and it still yielded 3 rules and 8 concepts — **document length does not predict extraction yield.**

### (b) Two same-stem near-misses in five sentences (§3 D2)

The reuse search is lexical; the decision is semantic, and this policy produced two instances of the gap in one page:

| Surfaced | Why declined |
| :--- | :--- |
| `conceptFabricSupport` — *"Fabric Supports"* (NCD 280.1) | A **non-reusable DME supply** denied under §1861(n). A supply item, not a surgical technique. Shared word: "fabric". |
| `conceptAneurysmSurgery` (NCD 160.8 / TN 48) | A **procedural context for EEG monitoring**, not the aneurysm repair this policy names as the accepted treatment. |

Neither was a close call once read, but both would have been plausible auto-reuses on a label-similarity score. Recorded because the near-miss rate is what tells us whether the reuse search is safe to automate — and §4 item 49's proposed acronym-tolerant normalisation would have made **both of these more likely to fire**, not less.

### (c) The corpus reversed the recommendation, again (§3 D3)

**B2 — `conceptRupture` minted bare.** "Rupture" is the direct object of "prevent" in *"has not been shown to prevent eventual rupture"*, so it passes the S264 bare-term grammatical test and a concept is due. The open question was which form, and the draft recommendation was that a bare single-word concept would be too thin to be worth minting.

**Counting first showed the opposite is the established shape:**

| Bare concept | Qualified variants also present |
| :--- | :--- |
| `mortality` | `perioperative morbidity and/or mortality` |
| `bleeding` | `gastrointestinal bleeding`, `abnormal menstrual bleeding`, `major bleeding episode` |
| `hemorrhage` | `vitreous hemorrhage`, `pulmonary hemorrhage` |
| `metastasis` | `liver metastasis`, `metastases limited to the liver` |

**536 of 2,949 concepts (18%) carry single-token labels.** The pattern is: the bare event term is its own concept, and a qualified variant is minted only where a source states the qualifier. `conceptAneurysmRupture` was therefore rejected — *this clause* does not qualify the term. This is the third session running in which a measurement inverted a recommendation before it reached Tom (S263's mixed-polarity split, S264's `SKILL.md` No-Benefit-Category confirmation, this).

## §3 — Decisions (S265)

- **D1 (NCD 20.23 B1, Tom) — R3 is dual-typed `coverageScope` + `serviceDefinition`.** The external wall reinforcement sentence concedes a clinical indication for a *different* procedure while denying that procedure is the one being non-covered. One source unit, two assertions, kept whole — **the S262 D6 mixed-polarity shape applied to a pair that is not about polarity.** It is the policy's only non-negative content.
- **D2 — the reuse search returns lexical neighbours; the decision is semantic.** See §2(b). **Carry forward:** a same-stem hit is a prompt to read the existing concept's `gem:description`, not evidence of identity.
- **D3 (NCD 20.23 B2, Tom) — bare clinical-event concepts are the corpus's established shape.** See §2(c).
- **D4 — a source's own connective can decide the fold.** R1 folds three sentences (determination, evidentiary basis, statutory conclusion) because the source writes *"Accordingly"*; splitting them would leave the conclusion without its premise. Distinct from the enumerated-criteria fold rule — here the fold is licensed by a discourse marker, not by a disjunctive stem.
- **D5 — `statutoryFraming` fired on the strict test.** §1862(a)(1) is an actual citation. 199 corpus rules use the phrase "reasonable and necessary" and 173 of those cite no statute; the tag tracks the citation, not the phrase.

## §4 — Open items

Items 1–49 carry from S264 unless restated.

1. **Cadence checkpoint — next at 200.** `policies_processed` is **180**; 20 out. Not due.
2. **LCD/Article V1-date research — 18 candidates.** `policy_effective_date_v1` INFO = **24**, unchanged.
3. **CIM stub source availability — 49**, unchanged (S265 minted no transmittals of any kind).
4. **Era-gate mistokens — procedure established (S263), confirmed symmetric (S264); retrospective sweep still pending Tom.** Not exercised in S265.
5.–44. **Carry unchanged.**
45. **RE-MEASURED (S265), AND IT MOVED AGAIN DURING THE CLOSE.** `sources/` holds **333 PDFs, 260 NCD-named across 158 sections, 0 unparsed**. At the mid-session measure every section had a `planDone` individual; by the `git fetch` at close, **three renditions of NCD 220.6.13 had arrived** and the answer was stale within the hour. **This is the fifth consecutive session in which `sources/` changed mid-session.** Keep re-measuring; do not carry this answer forward.
46. **`predicate_order` vs `predicate_ordering` name mismatch.** Unchanged; still a live trap.
47. **Stub `dc:source` convention is inconsistent.** Unchanged; S265 minted no stubs.
48. **CLOSED (S264).**
49. **Carry, with a caution added (S265).** The proposed acronym-tolerant reuse pass would have made **both** of this session's near-misses (§2(b)) *more* likely to fire, not less. Normalising labels raises recall at the cost of precision, and the two failure modes are not symmetric: a missed reuse is caught by the forward URI pre-flight, while a **wrong** reuse silently merges two distinct clinical concepts and nothing catches it. **If item 49 is implemented, it must surface candidates for reading rather than auto-reuse.**

50. **CLOSED (S265) — by extracting its subject.** NCD 20.23 is in the graph. The corrected measurement (`^NCD\s*([0-9]+(?:\.[0-9]+)*)`, greedy, with an unparsed count that must be zero) now parses **158 sections, 0 unparsed**, and correctly surfaced the one section without a `planDone` individual. The instrument works; item 45 is the standing discipline that uses it.

51. **NEW (S265) — `sources/NCD 220.6.13.pdf` ×3 arrived during the close and is unextracted.** Three renditions: **2004-09-15**, 2005-01-28, 2009-04-03. A fifth FDG PET sibling, and **the first with a rendition predating the family's 2005-01-28 creation by TN 31** — which means its version history is *not* the shape the other four shared, and the S264 family findings should be tested against it rather than assumed. Committed with this close; first item for S266.

## §5 — Plan for S266

### §5.1 — Bootstrap (auto-authorized)

From the canonical directory, read the latest handoff in `handoffs/`, then run `python gem_audit.py --files-dir . --autofix` immediately, without asking. Expect a clean run with **no autofix write**, two INFO (`source_availability_unverified` **49**; `policy_effective_date_v1` **24**), plus **`[NCD CENSUS]`** (Active 140 · Stubs 6 · Retired 18 · Deleted 5 · Unknown 0 · Total 169). Any RED is a halt; surface YELLOW for decision.

**Mid-session `hash_verify` RED is normal** — it means canonical files have been edited since the previous handoff's §1 table was computed. The halt rule is about RED at **bootstrap**.

### §5.2 — Standing priority: finish the NCDs (Tom, S260)

**Re-measure `sources/` against the graph before planning** (§4 item 45), with the corrected regex, **printing the parsed-section and unparsed counts** so a collapse is visible rather than inferred.

**First: `NCD 220.6.13`, three renditions on hand** (§4 item 51). Ask Tom for the MCD URL. **Do not assume the S264 family pattern holds** — its 2004-09-15 rendition predates TN 31, so at minimum the version count, the creation transmittal and the date anchor differ. The four family findings worth *testing* rather than carrying: the benefit-category round-trip, the `§220.6` cross-reference, the TN 31 description, and whether V2 reports its own replacement.

Then the five stubs needing renditions from Tom:

| Policy | Note |
| :--- | :--- |
| **NCD 20.4** | Implantable Automatic Defibrillators (ICDs); CED with registry requirements; expect multi-version |
| **NCD 210.3** | Colorectal Cancer Screening Tests; extensive coding, long revision history; expect multi-version |
| **NCD 280.13** | TENS - RETIRED; counted under **Retired**, not **Stubs** |
| **NCD 80.7** | Cited by NCD 80.8 for excluded refractive procedures |
| **NCD 10.1** | Cited by NCD 80.8's bundling rule |

**`NCD 220.6` and `NCD 220.6.17` remain high-value promote targets** — both cited by all four extracted siblings; 220.6 is the parent the family was carved out of and now carries an inbound `revisesPolicy` from `tn31NCD`, and 220.6.17 is the section that replaced all of them.

### §5.2a — After the NCDs

§4 items 37, 38, 40, 46, 47, 49 (with the S265 caution), all small. Items 35 and 36 also stand.

### §5.3 — Do not

- `policies_processed` is **180** — advance it only on a genuine new extraction/promotion.
- Do not re-hardcode the audit namespace; do not re-add the frozen `LLM_ANNOTATED_VOCAB_CLASSES` tuple; do not promote the PyYAML lazy import to module level; do not split `SKILL.md` without agreement.
- `owl:versionInfo`, the `# Produced:` header date, and Tom-supplied `dc:source` URLs remain untouched.
- **Do not collapse `predicate_target_sort` to a single tier (S261).** V110/V111 guard both directions.
- **Do not re-introduce the literal-matching bug in `check_predicate_ordering` (S262 D7).** V112 pins it.
- **Do not split a single source unit that says *covered under X / not covered under Y* (S262 D6), or that asserts two things about one subject (S265 D1).** Keep it whole and dual-type it.
- **Do not retain removed content because it looks substantive (S264 D1).** Check only whether the removal is reported.
- **Do not carry a transmittal's edges across from a sibling policy (S264 D2).** Read its entry in the document in hand.
- **Do not treat a same-stem reuse hit as identity (S265 D2).** Read the existing concept's description first.
- **Do not assume a transmittal number identifies a document (S263 D2), in either direction (S264).** Check the era and check for an existing individual of the same number.
- **Do not trust an exact-prefLabel reuse search alone (S263 D5).** The forward URI pre-flight is the guarantee.
- **Do not conclude a text layer is damaged without re-extracting with `-enc UTF-8` (S262, S264 D5), and do not assume an apparent defect is tooling either (S263 D9).** Check.
- **Do not chase an authoritative CMS NCD index to measure remaining work (item 41).**
- **Do not read the census `Stubs` count as the promote queue, and do not count graph facts with a regex over the TTL (item 43).** Use rdflib.
- **Do not carry forward a previous session's "`sources/` is fully extracted" answer (item 45) — and do not trust a re-measure whose parsing you have not checked (item 50).** Print the section and unparsed counts.
- **Do not reprocess any already-extracted NCD until every NCD is processed (Tom, S260).**
- **Do not delete anything from `sources/`, and do not delete the Dropbox originals** (Tom, S260).
- **Do not read other policy-PDF locations.** `Dropbox\Projects\HOO2pilot\policies` is the sanctioned source directory.
- **Push at session close, not before.** The remote is the only off-machine copy of `sources/`.
