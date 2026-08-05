# GEM Policy-Extraction Handoff — Session 262 (2026-08-05)

## §1 — Canonical files (post-close state)

Hashes are md5 over the frozen output set; **M** marks a file changed this session. The canonical set is **15 files**.

| File | md5 | size | S262 |
| :--- | :--- | :--- | :--- |
| `GEM_ontology.ttl` | `5a77000e27e2ce03d6e2e0596e716934` | 340257 |  |
| `GEM_policy_instances.ttl` | `9fa3f2f7078e9741b01b0539880957fa` | 5709370 | **M** |
| `GEM_code_group_instances.ttl` | `10a70c01175dcf714a4bd8307bd07eeb` | 25942 |  |
| `cpt.ttl` | `351aa816b978ec63a6800feb50bfb5c4` | 35223 |  |
| `SKILL.md` | `7ab089d094d44f097d9aafa762127ed2` | 281863 | **M** |
| `gem_reference.md` | `4ddd97d8b96dec2b4aff8e0318376c46` | 120152 |  |
| `gem_rule_categories.md` | `4305932718b5376da21d925af0f7d7f8` | 1413569 | **M** |
| `gem_edit_log.md` | `c16e214da65ad073211757895ca3e4eb` | 104297 | **M** |
| `gem_structured_rule_guide.md` | `5dc562fdf25cdd7a492969be2b82fee5` | 60817 |  |
| `gem_turtle_style_guide.md` | `0c82c21cb54232de2c731fb1dcfce117` | 26524 |  |
| `manifest_format.md` | `24d134579244454795e39b2be1ce80d3` | 26227 |  |
| `policy_worklist.json` | `588e694793cc507507b20a3ec6579c00` | 322732 | **M** |
| `gem_llm_annotations.json` | `ae89620445889e7137e2bdc5ba4cd669` | 7213 |  |
| `worklist_schema.md` | `2519964abbdba260c621a6a5e9f8318b` | 16521 |  |
| `gem_audit.py` | `ca42901d454c76526ad484f2e4175322` | 329222 | **M** |

## §2 — Work completed in S262

Two extractions and one methodology sentence. No schema change: `GEM_ontology.ttl` is **byte-identical**, and `gem_audit.py`'s only edit is a data row, not logic.

**Graph movement:** `policies_processed` **164 → 166**; `referencesPolicy` **1122 → 1124**; `revisesPolicy` **242 → 244**; `revisedByPolicy` stays **0**. NCD census **Active 131 → 132, Retired 11 → 12, Total 149 → 151** (Stubs 2, Deleted 5, Unknown 0). Instances triples **51,781 → 51,933** (+152). Workflow state `planDone` **164 → 166**, `planPromote` **709 → 710**.

### (a) NCD 30.4 extracted — Electrosleep Therapy - RETIRED (§3 D1, D2)

Three-version retirement-lifecycle NCD, `gemi:ncd30.4` (ncdid=20). Never worklisted; minted direct on Tom's request. **+44 triples, 1 rule, 1 concept, 1 new stub.**

- **Sources.** Three text-layer renditions (4 embedded fonts each), 2 pp each, complete and ungated: V1 239 w, V2 211 w, V3 222 w. All-versions-supplied, so references are taken from every version.
- **The ninth member of the TN 11892 batch-retirement family** (110.19, 160.6, 160.22, 180.2, 190.4, 20.25, 210.4, 230.11, 240.2.2). `gemi:ncd180.2` is the exact structural twin — the same *"no national coverage determination (NCD) is appropriate at this time for X"* sentence plus the same MAC-delegation clause — and served as the template.
- **Dates.** V1 effective **1966-01-01**, read from the Other Versions table under the longstanding-NCD rule; S192 anchor. **No implementation date** — V2 publishes 06/22/2021 and V3 publishes 04/10/2023, V1 publishes none, and S192 drops rather than inherits. `KNOWN_V1_DATES["ncd30.4"] = ("1966-01-01", None)` added in the same Generate turn — **the first live exercise of the S260 D8 standing step**, which S261 was exempt from (NCD 50.2 is V1). The audit's "already confirmed" count moved **53 → 54** and the `[107]` INFO stayed at **24**, which is what that row buys.
- **Rule.** One rule, `coverageScope` + `statutoryFraming` + `gem:delegatesCoverageTo gemi:credentialMedicareAdministrativeContractor` — verbatim the `ncd180.2_r1` shape, both sentences kept in one rule.
- **Retired in place, not `_DELETED` — stated as a template call, not re-put to Tom.** V3 is a live MCD page with a version number and the `- RETIRED` title, so it takes the bare URI with `isInEffect true`, which `ncd_census` requires to corroborate the marker. Settled by NCD 190.4 B1 / NCD 160.6 B1 and seven siblings.
- **Transmittals.** V1 names none. **TN 10838 minted** (`gemi:tn10838NCD`, `planPromote`) with `gem:revisesPolicy gemi:ncd30.4` — it delivered the V2 removal, a change under the S151 transmittal-edge rule. Its `dc:source` is the **Coverage Transmittal Link printed in the V2 rendition** (the `tn181NCD` precedent), not an extrapolated URL. **TN 11892** accumulates `gem:revisesPolicy gemi:ncd30.4`, **9 revised policies → 10**; its `workflowDescription` takes the usual `(added S262 …)` accretion and its `description` is left alone. No CR named in either stamp.
- **Zeros.** 0 codes / modifiers / code groups / credentials / settings — V3 has **no Coding Information section at all**. 0 benefit categories (D1).
- **Source-fidelity note.** V3's published *Ending Effective Date* (01/01/2021) **precedes its own effective date** (04/10/2023). An MCD retired-version display characteristic, recorded rather than corrected — the NCD 160.6 B7 precedent.
- **Verification.** Predicate histogram derived from the emitter structures and diffed against the actual set-diff (S157): **21 predicates, 0 mismatches**; 45 added, 1 removed (the `tn11892NCD` workflowDescription rewrite). Pre-flight ran all three directions including the S146 `ncd30.4_DELETED` retiree check.

### (b) NCD 160.15 extracted — Electrotherapy for Treatment of Facial Nerve Paralysis (Bell's Palsy) (§3 D3–D6)

Single-version longstanding non-coverage NCD, `gemi:ncd160.15` (ncdid=94), the `ncd130.4` / `ncd230.15` shape from S260. **+108 triples, 2 rules, 13 concept links (11 mints, 2 reuse), 0 references, 0 new stubs.**

- **Source.** `sources/NCD 160.15.pdf`, text-layer, 2 pp, 259 words, complete and ungated. Effective **1966-01-01** (longstanding, Other-Versions read); no implementation date. `policyVersion 1`, so **no `KNOWN_V1_DATES` row is owed** and it is not a `[107]` candidate — the S260 D8 step fires only above V1. Benefit category Physicians' Services (reuse).
- **R1 captures the Item/Service Description whole as one Pattern-3 `serviceDefinition` rule**, because neither sentence carries an IF/THEN. This is **the S261 D11 test applied inside the section, reaching the opposite answer from NCD 50.2**, where sentence 3 was a conditional and forced a split. Stated as a template call rather than put to Tom now that the test is written down.
- **R2 takes `nonCoverage` only.** The reason given is empirical (*"because its clinical effectiveness has not been established"*) and no statute appears anywhere in the document — unlike `ncd230.15_r2`, whose §1862(a)(1) citation earns it `statutoryFraming`.
- **0 policy references and 0 new stubs.** No Cross Reference section, no Transmittal Information field, no NCA section. Corroborated independently: the audit needed **no** empirical-counts rewrite after this extraction, leaving 244 / 1124.
- **Verification.** 19 predicates, **0 mismatches**, 108 added, **0 removed**.

### (c) `SKILL.md` §Extraction Taxonomy — the "No Benefit Category" sentence (§3 D1, promoted)

Tom asked for the NCD 30.4 B1 decision to be promoted to methodology. Added to the **Benefit categories** row: a live version whose Benefit Category field reads *"No Benefit Category"* yields **no link at all** — a stated absence, not a missing value — and a category listed only by a superseded version is not carried forward. Plus a Destination-column clause that **zero links is a valid, precedented state**, naming the six policies that carry it.

**The round-trip warning is the load-bearing half.** Without it the next session meets `ncd160.22`'s recorded note (*"V2 carried 'No Benefit Category'; V3 restores Diagnostic Tests (other)"*) and reasonably concludes the field is noise to be looked through. Both failure directions are now named: carrying a stale category forward, and treating an empty set as a gap to fill.

### (d) The promote queue is not the Stubs bucket (§4 item 43, new)

Preparing §5.2 surfaced that **the NCD queue is three policies, not two**: `ncd20.4`, `ncd210.3` and **`ncd280.13`** (Transcutaneous Electrical Nerve Stimulators - RETIRED). S261 §5.2 said "exactly two", and the census agrees — because `ncd_census` tests **lifecycle before workflow**, so a `planPromote` NCD carrying a `- RETIRED` prefLabel lands in **Retired**, not **Stubs**. `Stubs 2` is correct as defined and is *not* the promote queue. Recorded as item 43; no graph change.

### (e) No edit-log entry for (c) or (d)

Per S260 D5, `gem_edit_log.md` is scoped to corpus changes. Both extractions earn a line; the `SKILL.md` sentence and the queue finding do not.

## §3 — Decisions (S262)

- **D1 (NCD 30.4 B1) — no benefit category is asserted (Tom).** V1 listed Physicians' Services; the live V3 lists *"No Benefit Category"*. Capture-current-version-metadata-only governs, so the policy asserts none and V1's value is recorded in prose. **First member of the TN 11892 batch to carry zero** — every sibling kept one because its live version listed one, and `ncd160.22` and `ncd180.2` each *round-tripped* back to their original category at V3, which is exactly the trap. Five extracted NCDs already carried zero, and neither `SKILL.md` nor `gem_audit.py` addressed the field, which is why it was put rather than assumed. Promoted to `SKILL.md` the same session — see §2(c).
- **D2 (NCD 30.4 B2) — V1's content is removed, not retained (Tom).** V2 reports that CMS determined no NCD is appropriate, and **V3 carries no Item/Service Description section at all**, so the documented-removal rule fires (NCD 190.4 B2, NCD 160.6 B5) and S151 cross-version retention does not. 0 retained rules; the ten V1-only concepts unminted under the S152 corollary. **The legible contrast is `ncd160.22`**, whose Item/Service Description survives *on the live version* and is therefore kept: **the test is what the live version carries, not which retirement verb CMS used.**
- **D3 (NCD 160.15 B1) — the therapy is minted three ways (Tom).** The composite `conceptElectrotherapyForTheTreatmentOfFacialNerveParalysis` — literally the Item/Service Description sentence's subject, so named rather than fabricated — plus bare `conceptElectrotherapy` and `conceptFacialNerveParalysis`, the NCD 50.2 B4 single-term-linkage shape (S261 D3). Both single terms were independently absent from a 2,844-concept graph. **The instructive contrast is NCD 130.4**: same *"X for Treatment of Y"* title form, but **no composite**, because there the *body text's* subject was the bare therapy name. **Title-not-a-mint-site (S253) is what separates the two policies** — a future session comparing them by title alone would read the difference as inconsistency.
- **D4 (NCD 160.15 B2) — `conceptGalvanicCurrent` and `conceptFaradicCurrent` minted (Tom).** *"an electrical current with controlled frequency, intensity, wave form and type (galvanic or faradic)"* — the parenthetical enumerates values of the type of the electrical current named in the same sentence, so the head noun is supplied by the source rather than invented. Matches NCD 270.1's direct / alternating / pulsed current family; *"faradic"* is already live via NCD 130.4's `conceptNoxiousFaradicStimulation`.
- **D5 (NCD 160.15 B3) — `conceptFacialMuscle`, not `conceptAffectedFacialMuscle` (Tom).** *"Affected"* is **anaphoric** — it points back to the paralysis already named — rather than a defining property, so it is dropped; plural normalised per S43. Contrast **NCD 230.15 B3**, where *"small portable generator"* kept its qualifiers because they describe the device itself. The distinction to carry: a qualifier that points elsewhere in the sentence is discourse, not content.
- **D6 (NCD 160.15 B4) — bare *"frequency"*, *"intensity"*, *"wave form"* not minted (Tom).** Generic device parameters with no qualifier attaching them to anything; the corpus's precedents (`conceptStimulusFrequency`, `conceptStimulusIntensity`) are qualified. The NCD 50.2 B7 "bare tube" call. *"A device"* likewise not minted.

## §4 — Open items

Items 1–42 carry from S261. Only the items whose substance moved are restated; the rest stand exactly as S261 left them.

1. **Cadence checkpoint — next at 200.** `policies_processed` is now **166**, so 34 policies out. Not due.
2. **LCD/Article V1-date research — 18 candidates (`[107]` remainder).** Unchanged. `policy_effective_date_v1` INFO = **24**; the "already confirmed" tally moved 53 → **54** on NCD 30.4's new row.
3. **CIM stub source availability — 42.** Unchanged. TN 10838 carries a `dc:source` and is not a CIM, so it does not enter this queue.
4.–13. **Unchanged from S261.**
14.–32. **Carry unchanged.**
33. **`SKILL.md` progressive-disclosure split — still deferred, and the file grew again.** S262 added the benefit-category sentences to §Extraction Taxonomy. Still an agreed-scope decision, not a drive-by.
34.–38. **Unchanged.** Items 37 (close `deferred_proposals[92]`) and 38 (record the checkpoint census scope) remain cheap and pending Tom.
39. **RESOLVED (S262, Tom).** The promote-queue ratio is now **710 `planPromote` against 166 `planDone`**, and it needs no instrumentation. Tom: *"Now that I'm providing policies directly, we will typically have only a few stubs in the queue. Once we begin focusing on non-NCD policy documents, we'll consider all of the other stubs in the queue."* It is **phase ordering, not a measurement gap**. Do not propose surfacing the ratio in the INFO tier, and do not read a small NCD queue as progress toward completion. Left on the books as the record of how it was raised; no work owed.
40. **`memory edit #13` still reads as a followable pointer.** Cosmetic; unchanged.
41. **REFRAMED (S262, Tom) — the NCD corpus has no denominator, and does not need one.** Tom: *"there are less than 400 individual NCD policy documents… policies evolve, a few are retired or deleted, and new policies are created every few months… We'll keep gathering knowledge from policy documents — that's our goal."* **Completion is not the target**, and the denominator moves. Do **not** propose fetching or reconciling a CMS NCD index in order to measure remaining work or declare the phase finished, and do not present the corpus as nearly done. If an authoritative list earns its place later it will be for **change detection** — new issuances, revisions, retirements, deletions — which is the future-work track named below, and Tom will say when to start it. The framing carried by **both S260 and S261** ("Raise this before declaring the NCD priority met") is superseded; both were reframed in place on 2026-08-05 at Tom's request, each with a dated note preserving the original wording.
42. **The sort guard's tiers have only ever been exercised against the instances file's predicates.** Unchanged; both other TTLs remain GREEN with no repeated-target runs out of order.

43. **NEW (S262) — the census's `Stubs` bucket is not the promote queue.** `ncd_census` tests **lifecycle before workflow**, so a `planPromote` NCD whose prefLabel carries the `- RETIRED` marker is counted under **Retired**. `gemi:ncd280.13` (Transcutaneous Electrical Nerve Stimulators - RETIRED) is exactly that case, which is why S261 §5.2 recorded the NCD queue as two policies when the graph holds **three**. The census line is correct as defined; the error was reading `Stubs` as the queue. **When enumerating remaining work, query `gem:nextPlannedStep gem:planPromote` on `gem:NCDpolicy` directly** — and use rdflib, not a line-anchored regex over the TTL, which undercounts because not every workflow-state assertion sits at the start of a line (a regex read of the same file returned 423 of the true 710).

44. **NEW (S262) — policy-change management is named future work (Tom).** Policies evolve, retire and appear every few months, and Tom has stated that methods to support those changes come later. The groundwork already exists in the graph — `gem:revisesPolicy`, the `_DELETED` retiree convention, `gem:isInEffect`, and the retirement-lifecycle shape now exercised across ten policies — so this is a design task, not a data-collection one. Not scheduled; recorded so it is not re-derived.

## §5 — Plan for S263

### §5.1 — Bootstrap (auto-authorized)

From the canonical directory, read the latest handoff in `handoffs/`, then run `python gem_audit.py --files-dir . --autofix` immediately on the first prompt, without asking. Expect a clean run with **no autofix write**, two INFO (`source_availability_unverified` **42**; `policy_effective_date_v1` **24**), plus the always-on **`[NCD CENSUS]`** block (Active 132 · Stubs 2 · Retired 12 · Deleted 5 · Unknown 0 · Total 151). Any RED is a halt; surface YELLOW for decision.

**Fifteen simultaneous `hash_verify` YELLOWs** reading "present but not listed in handoff §1 table" is one cause, not fifteen problems: no handoff was resolved. `handoff_drift` and the `empirical_counts` session marker are silently inert in that state. Fix resolution first. A `handoff_resolution` YELLOW means handoffs exist in both `handoffs/` and the flat canonical directory — move or delete the flat copies.

**Mid-session `hash_verify` RED is normal and is not the halt case.** Once a session edits any canonical file, its row stops matching the §1 table of the *previous* handoff, which describes a closed state. S262 ran at 6 RED / 0 YELLOW for most of its length. The halt rule is about RED at **bootstrap**, before anything has been edited.

### §5.2 — Standing priority: finish the NCDs (Tom, S260)

**Process all NCDs first. The other policy documents follow.** Unchanged.

**The NCD queue is three policies** (queried directly on `gem:nextPlannedStep`, not read off the census `Stubs` line — see §4 item 43):

| Policy | Title | Note |
| :--- | :--- | :--- |
| **NCD 20.4** | Implantable Automatic Defibrillators (ICDs) | CED policy with registry requirements; expect multi-version |
| **NCD 210.3** | Colorectal Cancer Screening Tests | Extensive coding, long revision history; expect multi-version |
| **NCD 280.13** | Transcutaneous Electrical Nerve Stimulators (TENS) - RETIRED | Retired in place, contents incorporated into NCD 160.27; counted under Retired, not Stubs |

**Source workflow.** Tom drops the PDFs into `sources/` and a session picks them up. Do not source them another way and do not extrapolate their URLs. Pre-Extraction requirement 5 applies: **every version, not just the one in effect**.

**But the queue is not the corpus.** S262's two extractions were the fourth and fifth policies to reach the graph only because Tom named them. Re-check `sources/` for NCDs with a PDF on hand but no graph individual; as of this close that set is **empty** — all four PDFs added this session are extracted.

### §5.2a — After the NCDs

Cheap fill-in work, all still open: §4 items **37, 38, 40** — close `[92]`, add the census-scope sentence, gloss `memory edit #13`. Items 35 and 36 are also cheap. Item 39 is resolved and needs nothing.

Then, subject to the NCD priority: process the next policy, or promote a `planPromote` stub through its own Plan/Generate cycle — **TN 10838** is new to the queue this session. **Reprocessing remains closed** until every NCD is processed (§5.3).

### §5.3 — Do not

- `policies_processed` is **166** — advance it only on a genuine new extraction/promotion.
- Do not re-hardcode the audit namespace — detection is deliberate (Option B, S255).
- Do not re-add the frozen `LLM_ANNOTATED_VOCAB_CLASSES` tuple.
- Do not promote the PyYAML lazy import to module level.
- Do not split `SKILL.md` without agreement (item 33).
- `owl:versionInfo`, the `# Produced:` header date, and Tom-supplied `dc:source` URLs remain untouched.
- **Do not collapse `predicate_target_sort` to a single tier (S261).** V110 and V111 exist to make either collapse turn the suite red — if one of them fails, the check was changed, not the corpus.
- **Do not read a primary/secondary convention into `gem:ruleType` order (S261 D10).** It was measured and has none.
- **Do not chase an authoritative CMS NCD index to measure remaining work (S262, item 41).** Completion is not the goal.
- **Do not read the census `Stubs` count as the promote queue (S262, item 43).**
- **Do not reprocess any already-extracted NCD until every NCD is processed (Tom, S260).** Standing constraint.
- **Do not delete anything from `sources/`, and do not delete the Dropbox originals** (Tom, S260). Deletions happen only on an explicit request naming the files, and are not to be volunteered.
- **Do not read other policy-PDF locations.** `Dropbox\Projects\HOO2pilot\policies` is the sanctioned source directory; others are off-limits unless Tom names them.
- **Push at session close, not before.** `/gem-close` performs the push, only after the audit is GREEN and the §1 table is computed. The remote is the only off-machine copy of `sources/`.
