# GEM Policy-Extraction Handoff — Session 266 (2026-08-06)

## §1 — Canonical files (post-close state)

Hashes are md5 over the frozen output set; **M** marks a file changed this session. The canonical set is **15 files**.

| File | md5 | size | S266 |
| :--- | :--- | :--- | :--- |
| `GEM_ontology.ttl` | `5a77000e27e2ce03d6e2e0596e716934` | 340257 |  |
| `GEM_policy_instances.ttl` | `91cc6c2951ce4737fa8390044dcb2029` | 6022868 | **M** |
| `GEM_code_group_instances.ttl` | `10a70c01175dcf714a4bd8307bd07eeb` | 25942 |  |
| `cpt.ttl` | `351aa816b978ec63a6800feb50bfb5c4` | 35223 |  |
| `SKILL.md` | `7bdfed0f34d53a6666f9e4aada020b14` | 285703 | **M** |
| `gem_reference.md` | `4ddd97d8b96dec2b4aff8e0318376c46` | 120152 |  |
| `gem_rule_categories.md` | `18f7f0df82d386c237369b3c33f7a68a` | 1506608 | **M** |
| `gem_edit_log.md` | `5fd6b9e859d23141809f2d6a1c6b3225` | 157695 | **M** |
| `gem_structured_rule_guide.md` | `5dc562fdf25cdd7a492969be2b82fee5` | 60817 |  |
| `gem_turtle_style_guide.md` | `0c82c21cb54232de2c731fb1dcfce117` | 26524 |  |
| `manifest_format.md` | `24d134579244454795e39b2be1ce80d3` | 26227 |  |
| `policy_worklist.json` | `192ea7355006b51b575361cc4bea2283` | 322732 | **M** |
| `gem_llm_annotations.json` | `ae89620445889e7137e2bdc5ba4cd669` | 7213 |  |
| `worklist_schema.md` | `2519964abbdba260c621a6a5e9f8318b` | 16521 |  |
| `gem_audit.py` | `30045ff1db7e488bc7464f6aa45e3183` | 339158 | **M** |

## §2 — Work completed in S266

**One extraction and three repairs, two of which the extraction itself uncovered.** NCD 220.6.13 is the fifth FDG PET sibling and **the first one that kept its content** — 18 rules against the four siblings' 4 between them. Writing it to the documented file layout exposed a long-running banner drift; running the audit over it exposed a latent catastrophic-backtracking hang; and diagnosing that exposed an emitter bug of my own. No schema change (`GEM_ontology.ttl` byte-identical).

**Graph movement:** `policies_processed` **180 → 181**. Instances triples **53,792 → 54,331** (+539). Workflow `planDone` **180 → 181**, `planPromote` **759 → 763**, `planNone` **16** unchanged. NCD census **Active 140 → 141**, Stubs **6** (unchanged), Retired 18, Deleted 5, Unknown 0, **Total 169 → 170**. The four new stubs are a transmittal, two NCAs and a change request — **none is a gem:NCDpolicy**, so the census Stubs bucket does not move. Clinical concepts **2,957 → 2,998**; policy rules **1,977 → 1,995**; provider credentials **127 → 138**; healthcare settings **26** unchanged. `referencesPolicy` **1243 → 1254**, `revisesPolicy` **279 → 283**, `revisedByPolicy` **0** (invariant). `referencesChangeRequest` **142**. Both INFO queues unchanged: `source_availability_unverified` **49**, `policy_effective_date_v1` **24**.

**`sources/` held still for the first time in six sessions** — no new PDFs arrived mid-session or during the close.

### (a) The extraction

| Policy | Rules | Concepts | Credentials | Refs / new stubs | Δ |
| :--- | ---: | :--- | :--- | :--- | ---: |
| **NCD 220.6.13** FDG PET for Dementia and Neurodegenerative Diseases | 18 | 41 mint, 7 reuse | 11 mint, 1 reuse | 11 + 3 CRs / 4 | +539 |

Three-version **active** NCD, V3 effective 2009-04-03. `policyEffectiveDate` **2004-09-15** / `policyImplementationDate` **2004-10-04**, both V1's per S192; `KNOWN_V1_DATES` row added per S260 D8. 1 setting (reuse). 0 codes, 0 code groups.

### (b) Two of the four S264 family findings do not hold (§3 D1)

They were **tested rather than carried**, as §5.2 required, and half of them failed:

| S264 family finding | Holds here? |
| :--- | :--- |
| Dates anchor to 2005-01-28 / 2005-04-18 | **No.** TN 24 created this section in **2004**, a year before TN 31 carved out the other four. |
| Benefit-category round-trip (V1 category → V2 "No Benefit Category" → V3 restore) | **No.** All three versions read Diagnostic Tests (other). |
| Cross Reference prints `§220.6` correctly | Yes — a fourth independent confirmation that `ncd220.6.15`'s lone `§200.6` is a CMS typo. |
| A transmittal's edges are read per citing document (S264 D2) | Yes, and decisively — see (c). |

The round-trip result is the more useful one: it shows the pattern tracked the **replacement** of those sections, not TN 106/108/120. A policy that was never replaced never lost its category. That retires the reading recorded at `ncd220.6.4`.

### (c) TN 106 is not linked here, though all four siblings link it (§3 D2)

In the siblings' revision histories TN 106 carries its own dated entry. In this document it appears only inside TN 108's narrative — *"rescinds and replaces Transmittal 106"* — a mention within a mention, the same call as TN 110 and CR 6753 inside TN 120's entry. **S264 D2 doing real work:** the same transmittal, five citing documents, and the answer genuinely differs between them.

### (d) Three repairs, and one lesson under all three (§3 D4)

| Repair | Extent | Verified by |
| :--- | :--- | :--- |
| Missing per-policy banners | **21 of 23** restored (2 deferred, §4 item 52) | rdflib set-diff +539 / −0 |
| Block terminators missing their space | **75**, all mine, 0 elsewhere | rdflib set-diff +539 / −0 |
| `check_predicate_ordering` catastrophic backtracking | >25 min → **18 s** whole-audit | 6154 blocks both patterns, identical subject sets; V113–V115 |

**The banner count was measured three times and was wrong twice** — 6, then 18, then 23. The first pattern matched only the `# POLICY: X --` form and missed two older era-forms. The second was taken over a planDone list scraped from the workflow-state **text region**, whose regex stopped at the first `# ---` inside the block and returned **166 of 181** policies. Reading planDone from the **graph** gave the true figure. Three passes, three under-counts, one cause: an instrument that pattern-matches the file instead of asking rdflib. That is §4 item 43's rule, and it applies to file structure exactly as it applies to graph facts.

## §3 — Decisions (S266)

- **D1 — a family pattern is a hypothesis about the documents, not a property of the family.** Two of four S264 findings failed on the fifth sibling. Both failures were informative: the date break located the section's real creation transmittal (TN 24, 2004), and the benefit-category result reattributed the round-trip from the transmittal to the replacement. **Carry forward:** test sibling findings against each new member; a finding that survives a genuine test is worth more than one carried four times.
- **D2 — source enumeration is evidence about granularity, not a decision procedure (NCD 220.6.13 B1+B2, Tom).** Condition `f` stayed **one** rule and condition `e` **split into two**, both against the source's own lettering. What separates them: `f`'s parenthetical carve-out is grammatically dependent on the gate it excepts (its subject *"the indication"* has no antecedent once detached), while `e`'s two sentences differ in **modality** — flat indicative *"is performed in"* against soft *"should be done by"*. Merging a soft expectation into a mandatory neighbour destroys the distinction corollary #3 exists to preserve (the L36524 R1 precedent).
- **D3 — the S39 slash-rule extends to a comma-or list of roles (B4, Tom).** *"an expert in nuclear medicine, radiology, neurology, or psychiatry"* mints **four** credentials. The rationale is the rule's own: the roles are explicit alternatives, any one satisfies the condition alone, and different people fill them on different claims. Not reused onto `credentialRadiologist`/`credentialNeurologist` — *"expert in radiology"* is not *"radiologist"*, and *expert* asserts an attainment the bare specialty name does not.
- **D4 — a hang is not a diagnostic.** `check_predicate_ordering` ran **over 25 minutes without returning and produced no finding** on a block whose terminator was missing one space. It presented as a slow machine, and I compounded it by launching three overlapping audit runs and first misreading the CPU contention as the cause. The hardened regex cannot hang; the new `block_terminator` check reports what the hardened regex now silently skips. **Neither is sufficient alone.**
- **D5 — valid Turtle is not sufficient validation.** `dc:source gemi:p.` parses, and the S157 triple-count verification passed clean at +539/−0 while 75 blocks carried the defect. A check that reads the graph cannot see a defect that lives in the bytes; that is precisely the gap `block_terminator` fills.

## §4 — Open items

Items 1–51 carry from S265 unless restated.

1. **Cadence checkpoint — next at 200.** `policies_processed` is **181**; 19 out. Not due.
2. **LCD/Article V1-date research — 18 candidates.** `policy_effective_date_v1` INFO = **24**, unchanged.
3. **CIM stub source availability — 49**, unchanged.
4. **Era-gate mistokens — retrospective sweep still pending Tom.** Not exercised in S266 (`tn24NCD` is 2004, post-crystallization).
5.–44. **Carry unchanged.**
45. **RE-MEASURED (S266), AND IT HELD STILL.** `sources/` holds **333 PDFs, 260 NCD-named across 158 sections, 0 unparsed**, and **0 sections without a `planDone` individual**. First session in six with no mid-session movement. Keep re-measuring; do not carry this answer forward. **Measure planDone from the graph, not from the workflow-state text region** — the region regex under-reports (166 of 181), which is how this session's banner count went wrong twice.
46. **`predicate_order` vs `predicate_ordering` name mismatch.** Still live, and now joined by `block_terminator`, whose key and category **do** agree. Worth fixing while the neighbourhood is fresh.
47. **Stub `dc:source` convention is inconsistent.** S266 minted 4 stubs: `tn24NCD` carries a `dc:source` (its Coverage Transmittal Link is printed in V1), while `cag00088N`, `cag00088R` and `cr3426` carry none (no link is printed). That is the same split the item describes, now with a fresh instance of each side.
48. **CLOSED (S264).**
49. **Carry, with the S265 caution.** Not exercised; NCD 220.6.13's reuses were exact-label matches.
50. **CLOSED (S265).**
51. **CLOSED (S266) — by extracting its subject.** NCD 220.6.13 is in the graph.

52. **NEW (S266) — `gemi:a55426` and `gemi:a58247` are extracted policies living inside another policy's stub section.** Each was minted as a stub and later fully extracted **in place**, so each sits under an enclosing `POLICY STUBS (cited by …, not yet extracted)` sub-banner its own content contradicts: A55426 under L33797's, A58247 under A55426's. **This is the S147 shape** — a block contradicting its header — not a missing banner, and inserting a `# POLICY:` banner would leave the false enclosing header standing. The fix is relocation to top-level sections, which moves large regions of the file, so it was deliberately not folded into S266's banner pass. Tom is aware; needs a decision on whether to relocate.
53. **NEW (S266) — no audit check covers banner presence.** The whole class survived 100+ sessions and every GREEN close because nothing looks. A `banner_presence` check keyed on planDone policies would be cheap and would have caught all 23. Note the trap the same session demonstrated three times: such a check must read planDone **from the graph**, and must tolerate all three era-forms (`# POLICY: X --`, `# X --`, `# === POLICY: X --`) or normalise them first.

## §5 — Plan for S267

### §5.1 — Bootstrap (auto-authorized)

From the canonical directory, read the latest handoff in `handoffs/`, then run `python gem_audit.py --files-dir . --autofix` immediately, without asking. Expect a clean run with **no autofix write**, two INFO (`source_availability_unverified` **49**; `policy_effective_date_v1` **24**), plus **`[NCD CENSUS]`** (Active 141 · Stubs 6 · Retired 18 · Deleted 5 · Unknown 0 · Total 170). Any RED is a halt; surface YELLOW for decision.

**Mid-session `hash_verify` RED is normal** — it means canonical files have been edited since the previous handoff's §1 table was computed. The halt rule is about RED at **bootstrap**.

**The audit now runs in ~18 seconds.** If it takes minutes, something is wrong — do not wait it out, and do not start a second run alongside the first.

### §5.2 — Standing priority: finish the NCDs (Tom, S260)

**Re-measure `sources/` against the graph before planning** (§4 item 45), with the corrected filename regex, **printing the parsed-section and unparsed counts**, and reading planDone **from the graph**.

The FDG PET family is complete for the renditions on hand. **`NCD 220.6` and `NCD 220.6.17` remain the high-value promote targets** — both cited by all five extracted siblings; 220.6 is the parent the family was carved out of and now carries inbound `revisesPolicy` from `tn31NCD`, and 220.6.17 is the section that replaced four of them. `NCD 220.6.13` is the one sibling 220.6.17 did **not** replace.

Then the five stubs needing renditions from Tom:

| Policy | Note |
| :--- | :--- |
| **NCD 20.4** | Implantable Automatic Defibrillators (ICDs); CED with registry requirements; expect multi-version |
| **NCD 210.3** | Colorectal Cancer Screening Tests; extensive coding, long revision history; expect multi-version |
| **NCD 280.13** | TENS - RETIRED; counted under **Retired**, not **Stubs** |
| **NCD 80.7** | Cited by NCD 80.8 for excluded refractive procedures |
| **NCD 10.1** | Cited by NCD 80.8's bundling rule |

### §5.2a — After the NCDs

§4 items 52 and 53 are both fresh and both small-to-medium; 53 is the one that prevents recurrence. Then items 37, 38, 40, 46, 47, 49. Items 35 and 36 also stand.

### §5.3 — Do not

- `policies_processed` is **181** — advance it only on a genuine new extraction/promotion.
- Do not re-hardcode the audit namespace; do not re-add the frozen `LLM_ANNOTATED_VOCAB_CLASSES` tuple; do not promote the PyYAML lazy import to module level; do not split `SKILL.md` without agreement.
- `owl:versionInfo`, the `# Produced:` header date, and Tom-supplied `dc:source` URLs remain untouched.
- **Do not collapse `predicate_target_sort` to a single tier (S261).** V110/V111 guard both directions.
- **Do not re-introduce the literal-matching bug in `check_predicate_ordering` (S262 D7).** V112 pins it.
- **Do not restore the ambiguous block regex in `check_predicate_ordering` (S266 D4).** V115 pins it, and the failure mode is a silent multi-minute hang, not a finding.
- **Do not remove `block_terminator` as redundant with `predicate_order` (S266 D4).** They are complementary by construction: the regex cannot hang, and this cannot be silent.
- **Do not treat a clean rdflib triple-count as sufficient verification of emitted bytes (S266 D5).** Valid Turtle can still be wrong Turtle.
- **Do not split a single source unit that says *covered under X / not covered under Y* (S262 D6), or that asserts two things about one subject (S265 D1).** Keep it whole and dual-type it.
- **Do not treat the source's own lettering as the rule count (S266 D2).** Grammatical dependence keeps a condition whole; a modal shift breaks it apart.
- **Do not retain removed content because it looks substantive (S264 D1).** Check only whether the removal is reported.
- **Do not carry a transmittal's edges across from a sibling policy (S264 D2).** Read its entry in the document in hand — S266 is the clearest instance yet.
- **Do not carry a family finding forward untested (S266 D1).** Two of four failed on the fifth sibling.
- **Do not treat a same-stem reuse hit as identity (S265 D2).** Read the existing concept's description first.
- **Do not assume a transmittal number identifies a document (S263 D2), in either direction (S264).**
- **Do not trust an exact-prefLabel reuse search alone (S263 D5).** The forward URI pre-flight is the guarantee.
- **Do not conclude a text layer is damaged without re-extracting with `-enc UTF-8` (S262, S264 D5), and do not assume an apparent defect is tooling either (S263 D9).** Check.
- **Do not chase an authoritative CMS NCD index to measure remaining work (item 41).**
- **Do not read the census `Stubs` count as the promote queue, and do not count graph facts with a regex over the TTL (item 43) — nor file structure (S266).** Use rdflib.
- **Do not carry forward a previous session's "`sources/` is fully extracted" answer (item 45) — and do not trust a re-measure whose parsing you have not checked (item 50).** Print the section and unparsed counts.
- **Do not reprocess any already-extracted NCD until every NCD is processed (Tom, S260).**
- **Do not delete anything from `sources/`, and do not delete the Dropbox originals** (Tom, S260).
- **Do not read other policy-PDF locations.** `Dropbox\Projects\HOO2pilot\policies` is the sanctioned source directory.
- **Push at session close, not before.** The remote is the only off-machine copy of `sources/`.
