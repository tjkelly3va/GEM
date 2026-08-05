# GEM Policy-Extraction Handoff — Session 261 (2026-08-04)

## §1 — Canonical files (post-close state)

Hashes are md5 over the frozen output set; **M** marks a file changed this session. The canonical set is **15 files**.

| File | md5 | size | S261 |
| :--- | :--- | :--- | :--- |
| `GEM_ontology.ttl` | `5a77000e27e2ce03d6e2e0596e716934` | 340257 |  |
| `GEM_policy_instances.ttl` | `a604085786d70b6e6da1df06b3670555` | 5681892 | **M** |
| `GEM_code_group_instances.ttl` | `10a70c01175dcf714a4bd8307bd07eeb` | 25942 |  |
| `cpt.ttl` | `351aa816b978ec63a6800feb50bfb5c4` | 35223 |  |
| `SKILL.md` | `38c7ea479ae4e9953be6880a7109d416` | 281262 | **M** |
| `gem_reference.md` | `4ddd97d8b96dec2b4aff8e0318376c46` | 120152 |  |
| `gem_rule_categories.md` | `631725eba2938788a092a7232c090786` | 1400003 | **M** |
| `gem_edit_log.md` | `102cab0972438112bed9c05c9d8624fc` | 97320 | **M** |
| `gem_structured_rule_guide.md` | `5dc562fdf25cdd7a492969be2b82fee5` | 60817 |  |
| `gem_turtle_style_guide.md` | `0c82c21cb54232de2c731fb1dcfce117` | 26524 | **M** |
| `manifest_format.md` | `24d134579244454795e39b2be1ce80d3` | 26227 |  |
| `policy_worklist.json` | `86876baf1d3403dd1b487a36c83e42f9` | 322732 | **M** |
| `gem_llm_annotations.json` | `ae89620445889e7137e2bdc5ba4cd669` | 7213 |  |
| `worklist_schema.md` | `2519964abbdba260c621a6a5e9f8318b` | 16521 | **M** |
| `gem_audit.py` | `dee07e424955ec03b48e57e57253150d` | 329185 | **M** |


## §2 — Work completed in S261

S261 ran in **three parts**: one extraction, then the two items that extraction flagged, then the skill refinement it earned. The session opened on a false premise — Tom's *"I think that you were interrupted extracting policy 50.2"* — and the first finding was that nothing had been interrupted: the working tree was clean, `git log` ended at S260's last commit, and `ncd50.2` appeared **zero** times in `GEM_policy_instances.ttl`, `policy_worklist.json` and `gem_rule_categories.md`. Whatever ran before, it wrote nothing. There was nothing to resume, only to start.

**Graph movement:** `policies_processed` **163 → 164**; `referencesPolicy` **1121 → 1122**; `revisesPolicy` unchanged at **242**; `revisedByPolicy` stays **0**. NCD census **Active 130 → 131, Total 148 → 149** (Stubs 2, Retired 11, Deleted 5, Unknown 0). Instances triples **51,658 → 51,781**. `GEM_ontology.ttl` **unchanged** — no schema term was added or altered this session.

### (a) NCD 50.2 extracted — Electronic Speech Aids

Fresh extraction on Tom's request, `gemi:ncd50.2` (ncdid=237), never worklisted, minted direct to the graph. Two-turn: Plan manifest with eight borderlines, each Tom-confirmed, then Generate. **+123 triples, 3 rules.**

- **Source.** `sources/NCD 50.2.pdf` — text-layer (Skia/PDF, 4 embedded fonts), 2 pp, 246 words, complete and ungated, single pass. The text layer is **clean**: plain ASCII double quotes around the two terms of art, no curly quotes, no U+FFFD anywhere — contrast NCD 230.15 at S260, which needed a section sign asserted at emit time.
- **Not from the queue — the third demonstration in two sessions.** NCD 50.2 was absent from the graph entirely: not a `planPromote` stub, not cited by anything extracted, not on the worklist. It reached the corpus only because Tom named it. After NCD 20.15 and NCD 190.4 at S260, that is three in a row, and it is §4 item 41 shown rather than argued.
- **Version and dates.** Version 1, listed alone in the Other Versions table (`01/01/1966 - N/A`, "You are here"), so no cross-version retention walk applies. **Effective 1966-01-01**, read from the Other Versions table because the Tracking Information block declines to post it — the longstanding-NCD rule, the same read as NCD 130.4 and NCD 230.15. No implementation date published, none asserted. V1 in hand → **not** a `[107]` candidate, INFO unchanged at **24**, and **no `KNOWN_V1_DATES` row is owed** — the S260 D8 standing step applies only to `policyVersion > 1`. Pub. 100-3, section 50.2, pageCount 2.
- **Rules (3).** `r1` `serviceDefinition` — the two device types, Pattern 3. `r2` `serviceDefinition` + `eligibility` — the post-surgical / post-radiation model-selection conditional, Pattern 1. `r3` `coverageScope` + `eligibility` — the sole coverage statement, Pattern 1. No new axis-2 vocabulary; 3 tags used.
- **Concepts: 12 links, 12 mints, 0 reuse.** The first extraction since S260 began with **no concept reuse at all** — every phrasing this policy uses was new to the graph. Mints: `conceptElectronicSpeechAid`, `conceptSpeechAid` (B4), `conceptVibratingHead`, `conceptThroat`, `conceptMouth`, `conceptSoundWave` (all B7), `conceptRadicalNeckSurgery`, `conceptExtensiveRadiationToTheAnteriorPartOfTheNeck`, `conceptOralTubeModel`, `conceptThroatContactDevice` (both B5), `conceptLaryngectomy`, `conceptPermanentlyInoperativeLarynx` (B6). Four source plurals normalised to singular per S43.
- **1 reference, 0 new stubs.** The Cross Reference names the Medicare Benefit Policy Manual, Chapter 15 → `gemi:pub100_02_ch15`, already in the graph. The manual-chapter publication check passes: the citing text names the **Benefit Policy** Manual and that individual's `dc:source` is a `bp102c15.pdf` (Pub. 100-02) URL. The source renders a stray space before the comma (*"Manual , Chapter 15"*), a rendering artifact rather than content. The sentence yields the link but no rule — presence, not governance (the NCD 130.4 B5 shape).
- **Zero of nearly everything else, and one of those zeros is worth naming.** 0 ICD-10/HCPCS/CPT codes and **no Coding Information section at all**, 0 modifiers, 0 code groups, 0 healthcare settings. **0 provider credentials is an accurate zero**: the policy names only *"a patient"* and *"the user"*, and no performer, orderer or evaluator role appears anywhere in current prose, so the strict-prose rule licenses none. Recorded explicitly because an absent credential set and a missed one look identical in the graph. 1 benefit category (Prosthetic Devices, reuse).
- **Verification.** +123 triples **with the predicate histogram derived from the emitter's own structures and diffed against the actual set-diff** (S157): 20 predicates, **0 mismatches**, 0 triples removed. All 3 rules carry exactly one `gem:ruleDescription` and zero `gem:description`; all 12 concept links landed on `gem:refersToClinicalConcept`. Pre-flight URI audit ran all three directions — forward, inverse, and the S146 retiree check against `ncd50.2_DELETED` — 16 new URIs free. TTL re-parsed clean, 0 lone-LF, 0 tabs, terminal `.\r\n` intact.
- **Registry.** `### NCD 50.2` in `gem_rule_categories.md` and an S261 line in `gem_edit_log.md`, both authored in the same Generate turn (non-deferrable).

### (b) `checkpoint_cadence` retired from `policy_worklist.json` (§3 D8)

S260 D9 widened the cadence 20 → 40, and `SKILL.md` §Checkpoint Cadence claims *"The interval is stated here and nowhere else … so widening it again is a one-line edit rather than a hunt."* **That claim was false**: `policy_worklist.json` `metadata.checkpoint_cadence` still read `20`.

The field was **deleted, not corrected**. Nothing consumed it — no `gem_audit.py` check, no other reader — so it was documentation-grade state whose only effect was on a human or LLM reading the worklist and acting on the stale number. Deleting makes `SKILL.md`'s claim true **by construction** rather than by maintenance; updating it to 40 would only have reset the same hazard. `worklist_schema.md` drops the field from the metadata shape and carries a **tombstone** recording what it meant, why it went, and that a pre-S261 worklist carrying it is still valid.

A corpus sweep confirmed the other `20`-valued hits are historical records — `deferred_proposals` resolutions and past register entries, which S260 D9 deliberately left as written — and that `worklist_schema.md`'s remaining prose use is illustrative of the semantics, not an assertion of the current interval.

### (c) `predicate_target_sort` — new audit check, sweep, and a corrected style rule (§3 D9, D10)

This began as a cosmetic finding and turned into a corrected methodology rule. **Measuring the corpus before implementing the documented rule is what saved it**, and that sequence is the transferable part.

**The finding as first reported was wrong in its framing.** `gem_turtle_style_guide.md` §Predicate Ordering required repeated object-property targets to be sorted, and 34 policy blocks did not comply. The initial report implied the guide was the outlier; measurement showed the opposite — **107 of 141** blocks with 3+ concept links were already sorted. The drift was scattered from line 6,694 to line 59,686, i.e. intermittent across the project's whole life rather than a recent regression.

**Then the rule itself turned out to be wrong.** `gem:hasPolicyRule` targets are `gemi:<policy>_r<N>`, and the guide's blanket *"sort targets alphabetically by local name"* yields `_r1, _r10, _r11, _r2`. Measured: `gem:hasPolicyRule` is **131/131 numerically sorted** and only 80/131 lexicographic, and among the **51** blocks carrying ten or more rules exactly **0** are lexicographic. A check written from the sentence as it stood would have reported 51 correct blocks as drift and its autofix would have scrambled every large policy's rule links **while reporting success** — the S144 dead-check shape, an instrument agreeing with its specification and not with the corpus.

**Natural order cannot simply replace lexicographic either.** ICD targets go the other way: `gem:exclusivelyCoversCondition` is **21/23** lexicographic against 8/23 natural (`icd10:J96.11` before `icd10:J96.9`). Applying the numeric tier globally would have mis-sorted the code lists instead.

The corpus was already following an unwritten **two-tier** rule, now written down (Tom, §3 D9):

| Tier | Predicates | Order |
| :--- | :--- | :--- |
| Numbered children | `hasPolicyRule`, `hasPolicyGroup`, `hasPolicyCodingRule`, `hasAnchoredCodingScope` (`_r<N>`, `_group<N>`) | natural / numeric |
| Everything else | concepts, policies, credentials, benefit categories, settings, CRs, and code targets | lexicographic by local name |

- **`gem:ruleType` was checked for a semantic order and has none (§3 D10).** It entered scope late — the first measurement pass missed it because that regex only captured `gemi:`/code targets, which is why the reported run count moved 90 → 271. 857 rules carry ≥2 `ruleType`; 672 are alphabetical. Decisively, **35 of 126 distinct type-sets appear in more than one written order**, several near-even (`credentialedActor`+`documentation` 16 v 14; `studyDesign`+`outcomeMeasure` 13 v 12). A semantic convention would show one dominant direction. It is tier-2 drift and was swept.
- **The check.** `predicate_target_sort`, YELLOW, autofixable, `ALL_CHECKS` member, documented as checklist item **10a** inside the `AUDIT-CHECKLIST` sentinels. The autofix **rewrites only the target token in each line slot**, leaving indent, predicate and trailing punctuation in place — deliberate, because a run can be the last thing in a block and physically moving lines would move the `.` terminator with them. Runs are grouped **consecutively only**, so a reorder can never hop a target over an intervening predicate. Verification is stronger than a parse probe: a pure reorder must leave the parsed graph **identical as a set**, so the repair is probed by parsing and diffing triple sets, and any difference downgrades the finding to RED with no autofix offered. The probe runs only when there is something to repair, so a clean corpus costs no extra parse.
- **The sweep.** 271 runs across 9 predicates in `GEM_policy_instances.ttl`. **Graph identical: 51,781 triples before and after, 0 lost, 0 gained.** 60,699 CRLF, 0 lone-LF, 0 tabs, terminator intact. Re-run is a no-op (idempotent). A post-sweep per-subject verification found **0** unsorted runs across all three TTL files. The sweep also caught this session's own `ncd50.2_r2`, whose `ruleType` order was written `serviceDefinition, eligibility` and is now `eligibility, serviceDefinition` — the guard works on new work, not only legacy.
- **Self-test 108 → 111, all green.** V109 fires on the defect. **V110 and V111 are the point of the set**: V110 pins that the corpus's numeric `hasPolicyRule` order is GREEN, V111 that ICD targets stay lexicographic, so the two tiers cannot be collapsed in either direction. **Mutation-tested** — collapsing the check to lexicographic-everywhere fails V110, to natural-everywhere fails V111, and **V109 passes under both mutants**, which is the proof that V109 alone would have been coverage rather than a test. All three verified absent against the pre-edit script (`ValueError: Unknown check_category`) per the S144 regression-test rule.

### (d) `SKILL.md` §Rule Patterns — "a source section is not a Pattern unit" (§3 D11)

The NCD 50.2 B1+B2 decision promoted to methodology, inserted after Pattern 3's definition.

**Pattern 3's own wording was never wrong** — it already asks whether sentences form *"a single logical unit"*. What misleads is the **precedent set**: NCD 130.4, NCD 230.15, NCD 20.24, NCD 110.22 and NCD 230.12 each captured a whole Item/Service Description as one Pattern-3 `serviceDefinition` rule (all five verified against the graph as lone `serviceDefinition` `_r1` rules before being cited), and five worked examples pointing one way read as a shape that does not exist. In each of those the section happened to be a cohesive device or service description with no conditional in it — a fact about those five documents, not a rule about the section.

The note states the test as **the IF/THEN heuristic applied *inside* the section** and gives NCD 50.2 as the worked contrast. It also records the general lesson from how the decision was reached: when a sentence carries two readings, that is usually the signal it is its own rule **and** takes both `gem:ruleType` values, not the signal that one reading must win.

### (e) No edit-log entry for (b), (c) or (d)

Per S260 D5, `gem_edit_log.md` is scoped to **corpus** changes, and the S144/S145/S156–S159/S175/S182/S197/S237/S260 precedent is that audit-script and methodology sessions earn no entry. NCD 50.2 earns one because it is a corpus change. The sort sweep does not: `GEM_policy_instances.ttl` is byte-different but **graph-identical**, 0 triples gained or lost.

## §3 — Decisions (S261)

Eight extraction borderlines plus four methodology decisions, each Tom-confirmed individually.

- **D1 (B1+B2) — the Item/Service Description splits, and R2 is dual-typed.** Put as two separate borderlines; Tom's reply collapsed them: *"Both describe the service, but the second identifies a cause for using the device."* Sentence 3 is one IF/THEN, structurally distinct from sentences 1–2's taxonomy, so the section is not one logical unit; and because the sentence carries both readings, `r2` takes `serviceDefinition` **and** `eligibility`. A deliberate departure from the NCD 130.4 / NCD 230.15 shape — see §2(d).
- **D2 (B3) — `eligibility` on `r3`.** `coverageScope` carries the affirmative Part B / prosthetic-devices coverage; `eligibility` carries the two-leg patient-condition gate. The disjunction stays inside one rule — an internal OR does not fork.
- **D3 (B4) — mint `conceptSpeechAid` alongside `conceptElectronicSpeechAid`.** *"Speech aids"* is the subject of its own sentence, not a word-part fabricated from the composite. Redundant single-term coverage is a recall feature under the single-term-linkage rationale.
- **D4 (B5) — scare quotes dropped from prefLabels, head noun kept.** *"Oral tube model"*, *"throat contact device"*. The quotes mark a term of art; the head noun is what the source names (*"throat contact"* alone reads as a technique). Quoted forms survive verbatim in `r2`. Keeping the quotes was declined because it would put escaped quote characters into a `.ttl` literal — the corpus's most repeated authoring error (S157).
- **D5 (B6) — mint the composite `conceptPermanentlyInoperativeLarynx`; do NOT link `conceptLarynx`.** The source names a condition of the larynx, not the larynx as a concept in its own right. The S157 NCD 280.14 dual-capture shape was considered and declined: there is no heading here, so the broader term is never independently named.
- **D6 (B7) — bare anatomy and bare mechanism are minted.** Tom asked, before deciding, whether the corpus holds concepts that name only a body part or whether one must be supported by a medical condition. **It does, and none is required** — 18 bare-anatomy individuals across nine policies (`conceptAnus`/`Bladder`/`Cervix`/`Urethra`/`Uterus`/`Vagina`/`PelvicFloorMusculature` at TN 48; `Bone`/`BoneMarrow`/`Joint`/`SoftTissue` at NCD 190.15; `Brain`, `SpinalCord`, `Skin`, `Prostate`, `AnalCanal`, `AnalMusculature`, and **`conceptLarynx` itself** at A52492) plus 8 bare-mechanism individuals (`ElectricalCurrent`/`DirectCurrent`/`AlternatingCurrent`/`PulsedCurrent` at NCD 270.1, `Heat`, `Ultrasound`, `ElectricalStimulation`, `ElectricStimulation`). Bare *"tube"* not minted — the sentence's generic carrier; the specific form is `conceptOralTubeModel`.
- **D7 (B8) — `dc:source` is Tom-supplied.** `…/ncd.aspx?ncdid=237&ncdver=1`. The PDF's own footer publishes the same URL but truncates the query string after `&keyword=`; it was put to Tom rather than read off the footer, since the standing rule is that identifiers and URLs come from Tom.
- **D8 — `checkpoint_cadence` deleted, not corrected (Tom).** See §2(b). Deleting an unread field makes the single-home claim true by construction; correcting it would reset the same hazard.
- **D9 — the sort convention is two-tier, and the style guide was wrong (Tom).** See §2(c). Numbered children numerically, everything else lexicographically by local name. `gem_turtle_style_guide.md` now states both tiers **as a pair**, because each is what stops the other being over-applied.
- **D10 — `gem:ruleType` has no semantic order; it is tier 2.** Evidence, not assumption: 35 of 126 distinct type-sets appear in more than one written order, several near-even. Recorded so a future session does not re-open the question and read a primary/secondary convention into the data.
- **D11 — promote "a source section is not a Pattern unit" into `SKILL.md` §Rule Patterns (Tom).** Filed after Pattern 3's definition rather than in the decomposition framework, so a reader reaching for Pattern 3 meets the caveat there.
- **D12 — practice-repair is not subject to cost/benefit (Tom, standing).** Offered three dispositions for the sort drift (leave and record; check-and-sweep; retire the rule), Tom chose none of the framings and stated the principle: *"When we establish a practice, we need to follow it, even if it means that we need to work harder to repair deviations discovered later."* Arguments that the drift had been harmless for 260 sessions, that the payoff was only diff stability, and that §5.3 makes forward progress outrank revisiting finished policies were all **not** dispositive. **Carry this forward:** when drift from a documented convention surfaces, propose the repair plus the guard that prevents recurrence — not a case for leaving it.

## §4 — Open items

Items 1–41 carry from S260. Only the items whose substance moved are restated; the rest stand exactly as S260 left them.

1. **Cadence checkpoint — next at 200.** `policies_processed` is now **164**, so 36 policies out. Not due.
2. **LCD/Article V1-date research — 18 candidates (`[107]` remainder).** Unchanged: `a52467, a52492, a52494, a52495, a52510, a52514, a52517, a52519, a54969, a55426, a57115, a58075, lcd33612, lcd33718, lcd33797, lcd33800, lcd33923, lcd36524`. Blocked on Tom's renditions. `policy_effective_date_v1` INFO = **24**.
3. **CIM stub source availability — 42.** Unchanged. `source_availability_unverified` INFO = **42**.
4. **Possible era-gate mistokens among pre-crystallization transmittals (S236); CIM ceiling 169 (S247).** Pending Tom.
5.–13. **Referenced-document stubs** from NCD 220.5, 220.13, 210.4, 110.23, 90.2, 20.33, 40.1 and prior NCDs S234–S259. All `planPromote`. Item 11 (NCD 20.14) remains RESOLVED and untracked.
14.–30. **Carry unchanged from S259/S260.**
31. **Plan-turn reuse-search hygiene (S259).** Unchanged. Pending Tom's call.
32. **RESOLVED (S260)** — `gem-policy-docx` runtime verified. Not tracked.
33. **`SKILL.md` progressive-disclosure split — still deferred, and the file grew again.** S261 added the checklist item 10a line and the §Rule Patterns note. `SKILL.md` is loaded in full on every skill trigger. The split touches `CANONICAL_FILES`, the `skill_checklist_sync` sentinels and the §1 table, so it stays an agreed-scope decision, not a drive-by.
34. **RESOLVED (S260)** — `PYTHONUTF8` removed; the audit owns its output stream. Not tracked.
35. **`sources/` gitignore question — deferred (S260).** The directory remains tracked. If ever adopted, `.gitignore`'s comment block, `SKILL.md` §Session Close and `/gem-close` step 6 must change together. Note the S260 wording *"the repo currently has no remote"* is now stale — a remote exists and this session pushes to it.
36. **Two `sources/` files differ from their Dropbox originals (S260).** `A58824.pdf` and `NCA CAG-00296R3.pdf` are text-layer in `sources/` and still rasterized in Dropbox. A future re-copy would silently reintroduce the rasterized versions.
37. **Close `deferred_proposals[92]`? (S260 checkpoint, still pending Tom.)** Its standing trigger fires on a false 0-usage reading of two abstract parents carrying 3,252 and 410 triples through descendants. Recommendation unchanged: close it outright.
38. **Record the checkpoint census scope in `SKILL.md`? (S260, still pending Tom.)** The census must count across ontology + instances + code groups, not instances alone. One sentence closes it.
39. **RESOLVED — the promote-queue ratio needs no instrumentation.** At this session's close the graph held **709 `planPromote` stubs against 164 `planDone`**, and `policy_worklist.json` held 22 entries. Those counts are accurate as of S261; what was wrong was reading the gap as a problem.

    > **Resolved 2026-08-05 (S262), at Tom's request.** This item originally read *"Promote-queue ratio is invisible in the worklist (S260)… `policy_worklist.json` holds 22 entries and no longer reflects the backlog"* — a framing that treated the 709:164 ratio as a **measurement gap** needing a fix, with the candidate resolutions being to surface it in the audit's INFO tier or retarget the checkpoint's worklist-size agenda item. **It is neither. It is phase ordering.** Tom (2026-08-04): *"Now that I'm providing policies directly, we will typically have only a few stubs in the queue. Once we begin focusing on non-NCD policy documents, we'll consider all of the other stubs in the queue."* The `planPromote` population is overwhelmingly **non-NCD** — transmittals, change requests, NCAs, articles, LCDs — and is **deferred, not forgotten**: it comes into scope as a body when the corpus moves off NCDs. Do not propose instrumentation for the ratio, and do not read a small NCD queue as progress toward completion (see item 41, reframed the same day). No work is owed; the item stays on the books as the record of how it was raised. Carried forward in this resolved form as S262 §4 item 39.
40. **`memory edit #13` still reads as a followable pointer (S260).** Cosmetic; gloss it in place or drop the clause.
41. **The NCD queue is not the NCD corpus.** The graph holds **149** NCD sections, each either extracted or cited by something extracted. **S261 is the third consecutive demonstration**: NCD 50.2, like NCD 20.15 and NCD 190.4 before it, was absent from the graph entirely and reached the corpus only because Tom named it. That is the durable content of this item — **an empty or near-empty queue says nothing about how much NCD work remains**, because Tom is the intake, not the queue.

    > **Reframed 2026-08-05 (S262), at Tom's request.** The heading originally read *"The NCD corpus has no denominator — this gates 'all NCDs are processed'"*, and the item closed: *"Resolution needs an authoritative list — an MCD export or the Pub. 100-03 table of contents from Tom, or Tom's go-ahead to fetch and reconcile the CMS NCD index. **Raise this before declaring the NCD priority met.**"* **That framing treated a missing count as a blocker, and it is not one.** Tom (2026-08-05): *"there are less than 400 individual NCD policy documents… policies evolve, a few are retired or deleted, and new policies are created every few months… We'll keep gathering knowledge from policy documents — that's our goal."* So the scale is known well enough to work by, **the denominator moves**, and **completion is not the target**. Do **not** propose fetching or reconciling a CMS NCD index in order to measure remaining work or declare the phase finished, and do not present the corpus as nearly done. If an authoritative list earns its place later it will be for **change detection** — new issuances, revisions, retirements, deletions — which is S262 §4 item 44's future-work track, and Tom will say when to start it. Carried forward in this corrected form as S262 §4 item 41.

42. **NEW (S261) — the sort guard covers three TTL files; two are currently silent.** `predicate_target_sort` runs over `GEM_ontology.ttl` and `GEM_code_group_instances.ttl` as well as the instances file, and both are GREEN today with no repeated-target runs out of order. That is a real pass, not an inert one, but it means the tiers have only ever been exercised against the instances file's predicates. If a future session adds repeated object properties to the ontology or a code group whose targets carry numeric suffixes, confirm which tier they belong to rather than assuming tier 2.

## §5 — Plan for S262

### §5.1 — Bootstrap (auto-authorized)

From the canonical directory, read the latest handoff in `handoffs/`, then run `python gem_audit.py --files-dir . --autofix` immediately on the first prompt, without asking. Expect a clean run with **no autofix write**, two INFO (`source_availability_unverified` **42**; `policy_effective_date_v1` **24**), plus the always-on **`[NCD CENSUS]`** block (Active 131 · Stubs 2 · Retired 11 · Deleted 5 · Unknown 0 · Total 149). Any RED is a halt; surface YELLOW for decision.

**Sixteen simultaneous `hash_verify` YELLOWs** reading "present but not listed in handoff §1 table" is one cause, not sixteen problems: no handoff was resolved. `handoff_drift` and the `empirical_counts` session marker are silently inert in that state. Fix resolution first. A `handoff_resolution` YELLOW means handoffs exist in both `handoffs/` and the flat canonical directory — move or delete the flat copies.

### §5.2 — Standing priority: finish the NCDs (Tom, S260)

**Process all NCDs first. The other policy documents follow.** Unchanged, and it outranks §4 item 39's promote-queue analysis.

**The NCD queue is three policies**, all `planPromote` stubs:

> **Corrected 2026-08-05 (S262), at Tom's request.** This paragraph originally read *"The NCD queue is still exactly two policies"* and listed only NCD 20.4 and NCD 210.3. **It was wrong when written**, not made wrong by later work: `gemi:ncd280.13` already carried `gem:nextPlannedStep gem:planPromote` at this session's own close commit (`76d03ea`). The count was read off the audit's `[NCD CENSUS]` **`Stubs`** line, and that is not the promote queue — `ncd_census` tests **lifecycle before workflow**, so a `planPromote` NCD whose prefLabel carries the `- RETIRED` marker is counted under **Retired**. `Stubs 2` was correct as defined; reading it as the queue was the error. Enumerate remaining work by querying `gem:nextPlannedStep gem:planPromote` on `gem:NCDpolicy` directly — and with rdflib, not a line-anchored regex over the TTL, which undercounts because not every workflow-state assertion begins a line. Recorded as S262 §4 item 43. Only this paragraph and its table were amended; the rest of S261 stands as written.

| Policy | Title | Note |
| :--- | :--- | :--- |
| **NCD 20.4** | Implantable Automatic Defibrillators (ICDs) | CED policy with registry requirements; expect multi-version |
| **NCD 210.3** | Colorectal Cancer Screening Tests | Extensive coding, long revision history; expect multi-version |
| **NCD 280.13** | Transcutaneous Electrical Nerve Stimulators (TENS) - RETIRED | *(added by the S262 correction)* Retired in place, contents incorporated into NCD 160.27; counted under **Retired**, not **Stubs** |

**Source workflow.** NCD 20.4 and NCD 210.3 sit behind a CMS gate Tom can pass; **Tom drops the PDFs into `sources/`** and a session picks them up. Do not source them another way and do not extrapolate their URLs. Pre-Extraction requirement 5 applies: **every version, not just the one in effect**.

**But the queue is not the corpus (§4 item 41), and S261 is the third proof.** `sources/` should be re-checked for NCDs that have a PDF on hand but no graph individual — S260 verified that set was empty, and NCD 50.2's PDF was added after that check.

### §5.2a — After the NCDs

Cheap fill-in work, all still open: §4 items **37–40** — close `[92]`, add the census-scope sentence, retarget the worklist-size agenda item, gloss `memory edit #13`. Items 35 and 36 are also cheap. Note item 35's S260 wording is now stale on the remote question.

Then, subject to the NCD priority: process the next policy, or promote a `planPromote` stub through its own Plan/Generate cycle. **Reprocessing remains closed** until every NCD is processed (§5.3).

### §5.3 — Do not

- `policies_processed` is **164** — advance it only on a genuine new extraction/promotion.
- Do not re-hardcode the audit namespace — detection is deliberate (Option B, S255).
- Do not re-add the frozen `LLM_ANNOTATED_VOCAB_CLASSES` tuple.
- Do not promote the PyYAML lazy import to module level.
- Do not split `SKILL.md` without agreement (item 33).
- `owl:versionInfo`, the `# Produced:` header date, and Tom-supplied `dc:source` URLs remain untouched.
- **Do not collapse `predicate_target_sort` to a single tier (S261).** Lexicographic-everywhere scrambles `_r1, _r10, _r11, _r2` across 51 policies; natural-everywhere mis-sorts the ICD lists. V110 and V111 exist to make either collapse turn the suite red — if one of them fails, the check was changed, not the corpus.
- **Do not read a primary/secondary convention into `gem:ruleType` order (S261 D10).** It was measured and has none.
- **Do not reprocess any already-extracted NCD until every NCD is processed (Tom, S260).** Standing constraint; supersedes any individual reprocessing flag on the books, including `SKILL.md`'s NCD 240.2 R1 `long- term` note.
- **Do not delete anything from `sources/`, and do not delete the Dropbox originals** (Tom, S260). Deletions happen only on an explicit request naming the files, and are not to be volunteered.
- **Do not read other policy-PDF locations.** `Dropbox\Projects\HOO2pilot\policies` is the sanctioned source directory; `OneDrive\Projects\HOO2pilot\policies`, `Dropbox\Projects\GEMrag\docRepository` and any others are off-limits unless Tom names them.
- **Push at session close, not before.** `/gem-close` performs the push, only after the audit is GREEN and the §1 table is computed. The remote is the only off-machine copy of `sources/`.
