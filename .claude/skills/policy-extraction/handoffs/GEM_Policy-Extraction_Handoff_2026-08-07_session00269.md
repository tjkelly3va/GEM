# GEM Policy-Extraction Handoff — Session 269 (2026-08-07)

## §1 — Canonical files (post-close state)

Hashes are md5 over the frozen output set; **M** marks a file changed this session. The canonical set is **15 files**.

| File | md5 | size | S269 |
| :--- | :--- | :--- | :--- |
| `GEM_ontology.ttl` | `5a77000e27e2ce03d6e2e0596e716934` | 340257 |  |
| `GEM_policy_instances.ttl` | `a27f6d1fa5a6f49b4ee2e104e00e49f5` | 6207443 | **M** |
| `GEM_code_group_instances.ttl` | `10a70c01175dcf714a4bd8307bd07eeb` | 25942 |  |
| `cpt.ttl` | `351aa816b978ec63a6800feb50bfb5c4` | 35223 |  |
| `SKILL.md` | `16d6fc642bb33b95c18d9f40e7fdb1e1` | 285703 | **M** |
| `gem_reference.md` | `bd2a8164afcf31ccfeda5dc242fd6f63` | 121808 |  |
| `gem_rule_categories.md` | `f46d9aba8d2429feec11685ef335f367` | 1566508 | **M** |
| `gem_edit_log.md` | `f092ac2ab325153e928c9c259f720e4e` | 180509 | **M** |
| `gem_structured_rule_guide.md` | `5dc562fdf25cdd7a492969be2b82fee5` | 60817 |  |
| `gem_turtle_style_guide.md` | `0c82c21cb54232de2c731fb1dcfce117` | 26524 |  |
| `manifest_format.md` | `24d134579244454795e39b2be1ce80d3` | 26227 |  |
| `policy_worklist.json` | `351968f6223f7d46bbcfcb8566343543` | 322732 | **M** |
| `gem_llm_annotations.json` | `ae89620445889e7137e2bdc5ba4cd669` | 7213 |  |
| `worklist_schema.md` | `2519964abbdba260c621a6a5e9f8318b` | 16521 |  |
| `gem_audit.py` | `0c07534bba96de83d60b44fe88bb599e` | 340120 | **M** |

## §2 — Work completed in S269

**Three extractions, all fresh direct mints, all zero-borderline.** NCD 220.6.2 (Lung Cancer), NCD 220.6.5 (Lymphoma) and NCD 220.6.6 (Melanoma) are the eighth, ninth and tenth FDG PET siblings. Each was **absent from the graph entirely with zero inbound citers**, each is a replacement-lifecycle section whose live V3 states its removal in one sentence, and each yielded **exactly +41 triples** — the same shape three times over. No schema change (`GEM_ontology.ttl` byte-identical).

**Graph movement:** `policies_processed` **186 → 189**. Instances triples **55,438 → 55,561** (+123). Workflow `planDone` **186 → 189**; `planPromote` **803** and `planNone` **17** unchanged. NCD census **Retired 22 → 25**, **Total 174 → 177**; Active **142**, Stubs **5**, Deleted **5**, Unknown **0** all unchanged. Clinical concepts **3,027** unchanged; policy rules **2,034 → 2,037**; credentials **138** and settings **26** unchanged. `referencesPolicy` **1385 → 1418**, `revisesPolicy` **318 → 333**, `revisedByPolicy` **0** (invariant), `referencesChangeRequest` **178 → 184**.

**`sources/` gained 10 PDFs** (353 → 363). Re-measured at close: **363 PDFs, 290 NCD-named across 167 sections, 0 unparsed, and — for the first time since S267 — ONE section without a `planDone` individual: NCD 220.6.8.** See §5.2.

### (a) The extractions

| Policy | Rules | Concepts | Refs / new stubs | Δ |
| :--- | ---: | :--- | :--- | ---: |
| **NCD 220.6.2** FDG PET for Lung Cancer — RETIRED | 1 | 0 | 11 + 2 CRs / **0** | +41 |
| **NCD 220.6.5** FDG PET for Lymphoma — RETIRED | 1 | 0 | 11 + 2 CRs / **0** | +41 |
| **NCD 220.6.6** FDG PET for Melanoma — RETIRED | 1 | 0 | 11 + 2 CRs / **0** | +41 |

All three share the TN 31 date pair **2005-01-28 / 2005-04-18**, all three carry `policyVersion` 3, and all three took a `KNOWN_V1_DATES` row in the same Generate turn per S260 D8. All three were S157-verified against a predicate histogram derived from the emitter's own data structures: **0 mismatches, three for three, 0 triples removed.**

**The reference set is now a family constant.** `ncd220.6.2`, `.5` and `.6` each carry the identical 13 targets already held by `ncd220.6.3` — `ncd220.6`, `ncd220.6.17`, `tn31NCD`, `tn106NCD`, `tn108NCD`, `tn120NCD`, `tn11892NCD`, `tn527CP`, `tn956CP`, `tn1817CP`, `tn1833CP`, `cr3741`, `cr6632` — with the same five inbound `revisesPolicy` edges and the same two-step Claims Processing Instructions narrowing (V1 four, V2 two, V3 none), so `tn527CP` and `tn956CP` are recoverable from V1 alone under S267 B5.

### (b) Three tests of the removal rule, in increasing order of temptation

Each extraction put the S151/S152 removal rule under a heavier load than the last, and it held all three times:

| | What V1 carried | Why it was tempting to keep |
| :--- | :--- | :--- |
| **220.6.2** | 1,193 words — **the longest V1 of any replaced sibling** | sheer volume (four numbered parts, 1998–2005) |
| **220.6.5** | an explicit **MAC delegation** of restaging medical-necessity determinations | it is the exact sentence that carries `delegatesCoverageTo` in live rules |
| **220.6.6** | the family's only explicit **non-coverage** statement, stated twice | a *negative* rule is what a claims evaluator most wants kept |

All three yielded **0 retained rules and 0 clinical concepts**. Volume is not a reason to retain (S267 D1 on a small document); a rule that no longer exists cannot delegate; and a removed exclusion is as removed as a removed grant.

### (c) The benefit-category round-trip, recorded and not acted on

Present at all three (V1 Diagnostic Tests (other) → V2 "No Benefit Category" → V3 restored). The family tally is now **nine of ten** replaced sections. **No third causal reading was proposed** — the TN 106/108/120 reading was falsified at S266 and the replacement reading at S268 — per S268 D1 and §4 item 56. The live-version rule decided the value in every case, as it has for all twelve family members.

## §3 — Decisions (S269)

- **D1 — three zero-borderline extractions in one session is a result, not a shortcut.** Every call was decided by a rule confirmed across the eight preceding siblings: retention by S151/S152, the benefit category by the live-version rule, rule granularity by the `ncd220.6.15_r1` / `ncd220.6.3_r1` precedent, concepts by S152/S253, transmittal edges by S151/S169, mention-within-mention by S264 D2, reference scope by S267 B5. Each Plan turn said so plainly rather than manufacturing a question. **This is what a family looks like after its conventions are settled** — and it is worth recording precisely because a run of silent Plan turns can otherwise read as diligence decaying rather than convention working.
- **D2 — a live MAC delegation inside removed content gets no triple (220.6.5).** V1 states that *"the determination of the medical necessity for a PET scan for re-staging lymphoma is the responsibility of the local Medicare contractor"* — the exact sentence shape that carries `gem:delegatesCoverageTo gemi:credentialMedicareAdministrativeContractor` elsewhere in the corpus. It sits inside removed V1 rule content and gets nothing. **A rule that no longer exists cannot delegate.** This reaches the `ncd160.6` B3 outcome by the opposite route: there the delegation was simply absent; here it was present and went out with its rule. The distinction matters because the sentence is quotable, and quotability is not retention.
- **D3 — a removed exclusion is as removed as a removed grant (220.6.6).** V1 states twice that *"FDG PET is not covered for the evaluation of regional nodes"*, the family's only explicit non-coverage statement. It earns no rule for the same reason the positive content earns none. Recorded as a decision rather than a note because it is the removal rule's hardest case: a negative rule is the kind a downstream claims evaluator would most want kept, and that is not a reason to keep it.
- **D4 — no cross-document inference from a removed exclusion to a live exception.** `ncd220.6.17`'s synopsis table gives Melanoma a "Cover with exceptions" row whose footnote qualifies the initial-treatment-strategy cell, and it is inviting to read 220.6.6's regional-nodes exclusion as its ancestor. **No such edge is asserted.** Neither text makes the connection; Core Principle 10 (policies as jigsaw pieces) leaves the joining to downstream, and Core Principle 8 forbids synthesizing a claim the source never makes even when it would be convenient.
- **D5 — the cited document is authoritative for its own identity even when the citer supplies a WRONG title, not merely none.** TN 106's 09/2009 entries name `ncd220.6.5` *"FDG PET for Lymphoma **Cancer**"* and `ncd220.6.6` *"FDG PET for Melanoma **Cancer**"*. Neither word appears in either section's own title in any version, and **two occurrences make it a habit of TN 106's entries rather than a typo**. Both transmittal edges stand (the entries name their sections explicitly, S264 D2); both `prefLabel`s come from the sections' own renditions. This extends S268 D7, which settled the case where the citing document gives no title; here it gives a wrong one, and the discriminator is unchanged — availability of the **cited** document decides.
- **D6 — the TTL header processed-list update belongs in the emitter, not the close.** At 220.6.2 the mid-session audit raised `processed_list` YELLOW (header list 186, graph `planDone` 187): the `# Policies processed:` line in `GEM_policy_instances.ttl`'s header is a canonical artifact that no autofix maintains. It was corrected by hand, then **folded into the emitter as a fourth build step** for 220.6.5 and 220.6.6, both of which came out clean. A step that has to be remembered is a step that will be forgotten; the emitter already owns the bytes (S157/S158 contract), and this is one more property it should own.

## §4 — Open items

Items 1–57 carry from S268 unless restated.

1. **Cadence checkpoint — next at 200.** `policies_processed` is **189**; 11 out. Not due. The item-52 agenda entry stands.
2. **LCD/Article V1-date research — 18 candidates.** `policy_effective_date_v1` INFO unchanged.
3. **CIM stub source availability.** `tn106CIM` and `tn113CIM` remain the two strong `sourceUnobtainable` candidates awaiting Tom's direction rather than inference.
4. **Era-gate mistokens — retrospective sweep still pending Tom.** No new collisions in S269; the case rests at the nine from S267–S268.
5.–51. **Carry unchanged.**
52. **DEFERRED to the 200-policy checkpoint (Tom, S266).** Unchanged; nothing promoted this session, so no relocation was in scope.
53. **No audit check covers banner presence.** Unchanged. All three S269 sections were fresh top-level mints with their own banners, so neither known shape of the gap was exercised.
54. **`sources/` filename convention — the third form is now well established.** All 10 S269 arrivals use `NCD X vN.pdf`. Census now **166 dated · 94 undated · 30 versioned** (290 NCD-named).
55. **`gemi:ncd220.12` bare-identifier `prefLabel`.** Unchanged — still no rendition. D5 above sharpens the rule that governs it.
56. **The benefit-category round-trip has no known cause.** Now **nine of ten** replaced sections. Two readings falsified. Do **not** propose a third without evidence from outside the 220.6 family, and do not let the pattern influence what is written — the live-version rule already decides it.
57. **TN 13401's "update the Policy section" wording** still awaits its own extraction. Unchanged.
58. **NEW (S269) — no autofix maintains the `# Policies processed:` header list.** `processed_list` detects the disagreement and names the graph's `planDone` count as the source of truth, but leaves the fix to the author (see D6). Two candidates: teach the autofix to rewrite the line from the graph, or leave it to the emitter and treat the YELLOW as the guard. The emitter route is already in place and cost nothing; the audit route would make it unforgettable. Worth deciding, not urgent.

## §5 — Plan for S270

### §5.1 — Bootstrap (auto-authorized)

From the canonical directory, read the latest handoff in `handoffs/`, then run `python gem_audit.py --files-dir . --autofix` immediately, without asking. Expect a clean run with **no autofix write**, two INFO, plus **`[NCD CENSUS]`** (Active 142 · Stubs 5 · Retired 25 · Deleted 5 · Unknown 0 · Total 177). Any RED is a halt; surface YELLOW for decision.

**Mid-session `hash_verify` RED is normal.** The halt rule is about RED at **bootstrap**.

### §5.2 — Standing priority: finish the NCDs (Tom, S260)

**Check `sources/` before naming any NCD target** (Tom, S267) — cross-reference `^NCD\s+<section>` over `sources/*.pdf`, tolerating all three filename forms (§4 item 54), against `planDone` read from the **graph**.

Measured at the S269 close: **1 of 167 NCD sections in `sources/` lacks a `planDone` individual.** For the first time since S267, a target exists on disk:

| Policy | Note |
| :--- | :--- |
| **NCD 220.6.8** — FDG PET for Myocardial Viability | **The obvious S270 target.** `sources/NCD 220.6.8 v1.pdf`, ncdid=298. **Single-version and still live** — the Other Versions table lists only Version 1, 01/28/2005 – N/A, "You are here", so the supplied rendition is the complete set under SKILL.md §Pre-Extraction Requirement 5 and the S268 D2 halt does not apply. **The family's only cardiac section and its only substantive survivor:** created out of §220.6 by TN 31 on the same 2005-01-28 / 2005-04-18 date pair as its ten oncologic siblings, but never swept into 220.6.17, so it still carries real coverage content (hibernating myocardium, revascularization candidacy). Expect an Item/Service Description, an NCA (**CAG-00098N**), ICD-10 quarterly maintenance transmittals under S169(a), and — unlike every S268/S269 sibling — actual rules and clinical concepts. |

Every **other** remaining NCD still needs a rendition from Tom. The former list (NCD 20.4, 210.3, 280.13, 80.7, 10.1, 220.12) is unchanged and none of them is in `sources/`.

The FDG PET oncologic family is complete: 220.6 and subsections .2, .3, .4, .7, .10, .11, .13, .14, .15, .17, .20, plus .5 and .6 this session. **220.6.8 is the last section of §220.6 not yet extracted.**

### §5.2a — After the NCDs

§4 items 53, 54, 57, 58 are small and each prevents a recurrence. Then 52 (at the checkpoint), 4, 37, 38, 40, 46, 47, 49. Items 35 and 36 also stand. `sources/` holds **47 non-NCD documents not yet `planDone`** — the deferred non-NCD phase, available if Tom redirects, **not** to be started unprompted.

### §5.3 — Do not

- `policies_processed` is **189** — advance it only on a genuine new extraction/promotion.
- Do not re-hardcode the audit namespace; do not re-add the frozen `LLM_ANNOTATED_VOCAB_CLASSES` tuple; do not promote the PyYAML lazy import to module level; do not split `SKILL.md` without agreement.
- `owl:versionInfo`, the `# Produced:` header date, and Tom-supplied `dc:source` URLs remain untouched.
- **Do not retain a removed rule because it is negative (S269 D3), because it delegates (S269 D2), or because there is a lot of it (S267 D1).** All three temptations were tested and refused this session.
- **Do not join a removed exclusion to a live exception across documents (S269 D4).** Core Principles 8 and 10.
- **Do not take a policy's title from a transmittal that cites it (S269 D5).** TN 106 says "Lymphoma Cancer" and "Melanoma Cancer"; neither section does.
- **Do not leave the `# Policies processed:` header list to the close (S269 D6).** It is part of the extraction; the emitter owns it.
- **Do not propose a third causal reading of the benefit-category round-trip (S268 D1, §4 item 56).** Two have been falsified; it is now nine of ten and still explains nothing.
- **Do not extract from a superseded rendition when the live one is missing (S268 D2).** Halt and ask. Note that a policy with a *single* version is not this case — see NCD 220.6.8 in §5.2.
- **Do not drop a reference because the text citing it was removed (S268 D3).** The S152 corollary covers concepts, not references.
- **Do not split a table row into per-cell rules (S268 D4), and do not collapse a decision table into one rule.**
- **Do not mint a provenance paragraph as a rule (S268 D5).**
- **Do not mint a near-duplicate concept over an article (S268 D6)** — but do mint over a word change (S156).
- **Do not lower `CIM_MAX_TN` (S267 D4).** Raise only on a rendition; read a CIM-token RED as a question about the ceiling first.
- **Do not mint a transmittal because it is known to exist (S267 D4).** S131 mints what is *referenced* — `cr6753` was declined three times this session on exactly that ground.
- **Do not assert `sourceAvailability` from the archive-line pattern (S267 D5).**
- **Do not duplicate a transmittal across a differing CR or effective date within one manual (S267 D3).**
- **Do not read a cumulative revision history as the complete reference set (S267 D7).**
- **Do not link a mention within a mention (S264 D2).** TN 110 and CR 6753 were excluded at all three S269 policies.
- **Do not treat revision-history volume as evidence of codeable content (S268).**
- **Do not collapse `predicate_target_sort` to a single tier (S261).** V110/V111 guard both directions.
- **Do not re-introduce the literal-matching bug in `check_predicate_ordering` (S262 D7).** V112 pins it.
- **Do not restore the ambiguous block regex (S266 D4).** V115 pins it; the failure mode is a silent multi-minute hang.
- **Do not remove `block_terminator` as redundant with `predicate_order` (S266 D4).**
- **Do not treat a clean rdflib triple-count as sufficient verification of emitted bytes (S266 D5).**
- **Do not treat the source's own lettering as the rule count (S266 D2).** Grammatical dependence keeps a condition whole; a modal shift breaks it apart.
- **Do not carry a family finding forward untested (S266 D1).**
- **Do not treat a same-stem reuse hit as identity (S265 D2).** Read the existing description first.
- **Do not assume a transmittal number identifies a document (S263 D2), in either direction (S264), or within one policy's own version set (S267 D2).**
- **Do not chase an authoritative CMS NCD index to measure remaining work (item 41).**
- **Do not count graph facts, or file structure, with a regex over the TTL (item 43, S266).** Use rdflib.
- **Do not name an NCD target without cross-referencing `sources/` first (Tom, S267).**
- **Do not reprocess any already-extracted NCD until every NCD is processed (Tom, S260).**
- **Do not delete anything from `sources/`, and do not delete the Dropbox originals** (Tom, S260).
- **Do not read other policy-PDF locations.** `Dropbox\Projects\HOO2pilot\policies` is the sanctioned source directory.
- **Push at session close, not before.** The remote is the only off-machine copy of `sources/`.
