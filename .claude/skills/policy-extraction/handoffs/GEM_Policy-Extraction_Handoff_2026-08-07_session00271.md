# GEM Policy-Extraction Handoff — Session 271 (2026-08-07)

## §1 — Canonical files (post-close state)

Hashes are md5 over the frozen output set; **M** marks a file changed this session. The canonical set is **15 files**.

| File | md5 | size | S271 |
| :--- | :--- | :--- | :--- |
| `GEM_ontology.ttl` | `5a77000e27e2ce03d6e2e0596e716934` | 340257 |  |
| `GEM_policy_instances.ttl` | `b6198b8dd23a2bbec4df7c43f1548369` | 6343689 | **M** |
| `GEM_code_group_instances.ttl` | `10a70c01175dcf714a4bd8307bd07eeb` | 25942 |  |
| `cpt.ttl` | `351aa816b978ec63a6800feb50bfb5c4` | 35223 |  |
| `SKILL.md` | `31e9a60f6f3ac1cfc3bb17804e6feca9` | 285703 | **M** |
| `gem_reference.md` | `bd2a8164afcf31ccfeda5dc242fd6f63` | 121808 |  |
| `gem_rule_categories.md` | `e1f75630110e389a7a57dcbd3ae50a0c` | 1616489 | **M** |
| `gem_edit_log.md` | `4e8226979d1ce61c47b9386531b766fe` | 199412 | **M** |
| `gem_structured_rule_guide.md` | `5dc562fdf25cdd7a492969be2b82fee5` | 60817 |  |
| `gem_turtle_style_guide.md` | `0c82c21cb54232de2c731fb1dcfce117` | 26524 |  |
| `manifest_format.md` | `24d134579244454795e39b2be1ce80d3` | 26227 |  |
| `policy_worklist.json` | `dfeb86b008030ed2577830cd9ddd89a3` | 322732 | **M** |
| `gem_llm_annotations.json` | `ae89620445889e7137e2bdc5ba4cd669` | 7213 |  |
| `worklist_schema.md` | `2519964abbdba260c621a6a5e9f8318b` | 16521 |  |
| `gem_audit.py` | `ae3025e53c1f2309aec856ed3a572079` | 340169 |  |

## §2 — Work completed in S271

**Three extractions and one corpus-wide predicate repair.** The session opened on the largest lab NCD yet extracted (NCD 190.34, 9 rules and 65 concept links) and closed on two of the smallest policies in the corpus (NCD 150.8 at 232 words, NCD 110.11 at 216). **No schema change** — `GEM_ontology.ttl` byte-identical. `gem_audit.py` also unchanged: all three policies are `policyVersion` 1, so **no `KNOWN_V1_DATES` row was owed** (S260 D8 fires only above V1).

**Graph movement:** `policies_processed` **192 → 195**. Instances triples **55,816 → 56,422** (+606). Workflow `planDone` **192 → 195**, `planPromote` **803 → 806**, `planNone` **17** unchanged. NCD census **Active 144 → 147**, **Total 180 → 183**; Retired **26**, Stubs **5**, Deleted **5**, Unknown **0** unchanged. Clinical concepts **3,041 → 3,106** (+65); policy rules **2,047 → 2,059** (+12); credentials **138** and settings **26** unchanged. `referencesPolicy` **1439 → 1443**, `revisesPolicy` **340 → 343**, `revisedByPolicy` **0** (invariant), `referencesChangeRequest` **189 → 197**.

**`sources/` gained 3 PDFs** (367 → 370). Re-measured at close: **370 PDFs, 297 NCD-named across 172 sections, 73 non-NCD, and 0 sections without a `planDone` individual.** See §5.2.

### (a) The extractions

| Policy | Rules | Concepts | Refs / new stubs | Δ |
| :--- | ---: | :--- | :--- | ---: |
| **NCD 190.34** Fecal Occult Blood Test — **ACTIVE** | **9** | 50 mint, 15 reuse (65 links) | 6 + 1 CR / **2** | **+437** |
| **NCD 150.8** Fluidized Therapy Dry Heat — **ACTIVE** | 2 | 11 mint, **0 reuse** | **0** / 0 | +107 |
| **NCD 110.11** Food Allergy Testing and Treatment — **ACTIVE** | 1 | 4 mint, 1 reuse | 1 / **1** | +62 |

All three S157-verified against a predicate histogram derived from each emitter's own data structures: **0 mismatches, three for three**. The only triples removed all session were the **3** legacy edges converted by the §2(b) repair.

**NCD 190.34 is the seventh sibling of the 07/2002 lab negotiated-rulemaking batch** (after 190.25, 190.15, 190.20, 190.26, 190.19, 190.24) and by some margin the largest. `tn17NCD` and `pmAB02110` each gained a reciprocal `revisesPolicy` edge; `pub100_04_ch16` and `ncd210.3` were reused; **zero new transmittal stubs**. Its two new stubs are `cag00180N` (NCA) and `cag00187N` (**CAL**, typed `gem:NCAdocument` per S196 B9) — **the first policy in the corpus to carry both an NCA and a CAL section**. Both are source-pending.

### (b) The lab-batch policy→CR predicate repair

The batch disagreed with itself about whether a policy links the change request its Revision History names. Measured before deciding: **189** `referencesChangeRequest` edges (82 distinct CRs) against **3** legacy `referencesPolicy`→CR triples, **all three inside this batch** (`ncd190.20` → cr2130, cr3690; `ncd190.19` → cr2130). Four siblings omitted the edge entirely, and **`ncd190.26`'s `workflowDescription` cites a "NCD 190.20 precedent" that says the opposite of what 190.20 does**, while `ncd190.24` regressed against `ncd190.19`'s B6 resolution to include. Matching the batch was impossible because the batch has no single shape. Repaired: 3 legacy edges converted, the missing edge backfilled onto `ncd190.25`, `ncd190.15`, `ncd190.26`, `ncd190.24`. **Zero legacy policy→CR edges now remain corpus-wide** and all seven siblings carry one predicate.

### (c) Two rulings that together draw one line

At **NCD 150.8 B2** Tom expanded a four-way qualifier cross product into its combinations, *even though the disjunction excluded nothing*. At **NCD 110.11 B1** he declined to split a head noun whose coordinated modifiers name one procedure. Combined: **expand the qualifiers, do not split the head.** Opposite directions in one session, one coherent principle, and neither derivable from the other. Both overrode the extractor's recommendation; both recommendations are recorded in full so the next case is argued against the ruling.

## §3 — Decisions (S271)

- **D1 (190.34 B1/B2, Tom-confirmed) — the same discriminator, applied twice in one policy, produced a split and a join.** The iron-deficiency-anemia sentence **splits** from the causes catalog sharing its paragraph: it is permissive-modal and operative, what follows is flatly descriptive and opens a new subject — a modal shift with no grammatical dependence across the boundary (S266 D2). The three fecal-hemoglobin assay types stay **one** rule: no modal shift, and the lead-in's *"each directed at a different component"* is a claim about the set that only the three items complete. **A test that only ever produces one answer is a preference; this one produced both.**
- **D2 (190.34 B3, Tom-confirmed) — a batch with no single shape is repaired, not matched.** See §2(b). `referencesChangeRequest` is a sub-property of `referencesPolicy`, so the conversion entails what the legacy form asserted and loses nothing.
- **D3 (190.34 B4, Tom's ruling, overriding the recommendation) — a word-form variant is a distinct phrasing.** `conceptHiatalHernia` is minted rather than reusing `conceptHiatusHernia`. The extractor recommended reuse — adjectival and nominal forms of one Latin root, no content word and no scope change (S268 D6), citing S257's "anti-resorptive" fold and S270 D7's hyphen reuse, and noting that reuse would give the existing individual a second citer from an unrelated policy. **The ruling governs: word-form differences are not folded the way punctuation and articles are.**
- **D4 (190.34 B5, Tom-confirmed) — metastasis is minted by site, and the bare form is not linked.** `conceptMetastasisToTheGastrointestinalTract`, per the `conceptLiverMetastasis` / `conceptDistantMetastasis` precedent; bare `conceptMetastasis` exists and is declined because the source never names it unqualified. Source-fidelity flag: *"primary and secondary metastases"* is loose usage — a primary tumor is not a metastasis — and stays verbatim per Core Principle 8.
- **D5 — the only near-code in NCD 190.34 was declined at its hardest.** R9 directs the reader to report *"the HCPCS code for colorectal cancer screening; fecal-occult blood test, 1-3 simultaneous determinations"* — a full descriptor with **no code number anywhere in six pages**. Core Principle 2 forbids inferring it. The document all but hands the code over; the rule still says no.
- **D6 (150.8 B2, Tom's ruling, overriding the recommendation) — an enumerated qualifier set is expanded into its combinations, even when the disjunction excludes nothing.** *"Acute or subacute traumatic or nontraumatic musculoskeletal disorders of the extremities"* yields four concepts. The extractor recommended the head concept alone, reasoning that inclusive disjunctions exhaust the space and therefore narrow nothing — strip them and the extension is unchanged — unlike NCD 220.6.8 B2's load-bearing *"dysfunctional but viable"*. **The head concept and bare `conceptMusculoskeletalDisorder` are not minted**, and NCD 220.6.9 B2's recorded worry about minting every layer of an *X of Y of Z* chain is answered here.
- **D7 (110.11 B1, Tom's ruling, overriding the recommendation) — a coordinated modifier pair naming one procedure is not split into two, even though the head noun is shared.** *"Provocative and neutralization testing"* is one technique, so the three route qualifiers yield **three** concepts, not six. The extractor recommended six on the source's own coordination — repeated identically in its Revision History — **while flagging the contrary clinical fact in the same breath**, that provocation-neutralization is one procedure with a provoking and a neutralizing dose. Tom ruled on exactly that ground. **Both halves of the extractor's behaviour mattered: had the counter-argument not been surfaced, there would have been nothing to rule on.**
- **D8 (150.8 B3, 110.11 B2, Tom-confirmed) — two smaller calls, each reversed or confirmed by measurement rather than intuition.** The apparatus terms *are* minted (`conceptFinelyDividedSolidParticles`, `conceptHeatedAirStream`): the extractor had planned to drop them as device physics, and measuring the corpus showed it already mints `conceptHeatedHumidifierTubing`, `conceptImmersionHeater` and — hours earlier the same session — `conceptLongDistanceRunning`. Dropping them would have applied a stricter standard to one policy for no reason but its size. And the route set does **not** distribute over *"neutralization therapy"*, which spans the routes rather than being split by them; distributing it would have narrowed what the policy excludes.
- **D9 — a transmittal's manual suffix is dated against the series before its URI is written.** NCD 110.11 cites a bare "Transmittal Number 35" from 05/1989. **Both numbered series exist in the graph**: `tn31NCD`–`tn38NCD` are Pub. 100-03 NCD Manual (2005 era), while `tn33CIM`, `tn34CIM` (04/1989), `tn36CIM` and `tn38CIM` (08/1989) are Coverage Issues Manual. TN 35 falls exactly between `tn34CIM` and `tn38CIM`, so **`tn35NCD` would have merged a 1989 CIM transmittal into the 2005 series — a silent identity collision no audit check catches.** The audit then confirmed the reading from the other direction: `transmittal_manual_token` RED, *"manual token 'CIM' requires `gem:publicationNumber "6"`"*.
- **D10 — three self-inflicted errors this session share one cause, and it is not regexes.** (i) The B3 pre-count was reported as 4 legacy edges because an unanchored regex also matched the predicate quoted as **prose** inside `ncd190.19`'s `workflowDescription`; it is 3. (ii) An emitter guard then fired on its own `workflowDescription` sentence *"NO `gem:policyImplementationDate` is asserted"*. (iii) A stub-count query returned 0 because the file was read with newline translation on, so `\r\n` never matched. **Every canonical file in this corpus quotes predicate names in prose and every TTL is CRLF, so any check that treats a file as flat text will find its own documentation.** All emitter guards now run through one line-anchored `asserts_no()` helper reading with `newline=''`.
- **D11 — "first in the corpus" is a measurement, not an impression.** The NCD 190.34 register originally called its empty Tracking-block "Version Number" field *"the first occurrence in the corpus"*, asserted without counting. Scanning all 297 NCD renditions in `sources/`: **77 (26%) print an empty Version Number** — an ordinary MCD rendering artifact. **The correction is recorded in place rather than deleted**, because the false claim is the kind that reads as evidence to the next session. Applied immediately afterward: NCD 150.8's "zero references is ordinary" is stated as 26 measured policies.
- **D12 — an emitter that mints a stub owns that stub's workflow-run entry and the run header's count.** NCD 190.34's first Generate run drew two `workflow_state` REDs because the new stubs never joined the `planPromote` run. The step was missing because **S269 and S270 minted zero new stubs across six extractions**, so no recent emitter carried it.
- **D13 — `git checkout --` is only a safe undo while the working tree holds one extraction.** The D12 fix was made by reverting the TTL and correcting the emitter, keeping one source for the S157 histogram. The D9 fix could **not** be: the TTL by then held all three extractions with no intermediate commit, so a revert would have destroyed NCD 190.34 and NCD 150.8 as well. It was patched from the emitter's own data and the **whole** diff re-verified against the pre-110.11 snapshot.

## §4 — Open items

Items 1–59 carry from S270 unless restated.

1. **Cadence checkpoint — next at 200.** `policies_processed` is **195**; **5 out**. The item-52 agenda entry stands and is now close enough to plan for.
2. **LCD/Article V1-date research — 24 candidates.** `policy_effective_date_v1` INFO unchanged.
3. **CIM stub source availability — now 52.** `tn35CIM` joins the `source_availability_unverified` INFO list (51 → 52). `tn106CIM` and `tn113CIM` remain the two strong `sourceUnobtainable` candidates awaiting Tom's direction.
4. **Era-gate mistokens — retrospective sweep still pending Tom.** No new collisions in S271; D9 was a *prospective* near-miss, caught before the URI was written.
5.–51. **Carry unchanged.**
52. **DEFERRED to the 200-policy checkpoint (Tom, S266).** Now 5 policies out.
53. **No audit check covers banner presence.** Unchanged; all three S271 sections were fresh top-level mints with their own banners.
54. **`sources/` filename convention.** Census now **166 dated · 94 undated · 37 versioned** (297 NCD-named across 172 sections). All three S271 arrivals used `NCD X vN.pdf`.
55. **`gemi:ncd220.12` bare-identifier `prefLabel`.** Unchanged; still no rendition in `sources/`.
56. **The benefit-category round-trip has no known cause.** Unchanged at ten of eleven; nothing in S271 touched the 220.6 family.
57. **TN 13401's "update the Policy section" wording** still awaits its own extraction. Unchanged.
58. **No autofix maintains the `# Policies processed:` header list.** The emitter-owned fix held for all three S271 extractions — `processed_list` never fired. Audit-side option still open, still not urgent.
59. **`cag00098N` / `cag00099N` doubly-cited but source-pending.** Unchanged.
60. **NEW (S271) — four NCA/CAL stubs now await URLs, not two.** `cag00180N` and `cag00187N` join `cag00098N` and `cag00099N`. `cag00187N` is the more interesting of the pair: it is a **CAL**, and NCD 190.34 is the first policy in the corpus citing both an NCA and a CAL section. All four are extractable only if Tom supplies URLs; none is urgent.
61. **NEW (S271) — no audit check would catch a wrong transmittal manual suffix.** `transmittal_manual_token` verifies the suffix against `gem:publicationNumber` **once both are present**, but nothing detects a `tnNNNCIM`/`tnNNNNCD` URI assigned to the wrong series in the first place — the two series overlap numerically (D9). A check comparing a transmittal stub's cited date against the CIM/NCD era boundary would close it. Small, and it prevents a silent identity collision.

## §5 — Plan for S272

### §5.1 — Bootstrap (auto-authorized)

From the canonical directory, read the latest handoff in `handoffs/`, then run `python gem_audit.py --files-dir . --autofix` immediately, without asking. Expect a clean run with **no autofix write**, two INFO, plus **`[NCD CENSUS]`** (Active 147 · Stubs 5 · Retired 26 · Deleted 5 · Unknown 0 · Total 183). Any RED is a halt; surface YELLOW for decision.

**Mid-session `hash_verify` RED is normal.** The halt rule is about RED at **bootstrap**.

### §5.2 — Standing priority: finish the NCDs (Tom, S260)

**Check `sources/` before naming any NCD target** (Tom, S267) — cross-reference `^NCD\s+<section>` over `sources/*.pdf`, tolerating all three filename forms (§4 item 54), against `planDone` read from the **graph**.

Measured at the S271 close: **0 of 172 NCD sections in `sources/` lack a `planDone` individual.** As at S267, S268 and S270, **every remaining NCD target needs a rendition from Tom before it can be planned.** Do not name a target without checking first.

Standing candidates, **none of which is in `sources/`**: NCD 20.4 (Implantable Automatic Defibrillators; CED with registry requirements), NCD 210.3 (Colorectal Cancer Screening; extensive coding, and now cited by NCD 190.34), NCD 280.13 (TENS - RETIRED), NCD 80.7, NCD 10.1, NCD 220.12 (SPECT, §4 item 55).

### §5.2a — After the NCDs

§4 items 53, 54, 57, 58, 60, 61 are small and each prevents a recurrence — **61 is the newest and the sharpest**, since the failure it guards is silent. Then 52 (at the 200 checkpoint, now 5 policies out), 4, 37, 38, 40, 46, 47, 49. Items 35 and 36 also stand. `sources/` holds **73 non-NCD PDFs** — the deferred non-NCD phase, available if Tom redirects, **not** to be started unprompted.

### §5.3 — Do not

- `policies_processed` is **195** — advance it only on a genuine new extraction/promotion.
- Do not re-hardcode the audit namespace; do not re-add the frozen `LLM_ANNOTATED_VOCAB_CLASSES` tuple; do not promote the PyYAML lazy import to module level; do not split `SKILL.md` without agreement.
- `owl:versionInfo`, the `# Produced:` header date, and Tom-supplied `dc:source` URLs remain untouched.
- **Do not split a head noun whose coordinated modifiers name one procedure (S271 D7) — but do expand an enumerated qualifier set into its combinations (S271 D6).** Expand the qualifiers, do not split the head.
- **Do not fold a word-form variant into an existing concept (S271 D3).** "Hiatal" beside "hiatus" is a mint. Punctuation (S270 D7) and articles (S268 D6) still fold.
- **Do not match a batch that has no single shape — repair it (S271 D2).** And do not trust a `workflowDescription`'s account of a precedent without reading the precedent: `ncd190.26`'s was backwards.
- **Do not infer a code from its descriptor (S271 D5).** NCD 190.34 R9 names one in full and gives no number.
- **Do not assign a transmittal's manual suffix by default (S271 D9).** Date it against the CIM/NCD series first; the two overlap numerically and a wrong suffix is a silent identity collision.
- **Do not test a canonical file as flat text (S271 D10).** Every one quotes predicate names in prose and every TTL is CRLF: anchor to line starts and read with `newline=''`.
- **Do not write "first in the corpus" into a canonical file without counting (S271 D11).** 26% of renditions had the "unique" trait.
- **Do not mint a stub without its `planPromote` workflow-run entry and header count (S271 D12)**, and **do not assume `git checkout --` is available as an undo once the tree holds more than one extraction (S271 D13)** — patch and re-verify the full diff instead.
- **Do not halt on a single-version policy (S270 D1).** One rendition with no ending effective date and "You are here" is the complete set.
- **Do not type "covered only for X" as `nonCoverage` (S270 D3).** The source must name the excluded thing.
- **Do not decide a rule split on the source's numbering alone (S270 D2).** Check whether the sub-provision carries its own effective dates.
- **Do not mint a bare form that appears only inside a composite (S270 D4)** — and do not decline a nested layer that is itself a substantive clinical entity (S270 D5).
- **Do not proceed on an approved reading after finding a contrary precedent (S270 D6).** Surface it; the corpus's recorded practice outranks a fresh judgement. S271 D7 is the same move made *before* approval.
- **Do not retain a removed rule because it is a non-coverage determination (S270 D8), because it is negative (S269 D3), because it delegates (S269 D2), or because there is a lot of it (S267 D1).**
- **Do not join a removed exclusion to a live exception across documents (S269 D4).** Core Principles 8 and 10.
- **Do not take a policy's title from a transmittal that cites it (S269 D5).**
- **Do not leave the `# Policies processed:` header list to the close (S269 D6).** The emitter owns it.
- **Do not propose a third causal reading of the benefit-category round-trip (S268 D1, §4 item 56).**
- **Do not drop a reference because the text citing it was removed (S268 D3).**
- **Do not split a table row into per-cell rules (S268 D4), and do not collapse a decision table into one rule.**
- **Do not mint a provenance paragraph as a rule (S268 D5).**
- **Do not lower `CIM_MAX_TN` (S267 D4).**
- **Do not mint a transmittal or change request because it is known to exist (S267 D4).**
- **Do not assert `sourceAvailability` from the archive-line pattern (S267 D5).**
- **Do not duplicate a transmittal across a differing CR or effective date within one manual (S267 D3).**
- **Do not read a cumulative revision history as the complete reference set (S267 D7).**
- **Do not link a mention within a mention (S264 D2).**
- **Do not link an existing concept merely because the reuse search surfaced it (S270).** NCD 150.8 refused four candidates and reused nothing.
- **Do not collapse `predicate_target_sort` to a single tier (S261).** V110/V111 guard both directions.
- **Do not re-introduce the literal-matching bug in `check_predicate_ordering` (S262 D7).** V112 pins it.
- **Do not restore the ambiguous block regex (S266 D4).** V115 pins it.
- **Do not remove `block_terminator` as redundant with `predicate_order` (S266 D4).**
- **Do not treat a clean rdflib triple-count as sufficient verification of emitted bytes (S266 D5).**
- **Do not treat the source's own lettering as the rule count (S266 D2).**
- **Do not carry a family finding forward untested (S266 D1).**
- **Do not treat a same-stem reuse hit as identity (S265 D2).** Read the existing description first.
- **Do not assume a transmittal number identifies a document (S263 D2), in either direction (S264), or within one policy's own version set (S267 D2).** S271 D9 extends this to the manual suffix.
- **Do not chase an authoritative CMS NCD index to measure remaining work (item 41).**
- **Do not count graph facts, or file structure, with a regex over the TTL (item 43, S266).** Use rdflib.
- **Do not name an NCD target without cross-referencing `sources/` first (Tom, S267).**
- **Do not reprocess any already-extracted NCD until every NCD is processed (Tom, S260).**
- **Do not delete anything from `sources/`, and do not delete the Dropbox originals** (Tom, S260).
- **Do not read other policy-PDF locations.** `Dropbox\Projects\HOO2pilot\policies` is the sanctioned source directory.
- **Push at session close, not before.** The remote is the only off-machine copy of `sources/`.
