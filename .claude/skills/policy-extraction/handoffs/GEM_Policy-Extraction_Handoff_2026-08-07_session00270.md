# GEM Policy-Extraction Handoff — Session 270 (2026-08-07)

## §1 — Canonical files (post-close state)

Hashes are md5 over the frozen output set; **M** marks a file changed this session. The canonical set is **15 files**.

| File | md5 | size | S270 |
| :--- | :--- | :--- | :--- |
| `GEM_ontology.ttl` | `5a77000e27e2ce03d6e2e0596e716934` | 340257 |  |
| `GEM_policy_instances.ttl` | `300053684cc199fefc68f55d0f1b4fef` | 6253838 | **M** |
| `GEM_code_group_instances.ttl` | `10a70c01175dcf714a4bd8307bd07eeb` | 25942 |  |
| `cpt.ttl` | `351aa816b978ec63a6800feb50bfb5c4` | 35223 |  |
| `SKILL.md` | `385de60173a9fcad71cf538ec3950bc0` | 285703 | **M** |
| `gem_reference.md` | `bd2a8164afcf31ccfeda5dc242fd6f63` | 121808 |  |
| `gem_rule_categories.md` | `404f7e556dfa1f5799693463adb3c137` | 1586561 | **M** |
| `gem_edit_log.md` | `1598a88f44ce4848e64514c27a82a4b5` | 187890 | **M** |
| `gem_structured_rule_guide.md` | `5dc562fdf25cdd7a492969be2b82fee5` | 60817 |  |
| `gem_turtle_style_guide.md` | `0c82c21cb54232de2c731fb1dcfce117` | 26524 |  |
| `manifest_format.md` | `24d134579244454795e39b2be1ce80d3` | 26227 |  |
| `policy_worklist.json` | `99d331370f87c7f8bb0a8888968d87de` | 322732 | **M** |
| `gem_llm_annotations.json` | `ae89620445889e7137e2bdc5ba4cd669` | 7213 |  |
| `worklist_schema.md` | `2519964abbdba260c621a6a5e9f8318b` | 16521 |  |
| `gem_audit.py` | `ae3025e53c1f2309aec856ed3a572079` | 340169 | **M** |

## §2 — Work completed in S270

**Three extractions, all fresh direct mints, and the family's shape finally broke.** NCD 220.6.8 (Myocardial Viability) and NCD 220.6.9 (Refractory Seizures) are the FDG PET family's **two non-oncologic survivors** — carved out of §220.6 by TN 31 in 2005 like their siblings, but never swept into 220.6.17 by TN 106, which took only the oncologic sections. Both are **Active**, both carry real rules and concepts, and both are **single-version**. NCD 220.6.12 (Soft Tissue Sarcoma) returns to the replacement shape and closes it. No schema change (`GEM_ontology.ttl` byte-identical).

**Graph movement:** `policies_processed` **189 → 192**. Instances triples **55,561 → 55,816** (+255). Workflow `planDone` **189 → 192**; `planPromote` **803** and `planNone` **17** unchanged. NCD census **Active 142 → 144**, **Retired 25 → 26**, **Total 177 → 180**; Stubs **5**, Deleted **5**, Unknown **0** unchanged. Clinical concepts **3,027 → 3,041** (+14, the first mints since S268); policy rules **2,037 → 2,047** (+10); credentials **138** and settings **26** unchanged. `referencesPolicy` **1418 → 1439**, `revisesPolicy` **333 → 340**, `revisedByPolicy` **0** (invariant), `referencesChangeRequest` **184 → 189**.

**`sources/` gained 4 PDFs** (363 → 367). Re-measured at close: **367 PDFs, 294 NCD-named across 169 sections, 0 unparsed, and 0 sections without a `planDone` individual** — back to the S267/S268 state. See §5.2.

### (a) The extractions

| Policy | Rules | Concepts | Refs / new stubs | Δ |
| :--- | ---: | :--- | :--- | ---: |
| **NCD 220.6.8** FDG PET for Myocardial Viability — **ACTIVE** | **6** | 11 mint, 4 reuse | 6 + 2 CRs / **0** | **+148** |
| **NCD 220.6.9** FDG PET for Refractory Seizures — **ACTIVE** | 3 | 3 mint, 1 reuse | 3 + 1 CR / **0** | +65 |
| **NCD 220.6.12** FDG PET for Soft Tissue Sarcoma — RETIRED | 1 | 0 | 12 + 2 CRs / **0** | +42 |

All three S157-verified against a predicate histogram derived from each emitter's own data structures: **0 mismatches, three for three, 0 triples removed**. **Zero new stubs across the whole session** — every one of the 26 reference targets already existed.

**220.6.8 and 220.6.9 take no `KNOWN_V1_DATES` row.** Both are `policyVersion` 1, and S260 D8 fires only above V1; their dates are their own rather than anchored to an earlier rendition. 220.6.12 took a row as usual.

### (b) `sources/` filename convention — the versioned form is now a third of NCD arrivals

Census **166 dated · 94 undated · 34 versioned** (294 NCD-named). All four S270 arrivals use `NCD X vN.pdf`.

### (c) Three orphan NCAs recovered, all by the same rule

`cag00098N` (at 220.6.8) and `cag00099N` (at 220.6.12) were both minted at **S267 from NCD 220.6's Version 1 only** — NCAs existing nowhere but a superseded rendition, and only reachable because Tom's S267 B5 call scoped references across all supplied versions. Both are titled for the very sections that cite them here (*"…for Myocardial Viability"*, *"…for Soft Tissue Sarcoma (STS)"*). With `cag00095N` at 220.6.11, **three of the five orphan NCAs are now recovered**.

## §3 — Decisions (S270)

- **D1 — a policy with only one version is not the S268 D2 halt case.** 220.6.8 and 220.6.9 each publish a single version with no ending effective date and *"You are here"*. SKILL.md §Pre-Extraction Requirement 5 is satisfied by the one rendition — that is the complete set, not a gap. **S268 D2 is about a missing *live* rendition, not about a policy that has only ever had one.** Stated explicitly because the two situations look identical in a `sources/` listing (one file) and are opposite in what they require.
- **D2 (220.6.8 B1, Tom-confirmed) — the scanner-type provision splits from its coverage grant, and the split turns on dates, not grammar.** Each numbered item holds a coverage grant *and* a statement of which PET scanners qualify. **S266 D2 does not decide it** — no grammatical dependence to preserve, no modal shift to break. What decides it is that item 1's grant runs 2001-07-01 → 2002-09-30 while its scanner clause runs *"as of January 1, 2002"* with **no end date**: folded in, an open-ended equipment rule would be trapped inside a rule that expired. Counter-argument recorded: the source's own numbering makes each item one unit, as S268 D4 held for a table row; against it, a table row is a single grammatical unit read across columns, a numbered item here is a paragraph of independent sentences.
- **D3 (220.6.9 B1, Tom-confirmed) — "covered only for X" is a rule but is not `nonCoverage`.** It earns its own rule because it adds exclusivity the grant does not state. It takes `coverageScope` **alone** because it names nothing as non-covered. **The matched pair is the useful artifact:** `ncd220.6.8_r5`, written hours earlier, *did* earn `nonCoverage` because its source said outright that *"a follow up SPECT test is not covered"* — a named, non-covered service. **The discriminator is whether the source names the excluded thing, not whether exclusion is implied.** Supplying the negative from the word *"only"* would cross the Core Principle 8 line.
- **D4 (220.6.8 B2, Tom-confirmed) — the composite is the concept.** `conceptDysfunctionalButViableMyocardialTissue` is minted whole; `conceptViableMyocardialTissue` is not. The bare form never stands on its own in the source — the `conceptHypertension` / *"uncontrolled hypertension"* (NCD 110.21 B3) and `conceptLarynx` / *"permanently inoperative larynx"* (NCD 50.2 B6) declines. The contrast is also the clinical point. **83 of the corpus's 3,027 concept labels already carried an internal conjunction**, so the ungainly label is not novel, and §2f forbids the extractor tidying the source's wording.
- **D5 (220.6.9 B2, Tom-confirmed) — both layers of a two-deep nested phrase are minted, and the third layer is not.** *"Localization of a focus of refractory seizure activity"* yields `conceptFocusOfRefractorySeizureActivity` and `conceptRefractorySeizureActivity` — both prepositional objects, both clearing the S264 grammatical test, and clinically different things (target versus condition). *"Localization"* is declined as an action word whose content is supplied entirely by its object. **The counter-argument is recorded as stronger here than in the cited precedents** (`conceptSpeechAid`/`conceptElectronicSpeechAid`, `conceptEndoscopy`/`conceptEndoscopicProcedure`): in those the source named both forms in **separate** mentions, whereas here they are nested and never mentioned apart. What holds the decision is that the chain is only two deep and both layers are substantive.
- **D6 — a contrary precedent found *after* approval was surfaced rather than absorbed.** At 220.6.8 the extractor declined *"a FDG PET study"* as the source varying its own noun, Tom approved, and only then did `conceptFDGPositronEmissionTomographyScan`'s `workflowDescription` turn up recording that **NCD 220.6.13 deliberately minted three tracer-tagged granularities** *"each … separately under the catalog-phrasings rule"*. That precedent's condition was met, so the decline was **reversed before the write** and `conceptFDGPETStudy` minted. The rule this instantiates: **an approved-but-weaker reading is still the wrong reading**, and the corpus's own recorded practice outranks a fresh judgement. (The `conceptPositronEmissionTomographyScan` reuse in the same borderline was unaffected and stands on S268 D6 — that individual's description declares it *"the bare modality"* and its prefLabel carries the abbreviation inline.)
- **D7 — a hyphen is not a distinct phrasing.** 220.6.9 writes *"FDG-PET"*; `conceptFDGPET` is reused. Typography is strictly less than the definite article S268 D6 already reused across, and this is **not** the D6 case above: NCD 220.6.13's three granularities are three different *noun phrases*, not one phrase punctuated two ways.
- **D8 — the removal rule met its hardest case and held (220.6.12).** V1 was not a coverage grant with an exclusion inside it — **the whole policy was a national non-coverage determination**, and V1 is consequently the *shortest* of the three renditions, reversing the family pattern. V2 reports the replacement, so S151 does not fire and S152 takes the concepts: 0 rules, 0 concepts, **soft tissue sarcoma itself not minted**. This is **S269 D3 scaled from one sentence to an entire policy**. If any case justified an exception this was it; the discriminator was never how decision-relevant the content would be, only whether the live version retains it.
- **D9 — a two-instance generalisation from S269 is now bounded.** The S269 register called TN 106's *"Lymphoma Cancer"* / *"Melanoma Cancer"* interpolation *"a habit rather than a typo"*. TN 106's entry at 220.6.12 names its section **correctly**, so the quirk is confined to those two entries and is not a property of TN 106's revision-history text. S266 D1 firing against a generalisation made one session earlier — **the entry that stated the pattern is left unamended**, per the S268 D1 practice of not rewriting what was true of the documents at the time.

## §4 — Open items

Items 1–58 carry from S269 unless restated.

1. **Cadence checkpoint — next at 200.** `policies_processed` is **192**; 8 out. Not due, but close: the next session or two will reach it. The item-52 agenda entry stands.
2. **LCD/Article V1-date research — 18 candidates.** `policy_effective_date_v1` INFO unchanged.
3. **CIM stub source availability.** `tn106CIM` and `tn113CIM` remain the two strong `sourceUnobtainable` candidates awaiting Tom's direction.
4. **Era-gate mistokens — retrospective sweep still pending Tom.** No new collisions in S270.
5.–51. **Carry unchanged.**
52. **DEFERRED to the 200-policy checkpoint (Tom, S266).** Now 8 policies out. Nothing was promoted this session, so no relocation was in scope.
53. **No audit check covers banner presence.** Unchanged; all three S270 sections were fresh top-level mints with their own banners.
54. **`sources/` filename convention.** Census now **166 dated · 94 undated · 34 versioned** (294 NCD-named). The versioned form is now roughly a third of NCD arrivals and every arrival since S268 has used it.
55. **`gemi:ncd220.12` bare-identifier `prefLabel`.** **It now has a second citer** — NCD 220.6.8's Cross Reference names *"SPECT (§220.12)"* directly. The prefLabel is still bare and still correct: S268 D7's discriminator is availability of the **cited** document, and no rendition of NCD 220.12 exists in `sources/`.
56. **The benefit-category round-trip has no known cause.** Now **ten of eleven** replaced sections. Two readings falsified. Do not propose a third without evidence from outside the 220.6 family.
57. **TN 13401's "update the Policy section" wording** still awaits its own extraction. Unchanged.
58. **No autofix maintains the `# Policies processed:` header list.** The emitter-owned fix from S269 D6 worked cleanly for all three S270 extractions — `processed_list` never fired. The audit-side option remains open and remains not urgent.
59. **NEW (S270) — the two NCA stubs recovered this session are now doubly-cited but still `planPromote`.** `cag00098N` and `cag00099N` each have a live citer and a title that names their subject exactly, but neither has a source URL: the renditions list NCAs by title and identifier only, without a link (the `cag00094N` precedent). They are extractable only if Tom supplies URLs. Not urgent — but they are now the best-characterised NCA stubs in the graph, and worth naming if the non-NCD phase ever opens.

## §5 — Plan for S271

### §5.1 — Bootstrap (auto-authorized)

From the canonical directory, read the latest handoff in `handoffs/`, then run `python gem_audit.py --files-dir . --autofix` immediately, without asking. Expect a clean run with **no autofix write**, two INFO, plus **`[NCD CENSUS]`** (Active 144 · Stubs 5 · Retired 26 · Deleted 5 · Unknown 0 · Total 180). Any RED is a halt; surface YELLOW for decision.

**Mid-session `hash_verify` RED is normal.** The halt rule is about RED at **bootstrap**.

### §5.2 — Standing priority: finish the NCDs (Tom, S260)

**Check `sources/` before naming any NCD target** (Tom, S267) — cross-reference `^NCD\s+<section>` over `sources/*.pdf`, tolerating all three filename forms (§4 item 54), against `planDone` read from the **graph**.

Measured at the S270 close: **0 of 169 NCD sections in `sources/` lack a `planDone` individual.** As at S267 and S268, **every remaining NCD target needs a rendition from Tom before it can be planned.** Do not name a target without checking first.

**The FDG PET family is complete.** §220.6 and every subsection now in the graph: .2, .3, .4, .5, .6, .7, .8, .9, .10, .11, .12, .13, .14, .15, .17, .20. Eleven replaced-and-retired, two Active non-oncologic survivors (.8, .9), the keystone (.17), the never-replaced .13, and .20.

Standing candidates, **none of which is in `sources/`**: NCD 20.4 (Implantable Automatic Defibrillators; CED with registry requirements), NCD 210.3 (Colorectal Cancer Screening; extensive coding), NCD 280.13 (TENS - RETIRED), NCD 80.7, NCD 10.1, NCD 220.12 (SPECT — now doubly cited, §4 item 55).

### §5.2a — After the NCDs

§4 items 53, 54, 57, 58, 59 are small and each prevents a recurrence. Then 52 (at the 200 checkpoint, now 8 policies out), 4, 37, 38, 40, 46, 47, 49. Items 35 and 36 also stand. `sources/` holds **73 non-NCD PDFs** — the deferred non-NCD phase, available if Tom redirects, **not** to be started unprompted.

### §5.3 — Do not

- `policies_processed` is **192** — advance it only on a genuine new extraction/promotion.
- Do not re-hardcode the audit namespace; do not re-add the frozen `LLM_ANNOTATED_VOCAB_CLASSES` tuple; do not promote the PyYAML lazy import to module level; do not split `SKILL.md` without agreement.
- `owl:versionInfo`, the `# Produced:` header date, and Tom-supplied `dc:source` URLs remain untouched.
- **Do not halt on a single-version policy (S270 D1).** One rendition with no ending effective date and "You are here" is the complete set. The S268 D2 halt is for a missing **live** rendition.
- **Do not type "covered only for X" as `nonCoverage` (S270 D3).** The source must name the excluded thing. `ncd220.6.8_r5` and `ncd220.6.9_r2` are the matched pair.
- **Do not decide a rule split on the source's numbering alone (S270 D2).** Check whether the sub-provision carries its own effective dates.
- **Do not mint a bare form that appears only inside a composite (S270 D4)** — and do not decline a nested layer that is itself a substantive clinical entity (S270 D5). The S264 grammatical test governs both.
- **Do not treat a hyphen as a distinct phrasing (S270 D7).** Do treat a different noun phrase as one (S270 D6, the NCD 220.6.13 three-granularities precedent).
- **Do not proceed on an approved reading after finding a contrary precedent (S270 D6).** Surface it; the corpus's recorded practice outranks a fresh judgement.
- **Do not retain a removed rule because it is a non-coverage determination (S270 D8), because it is negative (S269 D3), because it delegates (S269 D2), or because there is a lot of it (S267 D1).** Four temptations, four refusals, all recorded.
- **Do not join a removed exclusion to a live exception across documents (S269 D4).** Core Principles 8 and 10.
- **Do not take a policy's title from a transmittal that cites it (S269 D5)** — and note the "Cancer" quirk is confined to TN 106's `.5` and `.6` entries (S270 D9).
- **Do not leave the `# Policies processed:` header list to the close (S269 D6).** The emitter owns it.
- **Do not propose a third causal reading of the benefit-category round-trip (S268 D1, §4 item 56).** Ten of eleven, and it still explains nothing.
- **Do not drop a reference because the text citing it was removed (S268 D3).**
- **Do not split a table row into per-cell rules (S268 D4), and do not collapse a decision table into one rule.**
- **Do not mint a provenance paragraph as a rule (S268 D5).** *"(This NCD last reviewed …)"* goes to `gem:description`.
- **Do not mint a near-duplicate concept over an article (S268 D6)** — but do mint over a word change (S156) or a scope change (`conceptLeftVentricularDysfunction`, S270).
- **Do not lower `CIM_MAX_TN` (S267 D4).**
- **Do not mint a transmittal or change request because it is known to exist (S267 D4).** `cr6753` has now been declined six times.
- **Do not assert `sourceAvailability` from the archive-line pattern (S267 D5).**
- **Do not duplicate a transmittal across a differing CR or effective date within one manual (S267 D3).**
- **Do not read a cumulative revision history as the complete reference set (S267 D7).**
- **Do not link a mention within a mention (S264 D2).**
- **Do not treat revision-history volume as evidence of codeable content (S268).**
- **Do not link an existing concept merely because the reuse search surfaced it (S270, `conceptRefractoryEpilepsy`).** Three were found and refused at 220.6.9.
- **Do not collapse `predicate_target_sort` to a single tier (S261).** V110/V111 guard both directions.
- **Do not re-introduce the literal-matching bug in `check_predicate_ordering` (S262 D7).** V112 pins it.
- **Do not restore the ambiguous block regex (S266 D4).** V115 pins it.
- **Do not remove `block_terminator` as redundant with `predicate_order` (S266 D4).**
- **Do not treat a clean rdflib triple-count as sufficient verification of emitted bytes (S266 D5).**
- **Do not treat the source's own lettering as the rule count (S266 D2).**
- **Do not carry a family finding forward untested (S266 D1).** S270 D9 bounded one.
- **Do not treat a same-stem reuse hit as identity (S265 D2).** Read the existing description first.
- **Do not assume a transmittal number identifies a document (S263 D2), in either direction (S264), or within one policy's own version set (S267 D2).**
- **Do not chase an authoritative CMS NCD index to measure remaining work (item 41).**
- **Do not count graph facts, or file structure, with a regex over the TTL (item 43, S266).** Use rdflib.
- **Do not name an NCD target without cross-referencing `sources/` first (Tom, S267).**
- **Do not reprocess any already-extracted NCD until every NCD is processed (Tom, S260).**
- **Do not delete anything from `sources/`, and do not delete the Dropbox originals** (Tom, S260).
- **Do not read other policy-PDF locations.** `Dropbox\Projects\HOO2pilot\policies` is the sanctioned source directory.
- **Push at session close, not before.** The remote is the only off-machine copy of `sources/`.
